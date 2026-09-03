import random
from typing import Dict, List, Any

class PostRelocationTracker:
    """
    Engine to track post-relocation household status based on infrastructure parameters.
    """
    
    @staticmethod
    def get_infrastructure_status(site_id: str) -> Dict[str, Any]:
        """
        Simulate getting infrastructure status for a site.
        In a real app, this would query the DB for the site's facilities.
        """
        # Hardcode some sites for demonstration
        if site_id == "site-1":
            return {
                "water_supply": True,
                "healthcare": True,
                "school": True,
                "electricity": True,
                "missing": []
            }
        elif site_id == "site-2":
            return {
                "water_supply": True,
                "healthcare": False,
                "school": True,
                "electricity": True,
                "missing": ["Healthcare (Clinic)"]
            }
        elif site_id == "site-3":
            return {
                "water_supply": False,
                "healthcare": False,
                "school": False,
                "electricity": True,
                "missing": ["Water Supply", "Healthcare", "School"]
            }
        else:
            return {
                "water_supply": True,
                "healthcare": True,
                "school": False,
                "electricity": True,
                "missing": ["School"]
            }

    @staticmethod
    def track_households(relocated_habitations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Takes a list of relocated habitations (assigned to sites) and evaluates their status.
        """
        
        results = []
        summary = {
            "stable": 0,
            "needs_attention": 0,
            "at_risk": 0
        }
        
        for hab in relocated_habitations:
            site_id = hab.get("assigned_site_id", "site-1")
            infra = PostRelocationTracker.get_infrastructure_status(site_id)
            
            missing_count = len(infra["missing"])
            households = hab.get("households", 0)
            
            if missing_count == 0:
                status = "Stable"
                summary["stable"] += households
            elif missing_count == 1:
                status = "Needs Attention"
                summary["needs_attention"] += households
            else:
                status = "At Risk"
                summary["at_risk"] += households
                
            results.append({
                "habitation_id": hab.get("id"),
                "habitation_name": hab.get("name"),
                "households": households,
                "assigned_site": hab.get("assigned_site_name", "Safe Site"),
                "status": status,
                "missing_infrastructure": infra["missing"]
            })
            
        return {
            "summary": summary,
            "tracking_details": results
        }
