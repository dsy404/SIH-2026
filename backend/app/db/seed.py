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
    "Housing", "Land", "Water", "Sanitation",
    "Healthcare", "Education", "Road Access", "Electricity",
]

RAW_DIMENSION_BASES = {
    "Housing": 1600,       # dwellings (~7,200 people @ 4.5/dwelling)
    "Land": 50,           # hectares (~7,500 people @ 150/ha)
    "Water": 500,         # kL/day (~7,142 people @ 70 LPCD)
    "Sanitation": 300,    # units (~7,500 people @ 25/toilet)
    "Healthcare": 30,     # clinic beds (~7,500 people @ 250/bed)
    "Education": 1500,    # seats (~7,500 people @ 5 pop/seat)
    "Road Access": 11000, # trips/day (~7,333 people @ 1.5 trips/person)
    "Electricity": 2600,  # kW (~7,428 people @ 0.35 kW/person)
}


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
            "distance_to_hazard": 75, "terrain_slope": 85, "soil_stability": 75,
            "historical_safety": 80, "road_accessibility": 65, "healthcare_proximity": 60,
            "education_proximity": 55, "area_capacity": 80, "water_access": 70,
            "power_access": 65, "distance_to_origin": 80, "environmental_impact": 70,
            "land_use": 75,
        },
        "S002": {
            "distance_to_hazard": 90, "terrain_slope": 90, "soil_stability": 85,
            "historical_safety": 95, "road_accessibility": 85, "healthcare_proximity": 80,
            "education_proximity": 75, "area_capacity": 95, "water_access": 85,
            "power_access": 90, "distance_to_origin": 70, "environmental_impact": 75,
            "land_use": 85,
        },
        "S003": {
            "distance_to_hazard": 80, "terrain_slope": 80, "soil_stability": 75,
            "historical_safety": 85, "road_accessibility": 75, "healthcare_proximity": 70,
            "education_proximity": 65, "area_capacity": 85, "water_access": 80,
            "power_access": 75, "distance_to_origin": 65, "environmental_impact": 80,
            "land_use": 75,
        },
        "S004": {
            "distance_to_hazard": 85, "terrain_slope": 75, "soil_stability": 80,
            "historical_safety": 90, "road_accessibility": 80, "healthcare_proximity": 75,
            "education_proximity": 70, "area_capacity": 90, "water_access": 80,
            "power_access": 80, "distance_to_origin": 70, "environmental_impact": 85,
            "land_use": 80,
        },
        "S005": {
            "distance_to_hazard": 95, "terrain_slope": 85, "soil_stability": 90,
            "historical_safety": 95, "road_accessibility": 90, "healthcare_proximity": 85,
            "education_proximity": 80, "area_capacity": 90, "water_access": 90,
            "power_access": 85, "distance_to_origin": 75, "environmental_impact": 90,
            "land_use": 90,
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
    """Generate deterministic capacity data for each site × each dimension using real physical units."""
    sites = Repository.get_all_sites(db)

    for site in sites:
        base = sum(ord(c) for c in site.id) % 25
        for i, dim in enumerate(CAPACITY_DIMENSIONS):
            base_val = RAW_DIMENSION_BASES.get(dim, 1000)
            # Modulate base capacity by ±15% deterministically per site
            factor = 0.85 + (((base * (i + 3)) % 30) / 100.0)
            max_cap = int(base_val * factor)
            # Utilization between 25% and 40%
            util_rate = 0.25 + (((base * (i + 1)) % 15) / 100.0)
            current = int(max_cap * util_rate)

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


def compute_optimizer_assignments(db: Session):
    """Run RelocationOptimizer on all habitations and sites, storing assignments in DB."""
    from ..engines.relocation.optimizer import RelocationOptimizer

    Repository.clear_assignments(db)
    all_habs = Repository.get_all_habitations(db)
    habs_for_opt = []
    for h in all_habs:
        d = {
            "id": h.id,
            "name": h.name,
            "population": h.population,
            "latitude": h.latitude,
            "longitude": h.longitude,
        }
        if h.risk_assessment:
            d["risk_score"] = h.risk_assessment.rpi
        else:
            d["risk_score"] = 0.0
        habs_for_opt.append(d)

    sites_for_opt = []
    for s in Repository.get_all_sites(db):
        sites_for_opt.append({
            "id": s.id,
            "site_id": s.id,
            "name": s.name,
            "site_name": s.name,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "factors": {
                "distance_to_hazard": s.distance_to_hazard or 50,
                "terrain_slope": s.terrain_slope_score or 50,
                "soil_stability": s.soil_stability or 50,
                "historical_safety": s.historical_safety or 50,
                "road_accessibility": s.road_accessibility or 50,
                "healthcare_proximity": s.healthcare_proximity or 50,
                "education_proximity": s.education_proximity or 50,
                "area_capacity": s.area_capacity or 50,
                "water_access": s.water_access or 50,
                "power_access": s.power_access or 50,
                "distance_to_origin": s.distance_to_origin or 50,
                "environmental_impact": s.environmental_impact or 50,
                "land_use": s.land_use or 50,
            },
        })

    opt_results = RelocationOptimizer.run_optimization(habs_for_opt, sites_for_opt)

    for assignment in opt_results.get("assignments", []):
        Repository.save_assignment(db, {
            "habitation_id": assignment["habitation_id"],
            "site_id": assignment["assigned_site_id"],
            "population": assignment["population"],
            "necessity_category": assignment.get("necessity"),
            "reason": assignment.get("reason", "Optimized assignment"),
            "status": "pending",
        })
    db.flush()


def reset_database(db: Session):
    """Clean all records to allow clean, idempotent re-seeding."""
    from .models import (
        RelocationAssignment, RelocationNecessity, RiskAssessment,
        SiteCapacityDimension, FieldVerification, PostRelocationRecord,
        Hazard, CandidateSite, Habitation, Block, District, State, AuditLog
    )
    for model in [
        RelocationAssignment, RelocationNecessity, RiskAssessment,
        SiteCapacityDimension, FieldVerification, PostRelocationRecord,
        Hazard, CandidateSite, Habitation, Block, District, State, AuditLog
    ]:
        db.query(model).delete()
    db.commit()



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
    db.commit()

    print("[SEED] Computing relocation assignments (RelocationOptimizer)...")
    compute_optimizer_assignments(db)
    db.commit()

    print("[SEED] Creating demo post-relocation records...")
    seed_post_relocation(db)

    print("[SEED] Creating demo field verification tasks...")
    seed_field_verifications(db)

    Repository.log_action(db, "seed", details="Full database seeded from synthetic data")

    db.commit()
    print(f"[SEED] Done. Habitations: {Repository.count_habitations(db)}, Sites: {Repository.count_sites(db)}")


