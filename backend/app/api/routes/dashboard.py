from flask import Blueprint, jsonify
from app.engines.relocation.optimizer import RelocationOptimizer
from app.engines.relocation.necessity import NecessityEngine

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/action-plan", methods=["GET"])
def get_action_plan():
    """
    Aggregates data across the system to provide the Government Action Plan dashboard.
    """
    habitations, candidate_sites = RelocationOptimizer.get_demo_data()
    
    # Run the optimizer to get the assignments
    plan = RelocationOptimizer.run_optimization(habitations, candidate_sites)
    
    # Calculate overall stats
    total_habitations = len(habitations)
    total_population = sum(h["population"] for h in habitations)
    
    # Count Red Zones (Immediate or Short-Term)
    red_zones = sum(1 for h in plan["assignments"] + plan["unassigned"] if h["necessity"] in ["Immediate", "Short-Term"])
    
    # Capacity deficit = total unassigned population
    capacity_deficit = sum(h["population"] for h in plan["unassigned"])
    
    # Build the priority table
    priority_table = []
    
    for idx, item in enumerate(plan["assignments"]):
        priority_table.append({
            "rank": idx + 1,
            "habitation_name": item["habitation_name"],
            "risk_score": next((h["risk_score"] for h in habitations if h["id"] == item["habitation_id"]), 0),
            "population": item["population"],
            "action_category": item["necessity"],
            "assigned_site": item["assigned_site_name"],
            "capacity_status": "Safe"
        })
        
    for idx, item in enumerate(plan["unassigned"]):
        priority_table.append({
            "rank": len(plan["assignments"]) + idx + 1,
            "habitation_name": item["habitation_name"],
            "risk_score": next((h["risk_score"] for h in habitations if h["id"] == item["habitation_id"]), 0),
            "population": item["population"],
            "action_category": item["necessity"],
            "assigned_site": "UNASSIGNED",
            "capacity_status": "Deficit"
        })
        
    # Sort by risk score (descending) just in case
    priority_table.sort(key=lambda x: x["risk_score"], reverse=True)
    
    # Re-rank after sorting
    for idx, row in enumerate(priority_table):
        row["rank"] = idx + 1

    return jsonify({
        "stats": {
            "total_habitations": total_habitations,
            "total_population": total_population,
            "red_zones": red_zones,
            "capacity_deficit": capacity_deficit
        },
        "priority_table": priority_table
    })
