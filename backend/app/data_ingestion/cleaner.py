"""
DataCleaner for Phase 5 Real Data Ingestion.

Cleans and standardizes:
- Trims whitespace
- Title Case for names
- Converts comma-separated number strings ("1,250" -> 1250)
- Normalizes hazard types and severity strings
- Builds canonical Point GeoJSON when latitude/longitude are present
"""
from __future__ import annotations
from typing import List, Dict, Any
import json


class DataCleaner:
    def clean(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned_data = []
        for record in data:
            cleaned_record = dict(record)

            # 1. Whitespace stripping & string normalization
            for key, value in list(cleaned_record.items()):
                if isinstance(value, str):
                    cleaned_val = value.strip()
                    if key.lower() in ["name", "village_name", "habitation_name", "site_name"]:
                        cleaned_val = cleaned_val.title()
                    elif key.lower() == "severity":
                        cleaned_val = cleaned_val.capitalize()
                    elif key.lower() == "type":
                        cleaned_val = cleaned_val.title()
                    cleaned_record[key] = cleaned_val

            # 2. Number parsing
            numeric_int_fields = ["population", "households", "record_count"]
            for field in numeric_int_fields:
                if field in cleaned_record and cleaned_record[field] is not None:
                    try:
                        str_val = str(cleaned_record[field]).replace(',', '').strip()
                        if str_val != '':
                            cleaned_record[field] = int(round(float(str_val)))
                    except (ValueError, TypeError):
                        pass

            numeric_float_fields = ["latitude", "longitude", "elevation", "slope", "aspect", "infrastructure_score"]
            for field in numeric_float_fields:
                if field in cleaned_record and cleaned_record[field] is not None:
                    try:
                        str_val = str(cleaned_record[field]).replace(',', '').strip()
                        if str_val != '':
                            cleaned_record[field] = round(float(str_val), 6)
                    except (ValueError, TypeError):
                        pass

            # 3. Canonical Geometry Construction for points
            if 'latitude' in cleaned_record and 'longitude' in cleaned_record:
                try:
                    lat = float(cleaned_record['latitude'])
                    lon = float(cleaned_record['longitude'])
                    if not cleaned_record.get('geom_geojson'):
                        cleaned_record['geom_geojson'] = json.dumps({
                            "type": "Point",
                            "coordinates": [lon, lat]
                        })
                except (ValueError, TypeError):
                    pass

            cleaned_data.append(cleaned_record)

        return cleaned_data
