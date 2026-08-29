from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
import json

from ..data_ingestion.demo_provider import DemoProvider
from ..data_ingestion.csv_provider import CSVProvider
from ..data_ingestion.geojson_provider import GeoJSONProvider
from ..data_ingestion.validator import DataValidator

router = APIRouter(prefix="/datasets", tags=["datasets"])

@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...), 
    category: str = Form(...),
    format: str = Form(...)
):
    provider = None
    if format == "demo":
        provider = DemoProvider()
        source = file.filename # Using filename as identifier for demo provider
        
    elif format == "csv":
        provider = CSVProvider()
        source = (await file.read()).decode("utf-8")
        
    elif format == "geojson":
        provider = GeoJSONProvider()
        source = (await file.read()).decode("utf-8")
        
    elif format in ["shapefile", "raster"]:
        raise HTTPException(status_code=501, detail=f"{format.capitalize()} format not implemented yet.")
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")

    try:
        raw_data = provider.read_data(source)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Basic required fields based on category
    required_fields = []
    if category == "habitations":
        required_fields = ["name", "population"]
    elif category == "hazards":
        required_fields = ["type", "severity"]

    # Validate
    validator = DataValidator(required_fields)
    valid_data, invalid_data = validator.validate(raw_data)

    # Clean and Standardize valid data
    from ..data_ingestion.cleaner import DataCleaner
    from ..data_ingestion.confidence_service import ConfidenceService
    from ..geospatial.crs import determine_crs_from_centroid
    
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean(valid_data)
    
    confidence_svc = ConfidenceService()
    final_data = confidence_svc.assign_confidence(cleaned_data, format, category)
    
    projected_crs = determine_crs_from_centroid(final_data)

    return {
        "status": "success",
        "category": category,
        "format": format,
        "projected_crs": projected_crs,
        "total_records": len(raw_data),
        "valid_records_count": len(valid_data),
        "invalid_records_count": len(invalid_data),
        "errors": invalid_data[:10] # Return top 10 errors for preview
    }
