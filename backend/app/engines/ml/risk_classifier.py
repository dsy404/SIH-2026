from typing import Dict, Any, List

class MLRiskClassifier:
    """
    Mock implementation of a Machine Learning classifier for demonstration purposes.
    Because there is insufficient historical training data, this returns static 
    synthetic feature importance to demonstrate the methodology.
    """
    
    @staticmethod
    def get_feature_importance() -> Dict[str, Any]:
        """
        Returns simulated Random Forest feature importance.
        """
        return {
            "model_type": "RandomForestClassifier",
            "accuracy": 0.89,
            "f1_score": 0.86,
            "warning": "Insufficient historical training data. Current model relies on synthetic data and should only be used to demonstrate methodology.",
            "features": [
                {"name": "Hazard Score (Flood/Landslide)", "importance": 45, "color": "bg-red-500"},
                {"name": "Elevation & Slope (Exposure)", "importance": 25, "color": "bg-orange-500"},
                {"name": "Population Density (Vulnerability)", "importance": 18, "color": "bg-yellow-500"},
                {"name": "Household Overcrowding", "importance": 8, "color": "bg-blue-500"},
                {"name": "Distance to River", "importance": 4, "color": "bg-indigo-500"}
            ]
        }
