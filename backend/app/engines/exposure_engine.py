from typing import List, Dict, Any

class ExposureEngine:
    def calculate_exposure_scores(self, habitations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculates Exposure Risk Scores (0-100) based on vulnerability factors.
        Lower elevation = higher flood risk. 
        Higher slope = higher landslide risk.
        Returns the habitations list with 'exposure_score' and 'explanation' fields.
        """
        for hab in habitations:
            score = 0.0
            explanations = []
            
            # Simple elevation scoring (Assuming < 150m is vulnerable in this demo region)
            elevation = hab.get('elevation')
            if elevation is not None:
                if float(elevation) < 100:
                    score += 50
                    explanations.append(f"Very low elevation ({elevation}m) significantly increases flood exposure (Score +50).")
                elif float(elevation) < 150:
                    score += 25
                    explanations.append(f"Low elevation ({elevation}m) moderately increases flood exposure (Score +25).")
                else:
                    explanations.append(f"High elevation ({elevation}m) offers good flood protection.")
                    
            # Simple slope scoring (Assuming > 20 degrees is vulnerable)
            slope = hab.get('slope')
            if slope is not None:
                if float(slope) > 25:
                    score += 50
                    explanations.append(f"Extremely steep slope ({slope}°) creates severe landslide exposure (Score +50).")
                elif float(slope) > 15:
                    score += 25
                    explanations.append(f"Steep slope ({slope}°) creates moderate landslide exposure (Score +25).")
                else:
                    explanations.append(f"Gentle slope ({slope}°) minimizes landslide exposure.")
                    
            # Cap at 100
            score = min(100.0, score)
            
            if not explanations:
                explanations.append("No topographic data available to determine physical exposure.")
                
            hab['exposure_score'] = score
            hab['exposure_explanation'] = {
                "engine": "ExposureEngine",
                "factors": explanations
            }
            
        return habitations
