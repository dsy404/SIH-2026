from typing import List, Dict, Any
from .base import DataProvider
import json

class GeoJSONProvider(DataProvider):
    def read_data(self, source: str) -> List[Dict[str, Any]]:
        # Source would be file content or file path
        try:
            data = json.loads(source)
            features = data.get('features', [])
            parsed_data = []
            for feature in features:
                props = feature.get('properties', {})
                geom = feature.get('geometry', {})
                props['geom_geojson'] = json.dumps(geom)
                parsed_data.append(props)
            return parsed_data
        except Exception as e:
            raise ValueError(f"Failed to parse GeoJSON: {str(e)}")

    def get_supported_format(self) -> str:
        return "geojson"
