"""
Tracking API — reads assignments and post-relocation data from DB.
"""
from flask import Blueprint, jsonify, request
from app.db.database import get_session_factory
from app.db.repository import Repository

tracking_bp = Blueprint('tracking', __name__)


@tracking_bp.route('/post-relocation', methods=['POST', 'GET'])
def get_post_relocation_status():
    """
    Returns post-relocation tracking data from the canonical database.
    """
    Session = get_session_factory()
    session = Session()
    try:
        records = Repository.get_post_relocation_records(session)

        if not records:
            return jsonify({"summary": {"stable": 0, "needs_attention": 0, "at_risk": 0}, "tracking_details": []})

        import json
        summary = {"stable": 0, "needs_attention": 0, "at_risk": 0}
        details = []

        for rec in records:
            hab = Repository.get_habitation(session, rec.habitation_id)
            site = Repository.get_site(session, rec.site_id)

            missing = json.loads(rec.missing_infrastructure) if rec.missing_infrastructure else []

            if rec.status == "Stable":
                summary["stable"] += rec.households_relocated
            elif rec.status == "Needs Attention":
                summary["needs_attention"] += rec.households_relocated
            else:
                summary["at_risk"] += rec.households_relocated

            details.append({
                "habitation_id": rec.habitation_id,
                "habitation_name": hab.name if hab else "Unknown",
                "households": rec.households_relocated,
                "assigned_site": site.name if site else "Unknown",
                "status": rec.status,
                "missing_infrastructure": missing,
            })

        return jsonify({"summary": summary, "tracking_details": details})
    finally:
        session.close()
