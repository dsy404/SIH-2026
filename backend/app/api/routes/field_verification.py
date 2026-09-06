"""
Field Verification API Routes — Phase 8.
Connected directly to database, audit trail, and cascading recalculation pipeline.
"""
from flask import Blueprint, jsonify, request
from app.db.database import get_session_factory
from app.db.repository import Repository
from app.engines.recalculation_service import RecalculationService

field_verification_bp = Blueprint('field_verification', __name__)


@field_verification_bp.route('/habitations', methods=['GET'])
def get_verification_habitations():
    """
    Returns habitations with their current baseline data, latest verification status,
    and ground truth observations.
    """
    Session = get_session_factory()
    session = Session()
    try:
        habitations = Repository.get_all_habitations(session)
        result = []

        for h in habitations:
            ra = h.risk_assessment
            nec = h.necessity
            latest_fv = Repository.get_latest_field_verification(session, h.id)

            item = {
                "id": h.id,
                "name": h.name,
                "population": h.population,
                "households": h.households,
                "latitude": h.latitude,
                "longitude": h.longitude,
                "elevation": h.elevation,
                "slope": h.slope,
                "road_accessible": h.road_accessible if h.road_accessible is not None else True,
                "road_status": h.road_status or "OPEN",
                "water_availability": h.water_availability or "ADEQUATE",
                "housing_condition": h.housing_condition or "PUCCA_GOOD",
                "healthcare_accessible": h.healthcare_accessible if h.healthcare_accessible is not None else True,
                "hazard_observation": h.hazard_observation or "NONE",
                "verification_status": h.verification_status or "NEEDS_VERIFICATION",
                "risk_score": ra.rpi if ra else 0.0,
                "risk_category": ra.risk_category if ra else "Moderate",
                "hazard_score": ra.hazard_score if ra else 0.0,
                "exposure_score": ra.exposure_score if ra else 0.0,
                "vulnerability_score": ra.vulnerability_score if ra else 0.0,
                "necessity_category": nec.category if nec else "Monitor",
                "last_verified": latest_fv.verified_at.isoformat() if (latest_fv and latest_fv.verified_at) else None,
                "verifier_name": latest_fv.verifier_name if latest_fv else None,
            }
            result.append(item)

        return jsonify(result)
    finally:
        session.close()


@field_verification_bp.route('/history', methods=['GET'])
def get_verification_history():
    """
    Returns the audit trail of all field verification submissions with before-vs-after diffs.
    """
    Session = get_session_factory()
    session = Session()
    try:
        hab_id = request.args.get('habitation_id')
        records = Repository.get_field_verifications(session, hab_id)
        return jsonify([Repository.field_verification_to_dict(r) for r in records])
    finally:
        session.close()


@field_verification_bp.route('/submit', methods=['POST'])
def submit_field_verification():
    """
    Submits a field verification report and triggers cascading recalculation.
    Never silently overwrites original source data; records provenance and before/after diff.
    """
    data = request.get_json() or {}
    if not data.get("habitation_id"):
        return jsonify({"error": "habitation_id is required"}), 400

    Session = get_session_factory()
    session = Session()
    try:
        result = RecalculationService.process_field_verification(session, data)
        return jsonify(result), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        session.rollback()
        return jsonify({"error": f"Cascading recalculation failed: {str(e)}"}), 500
    finally:
        session.close()
