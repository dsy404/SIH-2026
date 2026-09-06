"""
Datasets API — Production-Quality Real Data Ingestion (CSV & GeoJSON).

Workflow:
1. POST /api/datasets/inspect     -> Schema inspection, CRS/geometry detection & mapping suggestions
2. POST /api/datasets/validate    -> Constraint validation, anomaly detection & error reporting
3. POST /api/datasets/import      -> Cleaning, WGS84 standardization, DB persistence & automated recalculation
4. GET  /api/datasets             -> List all active datasets with full metadata
5. GET  /api/datasets/templates/<template_name> -> Download sample templates
6. POST /api/datasets/upload      -> Legacy single-step upload endpoint
"""
from flask import Blueprint, request, jsonify, send_file
import json
import os
from typing import Dict, Any, List

from app.data_ingestion.csv_provider import CSVProvider
from app.data_ingestion.geojson_provider import GeoJSONProvider
from app.data_ingestion.demo_provider import DemoProvider
from app.data_ingestion.validator import DataValidator
from app.data_ingestion.cleaner import DataCleaner
from app.data_ingestion.confidence_service import ConfidenceService
from app.geospatial.crs import determine_crs_from_centroid
from app.db.database import get_session_factory
from app.db.repository import Repository

datasets_bp = Blueprint('datasets', __name__)

TEMPLATES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'templates'))


def _apply_mapping(records: List[Dict[str, Any]], mapping: Dict[str, str]) -> List[Dict[str, Any]]:
    """Transforms raw records using the user's field mapping {uploaded_col: canonical_field}."""
    if not mapping:
        return records

    mapped_data = []
    for row in records:
        new_row = {}
        for uploaded_col, canonical_field in mapping.items():
            if canonical_field and canonical_field != "__ignore__":
                new_row[canonical_field] = row.get(uploaded_col)
        # Preserve existing coordinates or geometry if not overwritten
        if 'geom_geojson' in row and 'geom_geojson' not in new_row:
            new_row['geom_geojson'] = row['geom_geojson']
        mapped_data.append(new_row)
    return mapped_data


def _trigger_full_pipeline_recalculation(session):
    """
    Executes the analytical engines across all habitations and sites
    so newly ingested real datasets immediately receive RPI, necessity,
    and relocation optimizer assignments.
    """
    from app.engines.master_engine import MasterEngine
    from app.engines.relocation.necessity import NecessityEngine
    from app.engines.relocation.optimizer import RelocationOptimizer

    habitations = Repository.get_all_habitations(session)
    hazards = Repository.get_all_hazards(session)

    hab_dicts = [Repository.habitation_to_dict(h) for h in habitations]
    hazard_dicts = [
        {"id": hz.id, "type": hz.type, "severity": hz.severity, "geom_geojson": hz.geom_geojson}
        for hz in hazards
    ]

    me = MasterEngine()
    scored = me.calculate_priority_index(hab_dicts, hazard_dicts)

    for hab_data in scored:
        hab_id = hab_data['id']
        Repository.save_risk_assessment(session, {
            "habitation_id": hab_id,
            "hazard_score": hab_data.get('hazard_score', 0),
            "exposure_score": hab_data.get('exposure_score', 0),
            "vulnerability_score": hab_data.get('vulnerability_score', 0),
            "rpi": hab_data.get('rpi', 0),
            "risk_category": hab_data.get('risk_category', 'Low'),
            "hazard_explanation": json.dumps(hab_data.get('explanation')) if hab_data.get('explanation') else None,
            "exposure_explanation": json.dumps(hab_data.get('exposure_explanation')) if hab_data.get('exposure_explanation') else None,
            "vulnerability_explanation": json.dumps(hab_data.get('vulnerability_explanation')) if hab_data.get('vulnerability_explanation') else None,
            "rpi_explanation": json.dumps(hab_data.get('rpi_explanation')) if hab_data.get('rpi_explanation') else None,
        })

        necessity = NecessityEngine.evaluate_necessity(hab_id, hab_data.get('rpi', 0))
        Repository.save_necessity(session, {
            "habitation_id": hab_id,
            "risk_score": necessity["risk_score"],
            "category": necessity["category"],
            "color_code": necessity["color_code"],
            "action_timeline": necessity["action_timeline"],
            "reasons": json.dumps(necessity["reasons"]),
        })

    session.commit()

    # Re-run optimizer
    Repository.clear_assignments(session)
    habs_for_opt = []
    for h in Repository.get_all_habitations(session):
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
    for s in Repository.get_all_sites(session):
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
    for a in opt_results.get("assignments", []):
        Repository.save_assignment(session, {
            "habitation_id": a["habitation_id"],
            "site_id": a["assigned_site_id"],
            "population": a["population"],
            "necessity_category": a.get("necessity"),
            "reason": a.get("reason", "Optimized assignment"),
            "status": "pending",
        })
    for u in opt_results.get("unassigned", []):
        Repository.save_assignment(session, {
            "habitation_id": u["habitation_id"],
            "site_id": None,
            "population": u["population"],
            "necessity_category": u.get("necessity"),
            "reason": u.get("reason", "Unassigned due to capacity deficit"),
            "status": "unassigned",
        })
    session.commit()


