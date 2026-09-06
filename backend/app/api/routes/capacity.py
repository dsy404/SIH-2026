"""
Capacity API — 8-Dimensional Carrying Capacity & Bottleneck Analysis.
"""
from flask import Blueprint, request, jsonify
from app.engines.relocation.carrying_capacity import CapacityCalculator

capacity_bp = Blueprint('capacity', __name__)


@capacity_bp.route("/analyze", methods=["GET"])
def analyze_capacity():
    """
    Analyzes carrying capacity across 8 dimensions converted into people-supported units.
    Identifies dynamic binding bottlenecks and returns planning disclaimer.
    """
    site_id = request.args.get('site_id')
    incoming_population = request.args.get('incoming_population', 0, type=int)

    if not site_id:
        return jsonify({"error": "site_id is required"}), 400

    try:
        analysis = CapacityCalculator.analyze_capacity(site_id, incoming_population)
        if not analysis.get("dimensions"):
            return jsonify({"error": f"No capacity records found for site {site_id}"}), 404
        return jsonify(analysis)
    except Exception as e:
        return jsonify({"error": f"Failed to analyze capacity: {str(e)}"}), 500
