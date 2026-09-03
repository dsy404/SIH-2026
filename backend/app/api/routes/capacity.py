from flask import Blueprint, request, jsonify
from app.engines.relocation.carrying_capacity import CapacityCalculator

capacity_bp = Blueprint('capacity', __name__)

@capacity_bp.route("/analyze", methods=["GET"])
def analyze_capacity():
    """
    Analyzes the carrying capacity of a candidate site for a given incoming population.
    """
    site_id = request.args.get('site_id')
    incoming_population = request.args.get('incoming_population', type=int)
    
    if not site_id or incoming_population is None:
        return jsonify({"error": "site_id and incoming_population are required"}), 400
        
    analysis = CapacityCalculator.analyze_capacity(site_id, incoming_population)
    
    return jsonify(analysis)