# ────────────────────────────────────────────────────────────────────────
# Datasets Listing
# ────────────────────────────────────────────────────────────────────────

@datasets_bp.route("", methods=["GET"])
@datasets_bp.route("/", methods=["GET"])
def get_datasets():
    """Lists all active and uploaded datasets with full audit metadata."""
    Session = get_session_factory()
    session = Session()
    try:
        datasets = Repository.get_all_datasets(session)
        result = []
        for ds in datasets:
            result.append({
                "id": ds.id,
                "name": ds.name,
                "source": ds.source or "Uploaded File",
                "original_filename": ds.original_filename or ds.name,
                "category": ds.category or "habitations",
                "format": ds.format or "csv",
                "geometry_type": ds.geometry_type or "Point",
                "record_count": ds.record_count or 0,
                "valid_count": ds.valid_count or 0,
                "invalid_count": ds.invalid_count or 0,
                "missing_values_count": ds.missing_values_count or 0,
                "validation_status": ds.validation_status or "READY",
                "processing_status": ds.processing_status or "Completed",
                "is_real": ds.is_real if ds.is_real is not None else True,
                "confidence": ds.confidence or "REAL",
                "projected_crs": ds.projected_crs or "EPSG:4326",
                "created_at": ds.created_at.isoformat() if ds.created_at else None,
            })
        return jsonify(result)
    finally:
        session.close()


# ────────────────────────────────────────────────────────────────────────
# Step 1: Upload & Inspect
# ────────────────────────────────────────────────────────────────────────

@datasets_bp.route("/inspect", methods=["POST"])
def inspect_dataset():
    """
    Parses uploaded file (CSV or GeoJSON), returns headers, preview rows,
    detected CRS, geometry type, and suggested field mappings.
    Accepts multipart file upload or JSON payload {content, filename, category}.
    """
    if request.is_json:
        data = request.get_json() or {}
        content = data.get('content', '')
        filename = data.get('filename', 'uploaded_file')
        category = data.get('category', 'habitations')
    elif 'file' in request.files:
        file = request.files['file']
        category = request.form.get('category', 'habitations')
        filename = file.filename or "uploaded_file"
        content = file.read().decode('utf-8', errors='replace')
    else:
        return jsonify({"detail": "No file uploaded or content provided."}), 400

    if not content or not content.strip():
        return jsonify({"detail": "Uploaded file is empty (0 bytes)."}), 400

    # Auto-detect format from extension or content
    is_json = filename.lower().endswith('.geojson') or filename.lower().endswith('.json') or content.strip().startswith('{')
    format_type = "geojson" if is_json else "csv"

    try:
        if format_type == "geojson":
            provider = GeoJSONProvider()
            inspection = provider.inspect_data(content, category)
        else:
            provider = CSVProvider()
            inspection = provider.inspect_data(content, category)

        inspection["original_filename"] = filename
        inspection["content"] = content  # Echo back so client can carry it to validate/import without multi-part re-upload
        return jsonify(inspection)

    except Exception as e:
        return jsonify({"detail": f"Inspection error: {str(e)}"}), 400



