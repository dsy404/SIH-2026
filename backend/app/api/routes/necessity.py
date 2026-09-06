"""
Necessity API — reads stored risk score from DB.
"""
from flask import Blueprint, request, jsonify
from app.db.database import get_session_factory
from app.db.repository import Repository
from app.engines.relocation.necessity import NecessityEngine

necessity_bp = Blueprint('necessity', __name__)


@necessity_bp.route("/evaluate", methods=["GET"])
def evaluate_necessity():
    """
    Evaluates the relocation necessity for a given habitation.
    Uses the stored risk score from the canonical database.
    """
    habitation_id = request.args.get('habitation_id')

    if not habitation_id:
        return jsonify({"error": "habitation_id is required"}), 400

    Session = get_session_factory()
    session = Session()
    try:
        hab = Repository.get_habitation(session, habitation_id)
        if not hab:
            return jsonify({"error": f"Habitation {habitation_id} not found"}), 404

        # Use stored risk score, or explicit override
        risk_score_param = request.args.get('risk_score')
        if risk_score_param:
            try:
                risk_score = float(risk_score_param)
            except ValueError:
                risk_score = hab.risk_assessment.rpi if hab.risk_assessment else 0
        else:
            risk_score = hab.risk_assessment.rpi if hab.risk_assessment else 0

        decision = NecessityEngine.evaluate_necessity(habitation_id, risk_score)

        # Enrich with habitation data
        decision["habitation_name"] = hab.name
        decision["population"] = hab.population
        decision["latitude"] = hab.latitude
        decision["longitude"] = hab.longitude

        return jsonify(decision)
    finally:
        session.close()
