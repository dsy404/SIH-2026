from typing import Dict, Any, List

class CapacityCalculator:
    """
    Calculates per-dimension carrying capacity for a candidate relocation site and identifies bottlenecks.
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
        For demonstration, we generate simulated baseline capacities based on the site_id.
        """
        # Pseudo-random baseline generation based on site_id hash length/chars
        base = sum(ord(c) for c in site_id) % 100
        
        dimensions_analysis = []
        bottleneck = None
        min_surplus_ratio = float('inf')

        for i, dim in enumerate(CapacityCalculator.DIMENSIONS):
            # Simulate existing max capacity (e.g., number of people it can support)
            # Typically 2000 - 10000
            max_capacity = 2000 + ((base * (i + 1) * 37) % 8000)
            
            # Simulate current utilization (e.g., currently serving X people)
            current_utilization = int(max_capacity * (0.3 + ((base * i) % 40) / 100.0))
            
            # The additional capacity needed
            required_capacity = incoming_population
            
            # Available capacity for new people
            available_capacity = max_capacity - current_utilization
            
            # Post-relocation surplus/deficit
            post_relocation_surplus = available_capacity - required_capacity
            
            # Ratio for finding bottleneck (lower ratio = more critical)
            # Negative surplus means deficit
            surplus_ratio = post_relocation_surplus / (required_capacity if required_capacity > 0 else 1)

            dim_data = {
                "dimension": dim,
                "max_capacity": max_capacity,
                "current_utilization": current_utilization,
                "available_capacity": available_capacity,
                "required_capacity": required_capacity,
                "post_relocation_surplus": post_relocation_surplus,
                "status": "Critical" if post_relocation_surplus < 0 else ("Warning" if post_relocation_surplus < 500 else "Safe")
            }
            
            dimensions_analysis.append(dim_data)
            
            if surplus_ratio < min_surplus_ratio:
                min_surplus_ratio = surplus_ratio
                bottleneck = dim_data
                
        # Calculate overall feasible additional capacity (the max people we can add before ANY dimension fails)
        # This is essentially the lowest available_capacity across all dimensions
        feasible_additional_capacity = min(d["available_capacity"] for d in dimensions_analysis)

        return {
            "site_id": site_id,
            "incoming_population": incoming_population,
            "dimensions": dimensions_analysis,
            "bottleneck": bottleneck,
            "feasible_additional_capacity": feasible_additional_capacity,
            "is_feasible": feasible_additional_capacity >= incoming_population,
            "warning": "Planning estimate: Values are synthetic and based on proxy indicators."
        }
