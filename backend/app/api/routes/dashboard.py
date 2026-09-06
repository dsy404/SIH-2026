"""
Dashboard API — reads all data from the canonical database.
"""
from flask import Blueprint, jsonify
from app.db.database import get_session_factory
from app.db.repository import Repository

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route("/action-plan", methods=["GET"])
def get_action_plan():
    """
    Aggregates data across the system to provide the Government Action Plan dashboard.
    All data sourced from the canonical database.
    """
    Session = get_session_factory()
    session = Session()
    try:
        habitations = Repository.get_all_habitations(session)
        assignments = Repository.get_all_assignments(session)

        total_habitations = len(habitations)
        total_population = sum(h.population for h in habitations)

        # Count Red Zones (Immediate or Short-Term necessity)
        red_zones = 0
        for h in habitations:
            if h.necessity and h.necessity.category in ["Immediate", "Short-Term"]:
                red_zones += 1

        # Build assigned/unassigned lookup
        assigned_hab_ids = {a.habitation_id for a in assignments if a.site_id is not None}
        unassigned_habs = [h for h in habitations if h.id not in assigned_hab_ids and h.necessity and h.necessity.category in ["Immediate", "Short-Term", "Medium-Term"]]
        capacity_deficit = sum(h.population for h in unassigned_habs)

        # Build priority table
        priority_table = []

        for a in assignments:
            hab = Repository.get_habitation(session, a.habitation_id)
            if not hab:
                continue
            rpi = hab.risk_assessment.rpi if hab.risk_assessment else 0
            priority_table.append({
                "habitation_id": hab.id,
                "habitation_name": hab.name,
                "risk_score": round(rpi, 2),
                "population": hab.population,
                "action_category": a.necessity_category or (hab.necessity.category if hab.necessity else "Monitor"),
                "assigned_site": a.site.name if a.site else "UNASSIGNED",
                "capacity_status": "Safe" if a.site_id else "Deficit",
            })

        # Add unassigned high-risk habitations
        for hab in unassigned_habs:
            if hab.id not in assigned_hab_ids:
                rpi = hab.risk_assessment.rpi if hab.risk_assessment else 0
                priority_table.append({
                    "habitation_id": hab.id,
                    "habitation_name": hab.name,
                    "risk_score": round(rpi, 2),
                    "population": hab.population,
                    "action_category": hab.necessity.category if hab.necessity else "Monitor",
                    "assigned_site": "UNASSIGNED",
                    "capacity_status": "Deficit",
                })

        # Sort by risk score descending and assign ranks
        priority_table.sort(key=lambda x: x["risk_score"], reverse=True)
        for idx, row in enumerate(priority_table):
            row["rank"] = idx + 1

        return jsonify({
            "stats": {
                "total_habitations": total_habitations,
                "total_population": total_population,
                "red_zones": red_zones,
                "capacity_deficit": capacity_deficit,
            },
            "priority_table": priority_table,
        })
    finally:
        session.close()