# ────────────────────────────────────────────────────────────────────────
# Step 2: Validate Mapped Data
# ────────────────────────────────────────────────────────────────────────

@datasets_bp.route("/validate", methods=["POST"])
def validate_dataset():
    """
    Validates records against canonical category schemas using user-specified column mappings.
    Detects impossible coordinates, missing required attributes, and invalid geometries.
    """
    data = request.get_json() or {}
    category = data.get('category', 'habitations')
    filename = data.get('filename', '')
    format_type = data.get('format')
    if not format_type:
        format_type = 'geojson' if filename.lower().endswith(('.geojson', '.json')) else 'csv'

    mapping = data.get('mapping') or data.get('column_mapping') or {}
    crs = data.get('crs', 'EPSG:4326')
    content = data.get('content', '')
    records = data.get('records', [])

    if not records and content:
        provider = GeoJSONProvider() if format_type == "geojson" else CSVProvider()
        records = provider.read_data(content)

    if not records:
        return jsonify({
            "valid_count": 0,
            "invalid_count": 0,
            "errors": [{"row": 0, "field": "file", "message": "File contains 0 records."}],
            "can_import": False,
        }), 400

    mapped_records = _apply_mapping(records, mapping)

    # Define required canonical fields
    required_fields = ["name", "population"] if category == "habitations" else (
        ["type", "severity"] if category == "hazards" else ["name"]
    )

    validator = DataValidator(required_fields)
    val_result = validator.validate_detailed(mapped_records, category, crs)

    return jsonify({
        "status": "VALIDATED" if val_result["can_import"] else "FAILED",
        "category": category,
        "valid_count": val_result["valid_count"],
        "invalid_count": val_result["invalid_count"],
        "missing_values_count": val_result["missing_values_count"],
        "errors": val_result["errors"][:50],  # Return up to first 50 errors
        "can_import": val_result["can_import"],
        "sample_valid": val_result["valid_records"][:5],
    })


# ────────────────────────────────────────────────────────────────────────
# Step 3: Clean, Import & Recalculate
# ────────────────────────────────────────────────────────────────────────

