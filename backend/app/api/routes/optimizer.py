"""
Optimizer API — reads habitations and sites from DB, saves assignments back.
"""
from flask import Blueprint, jsonify
from app.db.database import get_session_factory
from app.db.repository import Repository
from app.engines.relocation.optimizer import RelocationOptimizer

optimizer_bp = Blueprint('optimizer', __name__)


@optimizer_bp.route("/run", methods=["POST", "GET"])
def run_optimization():
    """
    Executes the relocation optimizer using canonical DB data.
    Saves assignments back to the database.
    """
    Session = get_session_factory()
    session = Session()
    try:
        habitations = Repository.get_all_habitations(session)
        sites = Repository.get_all_sites(session)

        # Convert to dicts for the engine
        hab_dicts = []
        for h in habitations:
            d = Repository.habitation_to_dict(h)
            d["risk_score"] = h.risk_assessment.rpi if h.risk_assessment else 0
            hab_dicts.append(d)

        site_dicts = [Repository.site_to_dict(s) for s in sites]

        # Run optimization
        plan = RelocationOptimizer.run_optimization(hab_dicts, site_dicts)

        # Clear old assignments and save new ones
        Repository.clear_assignments(session)

        for a in plan.get("assignments", []):
            Repository.save_assignment(session, {
                "habitation_id": a["habitation_id"],
                "site_id": a["assigned_site_id"],
                "population": a["population"],
                "necessity_category": a["necessity"],
                "reason": a["reason"],
                "status": "pending",
            })

        for u in plan.get("unassigned", []):
            Repository.save_assignment(session, {
                "habitation_id": u["habitation_id"],
                "site_id": None,
                "population": u["population"],
                "necessity_category": u["necessity"],
                "reason": u["reason"],
                "status": "unassigned",
            })

        Repository.log_action(session, "optimize", details="Optimizer run completed")
        session.commit()

        return jsonify(plan)
    finally:
        session.close()
