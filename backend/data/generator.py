import json
import random
import os
import math

BASE_LAT = 25.0
BASE_LON = 82.0

def generate_random_point(base_lat, base_lon, radius_km=10.0):
    # Rough approximation: 1 degree latitude ~= 111 km
    lat_offset = (random.random() * 2 - 1) * (radius_km / 111.0)
    lon_offset = (random.random() * 2 - 1) * (radius_km / (111.0 * math.cos(math.radians(base_lat))))
    return [base_lon + lon_offset, base_lat + lat_offset]

def to_geojson_feature(geom_type, coords, properties):
    return {
        "type": "Feature",
        "geometry": {
            "type": geom_type,
            "coordinates": coords
        },
        "properties": properties
    }

def generate_dataset():
    out_dir = "synthetic"
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Habitations
    habitations = []
    # Force Rampur Kalan to be at a specific spot
    rampur_kalan_coords = [82.02, 25.02]
    habitations.append(to_geojson_feature("Point", rampur_kalan_coords, {
        "id": "H001",
        "name": "Rampur Kalan (DEMONSTRATION)",
        "block": "Block A",
        "population": 1250,
        "households": 250,
        "elevation": 120.5,
        "slope": 15.2,
        "aspect": 180.0,
        "dataset_type": "DEMO / SYNTHETIC DATA"
    }))
    
    for i in range(2, 21):
        coords = generate_random_point(BASE_LAT, BASE_LON, 15.0)
        habitations.append(to_geojson_feature("Point", coords, {
            "id": f"H{i:03d}",
            "name": f"Village {i} (DEMONSTRATION)",
            "block": random.choice(["Block A", "Block B", "Block C"]),
            "population": random.randint(300, 3000),
            "households": random.randint(60, 600),
            "elevation": round(random.uniform(100, 300), 1),
            "slope": round(random.uniform(0, 45), 1),
            "aspect": round(random.uniform(0, 360), 1),
            "dataset_type": "DEMO / SYNTHETIC DATA"
        }))
        
    with open(f"{out_dir}/habitations.geojson", "w") as f:
        json.dump({"type": "FeatureCollection", "features": habitations}, f, indent=2)

    # 2. Candidate Sites
    sites = []
    # Site A: Closer to Rampur Kalan (82.02, 25.02), but lower infra score
    site_a_coords = [82.03, 25.03]
    sites.append(to_geojson_feature("Point", site_a_coords, {
        "id": "S001",
        "name": "Site A",
        "elevation": 150.0,
        "slope": 2.0,
        "aspect": 90.0,
        "infrastructure_score": 45.0, # Lower score
        "dataset_type": "DEMO / SYNTHETIC DATA"
    }))
    
    # Site B: Further, but much better score
    site_b_coords = [82.08, 25.08]
    sites.append(to_geojson_feature("Point", site_b_coords, {
        "id": "S002",
        "name": "Site B",
        "elevation": 160.0,
        "slope": 1.5,
        "aspect": 120.0,
        "infrastructure_score": 85.0, # Higher score
        "dataset_type": "DEMO / SYNTHETIC DATA"
    }))
    
    for i in range(3, 6):
        coords = generate_random_point(BASE_LAT, BASE_LON, 20.0)
        sites.append(to_geojson_feature("Point", coords, {
            "id": f"S{i:03d}",
            "name": f"Site {chr(64+i)}",
            "elevation": round(random.uniform(100, 300), 1),
            "slope": round(random.uniform(0, 20), 1),
            "aspect": round(random.uniform(0, 360), 1),
            "infrastructure_score": round(random.uniform(30, 90), 1),
            "dataset_type": "DEMO / SYNTHETIC DATA"
        }))
        
    with open(f"{out_dir}/candidate_sites.geojson", "w") as f:
        json.dump({"type": "FeatureCollection", "features": sites}, f, indent=2)
        
    # 3. Hazards (Polygons)
    hazards = []
    # Make a polygon that overlaps Rampur Kalan
    hazards.append(to_geojson_feature("Polygon", [[
        [82.00, 25.00], [82.04, 25.00], [82.04, 25.04], [82.00, 25.04], [82.00, 25.00]
    ]], {
        "id": "HZ001",
        "type": "Flood",
        "severity": "High",
        "dataset_type": "DEMO / SYNTHETIC DATA"
    }))
    
    with open(f"{out_dir}/hazards.geojson", "w") as f:
        json.dump({"type": "FeatureCollection", "features": hazards}, f, indent=2)
        
    print(f"Generated synthetic data in {os.path.abspath(out_dir)}")

if __name__ == "__main__":
    generate_dataset()