@datasets_bp.route("/import", methods=["POST"])
def import_dataset():
    """
    Cleans, standardizes to WGS84, persists real records to the canonical DB,
    and automatically triggers the full engine pipeline recalculation.
    """
    data = request.get_json() or {}
    category = data.get('category', 'habitations')
    filename = data.get('filename') or data.get('original_filename', '')
    format_type = data.get('format')
    if not format_type:
        format_type = 'geojson' if filename.lower().endswith(('.geojson', '.json')) else 'csv'

    mapping = data.get('mapping') or data.get('column_mapping') or {}
    dataset_name = data.get('dataset_name', 'Real Data Ingestion')
    source = data.get('source', 'Field Survey / Official Source')
    original_filename = filename or f"{category}.{format_type}"
    crs = data.get('crs', 'EPSG:4326')
    content = data.get('content', '')
    records = data.get('records', [])

    if not records and content:
        provider = GeoJSONProvider() if format_type == "geojson" else CSVProvider()
        records = provider.read_data(content)

    if not records:
        return jsonify({"detail": "No records to import."}), 400

    # 1. Apply column mapping
    mapped_records = _apply_mapping(records, mapping)

    # 2. Validate
    required_fields = ["name", "population"] if category == "habitations" else (
        ["type", "severity"] if category == "hazards" else ["name"]
    )
    validator = DataValidator(required_fields)
    val_result = validator.validate_detailed(mapped_records, category, crs)

    if not val_result["valid_records"]:
        return jsonify({
            "status": "FAILED",
            "detail": "Cannot import: 0 valid records found.",
            "errors": val_result["errors"],
        }), 400

    # 3. Clean
    cleaner = DataCleaner()
    cleaned_records = cleaner.clean(val_result["valid_records"])

    # 4. Standardize Coordinates & Assign Confidence
    confidence_svc = ConfidenceService()
    final_records = confidence_svc.assign_confidence(cleaned_records, format_type, category)
    projected_crs = determine_crs_from_centroid(final_records)

    # 5. Persist to Canonical SQLite Database
    Session = get_session_factory()
    session = Session()
    saved_count = 0
    try:
        if category == "habitations":
            for idx, r in enumerate(final_records):
                hab_id = r.get('id') or f"HAB-R{idx+1:03d}"
                Repository.upsert_habitation(session, {
                    "id": hab_id,
                    "name": r.get('name', f'Habitation {hab_id}'),
                    "population": r.get('population', 0),
                    "households": r.get('households', 0),
                    "latitude": r.get('latitude', 0.0),
                    "longitude": r.get('longitude', 0.0),
                    "geom_geojson": r.get('geom_geojson'),
                    "elevation": r.get('elevation'),
                    "slope": r.get('slope'),
                    "aspect": r.get('aspect'),
                    "dataset_type": "REAL",
                    "confidence": "REAL",
                })
                saved_count += 1

        elif category == "hazards":
            for idx, r in enumerate(final_records):
                haz_id = r.get('id') or f"HAZ-R{idx+1:03d}"
                Repository.upsert_hazard(session, {
                    "id": haz_id,
                    "type": r.get('type', 'Unknown Hazard'),
                    "severity": r.get('severity', 'Moderate'),
                    "geom_geojson": r.get('geom_geojson'),
                    "dataset_type": "REAL",
                })
                saved_count += 1

        elif category == "candidate_sites":
            for idx, r in enumerate(final_records):
                site_id = r.get('id') or f"SITE-R{idx+1:03d}"
                Repository.upsert_site(session, {
                    "id": site_id,
                    "name": r.get('name', f'Candidate Site {site_id}'),
                    "latitude": r.get('latitude', 0.0),
                    "longitude": r.get('longitude', 0.0),
                    "geom_geojson": r.get('geom_geojson'),
                    "elevation": r.get('elevation'),
                    "slope": r.get('slope'),
                    "aspect": r.get('aspect'),
                    "infrastructure_score": r.get('infrastructure_score', 65.0),
                    "area_capacity": r.get('area_capacity', 80),
                    "dataset_type": "REAL",
                })
                saved_count += 1

        # 6. Save Dataset Metadata Record
        dataset_record = Repository.save_dataset(session, {
            "name": dataset_name,
            "source": source,
            "original_filename": original_filename,
            "category": category,
            "format": format_type,
            "geometry_type": "Polygon" if category == "hazards" else "Point",
            "record_count": len(records),
            "valid_count": len(final_records),
            "invalid_count": val_result["invalid_count"],
            "missing_values_count": val_result["missing_values_count"],
            "validation_status": "STANDARDIZED",
            "processing_status": "READY",
            "is_real": True,
            "confidence": "REAL",
            "projected_crs": projected_crs,
        })

        # Save validation errors if any invalid records occurred
        for inv in val_result["invalid_records"][:20]:
            Repository.save_validation_result(session, {
                "dataset_id": dataset_record.id,
                "row_number": inv.get('__row_num__', 0),
                "errors": json.dumps(inv.get('__errors__', [])),
            })

        Repository.log_action(session, "import_real_data", entity_type=category,
                              details=json.dumps({"name": dataset_name, "imported": saved_count}))
        session.commit()

        # 7. Automated Full System Pipeline Recalculation
        _trigger_full_pipeline_recalculation(session)

        total_habs = Repository.count_habitations(session)

        return jsonify({
            "status": "success",
            "success": True,
            "dataset_id": dataset_record.id,
            "imported_count": saved_count,
            "total_system_habitations": total_habs,
            "recalculated": True,
            "recalculation_summary": {
                "status": "completed",
                "total_habitations_evaluated": total_habs,
            },
            "message": f"Successfully imported {saved_count} real {category} records. Downstream risk, necessity, and optimizer pipelines recalculated."
        })

    except Exception as e:
        session.rollback()
        return jsonify({"detail": f"Import failed: {str(e)}"}), 500
    finally:
        session.close()


