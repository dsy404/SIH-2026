from flask import Blueprint, request, jsonify
import json
from app.data_ingestion.demo_provider import DemoProvider
from app.data_ingestion.csv_provider import CSVProvider
from app.data_ingestion.geojson_provider import GeoJSONProvider
from app.data_ingestion.validator import DataValidator
from app.data_ingestion.cleaner import DataCleaner
from app.data_ingestion.confidence_service import ConfidenceService
from app.geospatial.crs import determine_crs_from_centroid

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

    return jsonify({
        "status": "success",
        "category": category,
        "format": format,
        "projected_crs": projected_crs,
        "total_records": len(raw_data),
        "valid_records_count": len(valid_data),
        "invalid_records_count": len(invalid_data),
        "errors": invalid_data[:10]
    })
