"""
Habitation API Routes — canonical CRUD + GeoJSON export.

Every other component (dashboard, optimizer, map, etc.) should reference
habitations by their canonical ID from this endpoint.
"""
from flask import Blueprint, jsonify, request
from app.db.database import get_session_factory
from app.db.repository import Repository

habitations_bp = Blueprint('habitations', __name__)


@habitations_bp.route("/", methods=["GET"])
def list_habitations():
    """List all habitations with optional risk data."""
    Session = get_session_factory()
    session = Session()
    try:
        habs = Repository.get_all_habitations(session)
        result = []
        for hab in habs:
            d = Repository.habitation_to_dict(hab)
            if hab.risk_assessment:
                d["rpi"] = hab.risk_assessment.rpi
                d["risk_category"] = hab.risk_assessment.risk_category
                d["hazard_score"] = hab.risk_assessment.hazard_score
                d["exposure_score"] = hab.risk_assessment.exposure_score
                d["vulnerability_score"] = hab.risk_assessment.vulnerability_score
            if hab.necessity:
                d["necessity_category"] = hab.necessity.category
                d["action_timeline"] = hab.necessity.action_timeline
            result.append(d)
        return jsonify(result)
    finally:
        session.close()


@habitations_bp.route("/<hab_id>", methods=["GET"])
def get_habitation(hab_id: str):
    """Get a single habitation with all associated data."""
    Session = get_session_factory()
    session = Session()
    try:
        hab = Repository.get_habitation(session, hab_id)
        if not hab:
            return jsonify({"error": f"Habitation {hab_id} not found"}), 404

        d = Repository.habitation_to_dict(hab)
        if hab.risk_assessment:
            d["risk_assessment"] = {
                "hazard_score": hab.risk_assessment.hazard_score,
                "exposure_score": hab.risk_assessment.exposure_score,
                "vulnerability_score": hab.risk_assessment.vulnerability_score,
                "rpi": hab.risk_assessment.rpi,
                "risk_category": hab.risk_assessment.risk_category,
            }
        if hab.necessity:
            import json
            d["necessity"] = {
                "category": hab.necessity.category,
                "risk_score": hab.necessity.risk_score,
                "color_code": hab.necessity.color_code,
                "action_timeline": hab.necessity.action_timeline,
                "reasons": json.loads(hab.necessity.reasons) if hab.necessity.reasons else [],
            }
        d["assignments"] = [
            {
                "site_id": a.site_id,
                "site_name": a.site.name if a.site else "UNASSIGNED",
                "population": a.population,
                "necessity_category": a.necessity_category,
                "status": a.status,
            }
            for a in hab.assignments
        ]
        return jsonify(d)
    finally:
        session.close()


@habitations_bp.route("/geojson", methods=["GET"])
def habitations_geojson():
    """Return all habitations as a GeoJSON FeatureCollection (for map)."""
    Session = get_session_factory()
    session = Session()
    try:
        habs = Repository.get_all_habitations(session)
        features = [Repository.habitation_to_geojson_feature(h) for h in habs]
        return jsonify({"type": "FeatureCollection", "features": features})
    finally:
        session.close()


@habitations_bp.route("/field-verification", methods=["GET"])
def get_verification_tasks():
    """Return habitations that have field verification tasks."""
    Session = get_session_factory()
    session = Session()
    try:
        verifications = Repository.get_field_verifications(session)
        result = []
        for fv in verifications:
            hab = Repository.get_habitation(session, fv.habitation_id)
            if not hab:
                continue
            result.append({
                "id": hab.id,
                "name": hab.name,
                "rpi": hab.risk_assessment.rpi if hab.risk_assessment else 0,
                "status": fv.status,
                "assignedDate": fv.assigned_date,
                "distance": "N/A",
                "systemData": {
                    "elevation": hab.elevation,
                    "slope": hab.slope,
                    "population": hab.population,
                    "households": hab.households,
                },
            })
        return jsonify(result)
    finally:
        session.close()
