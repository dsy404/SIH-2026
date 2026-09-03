from flask import Blueprint, request, jsonify
from app.engines.relocation.necessity import NecessityEngine

necessity_bp = Blueprint('necessity', __name__)

@necessity_bp.route("/evaluate", methods=["GET"])
def evaluate_necessity():
    """
    Evaluates the relocation necessity for a given habitation.
    """
    habitation_id = request.args.get('habitation_id')
    
    if not habitation_id:
        return jsonify({"error": "habitation_id is required"}), 400
        
    # Optional explicitly provided risk score
    risk_score_param = request.args.get('risk_score')
    risk_score = None
    if risk_score_param:
        try:
            risk_score = float(risk_score_param)
        except ValueError:
            pass
            
    decision = NecessityEngine.evaluate_necessity(habitation_id, risk_score)
    
    return jsonify(decision)
