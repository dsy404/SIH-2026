"""
Canonical data model for the Disaster Relocation Decision Support System.

Every entity in the system lives here. All engines, routes, and frontend
components read from / write to these tables via the repository layer.

Naming: IDs use human-readable prefixes (HAB001, SITE001, HAZ001, etc.)
"""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Text, Boolean, DateTime,
    ForeignKey, JSON, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from .database import Base


# ────────────────────────────────────────────────────────────────────────
# Administrative Hierarchy
# ────────────────────────────────────────────────────────────────────────

class State(Base):
    __tablename__ = "states"

    id = Column(String, primary_key=True)           # e.g. "ST01"
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    districts = relationship("District", back_populates="state")


class District(Base):
    __tablename__ = "districts"

    id = Column(String, primary_key=True)            # e.g. "DIST01"
    name = Column(String, nullable=False)
    state_id = Column(String, ForeignKey("states.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    state = relationship("State", back_populates="districts")
    blocks = relationship("Block", back_populates="district")


class Block(Base):
    __tablename__ = "blocks"

    id = Column(String, primary_key=True)            # e.g. "BLK01"
    name = Column(String, nullable=False)
    district_id = Column(String, ForeignKey("districts.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    district = relationship("District", back_populates="blocks")
    habitations = relationship("Habitation", back_populates="block")


# ────────────────────────────────────────────────────────────────────────
# Habitation — THE canonical entity
# ────────────────────────────────────────────────────────────────────────

class Habitation(Base):
    __tablename__ = "habitations"

    id = Column(String, primary_key=True)            # e.g. "HAB001"
    name = Column(String, nullable=False)
    block_id = Column(String, ForeignKey("blocks.id"), nullable=True)

    # Demographics
    population = Column(Integer, nullable=False, default=0)
    households = Column(Integer, nullable=False, default=0)

    # Coordinates
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    geom_geojson = Column(Text, nullable=True)       # GeoJSON geometry string

    # Terrain
    elevation = Column(Float, nullable=True)
    slope = Column(Float, nullable=True)
    aspect = Column(Float, nullable=True)

    # Metadata
    dataset_type = Column(String, default="UNKNOWN")  # DEMO / SYNTHETIC DATA, UPLOADED, etc.
    confidence = Column(String, default="UNKNOWN")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    block = relationship("Block", back_populates="habitations")
    risk_assessment = relationship("RiskAssessment", back_populates="habitation", uselist=False)
    necessity = relationship("RelocationNecessity", back_populates="habitation", uselist=False)
    hazard_observations = relationship("HazardObservation", back_populates="habitation")
    assignments = relationship("RelocationAssignment", back_populates="habitation")
    field_verifications = relationship("FieldVerification", back_populates="habitation")
    post_relocation_records = relationship("PostRelocationRecord", back_populates="habitation")


# ────────────────────────────────────────────────────────────────────────
# Hazards
# ────────────────────────────────────────────────────────────────────────

class Hazard(Base):
    __tablename__ = "hazards"

    id = Column(String, primary_key=True)            # e.g. "HAZ001"
    type = Column(String, nullable=False)             # Flood, Landslide, Earthquake, etc.
    severity = Column(String, nullable=False)         # High, Moderate, Low
    geom_geojson = Column(Text, nullable=True)        # GeoJSON polygon
    dataset_type = Column(String, default="UNKNOWN")
    created_at = Column(DateTime, default=datetime.utcnow)

    observations = relationship("HazardObservation", back_populates="hazard")


class HazardObservation(Base):
    """Records that a specific habitation is affected by a specific hazard."""
    __tablename__ = "hazard_observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    habitation_id = Column(String, ForeignKey("habitations.id"), nullable=False)
    hazard_id = Column(String, ForeignKey("hazards.id"), nullable=False)
    hazard_score = Column(Float, default=0.0)         # 0–100 from HazardEngine
    explanation = Column(Text, nullable=True)          # JSON string of explanation
    created_at = Column(DateTime, default=datetime.utcnow)

    habitation = relationship("Habitation", back_populates="hazard_observations")
    hazard = relationship("Hazard", back_populates="observations")

    __table_args__ = (
        UniqueConstraint('habitation_id', 'hazard_id', name='uq_hab_hazard'),
    )


# ────────────────────────────────────────────────────────────────────────
# Candidate Relocation Sites
# ────────────────────────────────────────────────────────────────────────

class CandidateSite(Base):
    __tablename__ = "candidate_sites"

    id = Column(String, primary_key=True)             # e.g. "SITE001"
    name = Column(String, nullable=False)

    # Coordinates
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    geom_geojson = Column(Text, nullable=True)

    # Terrain
    elevation = Column(Float, nullable=True)
    slope = Column(Float, nullable=True)
    aspect = Column(Float, nullable=True)

    # Suitability factors (0–100 scores for each of the 13 criteria)
    infrastructure_score = Column(Float, nullable=True)
    distance_to_hazard = Column(Float, default=50.0)
    terrain_slope_score = Column(Float, default=50.0)
    soil_stability = Column(Float, default=50.0)
    historical_safety = Column(Float, default=50.0)
    road_accessibility = Column(Float, default=50.0)
    healthcare_proximity = Column(Float, default=50.0)
    education_proximity = Column(Float, default=50.0)
    area_capacity = Column(Float, default=50.0)
    water_access = Column(Float, default=50.0)
    power_access = Column(Float, default=50.0)
    distance_to_origin = Column(Float, default=50.0)
    environmental_impact = Column(Float, default=50.0)
    land_use = Column(Float, default=50.0)

    # Computed total suitability score
    total_suitability_score = Column(Float, nullable=True)

    dataset_type = Column(String, default="UNKNOWN")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    capacity_dimensions = relationship("SiteCapacityDimension", back_populates="site")
    assignments = relationship("RelocationAssignment", back_populates="site")
    post_relocation_records = relationship("PostRelocationRecord", back_populates="site")


class SiteCapacityDimension(Base):
    """Per-dimension carrying capacity for a candidate site."""
    __tablename__ = "site_capacity_dimensions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    site_id = Column(String, ForeignKey("candidate_sites.id"), nullable=False)
    dimension = Column(String, nullable=False)         # Housing, Water, Power, etc.
    max_capacity = Column(Integer, default=0)
    current_utilization = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    site = relationship("CandidateSite", back_populates="capacity_dimensions")

    __table_args__ = (
        UniqueConstraint('site_id', 'dimension', name='uq_site_dimension'),
    )


# ────────────────────────────────────────────────────────────────────────
# Risk Assessment (output of MasterEngine)
# ────────────────────────────────────────────────────────────────────────

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    habitation_id = Column(String, ForeignKey("habitations.id"), nullable=False, unique=True)

    hazard_score = Column(Float, default=0.0)
    exposure_score = Column(Float, default=0.0)
    vulnerability_score = Column(Float, default=0.0)
    rpi = Column(Float, default=0.0)                  # Relocation Priority Index
    risk_category = Column(String, default="LOW PRIORITY")

    # JSON blobs for detailed explanations
    hazard_explanation = Column(Text, nullable=True)
    exposure_explanation = Column(Text, nullable=True)
    vulnerability_explanation = Column(Text, nullable=True)
    rpi_explanation = Column(Text, nullable=True)

    weights_used = Column(Text, nullable=True)        # JSON of weights

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    habitation = relationship("Habitation", back_populates="risk_assessment")


# ────────────────────────────────────────────────────────────────────────
# Relocation Necessity (output of NecessityEngine)
# ────────────────────────────────────────────────────────────────────────

class RelocationNecessity(Base):
    __tablename__ = "relocation_necessities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    habitation_id = Column(String, ForeignKey("habitations.id"), nullable=False, unique=True)

    risk_score = Column(Float, default=0.0)
    category = Column(String, nullable=False)          # Immediate, Short-Term, Medium-Term, In-Situ, Monitor
    color_code = Column(String, nullable=True)
    action_timeline = Column(String, nullable=True)
    reasons = Column(Text, nullable=True)              # JSON array

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    habitation = relationship("Habitation", back_populates="necessity")


# ────────────────────────────────────────────────────────────────────────
# Relocation Assignment (output of Optimizer)
# ────────────────────────────────────────────────────────────────────────

class RelocationAssignment(Base):
    __tablename__ = "relocation_assignments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    habitation_id = Column(String, ForeignKey("habitations.id"), nullable=False)
    site_id = Column(String, ForeignKey("candidate_sites.id"), nullable=True)  # NULL = unassigned

    population = Column(Integer, default=0)
    necessity_category = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    status = Column(String, default="pending")         # pending, approved, in_progress, completed

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    habitation = relationship("Habitation", back_populates="assignments")
    site = relationship("CandidateSite", back_populates="assignments")

    __table_args__ = (
        UniqueConstraint('habitation_id', 'site_id', name='uq_hab_site_assignment'),
    )


# ────────────────────────────────────────────────────────────────────────
# Field Verification
# ────────────────────────────────────────────────────────────────────────

class FieldVerification(Base):
    __tablename__ = "field_verifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    habitation_id = Column(String, ForeignKey("habitations.id"), nullable=False)

    status = Column(String, default="pending")         # pending, verified, flagged
    assigned_date = Column(String, nullable=True)
    verified_date = Column(String, nullable=True)
    verifier_notes = Column(Text, nullable=True)
    verified_population = Column(Integer, nullable=True)
    verified_households = Column(Integer, nullable=True)
    verified_elevation = Column(Float, nullable=True)
    verified_slope = Column(Float, nullable=True)
    ground_truth_data = Column(Text, nullable=True)    # JSON blob

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    habitation = relationship("Habitation", back_populates="field_verifications")


# ────────────────────────────────────────────────────────────────────────
# Post-Relocation Tracking
# ────────────────────────────────────────────────────────────────────────

class PostRelocationRecord(Base):
    __tablename__ = "post_relocation_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    habitation_id = Column(String, ForeignKey("habitations.id"), nullable=False)
    site_id = Column(String, ForeignKey("candidate_sites.id"), nullable=False)

    households_relocated = Column(Integer, default=0)
    status = Column(String, default="Stable")          # Stable, Needs Attention, At Risk
    water_supply = Column(Boolean, default=True)
    healthcare = Column(Boolean, default=True)
    school = Column(Boolean, default=True)
    electricity = Column(Boolean, default=True)
    missing_infrastructure = Column(Text, nullable=True)  # JSON array

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    habitation = relationship("Habitation", back_populates="post_relocation_records")
    site = relationship("CandidateSite", back_populates="post_relocation_records")


# ────────────────────────────────────────────────────────────────────────
# Dataset & Validation
# ────────────────────────────────────────────────────────────────────────

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)           # habitations, hazards, sites
    format = Column(String, nullable=True)             # csv, geojson, demo
    record_count = Column(Integer, default=0)
    valid_count = Column(Integer, default=0)
    invalid_count = Column(Integer, default=0)
    confidence = Column(String, default="UNKNOWN")
    projected_crs = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    validation_results = relationship("DataValidationResult", back_populates="dataset")


class DataValidationResult(Base):
    __tablename__ = "data_validation_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    row_number = Column(Integer, nullable=True)
    errors = Column(Text, nullable=True)               # JSON array of error strings
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="validation_results")


# ────────────────────────────────────────────────────────────────────────
# Alerts
# ────────────────────────────────────────────────────────────────────────

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True)             # e.g. "ALR-xxxx"
    rule_id = Column(String, nullable=True)
    rule_name = Column(String, nullable=True)
    severity = Column(String, nullable=False)          # critical, high, warning, info
    category = Column(String, nullable=True)           # risk, hazard, exposure, vulnerability
    habitation_id = Column(String, ForeignKey("habitations.id"), nullable=True)
    habitation_name = Column(String, nullable=True)
    message = Column(Text, nullable=True)
    rpi = Column(Float, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ────────────────────────────────────────────────────────────────────────
# Audit Log
# ────────────────────────────────────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String, nullable=False)            # seed, upload, run_engine, optimize, etc.
    entity_type = Column(String, nullable=True)        # habitation, site, etc.
    entity_id = Column(String, nullable=True)
    details = Column(Text, nullable=True)              # JSON blob
    created_at = Column(DateTime, default=datetime.utcnow)
