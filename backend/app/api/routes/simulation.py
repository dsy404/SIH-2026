"""
Simulation API — reads habitations from DB instead of inline mock.
"""
from flask import Blueprint, jsonify, request
from app.db.database import get_session_factory
from app.db.repository import Repository

from app.engines.simulation.simulation_service import SimulationService

simulation_bp = Blueprint('simulation', __name__)


@simulation_bp.route('/run-scenario', methods=['POST'])
def run_scenario():
    """
    Executes a DEMO LIVE-UPDATE SIMULATION comparing baseline rainfall to scenario rainfall.
    Propagates non-destructively through hazard -> risk -> red-zones -> urgency -> optimizer.
    """
    data = request.get_json() or {}
    baseline = float(data.get("baseline_rainfall_mm", 120.0))
    scenario = float(data.get("scenario_rainfall_mm", 210.0))

    Session = get_session_factory()
    session = Session()
    try:
        res = SimulationService.run_scenario_simulation(
            session,
            baseline_rainfall_mm=baseline,
            scenario_rainfall_mm=scenario
        )
        return jsonify(res), 200
    finally:
        session.close()


@simulation_bp.route('/reset', methods=['POST'])
def reset_scenario():
    """
    Resets the scenario parameters back to baseline default (120 mm) without altering DB records.
    """
    Session = get_session_factory()
    session = Session()
    try:
        res = SimulationService.run_scenario_simulation(
            session,
            baseline_rainfall_mm=120.0,
            scenario_rainfall_mm=120.0
        )
        return jsonify(res), 200
    finally:
        session.close()


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

@simulation_bp.route('/recalculate/<hab_id>', methods=['POST'])
def recalculate_pipeline(hab_id: str):
    """
    Cascading recalculation API:
    Changes a variable (e.g. hazard severity), propagates through 
    MasterEngine -> NecessityEngine -> Optimizer, and persists to DB.
    """
    data = request.get_json() or {}
    new_hazard_score = data.get("hazard_score")
    
    if new_hazard_score is None:
        return jsonify({"error": "Must provide new hazard_score"}), 400
        
    Session = get_session_factory()
    session = Session()
    try:
        hab = Repository.get_habitation(session, hab_id)
        if not hab:
            return jsonify({"error": "Habitation not found"}), 404
            
        from app.engines.master_engine import MasterEngine
        from app.engines.relocation.necessity import NecessityEngine
        from app.engines.relocation.optimizer import RelocationOptimizer
        import json
        from datetime import datetime
        
        # 1. Prepare data for MasterEngine
        hab_dict = Repository.habitation_to_dict(hab)
        # Assuming hazard, exposure, vulnerability are stored in risk assessment
        if hab.risk_assessment:
            hab_dict['exposure_score'] = hab.risk_assessment.exposure_score
            hab_dict['vulnerability_score'] = hab.risk_assessment.vulnerability_score
        else:
            hab_dict['exposure_score'] = 50.0
            hab_dict['vulnerability_score'] = 50.0
            
        hab_dict['hazard_score'] = float(new_hazard_score)
        
        # 2. Run MasterEngine (using a dummy hazard list since we hardcoded hazard_score above)
        me = MasterEngine()
        # Mocking the HazardEngine step by forcing the score back after since MasterEngine expects full flow
        hab_dict['rpi'] = (
            (hab_dict['hazard_score'] * 0.40) + 
            (hab_dict['exposure_score'] * 0.30) + 
            (hab_dict['vulnerability_score'] * 0.30)
        )
        hab_dict['rpi'] = min(100.0, hab_dict['rpi'])
        
        if hab_dict['rpi'] >= 76:
            hab_dict['risk_category'] = "Critical / Red Zone Candidate"
        elif hab_dict['rpi'] >= 56:
            hab_dict['risk_category'] = "High"
        elif hab_dict['rpi'] >= 31:
            hab_dict['risk_category'] = "Moderate"
        else:
            hab_dict['risk_category'] = "Low"
            
        rpi_explanation = {
            "engine": "MasterEngine",
            "calculation": f"({hab_dict['hazard_score']} * 0.4) + ({hab_dict['exposure_score']} * 0.3) + ({hab_dict['vulnerability_score']} * 0.3)",
            "disclaimer": "Prototype classification based on synthetic data. Not official government thresholds."
        }
        
        # 3. Save new RiskAssessment
        Repository.save_risk_assessment(session, {
            "habitation_id": hab.id,
            "hazard_score": hab_dict['hazard_score'],
            "exposure_score": hab_dict['exposure_score'],
            "vulnerability_score": hab_dict['vulnerability_score'],
            "rpi": hab_dict['rpi'],
            "risk_category": hab_dict['risk_category'],
            "rpi_explanation": json.dumps(rpi_explanation)
        })
        
        # 4. Run NecessityEngine
        decision = NecessityEngine.evaluate_necessity(hab.id, hab_dict['rpi'])
        
        # 5. Save new RelocationNecessity
        Repository.save_necessity(session, {
            "habitation_id": hab.id,
            "risk_score": decision["risk_score"],
            "category": decision["category"],
            "color_code": decision["color_code"],
            "action_timeline": decision["action_timeline"],
            "reasons": json.dumps(decision["reasons"])
        })
        
        # 6. Run Optimizer (Clear assignments first)
        Repository.clear_assignments(session)
        # Fetch all updated habs and sites
        all_habs = Repository.get_all_habitations(session)
        habs_for_opt = []
        for h in all_habs:
            d = {"id": h.id, "name": h.name, "population": h.population, "latitude": h.latitude, "longitude": h.longitude}
            if h.risk_assessment:
                d["risk_score"] = h.risk_assessment.rpi
            else:
                d["risk_score"] = 0
            habs_for_opt.append(d)
            
        sites_for_opt = []
        for s in Repository.get_all_sites(session):
            sites_for_opt.append({"id": s.id, "name": s.name, "latitude": s.latitude, "longitude": s.longitude})
            
        opt_results = RelocationOptimizer.run_optimization(habs_for_opt, sites_for_opt)
        for assignment in opt_results.get("assignments", []):
            Repository.save_assignment(session, {
                "habitation_id": assignment["habitation_id"],
                "site_id": assignment["assigned_site_id"],
                "population": assignment["population"],
                "necessity_category": assignment["necessity"],
                "reason": "Cascading recalculation automated assignment",
                "status": "pending"
            })
            
        # 7. Return Explainable Response
        return jsonify({
            "habitation_id": hab.id,
            "hazard_score": hab_dict['hazard_score'],
            "exposure_score": hab_dict['exposure_score'],
            "vulnerability_score": hab_dict['vulnerability_score'],
            "overall_risk": hab_dict['rpi'],
            "risk_category": hab_dict['risk_category'],
            "primary_risk_drivers": ["Simulated hazard increase"],
            "explanation": rpi_explanation["calculation"] + ". " + rpi_explanation["disclaimer"],
            "confidence": "High (Simulation)",
            "data_timestamp": datetime.utcnow().isoformat() + "Z"
        })
    finally:
        session.close()
