"""
Alert Engine — Event-Driven Automated Alert Generator for Disaster Relocation DSS.

Generates and persists alerts automatically upon system events:
- Risk changed to Critical
- New Red Zone Candidate
- Immediate relocation required
- Candidate site capacity below threshold
- No feasible relocation capacity
- Field verification conflicts with model
- Road reported blocked
- Dataset outdated
- Simulation produces major risk escalation

All alerts are stored in canonical database table `alerts`.
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.db.models import Alert, Habitation, CandidateSite
from app.db.repository import Repository


# Standard Severity Levels
SEVERITY_INFO = "INFO"
SEVERITY_WARNING = "WARNING"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"


class AlertEngine:
    """
    Automated event-driven alert engine and state monitor.
    Can be invoked directly by backend triggers or run audit scans against DB.
    """

    @staticmethod
    def create_alert(
        db: Session,
        alert_type: str,
        severity: str,
        title: str,
        description: str,
        source_event: str = "SYSTEM_EVENT",
        habitation_id: Optional[str] = None,
        habitation_name: Optional[str] = None,
        site_id: Optional[str] = None,
        site_name: Optional[str] = None,
        rpi: Optional[float] = None,
        deduplicate: bool = True
    ) -> Alert:
        """
        Creates and persists an Alert in the database.
        If deduplicate is True, avoids generating duplicate active alerts for the same entity & type.
        """
        severity = severity.upper()
        if severity not in [SEVERITY_INFO, SEVERITY_WARNING, SEVERITY_HIGH, SEVERITY_CRITICAL]:
            severity = SEVERITY_INFO

        # Deduplication check: Check if an active (unresolved) alert exists with same type and target
        if deduplicate:
            query = db.query(Alert).filter(
                Alert.type == alert_type,
                Alert.is_resolved == False
            )
            if habitation_id:
                query = query.filter(Alert.habitation_id == habitation_id)
            elif site_id:
                query = query.filter(Alert.site_id == site_id)

            existing = query.order_by(Alert.created_at.desc()).first()
            if existing:
                # Update existing alert with latest context instead of spamming
                existing.title = title
                existing.description = description
                existing.severity = severity
                existing.source_event = source_event
                if rpi is not None:
                    existing.rpi = rpi
                db.flush()
                return existing

        alert_id = f"ALR-{uuid.uuid4().hex[:8].upper()}"

        alert_record = Alert(
            id=alert_id,
            type=alert_type,
            severity=severity,
            title=title,
            description=description,
            habitation_id=habitation_id,
            habitation_name=habitation_name,
            site_id=site_id,
            site_name=site_name,
            source_event=source_event,
            is_acknowledged=False,
            is_resolved=False,
            rpi=rpi,
            rule_id=alert_type,
            rule_name=title,
            category=alert_type.lower(),
            message=description,
            created_at=datetime.utcnow(),
        )

        db.add(alert_record)
        db.flush()
        return alert_record

    # ── Event Trigger Methods ──────────────────────────────────────────

    @classmethod
    def trigger_road_blocked(
        cls,
        db: Session,
        hab_id: str,
        hab_name: str,
        verifier: str = "Field Survey",
        source_event: str = "FIELD_VERIFICATION"
    ) -> Alert:
        """Triggered when road access is reported blocked."""
        return cls.create_alert(
            db=db,
            alert_type="ROAD_BLOCKED",
            severity=SEVERITY_HIGH,
            title=f"Access Route Blocked — {hab_name}",
            description=f"Field verification by {verifier} reported primary road access blocked for {hab_name} ({hab_id}). Immediate transit risk.",
            source_event=source_event,
            habitation_id=hab_id,
            habitation_name=hab_name,
        )

    @classmethod
    def trigger_verification_conflict(
        cls,
        db: Session,
        hab_id: str,
        hab_name: str,
        notes: str,
        source_event: str = "FIELD_VERIFICATION"
    ) -> Alert:
        """Triggered when field survey data contradicts model baseline."""
        return cls.create_alert(
            db=db,
            alert_type="FIELD_VERIFICATION_CONFLICT",
            severity=SEVERITY_WARNING,
            title=f"Field Verification Conflict — {hab_name}",
            description=f"Discrepancy detected between remote sensing model and field survey for {hab_name} ({hab_id}): {notes or 'Conflicting infrastructure/hazard attributes reported.'}",
            source_event=source_event,
            habitation_id=hab_id,
            habitation_name=hab_name,
        )

    @classmethod
    def trigger_risk_critical(
        cls,
        db: Session,
        hab_id: str,
        hab_name: str,
        rpi: float,
        risk_category: str,
        source_event: str = "RISK_RECALCULATION"
    ) -> Alert:
        """Triggered when risk score escalates to Critical or Red Zone."""
        return cls.create_alert(
            db=db,
            alert_type="RISK_CRITICAL",
            severity=SEVERITY_CRITICAL,
            title=f"Risk Level Escalated to Critical — {hab_name}",
            description=f"Habitation {hab_name} ({hab_id}) RPI risk index has reached {rpi:.1f} ({risk_category}). Relocation priority escalated.",
            source_event=source_event,
            habitation_id=hab_id,
            habitation_name=hab_name,
            rpi=rpi,
        )

    @classmethod
    def trigger_new_red_zone(
        cls,
        db: Session,
        hab_id: str,
        hab_name: str,
        rpi: float,
        source_event: str = "HAZARD_RECALCULATION"
    ) -> Alert:
        """Triggered when a habitation enters Red Zone classification."""
        return cls.create_alert(
            db=db,
            alert_type="NEW_RED_ZONE_CANDIDATE",
            severity=SEVERITY_CRITICAL,
            title=f"New Red Zone Candidate — {hab_name}",
            description=f"Habitation {hab_name} ({hab_id}) classified as Red Zone Candidate due to compounding hazard exposure and steep slope (RPI: {rpi:.1f}).",
            source_event=source_event,
            habitation_id=hab_id,
            habitation_name=hab_name,
            rpi=rpi,
        )

    @classmethod
    def trigger_immediate_relocation(
        cls,
        db: Session,
        hab_id: str,
        hab_name: str,
        urgency: str = "Immediate",
        source_event: str = "NECESSITY_EVALUATION"
    ) -> Alert:
        """Triggered when relocation urgency reaches Immediate."""
        return cls.create_alert(
            db=db,
            alert_type="IMMEDIATE_RELOCATION",
            severity=SEVERITY_CRITICAL,
            title=f"Immediate Relocation Required — {hab_name}",
            description=f"Emergency action triggered: {hab_name} ({hab_id}) assessed as requiring IMMEDIATE relocation. Safe transit and shelter allocation mandatory.",
            source_event=source_event,
            habitation_id=hab_id,
            habitation_name=hab_name,
        )

    @classmethod
    def trigger_site_capacity_low(
        cls,
        db: Session,
        site_id: str,
        site_name: str,
        remaining_capacity: int,
        initial_capacity: int,
        source_event: str = "OPTIMIZER_RUN"
    ) -> Alert:
        """Triggered when a candidate site's remaining capacity falls below safety threshold (<15% or <500)."""
        pct = (remaining_capacity / max(initial_capacity, 1)) * 100
        return cls.create_alert(
            db=db,
            alert_type="CANDIDATE_SITE_CAPACITY_LOW",
            severity=SEVERITY_WARNING,
            title=f"Candidate Site Capacity Critical — {site_name}",
            description=f"Relocation site {site_name} ({site_id}) available headroom is down to {remaining_capacity:,} persons ({pct:.1f}% remaining of {initial_capacity:,}). Additional zoning required.",
            source_event=source_event,
            site_id=site_id,
            site_name=site_name,
        )

    @classmethod
    def trigger_no_feasible_capacity(
        cls,
        db: Session,
        unassigned_count: int,
        total_deficit: int,
        habitation_names: List[str],
        source_event: str = "OPTIMIZER_RUN"
    ) -> Alert:
        """Triggered when relocation optimizer encounters unassigned population."""
        habs_str = ", ".join(habitation_names[:3])
        if len(habitation_names) > 3:
            habs_str += f" and {len(habitation_names) - 3} others"
        return cls.create_alert(
            db=db,
            alert_type="NO_FEASIBLE_CAPACITY",
            severity=SEVERITY_HIGH,
            title="Relocation Capacity Deficit Detected",
            description=f"Optimizer could not assign {total_deficit:,} persons across {unassigned_count} habitations ({habs_str}) due to exhausted regional site capacity.",
            source_event=source_event,
        )

    @classmethod
    def trigger_simulation_escalation(
        cls,
        db: Session,
        rainfall_surge_mm: float,
        red_zone_delta: int,
        escalated_hab_names: List[str],
        source_event: str = "LIVE_SCENARIO_SIMULATION"
    ) -> Alert:
        """Triggered when live scenario simulation produces major risk escalation."""
        habs_str = ", ".join(escalated_hab_names[:3])
        if len(escalated_hab_names) > 3:
            habs_str += f" + {len(escalated_hab_names) - 3} more"
        return cls.create_alert(
            db=db,
            alert_type="SIMULATION_RISK_ESCALATION",
            severity=SEVERITY_HIGH,
            title="Simulation: Major Risk Escalation",
            description=f"Rainfall surge of +{rainfall_surge_mm:.0f} mm/day simulated: {red_zone_delta} new Red Zones projected ({habs_str}). Pre-emptive disaster logistics recommended.",
            source_event=source_event,
        )

    @classmethod
    def trigger_dataset_outdated(
        cls,
        db: Session,
        dataset_name: str,
        reason: str,
        source_event: str = "DATASET_INGESTION"
    ) -> Alert:
        """Triggered when dataset is outdated or contains validation warnings."""
        return cls.create_alert(
            db=db,
            alert_type="DATASET_OUTDATED",
            severity=SEVERITY_INFO,
            title=f"Dataset Audit Notice — {dataset_name}",
            description=f"Ingestion audit for dataset '{dataset_name}': {reason}",
            source_event=source_event,
        )

    # ── Automatic Database Audit & Seeding ─────────────────────────────

    @classmethod
    def audit_and_seed_system_alerts(cls, db: Session) -> List[Alert]:
        """
        Evaluates current database records against operational thresholds.
        Ensures baseline alerts exist automatically without requiring manual button clicks.
        """
        created = []
        habitations = Repository.get_all_habitations(db)
        sites = Repository.get_all_sites(db)

        # 1. Habitation Risk & Road Audits
        for hab in habitations:
            ra = hab.risk_assessment
            rpi = ra.rpi if ra else 0.0
            risk_cat = ra.risk_category if ra else "Moderate"

            if rpi >= 70.0 or "Critical" in risk_cat:
                a = cls.trigger_risk_critical(db, hab.id, hab.name, rpi, risk_cat, source_event="SYSTEM_AUDIT")
                created.append(a)

            if hab.necessity and hab.necessity.category == "Immediate":
                a = cls.trigger_immediate_relocation(db, hab.id, hab.name, urgency="Immediate", source_event="SYSTEM_AUDIT")
                created.append(a)

            if hab.road_status == "BLOCKED" or hab.road_accessible is False:
                a = cls.trigger_road_blocked(db, hab.id, hab.name, verifier="Baseline Audit", source_event="SYSTEM_AUDIT")
                created.append(a)

            if hab.verification_status == "CONFLICTING_DATA":
                a = cls.trigger_verification_conflict(db, hab.id, hab.name, notes="Contradictory hazard reports on record", source_event="SYSTEM_AUDIT")
                created.append(a)

        # 2. Site Capacity Headroom Audits
        for site in sites:
            # Check remaining capacity from dimensions
            dims = site.capacity_dimensions
            if dims:
                min_cap = min(d.max_capacity - d.current_utilization for d in dims)
                max_cap = max(d.max_capacity for d in dims)
                if min_cap < 500 or (max_cap > 0 and min_cap / max_cap < 0.20):
                    a = cls.trigger_site_capacity_low(db, site.id, site.name, min_cap, max_cap, source_event="SYSTEM_AUDIT")
                    created.append(a)

        db.commit()
        return created

    # ── Backward Compatibility Rule Metadata ─────────────────────────

    @staticmethod
    def get_rules() -> List[Dict[str, str]]:
        return [
            {
                "id": "RULE_CRITICAL_RPI",
                "name": "Critical Risk Escalation",
                "description": "Triggered when Habitation RPI exceeds critical threshold (>=70) or enters Red Zone.",
                "severity": "CRITICAL",
                "category": "risk",
            },
            {
                "id": "RULE_IMMEDIATE_RELOCATION",
                "name": "Immediate Relocation Required",
                "description": "Triggered when relocation necessity classification reaches Immediate timeline.",
                "severity": "CRITICAL",
                "category": "relocation",
            },
            {
                "id": "RULE_ROAD_BLOCKED",
                "name": "Access Route Blocked",
                "description": "Triggered when ground verification surveys or sensors report road access severed.",
                "severity": "HIGH",
                "category": "infrastructure",
            },
            {
                "id": "RULE_NO_FEASIBLE_CAPACITY",
                "name": "No Feasible Relocation Capacity",
                "description": "Triggered when optimizer identifies displaced population exceeding all safe site headroom.",
                "severity": "HIGH",
                "category": "capacity",
            },
            {
                "id": "RULE_SIMULATION_ESCALATION",
                "name": "Simulation Risk Surge Escalation",
                "description": "Triggered when extreme rainfall or climate scenario projects severe hazard amplification.",
                "severity": "HIGH",
                "category": "simulation",
            },
            {
                "id": "RULE_SITE_CAPACITY_LOW",
                "name": "Candidate Site Capacity Critical",
                "description": "Triggered when candidate site available headroom drops below 15% or <500 persons.",
                "severity": "WARNING",
                "category": "capacity",
            },
            {
                "id": "RULE_VERIFICATION_CONFLICT",
                "name": "Field Verification Conflict",
                "description": "Triggered when on-ground surveyor reports contradict remote sensing baseline models.",
                "severity": "WARNING",
                "category": "verification",
            },
            {
                "id": "RULE_DATASET_OUTDATED",
                "name": "Dataset Attention / Outdated",
                "description": "Triggered when spatial or demographic datasets have validation issues or need refresh.",
                "severity": "INFO",
                "category": "datasets",
            },
        ]
