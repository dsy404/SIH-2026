"""
CSVProvider for Phase 5 Real Data Ingestion.

Supports:
- Parsing CSV string or file content
- Schema inspection & header extraction
- Previewing sample rows
- Intelligent auto-mapping suggestions
"""
from __future__ import annotations
from typing import List, Dict, Any
from .base import DataProvider
import csv
import io

# Common synonyms for auto-mapping
CANONICAL_MAPPING_SYNONYMS = {
    "name": ["name", "village_name", "habitation_name", "village", "hab_name", "site_name", "settlement"],
    "latitude": ["latitude", "lat", "latitude_deg", "y", "lat_deg", "northing"],
    "longitude": ["longitude", "lon", "lng", "long", "longitude_deg", "x", "lon_deg", "easting"],
    "population": ["population", "pop", "pop_total", "total_population", "population_total", "residents"],
    "households": ["households", "hh", "hh_count", "total_households", "houses"],
    "elevation": ["elevation", "elev", "alt", "altitude", "height_m"],
    "slope": ["slope", "slope_deg", "gradient"],
    "type": ["type", "hazard_type", "hazard", "disaster_type"],
    "severity": ["severity", "hazard_severity", "risk_level", "level", "impact_severity"],
}


class CSVProvider(DataProvider):
    def read_data(self, source: str) -> List[Dict[str, Any]]:
        """Parses full CSV content into a list of dicts."""
        if not source or not source.strip():
            return []
        try:
            f = io.StringIO(source.strip())
            reader = csv.DictReader(f)
            return [dict(row) for row in reader]
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {str(e)}")

    def inspect_data(self, source: str, category: str = "habitations") -> Dict[str, Any]:
        """Inspects CSV headers, returns preview rows, and generates mapping suggestions."""
        if not source or not source.strip():
            raise ValueError("Empty CSV file: File contains no data.")

        f = io.StringIO(source.strip())
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        if not headers:
            raise ValueError("CSV header row missing or empty.")

        rows = []
        for idx, row in enumerate(reader):
            rows.append(dict(row))

        sample_rows = rows[:10]
        suggested_mapping = {}

        # Auto-match headers to canonical names
        for col in headers:
            col_clean = col.strip().lower().replace(' ', '_')
            for canon_key, synonyms in CANONICAL_MAPPING_SYNONYMS.items():
                if col_clean in synonyms or any(syn in col_clean for syn in synonyms):
                    if canon_key not in suggested_mapping.values():
                        suggested_mapping[col] = canon_key
                        break

        # Detect CRS: CSV lat/lon is standard WGS84
        crs = "EPSG:4326"

        return {
            "format": "csv",
            "category": category,
            "total_records": len(rows),
            "headers": headers,
            "sample_rows": sample_rows,
            "suggested_mapping": suggested_mapping,
            "detected_crs": crs,
            "geometry_type": "Point",
        }

    def get_supported_format(self) -> str:
        return "csv"
