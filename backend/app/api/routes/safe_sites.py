"""
Safe Sites API — reads candidate sites from DB.
"""
from flask import Blueprint, request, jsonify
from app.db.database import get_session_factory
from app.db.repository import Repository
from app.engines.relocation.safe_site import SiteScorer

safe_sites_bp = Blueprint('safe_sites', __name__)


@safe_sites_bp.route("/compare", methods=["GET"])
def compare_safe_sites():
    """
    Returns candidate safe sites scored and ranked based on 13 safety/suitability factors.
    Reads site data from the canonical database.
    """
    habitation_id = request.args.get('habitation_id')
    if not habitation_id:
        return jsonify({"error": "Habitation ID is required"}), 400

    Session = get_session_factory()
    session = Session()
    try:
        sites = Repository.get_all_sites(session)
        site_dicts = [Repository.site_to_dict(s) for s in sites]

        # Score and rank
        ranked_sites = SiteScorer.compare_sites(site_dicts)
        return jsonify(ranked_sites)
    finally:
        session.close()
