"""
Datasets API — ingestion endpoint that saves cleaned data into the canonical DB.
"""
from flask import Blueprint, request, jsonify
import json
from app.data_ingestion.demo_provider import DemoProvider
from app.data_ingestion.csv_provider import CSVProvider
from app.data_ingestion.geojson_provider import GeoJSONProvider
from app.data_ingestion.validator import DataValidator
from app.data_ingestion.cleaner import DataCleaner
from app.data_ingestion.confidence_service import ConfidenceService
from app.geospatial.crs import determine_crs_from_centroid
from app.db.database import get_session_factory
from app.db.repository import Repository

datasets_bp = Blueprint('datasets', __name__)


@datasets_bp.route("/upload", methods=["POST"])
def upload_dataset():
    if 'file' not in request.files and request.form.get('format') != 'demo':
        return jsonify({"detail": "No file part"}), 400

    file = request.files.get('file')
    category = request.form.get('category')
    format = request.form.get('format')

    provider = None
    if format == "demo":
        provider = DemoProvider()
        source = file.filename if file else "habitations.geojson"
    elif format == "csv":
        provider = CSVProvider()
        source = file.read().decode("utf-8")
    elif format == "geojson":
        provider = GeoJSONProvider()
        source = file.read().decode("utf-8")
    elif format in ["shapefile", "raster"]:
        return jsonify({"detail": f"{format.capitalize()} format not implemented yet."}), 501
    else:
        return jsonify({"detail": "Unsupported format"}), 400

    try:
        raw_data = provider.read_data(source)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400

    required_fields = []
    if category == "habitations":
        required_fields = ["name", "population"]
    elif category == "hazards":
        required_fields = ["type", "severity"]

    validator = DataValidator(required_fields)
    valid_data, invalid_data = validator.validate(raw_data)

    cleaner = DataCleaner()
    cleaned_data = cleaner.clean(valid_data)

    confidence_svc = ConfidenceService()
    final_data = confidence_svc.assign_confidence(cleaned_data, format, category)

    projected_crs = determine_crs_from_centroid(final_data)

    # Save cleaned data into the canonical database
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
                    "dataset_type": "UPLOADED",
                    "confidence": record.get('confidence', 'MODERATE'),
                })
                saved_count += 1
        elif category == "hazards":
            for idx, record in enumerate(final_data):
                haz_id = record.get('id', f"HAZ-U{idx+1:03d}")
                Repository.upsert_hazard(session, {
                    "id": haz_id,
                    "type": record.get('type', 'Unknown'),
                    "severity": record.get('severity', 'Moderate'),
                    "geom_geojson": record.get('geom_geojson'),
                    "dataset_type": "UPLOADED",
                })
                saved_count += 1

        # Log the dataset
        Repository.save_dataset(session, {
            "name": source if isinstance(source, str) and len(source) < 100 else f"{category}_{format}",
            "category": category,
            "format": format,
            "record_count": len(raw_data),
            "valid_count": len(valid_data),
            "invalid_count": len(invalid_data),
            "confidence": final_data[0].get('confidence', 'UNKNOWN') if final_data else 'UNKNOWN',
            "projected_crs": projected_crs,
        })

        Repository.log_action(session, "upload", entity_type=category,
                              details=json.dumps({"format": format, "records": len(final_data)}))
        session.commit()
    finally:
        session.close()

    return jsonify({
        "status": "success",
        "category": category,
        "format": format,
        "projected_crs": projected_crs,
        "total_records": len(raw_data),
        "valid_records_count": len(valid_data),
        "invalid_records_count": len(invalid_data),
        "saved_to_db": saved_count,
        "errors": invalid_data[:10],
    })
