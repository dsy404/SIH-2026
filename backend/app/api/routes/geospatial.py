from flask import Blueprint, request, jsonify
from app.geospatial.distance import haversine_distance, euclidean_distance
from app.geospatial.bounding_box import calculate_bounding_box
from app.geospatial.clustering import find_clusters

geospatial_bp = Blueprint('geospatial', __name__)

@geospatial_bp.route("/distance", methods=["POST"])
def get_distance():
    coords = request.json
    dist = haversine_distance((coords['lon1'], coords['lat1']), (coords['lon2'], coords['lat2']))
    return jsonify({"distance_km": dist})

@geospatial_bp.route("/bounding_box", methods=["POST"])
def get_bounding_box():
    dataset = request.json
    bbox = calculate_bounding_box(dataset.get('data', []))
    return jsonify({"bounding_box": {"min_lon": bbox[0], "min_lat": bbox[1], "max_lon": bbox[2], "max_lat": bbox[3]}})

@geospatial_bp.route("/cluster", methods=["POST"])
def apply_clustering():
    dataset = request.json
    clustered_data = find_clusters(dataset.get('data', []), epsilon_km=2.0, min_samples=2)
    return jsonify({"clustered_data": clustered_data})
