from flask import Blueprint, request, jsonify
from app.engines.hazard_engine import HazardEngine
from app.engines.exposure_engine import ExposureEngine

engines_bp = Blueprint('engines', __name__)

@engines_bp.route("/hazard", methods=["POST"])
def run_hazard_engine():
    data = request.json
    engine = HazardEngine()
    scored_habitations = engine.calculate_hazard_scores(data.get('habitations', []), data.get('hazards', []))
    return jsonify({"results": scored_habitations})

@engines_bp.route("/exposure", methods=["POST"])
def run_exposure_engine():
    data = request.json
    engine = ExposureEngine()
    scored_habitations = engine.calculate_exposure_scores(data.get('habitations', []))
    return jsonify({"results": scored_habitations})

@engines_bp.route("/vulnerability", methods=["POST"])
def run_vulnerability_engine():
    data = request.json
    from app.engines.vulnerability_engine import VulnerabilityEngine
    engine = VulnerabilityEngine()
    scored_habitations = engine.calculate_vulnerability_scores(data.get('habitations', []))
    return jsonify({"results": scored_habitations})
