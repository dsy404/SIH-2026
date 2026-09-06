"""
Cascading Recalculation Service — Phase 8 Ground Truth Propagation.

Workflow:
Field Verification
    ↓
Updated Source/Verified Value
    ↓
Vulnerability Recalculation (VulnerabilityEngine)
    ↓
Hazard Recalculation (HazardEngine / Observation adjustments)
    ↓
Risk Recalculation (MasterEngine RPI & Risk Category)
    ↓
Relocation Necessity Recalculation (NecessityEngine)
    ↓
Optimizer Recommendation Refresh (RelocationOptimizer)
    ↓
Action Plan / Ledger Update
    ↓
Audit Log & Non-Destructive Provenance Persistence
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.db.repository import Repository
from app.db.models import Habitation, FieldVerification, RiskAssessment, RelocationNecessity
from app.engines.vulnerability_engine import VulnerabilityEngine
from app.engines.master_engine import MasterEngine
from app.engines.relocation.necessity import NecessityEngine
from app.engines.relocation.optimizer import RelocationOptimizer
from app.engines.alert_engine import AlertEngine



class RecalculationService:
    """
    Coordinates end-to-end cascading recalculation triggered by field verification reports.
    Never silently overwrites baseline provenance; persists before vs after state diffs.
    """

    @staticmethod
    def process_field_verification(session: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes cascading recalculation for a habitation given verified field observations.
        """
        hab_id = payload.get("habitation_id")
        if not hab_id:
            raise ValueError("habitation_id is required")

        hab = Repository.get_habitation(session, hab_id)
        if not hab:
            raise ValueError(f"Habitation {hab_id} not found in canonical database")

        # ── Step 1: Capture Exact "Before" Snapshot ───────────────────
        ra_before = hab.risk_assessment
        nec_before = hab.necessity
        assignments_before = Repository.get_assignments_for_habitation(session, hab_id)
        current_site_id = assignments_before[0].site_id if assignments_before else None
        current_site_name = assignments_before[0].site.name if (assignments_before and assignments_before[0].site) else "UNASSIGNED"

        before_state = {
            "habitation_id": hab.id,
            "habitation_name": hab.name,
            "population": hab.population,
            "road_accessible": hab.road_accessible,
            "road_status": hab.road_status,
            "water_availability": hab.water_availability,
            "housing_condition": hab.housing_condition,
            "healthcare_accessible": hab.healthcare_accessible,
            "hazard_observation": hab.hazard_observation,
            "verification_status": hab.verification_status,
            "vulnerability_score": ra_before.vulnerability_score if ra_before else 50.0,
            "hazard_score": ra_before.hazard_score if ra_before else 50.0,
            "exposure_score": ra_before.exposure_score if ra_before else 50.0,
            "rpi": ra_before.rpi if ra_before else 50.0,
            "risk_category": ra_before.risk_category if ra_before else "Moderate",
            "necessity_category": nec_before.category if nec_before else "Monitor",
            "assigned_site_id": current_site_id,
            "assigned_site_name": current_site_name,
        }

        # ── Step 2: Apply Verified Field Attributes ────────────────────
        verifier_name = payload.get("verifier_name", "Field Officer")
        road_status = str(payload.get("road_status", hab.road_status or "OPEN")).upper()
        road_accessible = bool(payload.get("road_accessible", road_status == "OPEN"))
        water_avail = str(payload.get("water_availability", hab.water_availability or "ADEQUATE")).upper()
        housing = str(payload.get("housing_condition", hab.housing_condition or "PUCCA_GOOD")).upper()
        healthcare_acc = bool(payload.get("healthcare_accessible", hab.healthcare_accessible if hab.healthcare_accessible is not None else True))
        hazard_obs = str(payload.get("hazard_observation", hab.hazard_observation or "NONE")).upper()
        verification_status = str(payload.get("verification_status", "VERIFIED")).upper()
        notes = payload.get("notes") or payload.get("verifier_notes") or ""

        # Update Habitation model record
        hab.road_accessible = road_accessible
        hab.road_status = road_status
        hab.water_availability = water_avail
        hab.housing_condition = housing
        hab.healthcare_accessible = healthcare_acc
        hab.hazard_observation = hazard_obs
        hab.verification_status = verification_status
        hab.updated_at = datetime.utcnow()

        # Optional demographic ground truth
        if payload.get("verified_population") is not None:
            hab.population = int(payload["verified_population"])
        if payload.get("verified_households") is not None:
            hab.households = int(payload["verified_households"])
        if payload.get("verified_elevation") is not None:
            hab.elevation = float(payload["verified_elevation"])
        if payload.get("verified_slope") is not None:
            hab.slope = float(payload["verified_slope"])

        session.flush()

        # ── Step 3: Vulnerability Recalculation ────────────────────────
        hab_dict = Repository.habitation_to_dict(hab)
        vuln_engine = VulnerabilityEngine()
        scored_hab_list = vuln_engine.calculate_vulnerability_scores([hab_dict])
        new_vuln_score = scored_hab_list[0]["vulnerability_score"]
        vuln_explanation = scored_hab_list[0].get("vulnerability_explanation", {})

        # ── Step 4: Hazard Score Recalculation with Field Hazard Observation
        base_hazard = ra_before.hazard_score if ra_before else 50.0
        new_hazard_score = base_hazard

        hazard_adjustments = []
        if hazard_obs == "FLASH_FLOOD" or hazard_obs == "RISING_WATER":
            new_hazard_score = min(100.0, base_hazard + 25.0)
            hazard_adjustments.append(f"Direct field observation: {hazard_obs} reported in immediate proximity (+25).")
        elif hazard_obs in ("ACTIVE_SLOPE_CRACK", "DEBRIS_FLOW"):
            new_hazard_score = min(100.0, base_hazard + 30.0)
            hazard_adjustments.append(f"Geotechnical failure observation: {hazard_obs} active (+30).")

        # ── Step 5: MasterEngine Risk (RPI) Recalculation ─────────────
        exposure_score = ra_before.exposure_score if ra_before else 50.0
        weights = {"hazard": 0.40, "exposure": 0.30, "vulnerability": 0.30}
        new_rpi = round(
            (new_hazard_score * weights["hazard"]) +
            (exposure_score * weights["exposure"]) +
            (new_vuln_score * weights["vulnerability"]),
            2
        )
        new_rpi = min(100.0, max(0.0, new_rpi))

        if new_rpi >= 76:
            new_risk_category = "Critical / Red Zone Candidate"
        elif new_rpi >= 56:
            new_risk_category = "High"
        elif new_rpi >= 31:
            new_risk_category = "Moderate"
        else:
            new_risk_category = "Low"

        # Update RiskAssessment in DB
        ra_explanation = {
            "engine": "MasterEngine",
            "calculation": f"({new_hazard_score} * 0.4) + ({exposure_score} * 0.3) + ({new_vuln_score} * 0.3)",
            "hazard_adjustments": hazard_adjustments,
            "disclaimer": "Recalculated with ground truth field verification.",
        }
        Repository.save_risk_assessment(session, {
            "habitation_id": hab.id,
            "hazard_score": new_hazard_score,
            "exposure_score": exposure_score,
            "vulnerability_score": new_vuln_score,
            "rpi": new_rpi,
            "risk_category": new_risk_category,
            "rpi_explanation": json.dumps(ra_explanation),
        })

        # ── Step 6: Relocation Necessity Recalculation ─────────────────
        decision = NecessityEngine.evaluate_necessity(hab.id, new_rpi)
        new_nec_category = decision["category"]

        Repository.save_necessity(session, {
            "habitation_id": hab.id,
            "risk_score": decision["risk_score"],
            "category": decision["category"],
            "color_code": decision["color_code"],
            "action_timeline": decision["action_timeline"],
            "reasons": json.dumps(decision["reasons"]),
        })

        # ── Step 7: Optimizer Allocation Refresh ───────────────────────
        all_habs = Repository.get_all_habitations(session)
        hab_dicts = []
        for h in all_habs:
            d = Repository.habitation_to_dict(h)
            d["risk_score"] = h.risk_assessment.rpi if h.risk_assessment else 0
            hab_dicts.append(d)

        site_dicts = [Repository.site_to_dict(s) for s in Repository.get_all_sites(session)]
        opt_plan = RelocationOptimizer.run_optimization(hab_dicts, site_dicts)

        # Clear old assignments and save refreshed ones
        Repository.clear_assignments(session)
        for a in opt_plan.get("assignments", []):
            Repository.save_assignment(session, {
                "habitation_id": a["habitation_id"],
                "site_id": a["assigned_site_id"],
                "population": a["population"],
                "necessity_category": a["necessity"],
                "reason": a["reason"],
                "status": "pending",
            })
        for u in opt_plan.get("unassigned", []):
            Repository.save_assignment(session, {
                "habitation_id": u["habitation_id"],
                "site_id": None,
                "population": u["population"],
                "necessity_category": u["necessity"],
                "reason": u["reason"],
                "status": "unassigned",
            })

        session.flush()

        # ── Step 8: Capture Exact "After" Snapshot ────────────────────
        assignments_after = Repository.get_assignments_for_habitation(session, hab_id)
        new_assigned_site_id = assignments_after[0].site_id if assignments_after else None
        new_assigned_site_name = assignments_after[0].site.name if (assignments_after and assignments_after[0].site) else "UNASSIGNED"

        after_state = {
            "habitation_id": hab.id,
            "habitation_name": hab.name,
            "population": hab.population,
            "road_accessible": hab.road_accessible,
            "road_status": hab.road_status,
            "water_availability": hab.water_availability,
            "housing_condition": hab.housing_condition,
            "healthcare_accessible": hab.healthcare_accessible,
            "hazard_observation": hab.hazard_observation,
            "verification_status": hab.verification_status,
            "vulnerability_score": new_vuln_score,
            "hazard_score": new_hazard_score,
            "exposure_score": exposure_score,
            "rpi": new_rpi,
            "risk_category": new_risk_category,
            "necessity_category": new_nec_category,
            "assigned_site_id": new_assigned_site_id,
            "assigned_site_name": new_assigned_site_name,
        }

        # ── Step 9: Compute Before vs After Diff ──────────────────────
        diff = {
            "vulnerability_delta": round(new_vuln_score - before_state["vulnerability_score"], 2),
            "hazard_delta": round(new_hazard_score - before_state["hazard_score"], 2),
            "rpi_delta": round(new_rpi - before_state["rpi"], 2),
            "risk_category_changed": before_state["risk_category"] != new_risk_category,
            "necessity_changed": before_state["necessity_category"] != new_nec_category,
            "site_changed": before_state["assigned_site_id"] != new_assigned_site_id,
            "road_status_changed": before_state["road_status"] != road_status,
        }

        # ── Step 10: Persist Field Verification Record & Audit Trail ───
        fv = Repository.save_field_verification(session, {
            "habitation_id": hab.id,
            "verifier_name": verifier_name,
            "verified_at": datetime.utcnow(),
            "latitude": float(payload.get("latitude") or hab.latitude),
            "longitude": float(payload.get("longitude") or hab.longitude),
            "road_accessible": road_accessible,
            "road_status": road_status,
            "water_availability": water_avail,
            "housing_condition": housing,
            "healthcare_accessible": healthcare_acc,
            "hazard_observation": hazard_obs,
            "verification_status": verification_status,
            "notes": notes,
            "previous_state_snapshot": json.dumps(before_state),
            "updated_state_snapshot": json.dumps(after_state),
            "recalculation_diff": json.dumps(diff),
        })

        Repository.log_action(
            session,
            action="field_verification_recalculation",
            entity_type="habitation",
            entity_id=hab.id,
            details=json.dumps({
                "verifier": verifier_name,
                "status": verification_status,
                "road_status": road_status,
                "rpi_delta": diff["rpi_delta"],
                "necessity_before": before_state["necessity_category"],
                "necessity_after": new_nec_category,
            })
        )

        # ── Step 11: Automated System Event Alert Triggers ────────────
        try:
            if road_status == "BLOCKED" or not road_accessible:
                AlertEngine.trigger_road_blocked(
                    session, hab.id, hab.name, verifier=verifier_name, source_event="FIELD_VERIFICATION"
                )

            if verification_status == "CONFLICTING_DATA":
                AlertEngine.trigger_verification_conflict(
                    session, hab.id, hab.name, notes=notes, source_event="FIELD_VERIFICATION"
                )

            if new_rpi >= 70.0 or "Critical" in new_risk_category:
                AlertEngine.trigger_risk_critical(
                    session, hab.id, hab.name, new_rpi, new_risk_category, source_event="FIELD_VERIFICATION_RECALCULATION"
                )

            if new_nec_category == "Immediate":
                AlertEngine.trigger_immediate_relocation(
                    session, hab.id, hab.name, urgency="Immediate", source_event="FIELD_VERIFICATION_RECALCULATION"
                )

            if new_rpi >= 60.0 and before_state["rpi"] < 60.0:
                AlertEngine.trigger_new_red_zone(
                    session, hab.id, hab.name, new_rpi, source_event="FIELD_VERIFICATION_RECALCULATION"
                )
        except Exception as e:
            print(f"[AlertEngine Hook Warning] Failed to trigger event alert: {e}")

        session.commit()

        return {
            "verification_id": fv.id,
            "habitation": {"id": hab.id, "name": hab.name},
            "status": verification_status,
            "verifier": verifier_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "before": before_state,
            "after": after_state,
            "difference": diff,
            "audit_trail_recorded": True,
            "cascading_pipeline_steps": [
                "1. Field Verification Ingested",
                f"2. Vulnerability Recalculated ({before_state['vulnerability_score']} → {new_vuln_score})",
                f"3. Hazard Recalculated ({before_state['hazard_score']} → {new_hazard_score})",
                f"4. RPI Risk Re-evaluated ({before_state['rpi']} → {new_rpi}, Category: {new_risk_category})",
                f"5. Relocation Necessity Shifted ({before_state['necessity_category']} → {new_nec_category})",
                f"6. Optimizer Reallocated Destination ({before_state['assigned_site_name']} → {new_assigned_site_name})",
                "7. Action Plan Priority Table Updated"
            ]
        }
