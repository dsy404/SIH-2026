from __future__ import annotations
from typing import List, Dict, Any

class ConfidenceService:
    def assign_confidence(self, data: List[Dict[str, Any]], format: str, category: str) -> List[Dict[str, Any]]:
        """
        Assigns a confidence label based on source quality/format.
        """
        confidence_label = "HIGH" # default
        
        if format == "demo":
            confidence_label = "SYNTHETIC"
        elif format == "csv":
            confidence_label = "MODERATE" # CSV is prone to manual errors
        elif format == "shapefile" or format == "geojson":
            confidence_label = "HIGH" # GIS formats are usually official
            
        for record in data:
            record["confidence"] = confidence_label
            
        return data

