"""
Relocation Optimizer — Multi-Criteria Greedy Assignment Engine.

Algorithm:
1. Sort affected habitations by relocation urgency (Immediate > Short-Term > Medium-Term > In-Situ > Monitor),
   then by risk score (RPI) descending.
2. Exclude unsafe sites (pre-ranking safety disqualification).
3. Exclude infeasible sites (zero capacity, out of bounds).
4. Check remaining capacity (8-dimensional people-supported headroom).
5. Calculate dynamic ranking score relative to source habitation coordinates.
6. Assign habitation population to the highest-scoring safe site with sufficient capacity.
7. Update remaining site capacity.
8. Continue until all habitations are assigned or no capacity remains.

Diagnostic Output Schema:
- habitation: {"id": ..., "name": ...}
- population_requiring_relocation: int
- recommended_site: {"id": ..., "name": ...} or None
- population_assigned: int
- remaining_unassigned_population: int
- site_capacity_before: int
- site_capacity_after: int
- distance_km: float
- suitability_score: float
- reason_for_selection: str
- sites_rejected_and_reasons: list of {"site_id": ..., "site_name": ..., "rejection_reason": ...}
- urgency: str
- capacity_deficit: int
"""
from typing import Dict, Any, List, Optional
from app.engines.relocation.safe_site import SiteScorer
from app.engines.relocation.carrying_capacity import CapacityCalculator
from app.engines.relocation.necessity import NecessityEngine


