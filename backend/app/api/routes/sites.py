"""
Candidate Sites API Routes — canonical CRUD + GeoJSON export.
"""
from flask import Blueprint, jsonify
from app.db.database import get_session_factory
from app.db.repository import Repository

sites_bp = Blueprint('sites', __name__)


@sites_bp.route("/", methods=["GET"])
def list_sites():
    """List all candidate sites."""
    Session = get_session_factory()
    session = Session()
    try:
        sites = Repository.get_all_sites(session)
        return jsonify([Repository.site_to_dict(s) for s in sites])
    finally:
        session.close()


@sites_bp.route("/geojson", methods=["GET"])
def sites_geojson():
    """Return all sites as a GeoJSON FeatureCollection (for map)."""
    Session = get_session_factory()
    session = Session()
    try:
        sites = Repository.get_all_sites(session)
        features = [Repository.site_to_geojson_feature(s) for s in sites]
        return jsonify({"type": "FeatureCollection", "features": features})
    finally:
        session.close()

@sites_bp.route("/<site_id>", methods=["GET"])
def get_site(site_id: str):
    """Get a single candidate site with capacity data."""
    Session = get_session_factory()
    session = Session()
    try:
        site = Repository.get_site(session, site_id)
        if not site:
            return jsonify({"error": f"Site {site_id} not found"}), 404

        d = Repository.site_to_dict(site)
        caps = Repository.get_site_capacity(session, site_id)
        d["capacity_dimensions"] = [
            {
                "dimension": c.dimension,
                "max_capacity": c.max_capacity,
                "current_utilization": c.current_utilization,
                "available_capacity": c.max_capacity - c.current_utilization,
            }
            for c in caps
        ]
        return jsonify(d)
    finally:
        session.close()
