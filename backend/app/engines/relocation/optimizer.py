from typing import Dict, Any, List
from app.engines.relocation.safe_site import SiteScorer
from app.engines.relocation.carrying_capacity import CapacityCalculator
from app.engines.relocation.necessity import NecessityEngine

class RelocationOptimizer:
    """
    Greedy assignment algorithm to map at-risk habitations to optimal candidate sites.
    Respects capacity constraints and safety minimums.
    """

    @staticmethod
    def run_optimization(habitations: List[Dict[str, Any]], candidate_sites: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Executes the greedy assignment.
        - habitations: List of dicts with keys (id, name, population, risk_score)
        - candidate_sites: List of dicts representing raw site data
        """
        # Step 1: Classify and Rank Habitations
        classified_habitations = []
        for hab in habitations:
            necessity = NecessityEngine.evaluate_necessity(hab["id"], hab.get("risk_score"))
            hab["necessity_category"] = necessity["category"]
            
            # Map category to priority weight
            priority_weight = {
                "Immediate": 5,
                "Short-Term": 4,
                "Medium-Term": 3,
                "In-Situ": 2,
                "Monitor": 1
            }.get(necessity["category"], 0)
            
            hab["priority_weight"] = priority_weight
            classified_habitations.append(hab)

        # Sort habitations: Highest priority category first, then highest risk score
        classified_habitations.sort(key=lambda x: (x["priority_weight"], x.get("risk_score", 0)), reverse=True)

        # Step 2: Score Candidate Sites (Only use safe sites > 50)
        scored_sites = SiteScorer.compare_sites(candidate_sites)
        safe_sites = [s for s in scored_sites if s["total_score"] >= 50]
        
        # Step 3: Compute Initial Capacities for Safe Sites
        site_capacities = {}
        for site in safe_sites:
            # Assume starting incoming population is 0 just to get baseline feasible capacity
            cap_analysis = CapacityCalculator.analyze_capacity(site["site_id"], 0)
            site_capacities[site["site_id"]] = cap_analysis["feasible_additional_capacity"]

        # Step 4: Greedy Assignment
        assignments = []
        unassigned = []

        for hab in classified_habitations:
            assigned = False
            for site in safe_sites:
                site_id = site["site_id"]
                current_available = site_capacities.get(site_id, 0)
                
                # Capacity Check
                if current_available >= hab["population"]:
                    # Assign
                    site_capacities[site_id] -= hab["population"]
                    
                    assignments.append({
                        "habitation_id": hab["id"],
                        "habitation_name": hab["name"],
                        "population": hab["population"],
                        "necessity": hab["necessity_category"],
                        "assigned_site_id": site_id,
                        "assigned_site_name": site["site_name"],
                        "reason": f"Assigned to {site['site_name']} because it is the highest-scoring safe site (Score: {site['total_score']}) with sufficient capacity (Remaining: {site_capacities[site_id]})."
                    })
                    assigned = True
                    break
            
            if not assigned:
                unassigned.append({
                    "habitation_id": hab["id"],
                    "habitation_name": hab["name"],
                    "population": hab["population"],
                    "necessity": hab["necessity_category"],
                    "reason": "Failed to assign: No safe sites found with sufficient capacity to absorb this population."
                })

        return {
            "summary": {
                "total_habitations": len(habitations),
                "assigned": len(assignments),
                "unassigned": len(unassigned)
            },
            "assignments": assignments,
            "unassigned": unassigned
        }

    @staticmethod
    def get_demo_data() -> tuple:
        """ Returns mock habitations and sites for testing """
        habitations = [
            {"id": "H1", "name": "Riverbend Village", "population": 800, "risk_score": 92},
            {"id": "H2", "name": "Cliffside Settlement", "population": 400, "risk_score": 88},
            {"id": "H3", "name": "Valley Floor Camp", "population": 1200, "risk_score": 75},
            {"id": "H4", "name": "Lower Plains", "population": 500, "risk_score": 60},
        ]
        
        # Raw site factors
        sites = [
            {"site_id": "S1", "site_name": "Highland Zone A", "factors": {"distance_to_hazard": 90, "terrain_slope": 85, "area_capacity": 95}},
            {"site_id": "S2", "site_name": "West Plateau", "factors": {"distance_to_hazard": 70, "terrain_slope": 90, "area_capacity": 40}},
            {"site_id": "S3", "site_name": "Unsafe Lowland", "factors": {"distance_to_hazard": 20, "terrain_slope": 30, "area_capacity": 100}}, # Should be filtered out
        ]
        return habitations, sites
