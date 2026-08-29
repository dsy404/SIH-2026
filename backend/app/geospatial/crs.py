import math

def calculate_utm_zone(longitude: float) -> int:
    """
    Calculates the UTM zone for a given longitude.
    Formula: Zone = floor((longitude + 180) / 6) + 1
    """
    return math.floor((longitude + 180) / 6) + 1

def determine_crs_from_centroid(data: list) -> str:
    """
    Determines the appropriate UTM EPSG code based on the data centroid.
    """
    if not data:
        return "EPSG:4326" # Default WGS84
        
    avg_lon = 0
    avg_lat = 0
    count = 0
    
    for record in data:
        if 'longitude' in record and 'latitude' in record:
            avg_lon += float(record['longitude'])
            avg_lat += float(record['latitude'])
            count += 1
            
    if count == 0:
        return "EPSG:4326"
        
    avg_lon /= count
    avg_lat /= count
    
    zone = calculate_utm_zone(avg_lon)
    
    # Northern hemisphere EPSG codes are 326xx, Southern are 327xx
    epsg_base = 32600 if avg_lat >= 0 else 32700
    return f"EPSG:{epsg_base + zone}"
