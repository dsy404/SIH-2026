"""
GeoJSONProvider for Phase 5 Real Data Ingestion.

Supports:
- Parsing GeoJSON FeatureCollection
- Extracting properties and coordinate geometry
- Schema inspection & property extraction
- Point & Polygon geometry detection
"""
from __future__ import annotations
from typing import List, Dict, Any
from .base import DataProvider
import json
from .csv_provider import CANONICAL_MAPPING_SYNONYMS


class GeoJSONProvider(DataProvider):
    def read_data(self, source: str) -> List[Dict[str, Any]]:
        """Parses GeoJSON string into a list of normalized property dicts."""
        if not source or not source.strip():
            return []
        try:
            data = json.loads(source.strip())
            features = data.get('features', [])
            parsed_data = []

            for feature in features:
                props = dict(feature.get('properties', {}))
                geom = feature.get('geometry', {})
                geom_type = geom.get('type')
                coords = geom.get('coordinates', [])

                props['geom_geojson'] = json.dumps(geom) if geom else None

                # If Point geometry, extract coordinates into properties if missing
                if geom_type == "Point" and len(coords) >= 2:
                    if 'longitude' not in props or not props['longitude']:
                        props['longitude'] = coords[0]
                    if 'latitude' not in props or not props['latitude']:
                        props['latitude'] = coords[1]

                parsed_data.append(props)

            return parsed_data
        except Exception as e:
            raise ValueError(f"Failed to parse GeoJSON: {str(e)}")

    def inspect_data(self, source: str, category: str = "habitations") -> Dict[str, Any]:
        """Inspects GeoJSON features, returns headers, sample records, and geometry info."""
        if not source or not source.strip():
            raise ValueError("Empty GeoJSON file: File contains no data.")

        try:
            data = json.loads(source.strip())
        except Exception as e:
            raise ValueError(f"Invalid JSON/GeoJSON syntax: {str(e)}")

        features = data.get('features', [])
        if not features and data.get('type') != 'FeatureCollection':
            raise ValueError("Invalid GeoJSON: Expected a 'FeatureCollection' with features array.")

        geom_types = set()
        headers = set()
        parsed_records = []

        for feature in features:
            props = dict(feature.get('properties', {}))
            geom = feature.get('geometry', {})
            geom_type = geom.get('type', 'Unknown')
            geom_types.add(geom_type)

            coords = geom.get('coordinates', [])
            props['geom_geojson'] = json.dumps(geom) if geom else None

            if geom_type == "Point" and len(coords) >= 2:
                if 'longitude' not in props or not props['longitude']:
                    props['longitude'] = coords[0]
                if 'latitude' not in props or not props['latitude']:
                    props['latitude'] = coords[1]

            headers.update(props.keys())
            parsed_records.append(props)

        # Remove internal geometry key from header list
        header_list = [h for h in headers if h != 'geom_geojson']

        # Determine CRS from GeoJSON spec (RFC 7946 specifies WGS84 / EPSG:4326)
        crs = "EPSG:4326"
        crs_prop = data.get('crs', {}).get('properties', {}).get('name')
        if crs_prop:
            crs = crs_prop

        # Suggested mapping
        suggested_mapping = {}
        for col in header_list:
            col_clean = col.strip().lower().replace(' ', '_')
            for canon_key, synonyms in CANONICAL_MAPPING_SYNONYMS.items():
                if col_clean in synonyms or any(syn in col_clean for syn in synonyms):
                    if canon_key not in suggested_mapping.values():
                        suggested_mapping[col] = canon_key
                        break

        geometry_type_str = ", ".join(geom_types) if geom_types else "Unknown"

        return {
            "format": "geojson",
            "category": category,
            "total_records": len(features),
            "headers": header_list,
            "sample_rows": parsed_records[:10],
            "suggested_mapping": suggested_mapping,
            "detected_crs": crs,
            "geometry_type": geometry_type_str,
        }

    def get_supported_format(self) -> str:
        return "geojson"
