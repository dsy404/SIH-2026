import math
from typing import Dict, List, Any

class SimulationService:
    """
    Simulation Engine to demonstrate dynamic risk changes based on rainfall.
    """
    
    @staticmethod
    def simulate_rainfall(rainfall_mm: float) -> Dict[str, Any]:
        """
        Takes additional rainfall in mm and recalculates RPI for demo habitations.
        """
        
        # Base synthetic habitations (similar to previous phases)
        habitations = [
            {"id": "hab-1", "name": "Riverbank Alpha", "base_hazard": 40, "exposure": 70, "vulnerability": 60, "elevation": 5},
            {"id": "hab-2", "name": "Valley Beta", "base_hazard": 20, "exposure": 40, "vulnerability": 50, "elevation": 12},
            {"id": "hab-3", "name": "Cliffside Gamma", "base_hazard": 60, "exposure": 80, "vulnerability": 75, "elevation": 150},
            {"id": "hab-4", "name": "Delta Delta", "base_hazard": 30, "exposure": 50, "vulnerability": 45, "elevation": 3},
            {"id": "hab-5", "name": "Highland Epsilon", "base_hazard": 10, "exposure": 20, "vulnerability": 30, "elevation": 250},
        ]
        
        results = []
        red_zones = 0
        
        for hab in habitations:
            # Simulated formula: Extra rainfall increases hazard score exponentially for low elevation
            # Base hazard + (rainfall * factor based on elevation)
            elevation_factor = max(0.1, (200 - hab["elevation"]) / 200) # Lower elevation = higher factor
            
            simulated_hazard = hab["base_hazard"] + (rainfall_mm * elevation_factor * 0.5)
            # Cap at 100
            simulated_hazard = min(100.0, simulated_hazard)
            
            # RPI = 40% Hazard + 30% Exposure + 30% Vulnerability
            rpi = (simulated_hazard * 0.40) + (hab["exposure"] * 0.30) + (hab["vulnerability"] * 0.30)
            
            status = "Low"
            if rpi > 75:
                status = "Critical (Red Zone)"
                red_zones += 1
            elif rpi > 50:
                status = "High"
            elif rpi > 25:
                status = "Moderate"
                
            results.append({
                "id": hab["id"],
                "name": hab["name"],
                "elevation": hab["elevation"],
                "simulated_hazard": round(simulated_hazard, 2),
                "rpi": round(rpi, 2),
                "status": status
            })
            
        return {
            "rainfall_input_mm": rainfall_mm,
            "total_red_zones": red_zones,
            "simulated_data": results
        }
