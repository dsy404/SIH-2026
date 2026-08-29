from __future__ import annotations
from typing import List, Dict, Any
from shapely.geometry import Point, shape
import json

class HazardEngine:
    def calculate_hazard_scores(self, habitations: List[Dict[str, Any]], hazards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculates Hazard Risk Scores (0-100) based on intersection with hazard polygons.
        Returns the habitations list with 'hazard_score' and 'explanation' fields added.
        """
        # Parse hazard polygons into shapely shapes for fast point-in-polygon checks
        parsed_hazards = []
        for hz in hazards:
            if 'geom_geojson' in hz:
                try:
                    geom = json.loads(hz['geom_geojson'])
                    parsed_hazards.append({
                        'shape': shape(geom),
                        'severity': hz.get('severity', 'Moderate').lower(),
                        'type': hz.get('type', 'Unknown Hazard')
                    })
                except Exception:
                    continue
                    
        for hab in habitations:
            score = 0.0
            explanations = []
            
            if 'longitude' in hab and 'latitude' in hab:
                pt = Point(float(hab['longitude']), float(hab['latitude']))
                
                # Check intersections
                for hz in parsed_hazards:
                    if hz['shape'].contains(pt):
                        severity_score = 0
                        if hz['severity'] == 'high':
                            severity_score = 100.0
                            score = max(score, severity_score)
                            explanations.append(f"Located directly inside HIGH severity {hz['type']} zone (Score: 100).")
                        elif hz['severity'] == 'moderate':
                            severity_score = 50.0
                            score = max(score, severity_score)
                            explanations.append(f"Located inside MODERATE severity {hz['type']} zone (Score: 50).")
                        else:
                            severity_score = 25.0
                            score = max(score, severity_score)
                            explanations.append(f"Located inside LOW severity {hz['type']} zone (Score: 25).")
                            
            if not explanations:
                explanations.append("Not located inside any known hazard zones.")
                
            hab['hazard_score'] = score
            hab['explanation'] = {
                "engine": "HazardEngine",
                "factors": explanations
            }
            
        return habitations

