"""
Repository layer — all database access goes through this module.

Every engine and route imports from here to read/write canonical data.
No engine or route should ever create its own mock data.
"""
from __future__ import annotations

import json
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from .models import (
    Habitation, Hazard, HazardObservation, CandidateSite,
    SiteCapacityDimension, RiskAssessment, RelocationNecessity,
    RelocationAssignment, FieldVerification, PostRelocationRecord,
    Alert, AuditLog, Dataset, DataValidationResult,
    State, District, Block,
)


class Repository:
    """Stateless helper: every public method takes a Session."""

    # ── Habitations ───────────────────────────────────────────────────

    @staticmethod
    def get_all_habitations(db: Session) -> List[Habitation]:
        return db.query(Habitation).order_by(Habitation.id).all()

    @staticmethod
    def get_habitation(db: Session, hab_id: str) -> Optional[Habitation]:
        return db.query(Habitation).filter(Habitation.id == hab_id).first()

    @staticmethod
    def upsert_habitation(db: Session, data: Dict[str, Any]) -> Habitation:
        existing = db.query(Habitation).filter(Habitation.id == data["id"]).first()
        if existing:
            for k, v in data.items():
                setattr(existing, k, v)
            db.flush()
            return existing
        hab = Habitation(**data)
        db.add(hab)
        db.flush()
        return hab

    @staticmethod
    def habitation_to_dict(hab: Habitation) -> Dict[str, Any]:
        return {
            "id": hab.id,
            "name": hab.name,
            "block_id": hab.block_id,
            "population": hab.population,
            "households": hab.households,
            "latitude": hab.latitude,
            "longitude": hab.longitude,
            "elevation": hab.elevation,
            "slope": hab.slope,
            "aspect": hab.aspect,
            "geom_geojson": hab.geom_geojson,
            "dataset_type": hab.dataset_type,
            "road_accessible": hab.road_accessible if hab.road_accessible is not None else True,
            "road_status": hab.road_status or "OPEN",
            "water_availability": hab.water_availability or "ADEQUATE",
            "housing_condition": hab.housing_condition or "PUCCA_GOOD",
            "healthcare_accessible": hab.healthcare_accessible if hab.healthcare_accessible is not None else True,
            "hazard_observation": hab.hazard_observation or "NONE",
            "verification_status": hab.verification_status or "NEEDS_VERIFICATION",
        }

    @staticmethod
    def habitation_to_geojson_feature(hab: Habitation) -> Dict[str, Any]:
        props = Repository.habitation_to_dict(hab)
        # Merge risk assessment if present
        if hab.risk_assessment:
            ra = hab.risk_assessment
            props["hazard_score"] = ra.hazard_score
            props["exposure_score"] = ra.exposure_score
            props["vulnerability_score"] = ra.vulnerability_score
            props["rpi"] = ra.rpi
            props["risk_category"] = ra.risk_category
        if hab.necessity:
            props["necessity_category"] = hab.necessity.category
            props["action_timeline"] = hab.necessity.action_timeline
        return {
            "type": "Feature",
            "geometry": json.loads(hab.geom_geojson) if hab.geom_geojson else {"type": "Point", "coordinates": [hab.longitude, hab.latitude]},
            "properties": props,
        }

    # ── Hazards ───────────────────────────────────────────────────────

    @staticmethod
    def get_all_hazards(db: Session) -> List[Hazard]:
        return db.query(Hazard).order_by(Hazard.id).all()

    @staticmethod
    def count_hazards(db: Session) -> int:
        return db.query(Hazard).count()

    @staticmethod
    def upsert_hazard(db: Session, data: Dict[str, Any]) -> Hazard:
        existing = db.query(Hazard).filter(Hazard.id == data["id"]).first()
        if existing:
            for k, v in data.items():
                setattr(existing, k, v)
            db.flush()
            return existing
        hz = Hazard(**data)
        db.add(hz)
        db.flush()
        return hz

    @staticmethod
    def hazard_to_geojson_feature(hz: Hazard) -> Dict[str, Any]:
        return {
            "type": "Feature",
            "geometry": json.loads(hz.geom_geojson) if hz.geom_geojson else None,
            "properties": {
                "id": hz.id,
                "type": hz.type,
                "severity": hz.severity,
                "dataset_type": hz.dataset_type,
            },
        }

    # ── Hazard Observations ───────────────────────────────────────────

    @staticmethod
    def get_hazard_observations(db: Session, habitation_id: str) -> List[HazardObservation]:
        return db.query(HazardObservation).filter(HazardObservation.habitation_id == habitation_id).all()

    @staticmethod
    def save_hazard_observation(db: Session, data: Dict[str, Any]) -> HazardObservation:
        existing = db.query(HazardObservation).filter(
            HazardObservation.habitation_id == data["habitation_id"],
            HazardObservation.hazard_id == data["hazard_id"],
        ).first()
        if existing:
            for k, v in data.items():
                if k not in ("habitation_id", "hazard_id"):
                    setattr(existing, k, v)
            db.flush()
            return existing
        obs = HazardObservation(**data)
        db.add(obs)
        db.flush()
        return obs

    # ── Candidate Sites ───────────────────────────────────────────────

    @staticmethod
    def get_all_sites(db: Session) -> List[CandidateSite]:
        return db.query(CandidateSite).order_by(CandidateSite.id).all()

    @staticmethod
    def get_site(db: Session, site_id: str) -> Optional[CandidateSite]:
        return db.query(CandidateSite).filter(CandidateSite.id == site_id).first()

    @staticmethod
    def upsert_site(db: Session, data: Dict[str, Any]) -> CandidateSite:
        existing = db.query(CandidateSite).filter(CandidateSite.id == data["id"]).first()
        if existing:
            for k, v in data.items():
                setattr(existing, k, v)
            db.flush()
            return existing
        site = CandidateSite(**data)
        db.add(site)
        db.flush()
        return site

    @staticmethod
    def site_to_dict(site: CandidateSite) -> Dict[str, Any]:
        return {
            "site_id": site.id,
            "site_name": site.name,
            "latitude": site.latitude,
            "longitude": site.longitude,
            "elevation": site.elevation,
            "slope": site.slope,
            "aspect": site.aspect,
            "infrastructure_score": site.infrastructure_score,
            "total_suitability_score": site.total_suitability_score,
            "dataset_type": site.dataset_type,
            "factors": {
                "distance_to_hazard": site.distance_to_hazard,
                "terrain_slope": site.terrain_slope_score,
                "soil_stability": site.soil_stability,
                "historical_safety": site.historical_safety,
                "road_accessibility": site.road_accessibility,
                "healthcare_proximity": site.healthcare_proximity,
                "education_proximity": site.education_proximity,
                "area_capacity": site.area_capacity,
                "water_access": site.water_access,
                "power_access": site.power_access,
                "distance_to_origin": site.distance_to_origin,
                "environmental_impact": site.environmental_impact,
                "land_use": site.land_use,
            },
        }

    @staticmethod
    def site_to_geojson_feature(site: CandidateSite) -> Dict[str, Any]:
        return {
            "type": "Feature",
            "geometry": json.loads(site.geom_geojson) if site.geom_geojson else {"type": "Point", "coordinates": [site.longitude, site.latitude]},
            "properties": {
                "id": site.id,
                "name": site.name,
                "infrastructure_score": site.infrastructure_score,
                "total_suitability_score": site.total_suitability_score,
                "dataset_type": site.dataset_type,
            },
        }

    # ── Site Capacity ─────────────────────────────────────────────────

    @staticmethod
    def get_site_capacity(db: Session, site_id: str) -> List[SiteCapacityDimension]:
        return db.query(SiteCapacityDimension).filter(SiteCapacityDimension.site_id == site_id).all()

    @staticmethod
    def upsert_capacity_dimension(db: Session, data: Dict[str, Any]) -> SiteCapacityDimension:
        existing = db.query(SiteCapacityDimension).filter(
            SiteCapacityDimension.site_id == data["site_id"],
            SiteCapacityDimension.dimension == data["dimension"],
        ).first()
        if existing:
            for k, v in data.items():
                if k not in ("site_id", "dimension"):
                    setattr(existing, k, v)
            db.flush()
            return existing
        cap = SiteCapacityDimension(**data)
        db.add(cap)
        db.flush()
        return cap

    # ── Risk Assessment ───────────────────────────────────────────────

    @staticmethod
    def get_risk_assessment(db: Session, habitation_id: str) -> Optional[RiskAssessment]:
        return db.query(RiskAssessment).filter(RiskAssessment.habitation_id == habitation_id).first()

    @staticmethod
    def get_all_risk_assessments(db: Session) -> List[RiskAssessment]:
        return db.query(RiskAssessment).order_by(RiskAssessment.rpi.desc()).all()

    @staticmethod
    def save_risk_assessment(db: Session, data: Dict[str, Any]) -> RiskAssessment:
        existing = db.query(RiskAssessment).filter(RiskAssessment.habitation_id == data["habitation_id"]).first()
        if existing:
            for k, v in data.items():
                if k != "habitation_id":
                    setattr(existing, k, v)
            db.flush()
            return existing
        ra = RiskAssessment(**data)
        db.add(ra)
        db.flush()
        return ra

    # ── Relocation Necessity ──────────────────────────────────────────

    @staticmethod
    def get_necessity(db: Session, habitation_id: str) -> Optional[RelocationNecessity]:
        return db.query(RelocationNecessity).filter(RelocationNecessity.habitation_id == habitation_id).first()

    @staticmethod
    def save_necessity(db: Session, data: Dict[str, Any]) -> RelocationNecessity:
        existing = db.query(RelocationNecessity).filter(RelocationNecessity.habitation_id == data["habitation_id"]).first()
        if existing:
            for k, v in data.items():
                if k != "habitation_id":
                    setattr(existing, k, v)
            db.flush()
            return existing
        nec = RelocationNecessity(**data)
        db.add(nec)
        db.flush()
        return nec

    # ── Relocation Assignments ────────────────────────────────────────

    @staticmethod
    def get_all_assignments(db: Session) -> List[RelocationAssignment]:
        return db.query(RelocationAssignment).order_by(RelocationAssignment.id).all()

    @staticmethod
    def get_assignments_for_habitation(db: Session, habitation_id: str) -> List[RelocationAssignment]:
        return db.query(RelocationAssignment).filter(RelocationAssignment.habitation_id == habitation_id).all()

    @staticmethod
    def clear_assignments(db: Session):
        db.query(RelocationAssignment).delete()
        db.flush()

    @staticmethod
    def save_assignment(db: Session, data: Dict[str, Any]) -> RelocationAssignment:
        assignment = RelocationAssignment(**data)
        db.add(assignment)
        db.flush()
        return assignment

    # ── Field Verification ────────────────────────────────────────────

    @staticmethod
    def get_field_verifications(db: Session, habitation_id: str = None) -> List[FieldVerification]:
        q = db.query(FieldVerification).order_by(FieldVerification.created_at.desc())
        if habitation_id:
            q = q.filter(FieldVerification.habitation_id == habitation_id)
        return q.all()

    @staticmethod
    def get_latest_field_verification(db: Session, habitation_id: str) -> Optional[FieldVerification]:
        return db.query(FieldVerification).filter(
            FieldVerification.habitation_id == habitation_id
        ).order_by(FieldVerification.created_at.desc()).first()

    @staticmethod
    def save_field_verification(db: Session, data: Dict[str, Any]) -> FieldVerification:
        fv = FieldVerification(**data)
        db.add(fv)
        db.flush()
        return fv

    @staticmethod
    def field_verification_to_dict(fv: FieldVerification) -> Dict[str, Any]:
        return {
            "id": fv.id,
            "habitation_id": fv.habitation_id,
            "habitation_name": fv.habitation.name if fv.habitation else fv.habitation_id,
            "verifier_name": fv.verifier_name or "Field Officer",
            "verified_at": fv.verified_at.isoformat() if fv.verified_at else (fv.created_at.isoformat() if fv.created_at else None),
            "latitude": fv.latitude,
            "longitude": fv.longitude,
            "road_accessible": fv.road_accessible if fv.road_accessible is not None else True,
            "road_status": fv.road_status or "OPEN",
            "water_availability": fv.water_availability or "ADEQUATE",
            "housing_condition": fv.housing_condition or "PUCCA_GOOD",
            "healthcare_accessible": fv.healthcare_accessible if fv.healthcare_accessible is not None else True,
            "hazard_observation": fv.hazard_observation or "NONE",
            "verification_status": fv.verification_status or "VERIFIED",
            "notes": fv.notes or fv.verifier_notes or "",
            "previous_state": json.loads(fv.previous_state_snapshot) if fv.previous_state_snapshot else None,
            "updated_state": json.loads(fv.updated_state_snapshot) if fv.updated_state_snapshot else None,
            "recalculation_diff": json.loads(fv.recalculation_diff) if fv.recalculation_diff else None,
            "created_at": fv.created_at.isoformat() if fv.created_at else None,
        }

    # ── Post-Relocation ───────────────────────────────────────────────

    @staticmethod
    def get_post_relocation_records(db: Session) -> List[PostRelocationRecord]:
        return db.query(PostRelocationRecord).all()

    @staticmethod
    def save_post_relocation_record(db: Session, data: Dict[str, Any]) -> PostRelocationRecord:
        rec = PostRelocationRecord(**data)
        db.add(rec)
        db.flush()
        return rec

    # ── Alerts ────────────────────────────────────────────────────────

    @staticmethod
    def alert_to_dict(alert: Alert) -> Dict[str, Any]:
        return {
            "id": alert.id,
            "type": alert.type or "SYSTEM_EVENT",
            "severity": (alert.severity or "INFO").upper(),
            "title": alert.title or alert.rule_name or "System Alert",
            "description": alert.description or alert.message or "",
            "habitation_id": alert.habitation_id,
            "habitation_name": alert.habitation_name,
            "site_id": alert.site_id,
            "site_name": alert.site_name,
            "source_event": alert.source_event or "SYSTEM_EVENT",
            "is_acknowledged": bool(alert.is_acknowledged),
            "acknowledged_at": alert.acknowledged_at.isoformat() + "Z" if alert.acknowledged_at else None,
            "is_resolved": bool(alert.is_resolved),
            "resolved_at": alert.resolved_at.isoformat() + "Z" if alert.resolved_at else None,
            "created_at": alert.created_at.isoformat() + "Z" if alert.created_at else None,
            # Backward compatibility
            "rule_id": alert.rule_id,
            "rule_name": alert.rule_name,
            "category": alert.category or "system",
            "message": alert.description or alert.message or "",
            "rpi": alert.rpi,
            "is_read": bool(alert.is_acknowledged or alert.is_resolved or alert.is_read),
        }

    @staticmethod
    def get_alerts(
        db: Session,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        source: Optional[str] = None,
        habitation_id: Optional[str] = None,
        site_id: Optional[str] = None
    ) -> List[Alert]:
        q = db.query(Alert).order_by(Alert.created_at.desc())

        if severity and severity.upper() != "ALL":
            q = q.filter(Alert.severity.ilike(severity))

        if status:
            s_up = status.upper()
            if s_up == "UNACKNOWLEDGED" or s_up == "ACTIVE":
                q = q.filter(Alert.is_acknowledged == False, Alert.is_resolved == False)
            elif s_up == "ACKNOWLEDGED":
                q = q.filter(Alert.is_acknowledged == True)
            elif s_up == "RESOLVED":
                q = q.filter(Alert.is_resolved == True)

        if source and source.upper() != "ALL":
            q = q.filter(Alert.source_event.ilike(f"%{source}%"))

        if habitation_id:
            q = q.filter(Alert.habitation_id == habitation_id)

        if site_id:
            q = q.filter(Alert.site_id == site_id)

        return q.all()

    @staticmethod
    def get_alert(db: Session, alert_id: str) -> Optional[Alert]:
        return db.query(Alert).filter(Alert.id == alert_id).first()

    @staticmethod
    def save_alert(db: Session, data: Dict[str, Any]) -> Alert:
        # Check if identical alert exists
        existing = db.query(Alert).filter(Alert.id == data.get("id")).first()
        if existing:
            for k, v in data.items():
                setattr(existing, k, v)
            db.flush()
            return existing

        alert = Alert(**data)
        db.add(alert)
        db.flush()
        return alert

    @staticmethod
    def acknowledge_alert(db: Session, alert_id: str) -> Optional[Alert]:
        from datetime import datetime
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.is_acknowledged = True
            if not alert.acknowledged_at:
                alert.acknowledged_at = datetime.utcnow()
            alert.is_read = True
            db.flush()
        return alert

    @staticmethod
    def resolve_alert(db: Session, alert_id: str) -> Optional[Alert]:
        from datetime import datetime
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.is_resolved = True
            alert.is_acknowledged = True
            if not alert.resolved_at:
                alert.resolved_at = datetime.utcnow()
            if not alert.acknowledged_at:
                alert.acknowledged_at = alert.resolved_at
            alert.is_read = True
            db.flush()
        return alert

    @staticmethod
    def acknowledge_all_alerts(db: Session) -> int:
        from datetime import datetime
        now = datetime.utcnow()
        unacked = db.query(Alert).filter(Alert.is_acknowledged == False).all()
        for a in unacked:
            a.is_acknowledged = True
            a.acknowledged_at = now
            a.is_read = True
        db.flush()
        return len(unacked)


    # ── Audit Log ─────────────────────────────────────────────────────

    @staticmethod
    def log_action(db: Session, action: str, entity_type: str = None,
                   entity_id: str = None, details: str = None):
        entry = AuditLog(action=action, entity_type=entity_type,
                         entity_id=entity_id, details=details)
        db.add(entry)
        db.flush()

    # ── Datasets ──────────────────────────────────────────────────────

    @staticmethod
    def get_all_datasets(db: Session) -> List[Dataset]:
        return db.query(Dataset).order_by(Dataset.created_at.desc()).all()

    @staticmethod
    def get_dataset(db: Session, dataset_id: int) -> Optional[Dataset]:
        return db.query(Dataset).filter(Dataset.id == dataset_id).first()

    @staticmethod
    def save_dataset(db: Session, data: Dict[str, Any]) -> Dataset:
        ds = Dataset(**data)
        db.add(ds)
        db.flush()
        return ds

    @staticmethod
    def save_validation_result(db: Session, data: Dict[str, Any]) -> DataValidationResult:
        res = DataValidationResult(**data)
        db.add(res)
        db.flush()
        return res


    # ── Utility ───────────────────────────────────────────────────────

    @staticmethod
    def count_habitations(db: Session) -> int:
        return db.query(Habitation).count()

    @staticmethod
    def count_sites(db: Session) -> int:
        return db.query(CandidateSite).count()
