from fastapi import APIRouter
from typing import List, Dict, Any
from ..geospatial.distance import haversine_distance, euclidean_distance
from ..geospatial.bounding_box import calculate_bounding_box
from ..geospatial.clustering import find_clusters
from pydantic import BaseModel

router = APIRouter(prefix="/geospatial", tags=["geospatial"])

class Coordinates(BaseModel):
    lon1: float
    lat1: float
    lon2: float
    lat2: float

@router.post("/distance")
def get_distance(coords: Coordinates):
    """Calculate Haversine distance between two points."""
    dist = haversine_distance((coords.lon1, coords.lat1), (coords.lon2, coords.lat2))
    return {"distance_km": dist}

class GeoDataset(BaseModel):
    data: List[Dict[str, Any]]

@router.post("/bounding_box")
def get_bounding_box(dataset: GeoDataset):
    """Calculate the bounding box of a dataset."""
    bbox = calculate_bounding_box(dataset.data)
    return {"bounding_box": {"min_lon": bbox[0], "min_lat": bbox[1], "max_lon": bbox[2], "max_lat": bbox[3]}}

@router.post("/cluster")
def apply_clustering(dataset: GeoDataset):
    """Group habitations into spatial clusters."""
    clustered_data = find_clusters(dataset.data, epsilon_km=2.0, min_samples=2)
    return {"clustered_data": clustered_data}
