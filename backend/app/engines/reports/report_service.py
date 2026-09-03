import csv
from io import StringIO
from typing import List, Dict, Any

class ReportService:
    """
    Service for generating downloadable reports.
    """
    
    @staticmethod
    def generate_csv_report(rows: List[Dict[str, Any]]) -> str:
        """
        Generates a CSV string from a list of priority table rows.
        """
        if not rows:
            return "No data available"
            
        output = StringIO()
        
        # Define headers based on the UI priority table
        headers = ["Rank", "Priority", "Habitation ID", "Habitation Name", "Risk Score", "Affected Pop", "Action Category", "Assigned Site", "Capacity Status"]
        writer = csv.DictWriter(output, fieldnames=headers)
        
        writer.writeheader()
        
        for rank, row in enumerate(rows, start=1):
            writer.writerow({
                "Rank": rank,
                "Priority": row.get("priority_level", "Unknown"),
                "Habitation ID": row.get("habitation_id", ""),
                "Habitation Name": row.get("habitation_name", ""),
                "Risk Score": row.get("risk_score", 0),
                "Affected Pop": row.get("affected_population", 0),
                "Action Category": row.get("action_category", ""),
                "Assigned Site": row.get("assigned_site", ""),
                "Capacity Status": row.get("capacity_status", "")
            })
            
        return output.getvalue()