class RelocationOptimizer:
    """
    Stateless, deterministic greedy assignment optimizer operating on actual backend data.
    """

    @staticmethod
    def run_optimization(habitations: List[Dict[str, Any]], candidate_sites: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Executes priority-based greedy relocation assignment.
        - habitations: List of dicts with (id, name, population, risk_score, latitude, longitude)
        - candidate_sites: List of dicts representing candidate site attributes
        """
        # Step 1: Classify and Sort Habitations by Relocation Urgency
        classified_habitations = []
        for hab in habitations:
            rpi = hab.get("risk_score")
            if rpi is None:
                rpi = hab.get("rpi", 0.0)
            necessity = NecessityEngine.evaluate_necessity(hab["id"], float(rpi or 0.0))

            hab_entry = dict(hab)
            hab_entry["risk_score"] = float(rpi or 0.0)
            hab_entry["necessity_category"] = necessity["category"]

            priority_weight = {
                "Immediate": 5,
                "Short-Term": 4,
                "Medium-Term": 3,
                "In-Situ": 2,
                "Monitor": 1
            }.get(necessity["category"], 0)

            hab_entry["priority_weight"] = priority_weight
            classified_habitations.append(hab_entry)

        # Sort habitations: Highest urgency category first, then highest risk score descending, then population
        classified_habitations.sort(
            key=lambda x: (x["priority_weight"], x["risk_score"], x.get("population", 0)),
            reverse=True
        )

        # Step 2 & 3: Initial Candidate Site Evaluation & Capacity Initialization
        site_capacities = {}
        initial_capacities = {}
        site_safety_map = {}
        site_disqualification_map = {}

        for raw_s in candidate_sites:
            s_id = raw_s.get("site_id") or raw_s.get("id", "unknown")
            s_name = raw_s.get("site_name") or raw_s.get("name", f"Site {s_id}")

            # Check intrinsic safety (hazard exposure, slope > 25)
            scored = SiteScorer.calculate_score(raw_s)
            site_safety_map[s_id] = scored["is_safe"]
            site_disqualification_map[s_id] = scored["disqualifying_conditions"]

            if scored["is_safe"]:
                # Check database capacity first via 8-dimensional Carrying Capacity Engine
                cap_analysis = CapacityCalculator.analyze_capacity(s_id, 0)
                feasible_cap = cap_analysis.get("feasible_additional_capacity", 0)

                factors = raw_s.get("factors") if isinstance(raw_s.get("factors"), dict) else raw_s

                # If site is not in DB or explicit people capacity provided
                if feasible_cap == 0:
                    if raw_s.get("feasible_capacity") is not None:
                        feasible_cap = int(raw_s["feasible_capacity"])
                    elif raw_s.get("capacity_people") is not None:
                        feasible_cap = int(raw_s["capacity_people"])
                    elif raw_s.get("area_capacity") is not None and raw_s.get("area_capacity") > 100:
                        feasible_cap = int(raw_s["area_capacity"])
                    elif isinstance(factors, dict) and factors.get("area_capacity") is not None and factors.get("area_capacity") > 100:
                        feasible_cap = int(factors["area_capacity"])

                # Strictly honor explicit zero capacity
                if raw_s.get("area_capacity") == 0 or raw_s.get("feasible_capacity") == 0:
                    feasible_cap = 0
                if isinstance(factors, dict) and factors.get("area_capacity") == 0:
                    feasible_cap = 0

                site_capacities[s_id] = feasible_cap
                initial_capacities[s_id] = feasible_cap
            else:
                site_capacities[s_id] = 0
                initial_capacities[s_id] = 0

        # Steps 4 - 8: Greedy Assignment Loop
        assignments = []
        unassigned = []

        for hab in classified_habitations:
            hab_id = hab["id"]
            hab_name = hab["name"]
            pop = int(hab.get("population", 0))
            urgency = hab["necessity_category"]

            origin_coords = None
            if "latitude" in hab and "longitude" in hab and hab["latitude"] is not None and hab["longitude"] is not None:
                origin_coords = {"latitude": float(hab["latitude"]), "longitude": float(hab["longitude"])}

            # Evaluate all candidate sites for this specific habitation
            scored_candidates = []
            rejection_reasons = []

            for raw_s in candidate_sites:
                s_id = raw_s.get("site_id") or raw_s.get("id", "unknown")
                s_name = raw_s.get("site_name") or raw_s.get("name", f"Site {s_id}")

                # Check safety
                scored = SiteScorer.calculate_score(raw_s, origin_coords=origin_coords)
                is_safe = scored["is_safe"]
                disq_conds = scored["disqualifying_conditions"]

                if not is_safe:
                    rejection_reasons.append({
                        "site_id": s_id,
                        "site_name": s_name,
                        "rejection_reason": f"Unsafe site: {'; '.join(disq_conds)}"
                    })
                    continue

                # Check feasible initial capacity
                initial_cap = initial_capacities.get(s_id, 0)
                if initial_cap <= 0:
                    rejection_reasons.append({
                        "site_id": s_id,
                        "site_name": s_name,
                        "rejection_reason": "Zero capacity: Site has no available infrastructure headroom."
                    })
                    continue

                scored_candidates.append(scored)

            # Sort candidate sites by overall suitability score descending
            scored_candidates.sort(key=lambda s: s["overall_suitability_score"], reverse=True)

            assigned_record = None

            for site in scored_candidates:
                s_id = site["site_id"]
                s_name = site["site_name"]
                avail = site_capacities.get(s_id, 0)

                # Capacity Check
                if avail >= pop:
                    cap_before = avail
                    cap_after = avail - pop
                    site_capacities[s_id] = cap_after

                    dist_val = site.get("distance_km")
                    dist_text = f"{dist_val} km away" if dist_val is not None else "nearby"

                    # Record why other lower-ranked candidates weren't selected
                    for other in scored_candidates:
                        other_id = other["site_id"]
                        if other_id != s_id:
                            rejection_reasons.append({
                                "site_id": other_id,
                                "site_name": other["site_name"],
                                "rejection_reason": f"Alternative option: Lower suitability score ({other['overall_suitability_score']}/100 vs {site['overall_suitability_score']}/100 for {s_name})."
                            })

                    assigned_record = {
                        "habitation": {"id": hab_id, "name": hab_name},
                        "population_requiring_relocation": pop,
                        "recommended_site": {"id": s_id, "name": s_name},
                        "population_assigned": pop,
                        "remaining_unassigned_population": 0,
                        "site_capacity_before": cap_before,
                        "site_capacity_after": cap_after,
                        "distance_km": dist_val,
                        "suitability_score": site["overall_suitability_score"],
                        "reason_for_selection": (
                            f"Assigned to {s_name} ({dist_text}, Suitability: {site['overall_suitability_score']}/100). "
                            f"Site provides verified safety clearance and sufficient capacity ({cap_before:,} → {cap_after:,} remaining)."
                        ),
                        "sites_rejected_and_reasons": rejection_reasons,
                        "urgency": urgency,
                        "capacity_deficit": 0,
                        # Backward-compatibility flat aliases
                        "habitation_id": hab_id,
                        "habitation_name": hab_name,
                        "population": pop,
                        "necessity": urgency,
                        "assigned_site_id": s_id,
                        "assigned_site_name": s_name,
                        "reason": (
                            f"Assigned to {s_name} ({dist_text}, Suitability: {site['overall_suitability_score']}/100). "
                            f"Site has sufficient feasible capacity (Remaining: {cap_after:,} people)."
                        ),
                    }
                    assignments.append(assigned_record)
                    break
                else:
                    # Site didn't have enough capacity
                    rejection_reasons.append({
                        "site_id": s_id,
                        "site_name": s_name,
                        "rejection_reason": f"Insufficient capacity: Required {pop:,} people, but only {avail:,} people available ({pop - avail:,} deficit)."
                    })

            if not assigned_record:
                # Could not assign to any candidate site
                unassigned_record = {
                    "habitation": {"id": hab_id, "name": hab_name},
                    "population_requiring_relocation": pop,
                    "recommended_site": None,
                    "population_assigned": 0,
                    "remaining_unassigned_population": pop,
                    "site_capacity_before": 0,
                    "site_capacity_after": 0,
                    "distance_km": None,
                    "suitability_score": 0.0,
                    "reason_for_selection": "Failed to assign: No safe candidate sites have sufficient available capacity to absorb this population.",
                    "sites_rejected_and_reasons": rejection_reasons,
                    "urgency": urgency,
                    "capacity_deficit": pop,
                    # Backward-compatibility flat aliases
                    "habitation_id": hab_id,
                    "habitation_name": hab_name,
                    "population": pop,
                    "necessity": urgency,
                    "assigned_site_id": None,
                    "assigned_site_name": None,
                    "reason": "Failed to assign: No safe candidate sites have sufficient available capacity to absorb this population.",
                }
                unassigned.append(unassigned_record)

        total_relocated = sum(a["population_assigned"] for a in assignments)
        total_deficit = sum(u["capacity_deficit"] for u in unassigned)
        remaining_site_capacities = [
            {"site_id": s_id, "initial_capacity": initial_capacities[s_id], "remaining_capacity": site_capacities[s_id]}
            for s_id in site_capacities
        ]

        return {
            "summary": {
                "total_habitations": len(habitations),
                "assigned": len(assignments),
                "unassigned": len(unassigned),
                "total_relocated_population": total_relocated,
                "total_capacity_deficit": total_deficit,
                "safe_sites_available": sum(1 for v in site_safety_map.values() if v),
            },
            "assignments": assignments,
            "unassigned": unassigned,
            "site_capacity_summary": remaining_site_capacities,
        }
