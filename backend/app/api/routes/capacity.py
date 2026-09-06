"""
Capacity API — reads site capacity dimensions from DB.
"""
from flask import Blueprint, request, jsonify
from app.db.database import get_session_factory
from app.db.repository import Repository

capacity_bp = Blueprint('capacity', __name__)


@capacity_bp.route("/analyze", methods=["GET"])
def analyze_capacity():
    """
    Analyzes the carrying capacity of a candidate site for a given incoming population.
    Reads capacity data from the canonical database.
    """
    site_id = request.args.get('site_id')
    incoming_population = request.args.get('incoming_population', type=int)

    if not site_id or incoming_population is None:
        return jsonify({"error": "site_id and incoming_population are required"}), 400

    Session = get_session_factory()
    session = Session()
    try:
        site = Repository.get_site(session, site_id)
        if not site:
            return jsonify({"error": f"Site {site_id} not found"}), 404

        caps = Repository.get_site_capacity(session, site_id)
        if not caps:
            return jsonify({"error": f"No capacity data for site {site_id}"}), 404

        dimensions_analysis = []
        bottleneck = None
        min_surplus_ratio = float('inf')

        for cap in caps:
            available = cap.max_capacity - cap.current_utilization
            post_surplus = available - incoming_population
            surplus_ratio = post_surplus / (incoming_population if incoming_population > 0 else 1)

            dim_data = {
                "dimension": cap.dimension,
                "max_capacity": cap.max_capacity,
                "current_utilization": cap.current_utilization,
                "available_capacity": available,
                "required_capacity": incoming_population,
                "post_relocation_surplus": post_surplus,
                "status": "Critical" if post_surplus < 0 else ("Warning" if post_surplus < 500 else "Safe"),
            }
            dimensions_analysis.append(dim_data)

            if surplus_ratio < min_surplus_ratio:
                min_surplus_ratio = surplus_ratio
                bottleneck = dim_data

        feasible = min(d["available_capacity"] for d in dimensions_analysis)

        return jsonify({
            "site_id": site_id,
            "site_name": site.name,
            "incoming_population": incoming_population,
            "dimensions": dimensions_analysis,
            "bottleneck": bottleneck,
            "feasible_additional_capacity": feasible,
            "is_feasible": feasible >= incoming_population,
        })
    finally:
        session.close()
