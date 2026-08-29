from typing import List, Dict, Any
import json
import os
from .base import DataProvider

class DemoProvider(DataProvider):
    def read_data(self, source: str) -> List[Dict[str, Any]]:
        # For the demo, source is just the filename in the synthetic data dir
        # In a real app, source might be an ID or an S3 key
        base_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'synthetic')
        file_path = os.path.join(base_dir, source)
        
        if not os.path.exists(file_path):
            return []
            
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        # Parse GeoJSON into standard dictionary format
        features = data.get('features', [])
        parsed_data = []
        for feature in features:
            props = feature.get('properties', {})
            geom = feature.get('geometry', {})
            props['geom_geojson'] = json.dumps(geom)
            
            # Extract coordinates for convenience if it's a Point
            if geom.get('type') == 'Point':
                coords = geom.get('coordinates', [0, 0])
                props['longitude'] = coords[0]
                props['latitude'] = coords[1]
                
            parsed_data.append(props)
            
        return parsed_data

    def get_supported_format(self) -> str:
        return "demo"
