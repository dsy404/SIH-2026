"""
Enhanced DataValidator for Phase 5 Real Data Ingestion.

Validates:
- Empty datasets
- Missing required fields
- Missing coordinates
- Impossible latitude/longitude bounds ([-90, 90], [-180, 180])
- Non-numeric or negative numbers
- Invalid GeoJSON geometries
- Unsupported geometries
- Duplicate records
- Counts missing values
"""
from __future__ import annotations
from typing import List, Dict, Any, Tuple, Set
import json
from shapely.geometry import shape


class DataValidator:
    def __init__(self, required_fields: List[str] = None):
        self.required_fields = required_fields or []

    def validate(self, data: List[Dict[str, Any]], category: str = "habitations", crs: str = "EPSG:4326") -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Validates the dataset.
        Returns a tuple: (valid_records, invalid_records)
        invalid_records will have an '__errors__' list attached.
        """
        result = self.validate_detailed(data, category, crs)
        return result["valid_records"], result["invalid_records"]

    def validate_detailed(self, data: List[Dict[str, Any]], category: str = "habitations", crs: str = "EPSG:4326") -> Dict[str, Any]:
        valid: List[Dict[str, Any]] = []
        invalid: List[Dict[str, Any]] = []
        all_errors: List[Dict[str, Any]] = []
        missing_values_count = 0

        # 1. Empty Dataset Check
        if not data:
            error_msg = "Dataset is empty: 0 records found in file."
            return {
                "valid_records": [],
                "invalid_records": [],
                "valid_count": 0,
                "invalid_count": 0,
                "missing_values_count": 0,
                "errors": [{"row": 0, "field": "file", "message": error_msg}],
                "can_import": False,
            }

        # 2. CRS Check
        if crs and crs.upper() not in ["EPSG:4326", "WGS84", "CRS84"] and not crs.startswith("EPSG:32"):
            all_errors.append({
                "row": 0,
                "field": "crs",
                "message": f"Unknown or unprojected CRS '{crs}'. Coordinates will be standardized to WGS84 (EPSG:4326)."
            })

        seen_keys: Set[str] = set()

        for idx, record in enumerate(data):
            row_num = idx + 1
            row_errors: List[str] = []

            # Count missing values across fields
            for k, v in record.items():
                if v is None or v == "":
                    missing_values_count += 1

            # A. Check required fields
            for field in self.required_fields:
                val = record.get(field)
                if val is None or val == "":
                    row_errors.append(f"Missing required field: '{field}'")

            # B. Coordinate validation (for habitations, candidate sites, or points)
            has_lat = 'latitude' in record and record['latitude'] is not None and record['latitude'] != ''
            has_lon = 'longitude' in record and record['longitude'] is not None and record['longitude'] != ''

            if category in ["habitations", "candidate_sites"]:
                if not has_lat or not has_lon:
                    row_errors.append("Missing required geographic coordinates (latitude and longitude).")
                else:
                    try:
                        lat = float(record['latitude'])
                        lon = float(record['longitude'])

                        if not (-90.0 <= lat <= 90.0):
                            row_errors.append(f"Impossible latitude '{lat}' (must be between -90 and 90).")
                        if not (-180.0 <= lon <= 180.0):
                            row_errors.append(f"Impossible longitude '{lon}' (must be between -180 and 180).")

                        # Null island check
                        if abs(lat) < 0.0001 and abs(lon) < 0.0001:
                            row_errors.append("Coordinates point to (0,0) [Null Island]. Expected valid regional coordinates.")

                    except (ValueError, TypeError):
                        row_errors.append(f"Invalid non-numeric coordinates: lat='{record.get('latitude')}', lon='{record.get('longitude')}'.")

            elif category == "hazards":
                # Hazards must have valid geometry
                geom_raw = record.get('geom_geojson')
                if not geom_raw and not (has_lat and has_lon):
                    row_errors.append("Hazard record is missing polygon or point geometry.")
                elif geom_raw:
                    try:
                        geom_dict = json.loads(geom_raw) if isinstance(geom_raw, str) else geom_raw
                        s = shape(geom_dict)
                        if not s.is_valid:
                            row_errors.append(f"Invalid geometry structure in hazard boundary.")
                        if s.geom_type not in ["Polygon", "MultiPolygon", "Point", "LineString"]:
                            row_errors.append(f"Unsupported geometry type '{s.geom_type}'.")
                    except Exception as e:
                        row_errors.append(f"Corrupt geometry JSON: {str(e)}")

            # C. Numeric values validation
            if 'population' in record and record['population'] is not None and record['population'] != '':
                try:
                    pop_val = float(str(record['population']).replace(',', ''))
                    if pop_val < 0:
                        row_errors.append(f"Population cannot be negative: '{pop_val}'.")
                except (ValueError, TypeError):
                    row_errors.append(f"Invalid non-numeric population value: '{record['population']}'.")

            if 'households' in record and record['households'] is not None and record['households'] != '':
                try:
                    hh_val = float(str(record['households']).replace(',', ''))
                    if hh_val < 0:
                        row_errors.append(f"Households cannot be negative: '{hh_val}'.")
                except (ValueError, TypeError):
                    row_errors.append(f"Invalid non-numeric households value: '{record['households']}'.")

            # D. Duplicate detection
            dedup_key = ""
            if category == "habitations":
                name_val = str(record.get('name', '')).strip().lower()
                lat_str = str(record.get('latitude', '')).strip()
                lon_str = str(record.get('longitude', '')).strip()
                dedup_key = f"{name_val}_{lat_str}_{lon_str}"
            elif category == "hazards":
                dedup_key = f"{record.get('id', '')}_{record.get('type', '')}"

            if dedup_key and dedup_key in seen_keys:
                row_errors.append(f"Duplicate record detected with identical signature: '{dedup_key}'.")
            elif dedup_key:
                seen_keys.add(dedup_key)

            # Record classification
            if row_errors:
                record_copy = dict(record)
                record_copy['__errors__'] = row_errors
                record_copy['__row_num__'] = row_num
                invalid.append(record_copy)
                for err in row_errors:
                    all_errors.append({"row": row_num, "field": "record", "message": err})
            else:
                valid.append(record)

        return {
            "valid_records": valid,
            "invalid_records": invalid,
            "valid_count": len(valid),
            "invalid_count": len(invalid),
            "missing_values_count": missing_values_count,
            "errors": all_errors,
            "can_import": len(valid) > 0,
        }
