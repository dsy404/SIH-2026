from typing import List, Dict, Any, Tuple

def calculate_bounding_box(data: List[Dict[str, Any]]) -> Tuple[float, float, float, float]:
    """
    Calculates the bounding box for a dataset.
    Returns (min_lon, min_lat, max_lon, max_lat)
    """
    if not data:
        return (0.0, 0.0, 0.0, 0.0)
        
    min_lon = float('inf')
    min_lat = float('inf')
    max_lon = float('-inf')
    max_lat = float('-inf')
    
    for record in data:
        if 'longitude' in record and 'latitude' in record:
            lon = float(record['longitude'])
            lat = float(record['latitude'])
            min_lon = min(min_lon, lon)
            min_lat = min(min_lat, lat)
            max_lon = max(max_lon, lon)
            max_lat = max(max_lat, lat)
            
    return (min_lon, min_lat, max_lon, max_lat)
