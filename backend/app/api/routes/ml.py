from flask import Blueprint, jsonify
from app.engines.ml.risk_classifier import MLRiskClassifier

ml_bp = Blueprint('ml', __name__)

@ml_bp.route('/feature-importance', methods=['GET'])
def get_feature_importance():
    """
    Endpoint to retrieve ML feature importance.
    """
    data = MLRiskClassifier.get_feature_importance()
    return jsonify(data), 200
