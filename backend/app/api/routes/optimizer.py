from flask import Blueprint, jsonify
from app.engines.relocation.optimizer import RelocationOptimizer

optimizer_bp = Blueprint('optimizer', __name__)

@optimizer_bp.route("/run", methods=["POST", "GET"])
def run_optimization():
    """
    Executes the relocation optimizer using demo data (for demonstration purposes).
    In production, this would accept a JSON payload of habitations and candidate sites.
    """
    # For Phase 16 demo, we pull mock data directly
    habitations, candidate_sites = RelocationOptimizer.get_demo_data()
    
    plan = RelocationOptimizer.run_optimization(habitations, candidate_sites)
    
    return jsonify(plan)
