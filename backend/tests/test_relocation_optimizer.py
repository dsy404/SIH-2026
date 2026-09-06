"""
Automated Test Suite for Phase 7: Relocation Optimizer.

Verifies:
1. Insufficient capacity handling (site rejected, deficit recorded).
2. Multiple habitations competing for one site (priority-based greedy assignment by urgency & risk).
3. Unsafe site exclusion (pre-ranking rejection, never assigned).
4. Site with zero capacity (properly excluded with diagnostic reason).
5. Population exceeding all available capacity (graceful deficit handling).
6. End-to-end API contracts (/api/optimizer/run, /api/optimizer/plan, /api/optimizer/vectors, /api/dashboard/action-plan).
"""
import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.db.database import get_session_factory
from app.db.repository import Repository
from app.engines.relocation.optimizer import RelocationOptimizer


class RelocationOptimizerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.Session = get_session_factory()
        self.session = self.Session()

    def tearDown(self):
        self.session.close()

    def test_01_insufficient_capacity_handling(self):
        """
        Habitation population exceeds candidate site capacity.
        Site must be rejected with clear capacity reason, and habitation left unassigned if no other site fits.
        """
        habitations = [
            {
                "id": "HAB_LARGE",
                "name": "Large Habitation",
                "population": 1200,
                "risk_score": 85.0,  # Immediate
                "latitude": 25.01,
                "longitude": 82.01,
            }
        ]

        # Site with feasible capacity of only 500 (less than 1200)
        candidate_sites = [
            {
                "site_id": "SITE_SMALL",
                "site_name": "Small Safe Site",
                "latitude": 25.05,
                "longitude": 82.05,
                "slope": 5.0,
                "factors": {
                    "distance_to_hazard": 85.0,
                    "historical_safety": 90,
                    "area_capacity": 500,
                    "road_accessibility": 80,
                    "healthcare_proximity": 80,
                    "education_proximity": 80,
                    "water_access": 80,
                    "power_access": 80,
                }
            }
        ]

        plan = RelocationOptimizer.run_optimization(habitations, candidate_sites)

        # Large habitation cannot fit into SITE_SMALL
        self.assertEqual(plan["summary"]["assigned"], 0)
        self.assertEqual(plan["summary"]["unassigned"], 1)
        self.assertEqual(plan["summary"]["total_capacity_deficit"], 1200)

        unassigned_record = plan["unassigned"][0]
        self.assertEqual(unassigned_record["habitation"]["id"], "HAB_LARGE")
        self.assertEqual(unassigned_record["remaining_unassigned_population"], 1200)
        self.assertEqual(unassigned_record["capacity_deficit"], 1200)
        self.assertIsNone(unassigned_record["recommended_site"])

        # Check diagnostic rejection reason
        rejected = unassigned_record["sites_rejected_and_reasons"]
        self.assertTrue(any("Insufficient capacity" in r["rejection_reason"] for r in rejected))

    def test_02_multiple_habitations_competing_priority_greedy(self):
        """
        Two habitations compete for a single safe site with limited capacity.
        Higher urgency habitation must be assigned first, consuming capacity.
        Second habitation should either be rejected for insufficient remaining capacity or assigned to an alternative.
        """
        habitations = [
            {
                "id": "HAB_URGENT",
                "name": "Urgent Habitation",
                "population": 300,
                "risk_score": 88.0,  # Immediate
                "latitude": 25.01,
                "longitude": 82.01,
            },
            {
                "id": "HAB_MODERATE",
                "name": "Moderate Habitation",
                "population": 300,
                "risk_score": 40.0,  # Medium-Term / In-Situ
                "latitude": 25.02,
                "longitude": 82.02,
            }
        ]

        # Site with capacity of 400 (enough for one of 300, but not both = 600)
        candidate_sites = [
            {
                "site_id": "SITE_LIMITED",
                "site_name": "Limited Capacity Site",
                "latitude": 25.05,
                "longitude": 82.05,
                "slope": 4.0,
                "factors": {
                    "distance_to_hazard": 90.0,
                    "historical_safety": 95,
                    "area_capacity": 400,
                    "road_accessibility": 85,
                    "healthcare_proximity": 85,
                    "education_proximity": 85,
                    "water_access": 85,
                    "power_access": 85,
                }
            }
        ]

        plan = RelocationOptimizer.run_optimization(habitations, candidate_sites)

        self.assertEqual(plan["summary"]["assigned"], 1)
        self.assertEqual(plan["summary"]["unassigned"], 1)

        assigned_record = plan["assignments"][0]
        # Urgent habitation wins the site
        self.assertEqual(assigned_record["habitation"]["id"], "HAB_URGENT")
        self.assertEqual(assigned_record["recommended_site"]["id"], "SITE_LIMITED")
        self.assertEqual(assigned_record["site_capacity_before"], 400)
        self.assertEqual(assigned_record["site_capacity_after"], 100)

        # Moderate habitation cannot fit into remaining 100 capacity
        unassigned_record = plan["unassigned"][0]
        self.assertEqual(unassigned_record["habitation"]["id"], "HAB_MODERATE")
        self.assertEqual(unassigned_record["capacity_deficit"], 300)

    def test_03_unsafe_site_pre_ranking_exclusion(self):
        """
        Candidate site is unsafe due to hazard exposure or excessive slope.
        Must be excluded before ranking and NEVER assigned, regardless of capacity.
        """
        habitations = [
            {
                "id": "HAB_TEST",
                "name": "Test Habitation",
                "population": 150,
                "risk_score": 80.0,
                "latitude": 25.01,
                "longitude": 82.01,
            }
        ]

        candidate_sites = [
            {
                "site_id": "SITE_UNSAFE_STEEP",
                "site_name": "Steep Hazardous Mountain Site",
                "latitude": 25.08,
                "longitude": 82.08,
                "slope": 32.0,  # Slope > 25° -> DISQUALIFIED
                "factors": {
                    "distance_to_hazard": 5.0,  # Hazard zone < 20 -> DISQUALIFIED
                    "historical_safety": 20,
                    "area_capacity": 5000,
                    "road_accessibility": 30,
                    "healthcare_proximity": 20,
                    "education_proximity": 20,
                    "water_access": 30,
                    "power_access": 30,
                }
            }
        ]

        plan = RelocationOptimizer.run_optimization(habitations, candidate_sites)

        # Cannot assign to unsafe site
        self.assertEqual(plan["summary"]["assigned"], 0)
        self.assertEqual(plan["summary"]["unassigned"], 1)

        unassigned_record = plan["unassigned"][0]
        rejected = unassigned_record["sites_rejected_and_reasons"]
        self.assertTrue(len(rejected) > 0)
        # Must specifically identify unsafe site rejection
        unsafe_rejection = next((r for r in rejected if r["site_id"] == "SITE_UNSAFE_STEEP"), None)
        self.assertIsNotNone(unsafe_rejection)
        self.assertIn("Unsafe site", unsafe_rejection["rejection_reason"])

    def test_04_site_with_zero_capacity(self):
        """
        Candidate site is safe but has zero available headroom.
        Must be excluded with zero capacity diagnostic reason.
        """
        habitations = [
            {
                "id": "HAB_TEST",
                "name": "Test Habitation",
                "population": 100,
                "risk_score": 75.0,
                "latitude": 25.01,
                "longitude": 82.01,
            }
        ]

        candidate_sites = [
            {
                "site_id": "SITE_ZERO_CAP",
                "site_name": "Zero Capacity Plot",
                "latitude": 25.04,
                "longitude": 82.04,
                "slope": 3.0,
                "factors": {
                    "distance_to_hazard": 90.0,
                    "historical_safety": 95,
                    "area_capacity": 0,  # Zero capacity
                    "road_accessibility": 90,
                    "healthcare_proximity": 90,
                    "education_proximity": 90,
                    "water_access": 90,
                    "power_access": 90,
                }
            }
        ]

        plan = RelocationOptimizer.run_optimization(habitations, candidate_sites)

        self.assertEqual(plan["summary"]["assigned"], 0)
        self.assertEqual(plan["summary"]["unassigned"], 1)

        unassigned_record = plan["unassigned"][0]
        rejected = unassigned_record["sites_rejected_and_reasons"]
        zero_rej = next((r for r in rejected if r["site_id"] == "SITE_ZERO_CAP"), None)
        self.assertIsNotNone(zero_rej)
        self.assertIn("Zero capacity", zero_rej["rejection_reason"])

    def test_05_population_exceeding_all_available_capacity(self):
        """
        Combined population of habitations exceeds total capacity of all candidate sites.
        Optimizer must assign up to available capacity, then flag remaining habitations as unassigned.
        """
        habitations = [
            {"id": "HAB_1", "name": "Habitation 1", "population": 400, "risk_score": 90.0, "latitude": 25.01, "longitude": 82.01},
            {"id": "HAB_2", "name": "Habitation 2", "population": 400, "risk_score": 80.0, "latitude": 25.02, "longitude": 82.02},
            {"id": "HAB_3", "name": "Habitation 3", "population": 400, "risk_score": 70.0, "latitude": 25.03, "longitude": 82.03},
        ]
        # Total population = 1200

        # Two sites with total capacity = 700
        candidate_sites = [
            {
                "site_id": "SITE_A",
                "site_name": "Site Alpha",
                "latitude": 25.05,
                "longitude": 82.05,
                "slope": 4.0,
                "factors": {
                    "distance_to_hazard": 90.0,
                    "historical_safety": 90,
                    "area_capacity": 450,
                    "road_accessibility": 80,
                    "healthcare_proximity": 80,
                    "education_proximity": 80,
                    "water_access": 80,
                    "power_access": 80,
                }
            },
            {
                "site_id": "SITE_B",
                "site_name": "Site Beta",
                "latitude": 25.06,
                "longitude": 82.06,
                "slope": 5.0,
                "factors": {
                    "distance_to_hazard": 85.0,
                    "historical_safety": 85,
                    "area_capacity": 250,
                    "road_accessibility": 75,
                    "healthcare_proximity": 75,
                    "education_proximity": 75,
                    "water_access": 75,
                    "power_access": 75,
                }
            }
        ]

        plan = RelocationOptimizer.run_optimization(habitations, candidate_sites)

        # HAB_1 (pop 400, risk 90) gets SITE_A (cap 450 -> 50 left)
        # HAB_2 (pop 400, risk 80) cannot fit in SITE_A (50 left) nor SITE_B (250 cap) -> Unassigned
        # HAB_3 (pop 400, risk 70) cannot fit in SITE_B (250 cap) nor SITE_A (50 left) -> Unassigned
        self.assertEqual(plan["summary"]["assigned"], 1)
        self.assertEqual(plan["summary"]["unassigned"], 2)
        self.assertEqual(plan["summary"]["total_relocated_population"], 400)
        self.assertEqual(plan["summary"]["total_capacity_deficit"], 800)

        # Check residual site capacities
        summary_a = next(s for s in plan["site_capacity_summary"] if s["site_id"] == "SITE_A")
        self.assertEqual(summary_a["remaining_capacity"], 50)

    def test_06_database_integration_and_api_endpoints(self):
        """
        Verify live API endpoints using canonical database records:
        - POST /api/optimizer/run
        - GET /api/optimizer/plan
        - GET /api/optimizer/vectors
        - GET /api/dashboard/action-plan
        """
        # Run optimizer
        res_run = self.client.post('/api/optimizer/run')
        self.assertEqual(res_run.status_code, 200)
        plan_data = res_run.get_json()

        self.assertIn("summary", plan_data)
        self.assertIn("assignments", plan_data)
        self.assertIn("unassigned", plan_data)
        self.assertIn("site_capacity_summary", plan_data)

        # Verify output schema fields on assignments
        for a in plan_data["assignments"]:
            self.assertIn("habitation", a)
            self.assertIn("population_requiring_relocation", a)
            self.assertIn("recommended_site", a)
            self.assertIn("population_assigned", a)
            self.assertIn("remaining_unassigned_population", a)
            self.assertIn("site_capacity_before", a)
            self.assertIn("site_capacity_after", a)
            self.assertIn("distance_km", a)
            self.assertIn("suitability_score", a)
            self.assertIn("reason_for_selection", a)
            self.assertIn("sites_rejected_and_reasons", a)
            self.assertIn("urgency", a)
            self.assertIn("capacity_deficit", a)

        # Test GET /api/optimizer/plan
        res_plan = self.client.get('/api/optimizer/plan')
        self.assertEqual(res_plan.status_code, 200)
        self.assertEqual(res_plan.get_json()["summary"]["total_habitations"], plan_data["summary"]["total_habitations"])

        # Test GET /api/optimizer/vectors
        res_vectors = self.client.get('/api/optimizer/vectors')
        self.assertEqual(res_vectors.status_code, 200)
        vectors_geojson = res_vectors.get_json()
        self.assertEqual(vectors_geojson["type"], "FeatureCollection")
        self.assertIsInstance(vectors_geojson["features"], list)

        if len(vectors_geojson["features"]) > 0:
            first_vector = vectors_geojson["features"][0]
            self.assertEqual(first_vector["geometry"]["type"], "LineString")
            self.assertEqual(len(first_vector["geometry"]["coordinates"]), 2)
            self.assertIn("habitation_name", first_vector["properties"])
            self.assertIn("site_name", first_vector["properties"])
            self.assertIn("population", first_vector["properties"])

        # Test GET /api/dashboard/action-plan reflects optimizer state
        res_action = self.client.get('/api/dashboard/action-plan')
        self.assertEqual(res_action.status_code, 200)
        action_data = res_action.get_json()
        self.assertIn("stats", action_data)
        self.assertIn("priority_table", action_data)
        self.assertEqual(action_data["stats"]["assigned_count"], plan_data["summary"]["assigned"])


if __name__ == '__main__':
    unittest.main()
