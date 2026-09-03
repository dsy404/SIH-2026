from typing import Dict, Any, List

class NecessityEngine:
    """
    Evaluates habitation risk scores to classify them into actionable relocation categories.
    Categories: Immediate, Short-Term, Medium-Term, In-Situ, Monitor.
    """
    
    @staticmethod
    def evaluate_necessity(habitation_id: str, risk_score: float = None) -> Dict[str, Any]:
        """
        Classifies habitation based on its risk score.
        If risk_score is None, a mock score is generated for demonstration.
        """
        # Generate a deterministic mock score if none provided
        if risk_score is None:
            # Pseudo-random but consistent risk based on habitation_id
            base = sum(ord(c) for c in habitation_id)
            risk_score = (base * 17) % 100
        
        category = ""
        reasons = []
        action_timeline = ""
        color_code = ""

        if risk_score > 85:
            category = "Immediate"
            color_code = "critical"
            action_timeline = "1-6 months"
            reasons = [
                "Critical multi-hazard risk detected (>85 score).",
                "High probability of severe localized impact in next seasonal cycle.",
                "Current infrastructure provides inadequate protection."
            ]
        elif risk_score >= 70:
            category = "Short-Term"
            color_code = "high"
            action_timeline = "1-3 years"
            reasons = [
                "High risk of hazard impact (70-85 score).",
                "Relocation recommended before the next major climatic anomaly.",
                "In-situ fortification is economically or technically unfeasible."
            ]
        elif risk_score >= 50:
            category = "Medium-Term"
            color_code = "medium"
            action_timeline = "3-5 years"
            reasons = [
                "Moderate risk with compounding vulnerabilities (50-70 score).",
                "Planned phased relocation recommended.",
                "Temporary infrastructure upgrades required during transition."
            ]
        elif risk_score >= 30:
            category = "In-Situ"
            color_code = "low-medium"
            action_timeline = "Ongoing"
            reasons = [
                "Low-Moderate risk profile (30-50 score).",
                "Full relocation not strictly required.",
                "Recommend local infrastructure fortification (e.g., retaining walls, embankments)."
            ]
        else:
            category = "Monitor"
            color_code = "low"
            action_timeline = "Annual Review"
            reasons = [
                "Low risk profile (<30 score).",
                "No immediate intervention required.",
                "Monitor for demographic or climatic shifts."
            ]

        return {
            "habitation_id": habitation_id,
            "risk_score": round(risk_score, 2),
            "category": category,
            "color_code": color_code,
            "action_timeline": action_timeline,
            "reasons": reasons
        }
