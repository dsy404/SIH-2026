from typing import List, Dict, Any
from .hazard_engine import HazardEngine
from .exposure_engine import ExposureEngine
from .vulnerability_engine import VulnerabilityEngine

class MasterEngine:
    def __init__(self):
        self.hazard_engine = HazardEngine()
        self.exposure_engine = ExposureEngine()
        self.vulnerability_engine = VulnerabilityEngine()
        
    def calculate_priority_index(self, habitations: List[Dict[str, Any]], hazards: List[Dict[str, Any]], weights: Dict[str, float] = None) -> List[Dict[str, Any]]:
        """
        Runs the full pipeline (Hazard -> Exposure -> Vulnerability) 
        and calculates the final Relocation Priority Index (RPI).
        """
        if weights is None:
            # Default IPCC standard weights
            weights = {
                "hazard": 0.40,
                "exposure": 0.30,
                "vulnerability": 0.30
            }
            
        # 1. Run all sub-engines
        habitations = self.hazard_engine.calculate_hazard_scores(habitations, hazards)
        habitations = self.exposure_engine.calculate_exposure_scores(habitations)
        habitations = self.vulnerability_engine.calculate_vulnerability_scores(habitations)
        
        # 2. Calculate Final RPI
        for hab in habitations:
            h_score = hab.get('hazard_score', 0)
            e_score = hab.get('exposure_score', 0)
            v_score = hab.get('vulnerability_score', 0)
            
            # Weighted average
            rpi = (
                (h_score * weights.get('hazard', 0.40)) + 
                (e_score * weights.get('exposure', 0.30)) + 
                (v_score * weights.get('vulnerability', 0.30))
            )
            
            # Cap at 100
            hab['rpi'] = min(100.0, rpi)
            
            # Determine Risk Category
            if hab['rpi'] >= 76:
                hab['risk_category'] = "Critical / Red Zone Candidate"
            elif hab['rpi'] >= 56:
                hab['risk_category'] = "High"
            elif hab['rpi'] >= 31:
                hab['risk_category'] = "Moderate"
            else:
                hab['risk_category'] = "Low"
                
            hab['rpi_explanation'] = {
                "engine": "MasterEngine",
                "weights_used": weights,
                "calculation": f"({h_score} * {weights.get('hazard')}) + ({e_score} * {weights.get('exposure')}) + ({v_score} * {weights.get('vulnerability')})",
                "disclaimer": "Prototype classification based on synthetic data. Not official government thresholds."
            }
            
        # Sort by highest RPI first
        habitations.sort(key=lambda x: x.get('rpi', 0), reverse=True)
        
        return habitations
