"""
Database seeder — reads synthetic GeoJSON files and populates the canonical DB.

Also runs the MasterEngine + NecessityEngine to compute and store initial
risk assessments and necessity classifications, and generates site capacity data.

Called automatically on app startup if the DB is empty.
"""
from __future__ import annotations

import json
import os
import random
from typing import List, Dict, Any

from sqlalchemy.orm import Session

from .models import (
    State, District, Block, Habitation, Hazard, CandidateSite,
    SiteCapacityDimension, PostRelocationRecord, FieldVerification,
)
from .repository import Repository


SYNTHETIC_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'synthetic')

CAPACITY_DIMENSIONS = [
    "Housing", "Water Supply", "Power Grid", "Healthcare",
    "Education", "Sanitation", "Transport", "Livelihood",
]


def _load_geojson(filename: str) -> List[Dict[str, Any]]:
    path = os.path.join(SYNTHETIC_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        data = json.load(f)
    return data.get('features', [])


def _seed_admin_hierarchy(db: Session):
    """Create a minimal administrative hierarchy for synthetic data."""
    state = State(id="ST01", name="Demonstration State")
    db.add(state)

    district = District(id="DIST01", name="Demonstration District", state_id="ST01")
    db.add(district)

    for block_name in ["Block A", "Block B", "Block C"]:
        block_id = f"BLK-{block_name.replace(' ', '-').upper()}"
        db.add(Block(id=block_id, name=block_name, district_id="DIST01"))

    db.flush()


def _block_name_to_id(block_name: str) -> str:
    return f"BLK-{block_name.replace(' ', '-').upper()}"


def seed_habitations(db: Session):
    """Seed habitations from synthetic GeoJSON."""
    features = _load_geojson('habitations.geojson')

    for feature in features:
        props = feature.get('properties', {})
        geom = feature.get('geometry', {})
        coords = geom.get('coordinates', [0, 0])

        raw_id = props.get('id', '')
        # Normalize ID: H001 → HAB001
        if raw_id.startswith('H') and not raw_id.startswith('HAB'):
            num = raw_id[1:]
            hab_id = f"HAB{num}"
        else:
            hab_id = raw_id

        block_name = props.get('block', 'Block A')
        block_id = _block_name_to_id(block_name)

        Repository.upsert_habitation(db, {
            "id": hab_id,
            "name": props.get('name', f'Habitation {hab_id}'),
            "block_id": block_id,
            "population": props.get('population', 0),
            "households": props.get('households', 0),
            "latitude": coords[1] if len(coords) >= 2 else 0,
            "longitude": coords[0] if len(coords) >= 1 else 0,
            "geom_geojson": json.dumps(geom),
            "elevation": props.get('elevation'),
            "slope": props.get('slope'),
            "aspect": props.get('aspect'),
            "dataset_type": props.get('dataset_type', 'DEMO / SYNTHETIC DATA'),
            "confidence": "SYNTHETIC",
        })

    db.flush()


def seed_hazards(db: Session):
    """Seed hazards from synthetic GeoJSON."""
    features = _load_geojson('hazards.geojson')

    for feature in features:
        props = feature.get('properties', {})
        geom = feature.get('geometry', {})

        raw_id = props.get('id', '')
        haz_id = raw_id if raw_id.startswith('HAZ') else f"HAZ{raw_id}"

        Repository.upsert_hazard(db, {
            "id": haz_id,
            "type": props.get('type', 'Unknown'),
            "severity": props.get('severity', 'Moderate'),
            "geom_geojson": json.dumps(geom),
            "dataset_type": props.get('dataset_type', 'DEMO / SYNTHETIC DATA'),
        })

    db.flush()


def seed_sites(db: Session):
    """Seed candidate sites from synthetic GeoJSON."""
    features = _load_geojson('candidate_sites.geojson')

    # Deterministic suitability factors for demo sites
    demo_factors = {
        "S001": {
            "distance_to_hazard": 70, "terrain_slope": 85, "soil_stability": 75,
            "historical_safety": 80, "road_accessibility": 60, "healthcare_proximity": 55,
            "education_proximity": 50, "area_capacity": 80, "water_access": 70,
            "power_access": 65, "distance_to_origin": 80, "environmental_impact": 70,
            "land_use": 75,
        },
        "S002": {
            "distance_to_hazard": 90, "terrain_slope": 90, "soil_stability": 85,
            "historical_safety": 95, "road_accessibility": 85, "healthcare_proximity": 80,
            "education_proximity": 75, "area_capacity": 95, "water_access": 85,
            "power_access": 90, "distance_to_origin": 40, "environmental_impact": 75,
            "land_use": 85,
        },
    }

    for feature in features:
        props = feature.get('properties', {})
        geom = feature.get('geometry', {})
        coords = geom.get('coordinates', [0, 0])

        raw_id = props.get('id', '')
        site_id = f"SITE{raw_id[1:]}" if raw_id.startswith('S') and not raw_id.startswith('SITE') else raw_id

        factors = demo_factors.get(raw_id, {})

        Repository.upsert_site(db, {
            "id": site_id,
            "name": props.get('name', f'Site {site_id}'),
            "latitude": coords[1],
            "longitude": coords[0],
            "geom_geojson": json.dumps(geom),
            "elevation": props.get('elevation'),
            "slope": props.get('slope'),
            "aspect": props.get('aspect'),
            "infrastructure_score": props.get('infrastructure_score'),
            "distance_to_hazard": factors.get('distance_to_hazard', 50),
            "terrain_slope_score": factors.get('terrain_slope', 50),
            "soil_stability": factors.get('soil_stability', 50),
            "historical_safety": factors.get('historical_safety', 50),
            "road_accessibility": factors.get('road_accessibility', 50),
            "healthcare_proximity": factors.get('healthcare_proximity', 50),
            "education_proximity": factors.get('education_proximity', 50),
            "area_capacity": factors.get('area_capacity', 50),
            "water_access": factors.get('water_access', 50),
            "power_access": factors.get('power_access', 50),
            "distance_to_origin": factors.get('distance_to_origin', 50),
            "environmental_impact": factors.get('environmental_impact', 50),
            "land_use": factors.get('land_use', 50),
            "dataset_type": props.get('dataset_type', 'DEMO / SYNTHETIC DATA'),
        })

    db.flush()


def seed_capacity(db: Session):
    """Generate deterministic capacity data for each site × each dimension."""
    sites = Repository.get_all_sites(db)

    for site in sites:
        base = sum(ord(c) for c in site.id) % 100
        for i, dim in enumerate(CAPACITY_DIMENSIONS):
            max_cap = 2000 + ((base * (i + 1) * 37) % 8000)
            current = int(max_cap * (0.3 + ((base * i) % 40) / 100.0))
            Repository.upsert_capacity_dimension(db, {
                "site_id": site.id,
                "dimension": dim,
                "max_capacity": max_cap,
                "current_utilization": current,
            })

    db.flush()


def compute_risk_assessments(db: Session):
    """Run MasterEngine on all habitations and store results in DB."""
    from ..engines.hazard_engine import HazardEngine
    from ..engines.exposure_engine import ExposureEngine
    from ..engines.vulnerability_engine import VulnerabilityEngine
    from ..engines.master_engine import MasterEngine

    habitations = Repository.get_all_habitations(db)
    hazards = Repository.get_all_hazards(db)

    # Convert to dicts for the engines (they operate on dicts)
    hab_dicts = [Repository.habitation_to_dict(h) for h in habitations]
    hazard_dicts = [
        {"id": hz.id, "type": hz.type, "severity": hz.severity, "geom_geojson": hz.geom_geojson}
        for hz in hazards
    ]

    engine = MasterEngine()
    scored = engine.calculate_priority_index(hab_dicts, hazard_dicts)

    for hab_data in scored:
        hab_id = hab_data['id']
        Repository.save_risk_assessment(db, {
            "habitation_id": hab_id,
            "hazard_score": hab_data.get('hazard_score', 0),
            "exposure_score": hab_data.get('exposure_score', 0),
            "vulnerability_score": hab_data.get('vulnerability_score', 0),
            "rpi": hab_data.get('rpi', 0),
            "risk_category": hab_data.get('risk_category', 'LOW PRIORITY'),
            "hazard_explanation": json.dumps(hab_data.get('explanation')) if hab_data.get('explanation') else None,
            "exposure_explanation": json.dumps(hab_data.get('exposure_explanation')) if hab_data.get('exposure_explanation') else None,
            "vulnerability_explanation": json.dumps(hab_data.get('vulnerability_explanation')) if hab_data.get('vulnerability_explanation') else None,
            "rpi_explanation": json.dumps(hab_data.get('rpi_explanation')) if hab_data.get('rpi_explanation') else None,
        })

    db.flush()


def compute_necessities(db: Session):
    """Run NecessityEngine on all habitations using stored risk scores."""
    from ..engines.relocation.necessity import NecessityEngine

    assessments = Repository.get_all_risk_assessments(db)
    for ra in assessments:
        result = NecessityEngine.evaluate_necessity(ra.habitation_id, ra.rpi)
        Repository.save_necessity(db, {
            "habitation_id": ra.habitation_id,
            "risk_score": result["risk_score"],
            "category": result["category"],
            "color_code": result["color_code"],
            "action_timeline": result["action_timeline"],
            "reasons": json.dumps(result["reasons"]),
        })

    db.flush()


def seed_post_relocation(db: Session):
    """Create some demo post-relocation records for habitations assigned to sites."""
    sites = Repository.get_all_sites(db)
    habitations = Repository.get_all_habitations(db)

    if not sites or not habitations:
        return

    # Assign first few habitations to sites with different infrastructure statuses
    infra_configs = [
        {"water_supply": True, "healthcare": True, "school": True, "electricity": True, "missing_infrastructure": "[]"},
        {"water_supply": True, "healthcare": False, "school": True, "electricity": True, "missing_infrastructure": json.dumps(["Healthcare (Clinic)"])},
        {"water_supply": False, "healthcare": False, "school": False, "electricity": True, "missing_infrastructure": json.dumps(["Water Supply", "Healthcare", "School"])},
        {"water_supply": True, "healthcare": True, "school": False, "electricity": True, "missing_infrastructure": json.dumps(["School"])},
    ]

    for i, hab in enumerate(habitations[:min(4, len(habitations))]):
        site = sites[i % len(sites)]
        infra = infra_configs[i % len(infra_configs)]
        missing = json.loads(infra["missing_infrastructure"])
        missing_count = len(missing)

        if missing_count == 0:
            status = "Stable"
        elif missing_count == 1:
            status = "Needs Attention"
        else:
            status = "At Risk"

        db.add(PostRelocationRecord(
            habitation_id=hab.id,
            site_id=site.id,
            households_relocated=hab.households,
            status=status,
            **{k: v for k, v in infra.items() if k != "missing_infrastructure"},
            missing_infrastructure=infra["missing_infrastructure"],
        ))

    db.flush()


def seed_field_verifications(db: Session):
    """Create some demo field verification tasks."""
    habitations = Repository.get_all_habitations(db)
    if not habitations:
        return

    # First 3 habitations get verification tasks
    statuses = ["pending", "pending", "verified"]
    for i, hab in enumerate(habitations[:min(3, len(habitations))]):
        db.add(FieldVerification(
            habitation_id=hab.id,
            status=statuses[i],
            assigned_date="2026-09-03",
            verified_date="2026-09-04" if statuses[i] == "verified" else None,
        ))

    db.flush()


def seed_database(db: Session):
    """Main seeder: seeds everything in order."""
    print("[SEED] Seeding administrative hierarchy...")
    _seed_admin_hierarchy(db)

    print("[SEED] Seeding habitations from synthetic GeoJSON...")
    seed_habitations(db)

    print("[SEED] Seeding hazards from synthetic GeoJSON...")
    seed_hazards(db)

    print("[SEED] Seeding candidate sites from synthetic GeoJSON...")
    seed_sites(db)

    print("[SEED] Generating capacity dimensions for sites...")
    seed_capacity(db)

    print("[SEED] Computing risk assessments (MasterEngine)...")
    compute_risk_assessments(db)

    print("[SEED] Computing relocation necessities...")
    compute_necessities(db)

    print("[SEED] Creating demo post-relocation records...")
    seed_post_relocation(db)

    print("[SEED] Creating demo field verification tasks...")
    seed_field_verifications(db)

    Repository.log_action(db, "seed", details="Full database seeded from synthetic data")

    db.commit()
    print(f"[SEED] Done. Habitations: {Repository.count_habitations(db)}, Sites: {Repository.count_sites(db)}")
