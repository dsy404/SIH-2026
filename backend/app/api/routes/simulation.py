"""
Simulation API — reads habitations from DB instead of inline mock.
"""
from flask import Blueprint, jsonify, request
from app.db.database import get_session_factory
from app.db.repository import Repository

simulation_bp = Blueprint('simulation', __name__)


@simulation_bp.route('/run', methods=['POST'])
def run_simulation():
    """
    Runs a dynamic rainfall simulation using habitations from the canonical DB.
    """
    data = request.get_json() or {}
    rainfall_mm = data.get("rainfall_mm", 0)

    try:
        rainfall_mm = float(rainfall_mm)
    except ValueError:
        rainfall_mm = 0.0

    Session = get_session_factory()
    session = Session()
    try:
        habitations = Repository.get_all_habitations(session)

        results = []
        red_zones = 0

        for hab in habitations:
            ra = hab.risk_assessment
            base_hazard = ra.hazard_score if ra else 0
            exposure = ra.exposure_score if ra else 0
            vulnerability = ra.vulnerability_score if ra else 0
            elevation = hab.elevation or 100

            # Simulated formula: Extra rainfall increases hazard score for low elevation
            elevation_factor = max(0.1, (200 - elevation) / 200)
            simulated_hazard = min(100.0, base_hazard + (rainfall_mm * elevation_factor * 0.5))

            # RPI = 40% Hazard + 30% Exposure + 30% Vulnerability
            rpi = (simulated_hazard * 0.40) + (exposure * 0.30) + (vulnerability * 0.30)

            status = "Low"
            if rpi > 75:
                status = "Critical (Red Zone)"
                red_zones += 1
            elif rpi > 50:
                status = "High"
            elif rpi > 25:
                status = "Moderate"

            results.append({
                "id": hab.id,
                "name": hab.name,
                "elevation": elevation,
                "simulated_hazard": round(simulated_hazard, 2),
                "rpi": round(rpi, 2),
                "status": status,
            })

        return jsonify({
            "rainfall_input_mm": rainfall_mm,
            "total_red_zones": red_zones,
            "simulated_data": results,
        })
    finally:
        session.close()
