from flask import Blueprint, jsonify, request
from app.engines.simulation.simulation_service import SimulationService

simulation_bp = Blueprint('simulation', __name__)

@simulation_bp.route('/run', methods=['POST'])
def run_simulation():
    """
    POST endpoint to run a dynamic rainfall simulation.
    Accepts JSON: { "rainfall_mm": float }
    """
    data = request.get_json() or {}
    rainfall_mm = data.get("rainfall_mm", 0)
    
    try:
        rainfall_mm = float(rainfall_mm)
    except ValueError:
        rainfall_mm = 0.0
        
    result = SimulationService.simulate_rainfall(rainfall_mm)
    return jsonify(result), 200