# ────────────────────────────────────────────────────────────────────────
# Templates Download
# ────────────────────────────────────────────────────────────────────────

@datasets_bp.route("/templates/<template_name>", methods=["GET"])
def download_template(template_name: str):
    """Provides downloadable reference templates for CSV and GeoJSON."""
    allowed = {
        "sample_habitations.csv": "sample_habitations.csv",
        "sample_habitations.geojson": "sample_habitations.geojson",
        "sample_hazards.geojson": "sample_hazards.geojson",
        "sample_candidate_sites.csv": "sample_candidate_sites.csv",
        "habitations.csv": "sample_habitations.csv",
        "habitations.geojson": "sample_habitations.geojson",
        "hazards.geojson": "sample_hazards.geojson",
        "candidate_sites.csv": "sample_candidate_sites.csv",
    }

    target_file = allowed.get(template_name)
    if not target_file:
        return jsonify({"detail": f"Template '{template_name}' not found."}), 404

    file_path = os.path.join(TEMPLATES_DIR, target_file)
    if not os.path.exists(file_path):
        return jsonify({"detail": f"Template file not found on disk."}), 404

    return send_file(file_path, as_attachment=True, download_name=target_file)


# ────────────────────────────────────────────────────────────────────────
# Legacy Upload Route (for backward compatibility)
# ────────────────────────────────────────────────────────────────────────

@datasets_bp.route("/upload", methods=["POST"])
def upload_dataset():
    """Legacy single-step upload handler."""
    if 'file' not in request.files and request.form.get('format') != 'demo':
        return jsonify({"detail": "No file part"}), 400

    file = request.files.get('file')
    category = request.form.get('category', 'habitations')
    format_type = request.form.get('format', 'geojson')

    if format_type == "demo":
        provider = DemoProvider()
        source = file.filename if file else "habitations.geojson"
    elif format_type == "csv":
        provider = CSVProvider()
        source = file.read().decode("utf-8", errors='replace')
    elif format_type == "geojson":
        provider = GeoJSONProvider()
        source = file.read().decode("utf-8", errors='replace')
    else:
        return jsonify({"detail": f"Unsupported format {format_type}"}), 400

    try:
        raw_data = provider.read_data(source)
        inspection = provider.inspect_data(source, category) if hasattr(provider, 'inspect_data') else {}
        suggested_mapping = inspection.get("suggested_mapping", {})
        mapped = _apply_mapping(raw_data, suggested_mapping)

        validator = DataValidator(["name", "population"] if category == "habitations" else ["type", "severity"])
        val_res = validator.validate_detailed(mapped, category)

        cleaner = DataCleaner()
        cleaned = cleaner.clean(val_res["valid_records"])

        confidence_svc = ConfidenceService()
        final_data = confidence_svc.assign_confidence(cleaned, format_type, category)
        projected_crs = determine_crs_from_centroid(final_data)

        Session = get_session_factory()
        session = Session()
        saved_count = 0
        try:
            if category == "habitations":
                for idx, record in enumerate(final_data):
                    hab_id = record.get('id', f"HAB-U{idx+1:03d}")
                    Repository.upsert_habitation(session, {
                        "id": hab_id,
                        "name": record.get('name', f'Habitation {hab_id}'),
                        "population": record.get('population', 0),
                        "households": record.get('households', 0),
                        "latitude": record.get('latitude', 0),
                        "longitude": record.get('longitude', 0),
                        "geom_geojson": record.get('geom_geojson'),
                        "elevation": record.get('elevation'),
                        "slope": record.get('slope'),
                        "aspect": record.get('aspect'),
                        "dataset_type": "REAL",
                        "confidence": "REAL",
                    })
                    saved_count += 1
            session.commit()
            _trigger_full_pipeline_recalculation(session)
        finally:
            session.close()

        return jsonify({
            "status": "success",
            "category": category,
            "format": format_type,
            "projected_crs": projected_crs,
            "total_records": len(raw_data),
            "valid_records_count": len(final_data),
            "saved_to_db": saved_count,
        })
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
