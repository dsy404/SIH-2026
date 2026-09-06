"""
Automated Test Suite for Phase 6: Safe-Site Suitability + Carrying Capacity.

Verifies:
1. Dynamic Safe-Site Evaluation across at least 3 candidate sites without hardcoded winners.
2. Pre-ranking exclusion of unsafe/disqualified candidate sites (hazard exposure, slope > 25°).
3. Incompatible infrastructure unit conversion into people-supported equivalents (no raw population subtractions).
4. Dynamic binding bottleneck identification (feasible capacity = min across all 8 dimensions).
5. RelocationOptimizer dynamic assignment respecting safe-site suitability and binding people headroom.
6. API endpoint contracts:
   - /api/safe-sites/compare
   - /api/capacity/analyze (including mandatory planning disclaimer)
"""
import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.db.database import get_session_factory
from app.db.repository import Repository
from app.engines.relocation.safe_site import SiteScorer
from app.engines.relocation.carrying_capacity import CapacityCalculator
from app.engines.relocation.optimizer import RelocationOptimizer


class SafeSiteAndCapacityTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.Session = get_session_factory()
        self.session = self.Session()

    def tearDown(self):
        self.session.close()

    def test_01_dynamic_evaluation_multiple_candidate_sites(self):
        """Test dynamic suitability scoring across at least 3 candidate sites without hardcoded bias."""
        sites = Repository.get_all_sites(self.session)
        self.assertGreaterEqual(len(sites), 3, "Database must have at least 3 candidate sites for evaluation")

        site_dicts = [Repository.site_to_dict(s) for s in sites[:3]]

        # Evaluate without origin
        res_generic = SiteScorer.compare_sites(site_dicts)
        self.assertEqual(len(res_generic), 3)
        for s in res_generic:
            self.assertIn("overall_suitability_score", s)
            self.assertIn("component_scores", s)
            self.assertIn("advantages", s)
            self.assertIn("trade_offs", s)
            self.assertIn("reasoning", s)
            self.assertIn("confidence", s)
            self.assertTrue(s["is_safe"])
            self.assertFalse(s["disqualified"])

        # Evaluate with origin near Site A (SITE001 coordinates: ~25.03, 82.03)
        origin_near_a = {"latitude": 25.035, "longitude": 82.035}
        scored_near_a = SiteScorer.compare_sites(site_dicts, origin_coords=origin_near_a)

        # Evaluate with origin far from Site A and near another site (~25.11, 82.11)
        origin_far_a = {"latitude": 25.115, "longitude": 82.115}
        scored_far_a = SiteScorer.compare_sites(site_dicts, origin_coords=origin_far_a)

        # Proximity scores and distances must differ dynamically
        site_a_near = next(s for s in scored_near_a if s["site_id"] == "SITE001")
        site_a_far = next(s for s in scored_far_a if s["site_id"] == "SITE001")
        self.assertLess(site_a_near["distance_km"], site_a_far["distance_km"])
        self.assertGreater(
            site_a_near["component_scores"]["proximity_to_origin"],
            site_a_far["component_scores"]["proximity_to_origin"]
        )

    def test_02_safety_pre_ranking_exclusion_of_unsafe_sites(self):
        """Unsafe sites (in hazard zone, buffer < 300m, or slope > 25°) must be disqualified and excluded before ranking."""
        test_candidates = [
            {
                "id": "SAFE_1",
                "name": "High Plateau Safe Site",
                "latitude": 23.70,
                "longitude": 85.50,
                "distance_to_hazard": 85.0,
                "slope": 3.5,
                "water_access": 75.0,
                "road_accessibility": 80.0,
            },
            {
                "id": "UNSAFE_FLOOD",
                "name": "River Basin Hazard Zone Site",
                "latitude": 23.60,
                "longitude": 85.40,
                "distance_to_hazard": 10.0,  # inside hazard buffer
                "in_hazard_zone": True,
                "slope": 2.0,
                "water_access": 80.0,
                "road_accessibility": 80.0,
            },
            {
                "id": "UNSAFE_SLOPE",
                "name": "Steep Escarpment Site",
                "latitude": 23.80,
                "longitude": 85.60,
                "distance_to_hazard": 90.0,
                "slope": 31.5,  # Excessive slope > 25 degrees
                "water_access": 70.0,
                "road_accessibility": 70.0,
            },
            {
                "id": "UNSAFE_NO_WATER",
                "name": "Arid Ridge Site",
                "latitude": 23.75,
                "longitude": 85.55,
                "distance_to_hazard": 80.0,
                "slope": 5.0,
                "water_access": 0.0,  # Zero water access
                "road_accessibility": 75.0,
            }
        ]

        detailed = SiteScorer.compare_sites_detailed(test_candidates)
        safe_ranked = detailed["ranked_safe_sites"]
        disqualified = detailed["disqualified_sites"]

        # Only 1 site should be eligible and safe
        self.assertEqual(len(safe_ranked), 1)
        self.assertEqual(safe_ranked[0]["site_id"], "SAFE_1")
        self.assertTrue(safe_ranked[0]["is_safe"])

        # 3 sites must be disqualified
        self.assertEqual(len(disqualified), 3)
        disq_ids = {d["site_id"] for d in disqualified}
        self.assertEqual(disq_ids, {"UNSAFE_FLOOD", "UNSAFE_SLOPE", "UNSAFE_NO_WATER"})

        # Check disqualifying conditions
        flood_site = next(d for d in disqualified if d["site_id"] == "UNSAFE_FLOOD")
        self.assertTrue(any("hazard" in c.lower() for c in flood_site["disqualifying_conditions"]))

        slope_site = next(d for d in disqualified if d["site_id"] == "UNSAFE_SLOPE")
        self.assertTrue(any("slope" in c.lower() for c in slope_site["disqualifying_conditions"]))

        water_site = next(d for d in disqualified if d["site_id"] == "UNSAFE_NO_WATER")
        self.assertTrue(any("water" in c.lower() for c in water_site["disqualifying_conditions"]))

    def test_03_capacity_unit_conversion_to_people(self):
        """Do NOT subtract population from incompatible units; verify conversion to people-supported capacity."""
        # Test unit conversion helper functions
        # Housing: 100 dwellings * 4.5 = 450 people
        self.assertEqual(CapacityCalculator.convert_to_people("Housing", 100), 450)
        # Land: 10 hectares * 150 = 1,500 people
        self.assertEqual(CapacityCalculator.convert_to_people("Land", 10), 1500)
        # Water: 70 kL/day = 70,000 L / 70 LPCD = 1,000 people
        self.assertEqual(CapacityCalculator.convert_to_people("Water", 70), 1000)
        # Healthcare: 4 clinic beds * 250 = 1,000 people
        self.assertEqual(CapacityCalculator.convert_to_people("Healthcare", 4), 1000)
        # Education: 200 classroom seats * 5 = 1,000 people
        self.assertEqual(CapacityCalculator.convert_to_people("Education", 200), 1000)
        # Electricity: 350 kW / 0.35 kW/person = 1,000 people
        self.assertEqual(CapacityCalculator.convert_to_people("Electricity", 350), 1000)

        # Full site analysis on SITE001
        analysis = CapacityCalculator.analyze_capacity("SITE001", 800)
        self.assertEqual(len(analysis["dimensions"]), 8, "Must evaluate all 8 standardized dimensions")

        for d in analysis["dimensions"]:
            self.assertIn("raw_unit", d)
            self.assertIn("raw_max_capacity", d)
            self.assertIn("raw_current_utilization", d)
            self.assertIn("total_supported_population", d)
            self.assertIn("existing_population", d)
            self.assertIn("additional_capacity", d)
            self.assertIn("remaining_capacity", d)
            self.assertIn("conversion_standard", d)
            # Verify additional capacity is non-negative and derived from people capacity
            self.assertGreaterEqual(d["total_supported_population"], d["existing_population"])
            self.assertEqual(d["additional_capacity"], d["total_supported_population"] - d["existing_population"])

    def test_04_dynamic_bottleneck_identification(self):
        """Feasible site capacity must equal the minimum additional people capacity across all 8 dimensions."""
        for site_id in ["SITE001", "SITE002", "SITE003"]:
            analysis = CapacityCalculator.analyze_capacity(site_id, 0)
            dims = analysis["dimensions"]
            min_dim = min(dims, key=lambda d: d["additional_capacity"])

            self.assertEqual(analysis["feasible_additional_capacity"], min_dim["additional_capacity"])
            self.assertEqual(analysis["critical_bottleneck"], min_dim["dimension"])
            self.assertIn(min_dim["dimension"], analysis["capacity_explanation"])

    def test_05_optimizer_dynamic_assignment_and_capacity_respect(self):
        """RelocationOptimizer assigns habitations without hardcoded winners, respecting dynamic suitability & capacities."""
        habitations = [
            {"id": "H1", "name": "North Hamlet", "population": 800, "risk_score": 85.0, "latitude": 25.04, "longitude": 82.04},
            {"id": "H2", "name": "East Village", "population": 600, "risk_score": 75.0, "latitude": 25.10, "longitude": 82.10},
        ]
        sites = [Repository.site_to_dict(s) for s in Repository.get_all_sites(self.session)]

        result = RelocationOptimizer.run_optimization(habitations, sites)
        self.assertEqual(result["summary"]["total_habitations"], 2)
        self.assertEqual(result["summary"]["assigned"], 2)
        self.assertEqual(result["summary"]["unassigned"], 0)

        for a in result["assignments"]:
            self.assertIsNotNone(a["assigned_site_id"])
            self.assertIsNotNone(a["assigned_site_name"])
            self.assertIn("Suitability", a["reason"])
            self.assertGreater(a["suitability_score"], 50.0)

    def test_06_api_endpoints_and_mandatory_disclaimer(self):
        """Verify /api/safe-sites/compare and /api/capacity/analyze endpoints and required disclaimer."""
        # 1. Safe sites compare endpoint
        res = self.client.get('/api/safe-sites/compare?habitation_id=HAB001')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("ranked_safe_sites", data)
        self.assertIn("disqualified_sites", data)
        self.assertGreaterEqual(len(data["ranked_safe_sites"]), 3)

        top_site = data["ranked_safe_sites"][0]
        self.assertIn("overall_suitability_score", top_site)
        self.assertIn("component_scores", top_site)
        self.assertIn("advantages", top_site)
        self.assertIn("trade_offs", top_site)

        # 2. Capacity analyze endpoint
        cap_res = self.client.get('/api/capacity/analyze?site_id=SITE001&incoming_population=1000')
        self.assertEqual(cap_res.status_code, 200)
        cap_data = cap_res.get_json()
        self.assertEqual(cap_data["site_id"], "SITE001")
        self.assertEqual(len(cap_data["dimensions"]), 8)
        self.assertIn("critical_bottleneck", cap_data)
        self.assertIn("feasible_additional_capacity", cap_data)

        # Mandatory disclaimer verification
        self.assertEqual(cap_data["disclaimer"], "Planning estimate — not legally certified carrying capacity.")


if __name__ == '__main__':
    unittest.main()
