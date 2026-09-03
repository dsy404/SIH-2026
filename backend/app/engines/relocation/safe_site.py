from typing import List, Dict, Any

class SiteScorer:
    """
    Engine for calculating multi-criteria safety scores for candidate relocation sites.
    """

    # Weights for the 13 factors (total 100)
    # Adjust weights based on priority (e.g. Safety > Infrastructure)
    WEIGHTS = {
        "distance_to_hazard": 15,
        "terrain_slope": 10,
        "soil_stability": 10,
        "historical_safety": 10,
        "road_accessibility": 8,
        "healthcare_proximity": 7,
        "education_proximity": 5,
        "area_capacity": 8,
        "water_access": 7,
        "power_access": 5,
        "distance_to_origin": 5,
        "environmental_impact": 5,
        "land_use": 5
    }

    @staticmethod
    def calculate_score(site_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates the suitability score for a single site.
        Assumes site_data contains raw values or pre-normalized (0-100) scores for each factor.
        For demonstration, we expect pre-normalized (0-100) scores in `factors`.
        """
        factors = site_data.get("factors", {})
        
        total_score = 0.0
        breakdown = {}

        for factor, weight in SiteScorer.WEIGHTS.items():
            # Default to 50 if data is missing, to penalize but not fail completely
            factor_score = factors.get(factor, 50)
            
            # Weighted contribution
            contribution = (factor_score * weight) / 100.0
            total_score += contribution
            
            breakdown[factor] = {
                "score": factor_score,
                "weight": weight,
                "contribution": round(contribution, 2)
            }

        return {
            "site_id": site_data.get("site_id", "unknown"),
            "site_name": site_data.get("site_name", "Unknown Site"),
            "total_score": round(total_score, 2),
            "breakdown": breakdown,
            "coordinates": site_data.get("coordinates")
        }

    @staticmethod
    def compare_sites(sites: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scores multiple sites and returns them sorted by highest score.
        """
        scored_sites = [SiteScorer.calculate_score(site) for site in sites]
        # Sort descending by total score
        scored_sites.sort(key=lambda x: x["total_score"], reverse=True)
        return scored_sites

    @staticmethod
    def get_mock_candidates(habitation_id: str) -> List[Dict[str, Any]]:
        """
        Generates mock candidate sites for demonstration purposes.
        """
        return [
            {
                "site_id": f"site_A_{habitation_id}",
                "site_name": "Highland Safe Zone A",
                "coordinates": [75.12, 12.34],
                "factors": {
                    "distance_to_hazard": 90,
                    "terrain_slope": 85,
                    "soil_stability": 80,
                    "historical_safety": 100,
                    "road_accessibility": 70,
                    "healthcare_proximity": 60,
                    "education_proximity": 50,
                    "area_capacity": 95,
                    "water_access": 80,
                    "power_access": 90,
                    "distance_to_origin": 40,
                    "environmental_impact": 75,
                    "land_use": 85
                }
            },
            {
                "site_id": f"site_B_{habitation_id}",
                "site_name": "Valley Edge Resettlement B",
                "coordinates": [75.15, 12.31],
                "factors": {
                    "distance_to_hazard": 60,
                    "terrain_slope": 70,
                    "soil_stability": 65,
                    "historical_safety": 50,
                    "road_accessibility": 95,
                    "healthcare_proximity": 90,
                    "education_proximity": 85,
                    "area_capacity": 60,
                    "water_access": 100,
                    "power_access": 100,
                    "distance_to_origin": 85,
                    "environmental_impact": 50,
                    "land_use": 60
                }
            }
        ]
