"""
Safe-Site Suitability Engine.

Evaluates candidate relocation sites dynamically across multi-criteria factors:
- Hazard Safety (flood/landslide buffer, historical safety)
- Terrain (slope, elevation, soil stability)
- Road & Transport Accessibility
- Social Infrastructure (healthcare, education proximity)
- Utilities (water access, electricity/power)
- Proximity to Affected Habitation (dynamic distance)
- Land Area & Capacity

Pre-Ranking Safety Disqualification:
Unsafe sites (located within hazard buffer, slope > 25 degrees, or zero road/water)
are disqualified before ranking and excluded from relocation allocation.
"""
from typing import List, Dict, Any, Optional
import math


class SiteScorer:
    """
    Dynamic multi-criteria suitability evaluator with pre-ranking safety exclusion.
    """

    # Default configurable weights (sum = 100)
    DEFAULT_WEIGHTS = {
        "distance_to_hazard": 18,
        "historical_safety": 10,
        "terrain_slope": 12,
        "soil_stability": 10,
        "road_accessibility": 12,
        "healthcare_proximity": 8,
        "education_proximity": 7,
        "water_access": 10,
        "power_access": 5,
        "distance_to_origin": 8,
    }

    @staticmethod
    def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Computes great-circle distance between two coordinates in kilometers."""
        R = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(R * c, 2)

    @staticmethod
    def calculate_score(site_data: Dict[str, Any], origin_coords: Optional[Dict[str, float]] = None,
                        custom_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Calculates dynamic suitability score, component scores, advantages,
        trade-offs, and pre-ranking disqualifications for a candidate site.
        """
        factors = site_data.get("factors")
        if not factors or not isinstance(factors, dict):
            factors = site_data

        site_id = site_data.get("site_id") or site_data.get("id", "unknown")
        site_name = site_data.get("site_name") or site_data.get("name", "Unknown Site")

        weights = custom_weights or SiteScorer.DEFAULT_WEIGHTS

        # 1. Resolve coordinates
        lat = site_data.get("latitude")
        lon = site_data.get("longitude")
        coords = site_data.get("coordinates")
        if coords and isinstance(coords, (list, tuple)) and len(coords) >= 2:
            lon, lat = coords[0], coords[1]
        elif lat is None:
            lat = factors.get("latitude", 23.65)
            lon = factors.get("longitude", 85.55)

        # 2. Dynamic Proximity to Origin Calculation
        distance_km = None
        proximity_score = factors.get("distance_to_origin", 50)
        if origin_coords and "latitude" in origin_coords and "longitude" in origin_coords and lat and lon:
            distance_km = SiteScorer.haversine_distance_km(
                origin_coords["latitude"], origin_coords["longitude"], lat, lon
            )
            # Distance scoring: < 5km -> 95, 5-15km -> 80, 15-30km -> 60, > 30km -> decay
            if distance_km <= 5.0:
                proximity_score = 95.0
            elif distance_km <= 15.0:
                proximity_score = max(50.0, 95.0 - (distance_km - 5.0) * 1.5)
            elif distance_km <= 30.0:
                proximity_score = max(30.0, 80.0 - (distance_km - 15.0) * 2.0)
            else:
                proximity_score = max(10.0, 50.0 - (distance_km - 30.0) * 1.0)

        # 3. Disqualification Evaluation (Pre-ranking Safety Filter)
        disqualifying_conditions = []

        dist_hazard = factors.get("distance_to_hazard", 50)
        raw_slope = site_data.get("slope") if site_data.get("slope") is not None else factors.get("slope")
        slope_score = factors.get("terrain_slope", 50)
        water_access = factors.get("water_access", 50)
        road_access = factors.get("road_accessibility", 50)
        soil_stab = factors.get("soil_stability", 50)

        # Safety rule: Inside or immediately adjacent to hazard buffer
        if dist_hazard < 20.0 or site_data.get("in_hazard_zone") is True:
            disqualifying_conditions.append("Direct hazard exposure: Site is situated inside or within <300m of an active hazard zone.")

        # Safety rule: Steep slope (> 25 degrees)
        if (raw_slope is not None and raw_slope > 25.0) or slope_score < 15.0:
            disqualifying_conditions.append(f"Excessive slope ({raw_slope or '>25'}°): Terrain presents acute slope failure and construction hazards.")

        # Safety rule: Complete lack of potable water access
        if water_access <= 5.0:
            disqualifying_conditions.append("Critical utility failure: No viable water source or potable supply available.")

        # Safety rule: Inaccessible by transport
        if road_access <= 5.0:
            disqualifying_conditions.append("Severe transport isolation: Inaccessible by emergency and public transit roadways.")

        # Safety rule: Severe soil instability
        if soil_stab <= 10.0:
            disqualifying_conditions.append("Soil instability: Ground exhibits acute subsidence or liquefaction risk.")

        is_safe = len(disqualifying_conditions) == 0

        # 4. Multi-Criteria Score Calculation
        factor_values = {
            "distance_to_hazard": dist_hazard,
            "historical_safety": factors.get("historical_safety", 50),
            "terrain_slope": slope_score,
            "soil_stability": soil_stab,
            "road_accessibility": road_access,
            "healthcare_proximity": factors.get("healthcare_proximity", 50),
            "education_proximity": factors.get("education_proximity", 50),
            "water_access": water_access,
            "power_access": factors.get("power_access", 50),
            "distance_to_origin": proximity_score,
        }

        total_score = 0.0
        weight_sum = sum(weights.values())
        breakdown = {}

        for f_name, f_val in factor_values.items():
            f_weight = weights.get(f_name, 10.0)
            norm_val = max(0.0, min(100.0, float(f_val)))
            contribution = (norm_val * f_weight) / weight_sum
            total_score += contribution
            breakdown[f_name] = {
                "score": round(norm_val, 1),
                "weight": f_weight,
                "contribution": round(contribution, 2),
            }

        # 5. Component Scores Grouping
        component_scores = {
            "hazard_safety": round((factor_values["distance_to_hazard"] * 0.65 + factor_values["historical_safety"] * 0.35), 1),
            "terrain_suitability": round((factor_values["terrain_slope"] * 0.55 + factor_values["soil_stability"] * 0.45), 1),
            "accessibility": round(float(factor_values["road_accessibility"]), 1),
            "social_infrastructure": round((factor_values["healthcare_proximity"] * 0.5 + factor_values["education_proximity"] * 0.5), 1),
            "utilities": round((factor_values["water_access"] * 0.65 + factor_values["power_access"] * 0.35), 1),
            "proximity_to_origin": round(float(proximity_score), 1),
        }

        # 6. Advantages & Trade-Offs Discovery
        advantages = []
        trade_offs = []

        if factor_values["distance_to_hazard"] >= 75:
            advantages.append("Well-buffered from all regional riverine and landslide hazards.")
        if factor_values["road_accessibility"] >= 75:
            advantages.append("Excellent road connectivity enabling transit and emergency access.")
        if factor_values["water_access"] >= 75:
            advantages.append("Robust water supply network capable of absorbing expansion.")
        if factor_values["terrain_slope"] >= 75:
            advantages.append("Favorable flat to gentle topography with low grading costs.")
        if distance_km and distance_km <= 8.0:
            advantages.append(f"Close proximity to origin community ({distance_km:.1f} km), preserving social networks.")

        if factor_values["healthcare_proximity"] < 45:
            trade_offs.append("Limited hospital and emergency clinic proximity; requires local PHC development.")
        if factor_values["education_proximity"] < 45:
            trade_offs.append("Schools are beyond standard walking distance (requires student transport).")
        if factor_values["power_access"] < 45:
            trade_offs.append("Grid substation headroom is constrained; feeder extension needed.")
        if distance_km and distance_km > 20.0:
            trade_offs.append(f"Significant relocation distance ({distance_km:.1f} km) requiring livelihood transition support.")

        if not advantages:
            advantages.append("Meets minimum baseline environmental criteria for resettlement.")
        if not trade_offs:
            trade_offs.append("No critical socio-technical deficits identified.")

        # 7. Narrative Reasoning Synthesis
        if not is_safe:
            reasoning = f"Site disqualified from relocation consideration due to critical safety hazards: {'; '.join(disqualifying_conditions)}"
        elif total_score >= 80:
            reasoning = (f"{site_name} is highly recommended with a suitability score of {total_score:.1f}/100. "
                         f"It demonstrates superior hazard clearance ({component_scores['hazard_safety']}/100) and infrastructure readiness.")
        elif total_score >= 60:
            reasoning = (f"{site_name} is a viable relocation site (score {total_score:.1f}/100) offering acceptable safety, "
                         f"though secondary infrastructure investments ({trade_offs[0]}) are recommended.")
        else:
            reasoning = (f"{site_name} achieved a marginal suitability score of {total_score:.1f}/100. "
                         f"Significant capital outlay would be required to remediate infrastructure deficits.")

        confidence = "HIGH" if site_data.get("is_real") else "MEDIUM"

        return {
            "site_id": site_id,
            "site_name": site_name,
            "overall_suitability_score": round(total_score, 1),
            "total_score": round(total_score, 1),  # backward compatibility
            "is_safe": is_safe,
            "disqualified": not is_safe,
            "disqualifying_conditions": disqualifying_conditions,
            "component_scores": component_scores,
            "breakdown": breakdown,  # backward compatibility
            "advantages": advantages,
            "trade_offs": trade_offs,
            "reasoning": reasoning,
            "distance_km": distance_km,
            "confidence": confidence,
            "latitude": lat,
            "longitude": lon,
            "coordinates": [lon, lat] if lon is not None and lat is not None else None,
        }

    @staticmethod
    def compare_sites(sites: List[Dict[str, Any]], origin_coords: Optional[Dict[str, float]] = None,
                      exclude_unsafe: bool = True) -> List[Dict[str, Any]]:
        """
        Scores multiple candidate sites dynamically.
        By default, excludes unsafe / disqualified sites before ranking.
        """
        evaluated = [SiteScorer.calculate_score(s, origin_coords=origin_coords) for s in sites]

        if exclude_unsafe:
            safe_sites = [s for s in evaluated if s["is_safe"]]
            safe_sites.sort(key=lambda x: x["overall_suitability_score"], reverse=True)
            return safe_sites
        else:
            evaluated.sort(key=lambda x: (x["is_safe"], x["overall_suitability_score"]), reverse=True)
            return evaluated

    @staticmethod
    def compare_sites_detailed(sites: List[Dict[str, Any]], origin_coords: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Returns full diagnostic comparison including both ranked safe sites
        and partitioned disqualified sites with clear failure reasons.
        """
        evaluated = [SiteScorer.calculate_score(s, origin_coords=origin_coords) for s in sites]

        safe_sites = [s for s in evaluated if s["is_safe"]]
        safe_sites.sort(key=lambda x: x["overall_suitability_score"], reverse=True)

        disqualified_sites = [s for s in evaluated if not s["is_safe"]]
        disqualified_sites.sort(key=lambda x: x["overall_suitability_score"], reverse=True)

        return {
            "ranked_safe_sites": safe_sites,
            "disqualified_sites": disqualified_sites,
            "total_evaluated": len(sites),
            "safe_count": len(safe_sites),
            "disqualified_count": len(disqualified_sites),
        }
