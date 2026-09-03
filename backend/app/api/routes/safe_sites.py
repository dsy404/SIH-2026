from flask import Blueprint, request, jsonify
from app.engines.relocation.safe_site import SiteScorer

safe_sites_bp = Blueprint('safe_sites', __name__)

@safe_sites_bp.route("/compare", methods=["GET"])
def compare_safe_sites():
    """
    Returns candidate safe sites for a given habitation, scored and ranked based on 13 safety/suitability factors.
    """
    habitation_id = request.args.get('habitation_id')
    if not habitation_id:
        return jsonify({"error": "Habitation ID is required"}), 400
        
    # In a real scenario, this would query a GIS DB for candidate sites within a radius of the habitation
    # For now, we use the mock generator
    raw_sites = SiteScorer.get_mock_candidates(habitation_id)
    
    # Score and rank them
    ranked_sites = SiteScorer.compare_sites(raw_sites)
    
    return jsonify(ranked_sites)
