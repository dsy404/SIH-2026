from typing import Dict, Any, List

class CapacityCalculator:
    """
    Calculates per-dimension carrying capacity for a candidate relocation site and identifies bottlenecks.
    
    Now reads capacity data from the canonical database via the repository.
    The analyze_capacity method remains for backward compatibility with the optimizer,
    which calls it during the greedy assignment loop.
    """
    DIMENSIONS = [
        "Housing",
        "Water Supply",
        "Power Grid",
        "Healthcare",
        "Education",
        "Sanitation",
        "Transport",
        "Livelihood"
    ]

    @staticmethod
    def analyze_capacity(site_id: str, incoming_population: int) -> Dict[str, Any]:
        """
        Analyzes the capacity of a site to support an incoming population.
        Reads from the canonical database.
        """
        from app.db.database import get_session_factory
        from app.db.repository import Repository

        Session = get_session_factory()
        session = Session()
        try:
            caps = Repository.get_site_capacity(session, site_id)
            
            if not caps:
                # Fallback: if no capacity data in DB, return a conservative estimate
                return {
                    "site_id": site_id,
                    "incoming_population": incoming_population,
                    "dimensions": [],
                    "bottleneck": None,
                    "feasible_additional_capacity": 0,
                    "is_feasible": False,
                    "warning": "No capacity data found for this site.",
                }

            dimensions_analysis = []
            bottleneck = None
            min_surplus_ratio = float('inf')

            for cap in caps:
                available = cap.max_capacity - cap.current_utilization
                post_surplus = available - incoming_population
                surplus_ratio = post_surplus / (incoming_population if incoming_population > 0 else 1)

                dim_data = {
                    "dimension": cap.dimension,
                    "max_capacity": cap.max_capacity,
                    "current_utilization": cap.current_utilization,
                    "available_capacity": available,
                    "required_capacity": incoming_population,
                    "post_relocation_surplus": post_surplus,
                    "status": "Critical" if post_surplus < 0 else ("Warning" if post_surplus < 500 else "Safe"),
                }
                dimensions_analysis.append(dim_data)

                if surplus_ratio < min_surplus_ratio:
                    min_surplus_ratio = surplus_ratio
                    bottleneck = dim_data

            feasible = min(d["available_capacity"] for d in dimensions_analysis)

            return {
                "site_id": site_id,
                "incoming_population": incoming_population,
                "dimensions": dimensions_analysis,
                "bottleneck": bottleneck,
                "feasible_additional_capacity": feasible,
                "is_feasible": feasible >= incoming_population,
            }
        finally:
            session.close()
