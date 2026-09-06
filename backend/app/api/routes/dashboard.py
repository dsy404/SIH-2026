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
    All data sourced from the canonical database via live aggregation.
    """
    Session = get_session_factory()
    session = Session()
    try:
        habitations = Repository.get_all_habitations(session)
        assignments = Repository.get_all_assignments(session)
        sites = Repository.get_all_sites(session)

        total_habitations = len(habitations)
        total_population = sum(h.population for h in habitations)

        # Count Red Zones (Immediate or Short-Term necessity) and affected population
        red_zones = 0
        affected_population = 0
        risk_distribution = {}
        necessity_distribution = {}

        for h in habitations:
            if h.risk_assessment:
                rc = h.risk_assessment.risk_category
                risk_distribution[rc] = risk_distribution.get(rc, 0) + 1
            if h.necessity:
                nc = h.necessity.category
                necessity_distribution[nc] = necessity_distribution.get(nc, 0) + 1
                if nc in ["Immediate", "Short-Term"]:
                    red_zones += 1
                    affected_population += h.population

        # Build assigned lookup
        assignment_by_hab = {a.habitation_id: a for a in assignments}
        assigned_hab_ids = {a.habitation_id for a in assignments if a.site_id is not None}
        unassigned_at_risk = [
            h for h in habitations
            if h.id not in assigned_hab_ids and h.necessity and h.necessity.category in ["Immediate", "Short-Term", "Medium-Term"]
        ]
        capacity_deficit = sum(h.population for h in unassigned_at_risk)

        # Build complete priority table for all habitations
        priority_table = []
        for hab in habitations:
            rpi = hab.risk_assessment.rpi if hab.risk_assessment else 0.0
            a = assignment_by_hab.get(hab.id)
            nec_cat = hab.necessity.category if hab.necessity else "Monitor"

            assigned_site_name = "UNASSIGNED"
            capacity_status = "Deficit"
            if a and a.site:
                assigned_site_name = a.site.name
                capacity_status = "Safe"
            elif nec_cat in ["In-Situ", "Monitor"]:
                capacity_status = "In-Situ Fortification" if nec_cat == "In-Situ" else "Monitoring"

            priority_table.append({
                "habitation_id": hab.id,
                "habitation_name": hab.name,
                "risk_score": round(rpi, 2),
                "population": hab.population,
                "action_category": nec_cat,
                "assigned_site": assigned_site_name,
                "capacity_status": capacity_status,
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
                "affected_population": affected_population,
                "capacity_deficit": capacity_deficit,
                "assigned_count": len(assigned_hab_ids),
                "unassigned_count": len(unassigned_at_risk),
                "risk_distribution": risk_distribution,
                "necessity_distribution": necessity_distribution,
            },
            "priority_table": priority_table,
        })
    finally:
        session.close()

