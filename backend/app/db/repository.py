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
        q = db.query(FieldVerification)
        if habitation_id:
            q = q.filter(FieldVerification.habitation_id == habitation_id)
        return q.all()

    @staticmethod
    def save_field_verification(db: Session, data: Dict[str, Any]) -> FieldVerification:
        fv = FieldVerification(**data)
        db.add(fv)
        db.flush()
        return fv

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
    def get_alerts(db: Session, severity: str = None) -> List[Alert]:
        q = db.query(Alert).order_by(Alert.created_at.desc())
        if severity:
            q = q.filter(Alert.severity == severity)
        return q.all()

    @staticmethod
    def save_alert(db: Session, data: Dict[str, Any]) -> Alert:
        alert = Alert(**data)
        db.add(alert)
        db.flush()
        return alert

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
    def save_dataset(db: Session, data: Dict[str, Any]) -> Dataset:
        ds = Dataset(**data)
        db.add(ds)
        db.flush()
        return ds

    # ── Utility ───────────────────────────────────────────────────────

    @staticmethod
    def count_habitations(db: Session) -> int:
        return db.query(Habitation).count()

    @staticmethod
    def count_sites(db: Session) -> int:
        return db.query(CandidateSite).count()
