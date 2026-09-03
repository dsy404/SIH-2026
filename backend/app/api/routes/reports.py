from flask import Blueprint, Response
from app.engines.reports.report_service import ReportService
from app.engines.relocation.optimizer import RelocationOptimizer

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/csv', methods=['GET'])
def download_csv():
    """
    Generates and returns the priority table as a CSV file.
    """
    habitations, candidate_sites = RelocationOptimizer.get_demo_data()
    plan = RelocationOptimizer.run_optimization(habitations, candidate_sites)
    priority_table = []
    
    for item in plan["assignments"]:
        priority_table.append({
            "habitation_name": item["habitation_name"],
            "risk_score": next((h["risk_score"] for h in habitations if h["id"] == item["habitation_id"]), 0),
            "affected_population": item["population"],
            "action_category": item["necessity"],
            "assigned_site": item["assigned_site_name"],
            "capacity_status": "Safe"
        })
        
    for item in plan["unassigned"]:
        priority_table.append({
            "habitation_name": item["habitation_name"],
            "risk_score": next((h["risk_score"] for h in habitations if h["id"] == item["habitation_id"]), 0),
            "affected_population": item["population"],
            "action_category": item["necessity"],
            "assigned_site": "UNASSIGNED",
            "capacity_status": "Deficit"
        })
        
    priority_table.sort(key=lambda x: x["risk_score"], reverse=True)
    for idx, row in enumerate(priority_table):
        row["rank"] = idx + 1
        row["priority_level"] = row["action_category"]
    
    csv_data = ReportService.generate_csv_report(priority_table)
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=relocation_priority_report.csv"}
    )
