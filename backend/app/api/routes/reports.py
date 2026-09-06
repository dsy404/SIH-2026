"""
Reports API — reads from DB instead of get_demo_data().
"""
from flask import Blueprint, Response
from app.engines.reports.report_service import ReportService
from app.db.database import get_session_factory
from app.db.repository import Repository

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/csv', methods=['GET'])
def download_csv():
    """
    Generates and returns the priority table as a CSV file.
    Data sourced from the canonical database.
    """
    Session = get_session_factory()
    session = Session()
    try:
        habitations = Repository.get_all_habitations(session)
        assignments = Repository.get_all_assignments(session)

        # Build a lookup of assignment by habitation_id
        assign_lookup = {}
        for a in assignments:
            assign_lookup[a.habitation_id] = a

        priority_table = []
        for hab in habitations:
            rpi = hab.risk_assessment.rpi if hab.risk_assessment else 0
            nec = hab.necessity.category if hab.necessity else "Monitor"
            assignment = assign_lookup.get(hab.id)

            priority_table.append({
                "habitation_id": hab.id,
                "habitation_name": hab.name,
                "risk_score": round(rpi, 2),
                "affected_population": hab.population,
                "action_category": nec,
                "assigned_site": assignment.site.name if assignment and assignment.site else "UNASSIGNED",
                "capacity_status": "Safe" if assignment and assignment.site_id else "Deficit",
            })

        priority_table.sort(key=lambda x: x["risk_score"], reverse=True)
        for idx, row in enumerate(priority_table):
            row["rank"] = idx + 1
            row["priority_level"] = row["action_category"]

        csv_data = ReportService.generate_csv_report(priority_table)

        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=relocation_priority_report.csv"},
        )
    finally:
        session.close()
