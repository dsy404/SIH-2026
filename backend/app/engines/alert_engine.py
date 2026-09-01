"""
Alert Engine — Rule-Based Alert Generator for Disaster Relocation DSS

Evaluates habitation data against risk thresholds and generates alerts
and notifications. Can be triggered on-demand via API or after data ingestion.
"""

from __future__ import annotations
from typing import List, Dict, Any
from datetime import datetime
import uuid


# ─── Alert Rules ──────────────────────────────────────────────────────
# Each rule has a condition function and metadata for the alert it generates.

ALERT_RULES = [
    {
        "id": "RULE_CRITICAL_RPI",
        "name": "Critical RPI Threshold",
        "description": "Habitation RPI exceeds critical threshold (>75)",
        "severity": "critical",
        "category": "risk",
        "check": lambda hab: hab.get("rpi", 0) > 75,
        "message": lambda hab: f"CRITICAL: {hab['name']} has an RPI of {hab['rpi']:.1f} — immediate relocation assessment required.",
    },
    {
        "id": "RULE_HIGH_RPI",
        "name": "High RPI Threshold",
        "description": "Habitation RPI exceeds high threshold (>50)",
        "severity": "high",
        "category": "risk",
        "check": lambda hab: 50 < hab.get("rpi", 0) <= 75,
        "message": lambda hab: f"HIGH RISK: {hab['name']} has an RPI of {hab['rpi']:.1f} — urgent relocation planning recommended.",
    },
    {
        "id": "RULE_FLOOD_ZONE",
        "name": "Flood Zone Exposure",
        "description": "Habitation is inside a high-severity flood zone",
        "severity": "critical",
        "category": "hazard",
        "check": lambda hab: hab.get("hazard_score", 0) >= 100,
        "message": lambda hab: f"FLOOD ALERT: {hab['name']} is located inside a HIGH severity flood zone (Hazard Score: {hab['hazard_score']}).",
    },
    {
        "id": "RULE_LOW_ELEVATION",
        "name": "Low Elevation Warning",
        "description": "Habitation elevation below 100m — high flood exposure",
        "severity": "warning",
        "category": "exposure",
        "check": lambda hab: hab.get("elevation") is not None and float(hab.get("elevation", 999)) < 100,
        "message": lambda hab: f"LOW ELEVATION: {hab['name']} is at {hab.get('elevation')}m elevation — significantly increased flood exposure.",
    },
    {
        "id": "RULE_STEEP_SLOPE",
        "name": "Steep Slope Warning",
        "description": "Habitation slope exceeds 25° — severe landslide exposure",
        "severity": "warning",
        "category": "exposure",
        "check": lambda hab: hab.get("slope") is not None and float(hab.get("slope", 0)) > 25,
        "message": lambda hab: f"LANDSLIDE RISK: {hab['name']} has a slope of {hab.get('slope')}° — severe landslide exposure.",
    },
    {
        "id": "RULE_HIGH_POPULATION",
        "name": "High Population at Risk",
        "description": "Habitation with >1000 people in a risk zone",
        "severity": "high",
        "category": "vulnerability",
        "check": lambda hab: hab.get("population", 0) > 1000 and hab.get("rpi", 0) > 25,
        "message": lambda hab: f"POPULATION AT RISK: {hab['name']} has {hab.get('population')} residents in a risk zone (RPI: {hab.get('rpi', 0):.1f}).",
    },
    {
        "id": "RULE_OVERCROWDING",
        "name": "Overcrowding Alert",
        "description": "Household density exceeds 7 persons/household in risk zone",
        "severity": "warning",
        "category": "vulnerability",
        "check": lambda hab: (
            hab.get("population", 0) > 0
            and hab.get("households", 1) > 0
            and (hab.get("population", 0) / hab.get("households", 1)) > 7
            and hab.get("rpi", 0) > 25
        ),
        "message": lambda hab: f"OVERCROWDING: {hab['name']} has {hab.get('population', 0) / max(hab.get('households', 1), 1):.1f} persons/household — evacuation complexity increased.",
    },
]


class AlertEngine:
    """
    Rule-based engine that evaluates scored habitations against predefined
    thresholds and generates alerts + notifications.
    """

    def __init__(self):
        self.rules = ALERT_RULES

    def evaluate(self, scored_habitations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate all habitations against all rules.
        Returns a dict with generated alerts and notifications.
        """
        alerts = []
        notifications = []
        now = datetime.now().isoformat()

        for hab in scored_habitations:
            for rule in self.rules:
                try:
                    if rule["check"](hab):
                        alert_id = str(uuid.uuid4())[:8]
                        
                        alert = {
                            "id": f"ALR-{alert_id}",
                            "rule_id": rule["id"],
                            "rule_name": rule["name"],
                            "severity": rule["severity"],
                            "category": rule["category"],
                            "habitation_id": hab.get("id", "unknown"),
                            "habitation_name": hab.get("name", "Unknown"),
                            "message": rule["message"](hab),
                            "rpi": hab.get("rpi"),
                            "is_read": False,
                            "created_at": now,
                        }
                        alerts.append(alert)

                        notification = {
                            "id": f"NTF-{alert_id}",
                            "alert_id": alert["id"],
                            "title": rule["name"],
                            "message": rule["message"](hab),
                            "severity": rule["severity"],
                            "category": rule["category"],
                            "target_role": "administrator",
                            "is_read": False,
                            "created_at": now,
                        }
                        notifications.append(notification)

                except Exception:
                    continue

        # Sort by severity (critical first, then high, then warning)
        severity_order = {"critical": 0, "high": 1, "warning": 2, "info": 3}
        alerts.sort(key=lambda a: severity_order.get(a["severity"], 99))
        notifications.sort(key=lambda n: severity_order.get(n["severity"], 99))

        return {
            "alerts": alerts,
            "notifications": notifications,
            "summary": {
                "total_alerts": len(alerts),
                "critical": len([a for a in alerts if a["severity"] == "critical"]),
                "high": len([a for a in alerts if a["severity"] == "high"]),
                "warning": len([a for a in alerts if a["severity"] == "warning"]),
                "habitations_evaluated": len(scored_habitations),
                "rules_checked": len(self.rules),
                "generated_at": now,
            },
        }

    def get_rules(self) -> List[Dict[str, str]]:
        """Return metadata about all configured rules (without lambda functions)."""
        return [
            {
                "id": r["id"],
                "name": r["name"],
                "description": r["description"],
                "severity": r["severity"],
                "category": r["category"],
            }
            for r in self.rules
        ]
