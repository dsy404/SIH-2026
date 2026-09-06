"""
Safe Sites API — Dynamic multi-criteria suitability & safety evaluation.
"""
from flask import Blueprint, request, jsonify
from app.db.database import get_session_factory
from app.db.repository import Repository
from app.engines.relocation.safe_site import SiteScorer

safe_sites_bp = Blueprint('safe_sites', __name__)


@safe_sites_bp.route("", methods=["GET"])
@safe_sites_bp.route("/", methods=["GET"])
def list_safe_sites():
    """Returns all candidate sites with dynamic suitability scores."""
    Session = get_session_factory()
    session = Session()
    try:
        sites = Repository.get_all_sites(session)
        site_dicts = [Repository.site_to_dict(s) for s in sites]
        evaluated = [SiteScorer.calculate_score(s) for s in site_dicts]
        return jsonify(evaluated)
    finally:
        session.close()


@safe_sites_bp.route("/compare", methods=["GET"])
def compare_safe_sites():
    """
    Returns candidate safe sites dynamically scored and ranked based on multi-criteria factors.
    Unsafe / disqualified sites are partitioned and excluded from ranking.
    Dynamically computes proximity to source habitation if habitation_id is provided.
    """
    habitation_id = request.args.get('habitation_id')
    output_format = request.args.get('format', 'detailed')

    Session = get_session_factory()
    session = Session()
    try:
        sites = Repository.get_all_sites(session)
        site_dicts = [Repository.site_to_dict(s) for s in sites]

        origin_coords = None
        hab_info = None
        if habitation_id:
            hab = Repository.get_habitation(session, habitation_id)
            if hab:
                origin_coords = {"latitude": hab.latitude, "longitude": hab.longitude}
                hab_info = {
                    "id": hab.id,
                    "name": hab.name,
                    "latitude": hab.latitude,
                    "longitude": hab.longitude,
                    "population": hab.population,
                }

        # Run detailed multi-criteria evaluation with safety pre-ranking filter
        detailed = SiteScorer.compare_sites_detailed(site_dicts, origin_coords=origin_coords)

        if output_format == "list":
            return jsonify(detailed["ranked_safe_sites"])

        return jsonify({
            "source_habitation": hab_info,
            "ranked_safe_sites": detailed["ranked_safe_sites"],
            "disqualified_sites": detailed["disqualified_sites"],
            "total_evaluated": detailed["total_evaluated"],
            "safe_count": detailed["safe_count"],
            "disqualified_count": detailed["disqualified_count"],
            # Convenience alias
            "sites": detailed["ranked_safe_sites"],
        })
    finally:
        session.close()
