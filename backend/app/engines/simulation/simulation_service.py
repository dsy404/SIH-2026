"""
Live Scenario Simulation Engine — Phase 9.
DEMO LIVE-UPDATE SIMULATION.
Simulates environmental shifts (e.g. rainfall surges) non-destructively without mutating canonical DB.
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.db.repository import Repository
from app.engines.relocation.necessity import NecessityEngine
from app.engines.relocation.optimizer import RelocationOptimizer
from app.engines.alert_engine import AlertEngine



class SimulationService:
    """
    Simulation Engine calculating dynamic hazard, RPI risk, urgency, and optimizer re-allocations.
    Purely in-memory: Never permanently overwrites production database records.
    """

    DEFAULT_BASELINE_RAINFALL = 120.0  # mm/day
    DEFAULT_SCENARIO_RAINFALL = 210.0  # mm/day

    @staticmethod
    def run_scenario_simulation(
        session: Session,
        baseline_rainfall_mm: float = 120.0,
        scenario_rainfall_mm: float = 210.0
    ) -> Dict[str, Any]:
        """
        Runs non-destructive scenario simulation across all database habitations.
        Compares baseline environmental conditions against scenario conditions.
        """
        habitations = Repository.get_all_habitations(session)
        sites = Repository.get_all_sites(session)
        site_dicts = [Repository.site_to_dict(s) for s in sites]

        baseline_hab_dicts = []
        scenario_hab_dicts = []

        rainfall_delta = scenario_rainfall_mm - baseline_rainfall_mm

        # ── Step 1: Calculate Habitation-Level Baseline & Scenario Risk ───
        for hab in habitations:
            ra = hab.risk_assessment
            nec = hab.necessity

            base_h = ra.hazard_score if ra else 45.0
            base_e = ra.exposure_score if ra else 50.0
            base_v = ra.vulnerability_score if ra else 50.0
            base_rpi = ra.rpi if ra else 48.0
            base_category = ra.risk_category if ra else "Moderate"
            base_urgency = nec.category if nec else "Monitor"

            elevation = hab.elevation if hab.elevation is not None else 100.0
            slope = hab.slope if hab.slope is not None else 8.0

            # ── Scenario Hazard Surge Modeling ────────────────────────
            # Lower elevation creates higher flood inundation factor
            elevation_factor = max(0.2, (250.0 - min(250.0, elevation)) / 250.0)
            # Steep slope creates landslide slip acceleration
            slope_factor = 1.0 + (min(45.0, slope) / 45.0) * 0.5

            if rainfall_delta >= 0:
                # Rainfall surge increases hazard
                hazard_surge = (rainfall_delta / 3.5) * elevation_factor * slope_factor
                sim_h = min(100.0, base_h + hazard_surge)
            else:
                # Rainfall relief decreases hazard
                hazard_relief = (abs(rainfall_delta) / 5.0) * elevation_factor
                sim_h = max(10.0, base_h - hazard_relief)

            sim_h = round(sim_h, 1)

            # Recalculate Scenario RPI (IPCC 40% Hazard, 30% Exposure, 30% Vulnerability)
            sim_rpi = round((sim_h * 0.40) + (base_e * 0.30) + (base_v * 0.30), 1)
            sim_rpi = min(100.0, max(0.0, sim_rpi))

            if sim_rpi >= 76.0:
                sim_category = "Critical / Red Zone Candidate"
            elif sim_rpi >= 56.0:
                sim_category = "High"
            elif sim_rpi >= 31.0:
                sim_category = "Moderate"
            else:
                sim_category = "Low"

            # Recalculate Scenario Relocation Necessity Tier
            nec_eval = NecessityEngine.evaluate_necessity(hab.id, sim_rpi)
            sim_urgency = nec_eval["category"]

            # Store baseline payload for optimizer
            b_item = Repository.habitation_to_dict(hab)
            b_item["risk_score"] = base_rpi
            b_item["hazard_score"] = base_h
            b_item["risk_category"] = base_category
            b_item["urgency"] = base_urgency
            baseline_hab_dicts.append(b_item)

            # Store scenario payload for optimizer
            s_item = Repository.habitation_to_dict(hab)
            s_item["risk_score"] = sim_rpi
            s_item["hazard_score"] = sim_h
            s_item["risk_category"] = sim_category
            s_item["urgency"] = sim_urgency
            scenario_hab_dicts.append(s_item)

        # ── Step 2: Run In-Memory Optimizer on Both Scenarios ───────────
        baseline_opt = RelocationOptimizer.run_optimization(baseline_hab_dicts, site_dicts)
        scenario_opt = RelocationOptimizer.run_optimization(scenario_hab_dicts, site_dicts)

        baseline_assignment_map = {
            a["habitation_id"]: a for a in baseline_opt.get("assignments", [])
        }
        for u in baseline_opt.get("unassigned", []):
            baseline_assignment_map[u["habitation_id"]] = u

        scenario_assignment_map = {
            a["habitation_id"]: a for a in scenario_opt.get("assignments", [])
        }
        for u in scenario_opt.get("unassigned", []):
            scenario_assignment_map[u["habitation_id"]] = u

        # ── Step 3: Compute Differential Comparison per Habitation ─────
        diff_records = []
        hazard_changed_count = 0
        risk_category_changed_count = 0
        urgency_changed_count = 0
        site_changed_count = 0

        baseline_red_zones = sum(1 for h in baseline_hab_dicts if h["risk_score"] >= 76.0 or h["urgency"] in ("Immediate", "Short-Term"))
        scenario_red_zones = sum(1 for h in scenario_hab_dicts if h["risk_score"] >= 76.0 or h["urgency"] in ("Immediate", "Short-Term"))

        baseline_affected_pop = sum(h["population"] for h in baseline_hab_dicts if h["urgency"] in ("Immediate", "Short-Term", "Medium-Term"))
        scenario_affected_pop = sum(h["population"] for h in scenario_hab_dicts if h["urgency"] in ("Immediate", "Short-Term", "Medium-Term"))

        for idx, hab in enumerate(habitations):
            b = baseline_hab_dicts[idx]
            s = scenario_hab_dicts[idx]

            b_alloc = baseline_assignment_map.get(hab.id, {})
            s_alloc = scenario_assignment_map.get(hab.id, {})

            b_site_name = b_alloc.get("assigned_site_name") or (b_alloc.get("recommended_site") or {}).get("name") or "UNASSIGNED"
            s_site_name = s_alloc.get("assigned_site_name") or (s_alloc.get("recommended_site") or {}).get("name") or "UNASSIGNED"

            h_diff = round(s["hazard_score"] - b["hazard_score"], 1)
            rpi_diff = round(s["risk_score"] - b["risk_score"], 1)

            h_changed = abs(h_diff) >= 1.0
            rc_changed = b["risk_category"] != s["risk_category"]
            urg_changed = b["urgency"] != s["urgency"]
            site_changed = b_site_name != s_site_name

            if h_changed:
                hazard_changed_count += 1
            if rc_changed:
                risk_category_changed_count += 1
            if urg_changed:
                urgency_changed_count += 1
            if site_changed:
                site_changed_count += 1

            record = {
                "habitation_id": hab.id,
                "habitation_name": hab.name,
                "population": hab.population,
                "elevation": hab.elevation,
                "slope": hab.slope,
                "baseline": {
                    "hazard_score": b["hazard_score"],
                    "rpi": b["risk_score"],
                    "risk_category": b["risk_category"],
                    "urgency": b["urgency"],
                    "recommended_site": b_site_name,
                },
                "scenario": {
                    "hazard_score": s["hazard_score"],
                    "rpi": s["risk_score"],
                    "risk_category": s["risk_category"],
                    "urgency": s["urgency"],
                    "recommended_site": s_site_name,
                },
                "difference": {
                    "hazard_delta": h_diff,
                    "rpi_delta": rpi_diff,
                    "hazard_changed": h_changed,
                    "risk_category_changed": rc_changed,
                    "urgency_changed": urg_changed,
                    "site_changed": site_changed,
                    "is_impacted": h_changed or rc_changed or urg_changed or site_changed,
                }
            }
            diff_records.append(record)

        # Sort diff records: Most impacted/escalated first
        diff_records.sort(
            key=lambda r: (
                r["difference"]["risk_category_changed"],
                r["difference"]["urgency_changed"],
                r["difference"]["site_changed"],
                r["difference"]["rpi_delta"]
            ),
            reverse=True
        )

        # Trigger Simulation Escalation Alert if risk surged significantly
        red_zone_delta = scenario_red_zones - baseline_red_zones
        if rainfall_delta >= 30 and (red_zone_delta > 0 or risk_category_changed_count > 0):
            try:
                escalated_names = [
                    r["habitation_name"] for r in diff_records
                    if r["difference"]["risk_category_changed"] or r["difference"]["urgency_changed"]
                ]
                AlertEngine.trigger_simulation_escalation(
                    session,
                    rainfall_surge_mm=rainfall_delta,
                    red_zone_delta=max(red_zone_delta, 1),
                    escalated_hab_names=escalated_names,
                    source_event="LIVE_SCENARIO_SIMULATION"
                )
                session.commit()
            except Exception as e:
                print(f"[AlertEngine Hook Warning] Simulation alert error: {e}")

        return {
            "mode": "DEMO LIVE-UPDATE SIMULATION",
            "is_simulation": True,
            "saved_to_db": False,
            "parameters": {
                "baseline_rainfall_mm": baseline_rainfall_mm,
                "scenario_rainfall_mm": scenario_rainfall_mm,
                "rainfall_surge_mm": round(rainfall_delta, 1),
            },
            "summary": {
                "total_habitations": len(habitations),
                "baseline_red_zones": baseline_red_zones,
                "scenario_red_zones": scenario_red_zones,
                "red_zone_delta": scenario_red_zones - baseline_red_zones,
                "baseline_affected_population": baseline_affected_pop,
                "scenario_affected_population": scenario_affected_pop,
                "affected_population_delta": scenario_affected_pop - baseline_affected_pop,
                "habitations_hazard_changed": hazard_changed_count,
                "habitations_risk_category_changed": risk_category_changed_count,
                "habitations_urgency_changed": urgency_changed_count,
                "habitations_site_reassigned": site_changed_count,
                "scenario_total_capacity_deficit": scenario_opt.get("summary", {}).get("total_capacity_deficit", 0),
            },
            "comparison": diff_records,
            "scenario_optimizer_summary": scenario_opt.get("summary", {}),
        }
