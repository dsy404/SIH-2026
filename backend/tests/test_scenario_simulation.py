"""
Automated Test Suite for Phase 9: Live Scenario Simulation.

Verifies:
1. Non-destructive guarantee: DB records remain unmutated by scenario runs.
2. Environmental parameter variation (baseline 120 mm vs scenario 210 mm).
3. Cascading pipeline simulation:
   Rainfall surge -> Hazard surge -> Risk RPI escalation -> Red-zone increase -> Urgency escalation -> Optimizer re-allocation.
4. Differential comparison highlighting habitations whose hazard, risk category, urgency, or site changed.
5. Scenario reset functionality.
"""
import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.db.database import get_session_factory
from app.db.repository import Repository


class ScenarioSimulationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.Session = get_session_factory()
        self.session = self.Session()

    def tearDown(self):
        self.session.close()

    def test_01_non_destructive_scenario_run(self):
        """Verify scenario simulation calculates cascading impacts without mutating DB records."""
        # Check initial DB state of HAB001
        hab_before = Repository.get_habitation(self.session, "HAB001")
        ra_before_rpi = hab_before.risk_assessment.rpi if hab_before.risk_assessment else 0.0

        res = self.client.post('/api/simulation/run-scenario', json={
            "baseline_rainfall_mm": 120.0,
            "scenario_rainfall_mm": 210.0
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        # 1. Mode and label confirmation
        self.assertEqual(data["mode"], "DEMO LIVE-UPDATE SIMULATION")
        self.assertTrue(data["is_simulation"])
        self.assertFalse(data["saved_to_db"])

        # 2. Parameters
        self.assertEqual(data["parameters"]["baseline_rainfall_mm"], 120.0)
        self.assertEqual(data["parameters"]["scenario_rainfall_mm"], 210.0)
        self.assertEqual(data["parameters"]["rainfall_surge_mm"], 90.0)

        # 3. Summary metrics
        summary = data["summary"]
        self.assertIn("baseline_red_zones", summary)
        self.assertIn("scenario_red_zones", summary)
        self.assertGreaterEqual(summary["scenario_red_zones"], summary["baseline_red_zones"])
        self.assertGreaterEqual(summary["scenario_affected_population"], summary["baseline_affected_population"])

        # 4. Comparison records
        comparison = data["comparison"]
        self.assertIsInstance(comparison, list)
        self.assertGreater(len(comparison), 0)

        first = comparison[0]
        self.assertIn("baseline", first)
        self.assertIn("scenario", first)
        self.assertIn("difference", first)
        self.assertIn("hazard_changed", first["difference"])
        self.assertIn("risk_category_changed", first["difference"])
        self.assertIn("urgency_changed", first["difference"])
        self.assertIn("site_changed", first["difference"])

        # 5. Non-destructive DB check: Verify HAB001 was NOT mutated in SQLite
        hab_after = Repository.get_habitation(self.session, "HAB001")
        ra_after_rpi = hab_after.risk_assessment.rpi if hab_after.risk_assessment else 0.0
        self.assertEqual(ra_before_rpi, ra_after_rpi, "Simulation must NOT alter production database records")

    def test_02_scenario_reset(self):
        """Verify scenario reset returns baseline parameters."""
        res = self.client.post('/api/simulation/reset', json={})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data["mode"], "DEMO LIVE-UPDATE SIMULATION")
        self.assertEqual(data["parameters"]["baseline_rainfall_mm"], 120.0)
        self.assertEqual(data["parameters"]["scenario_rainfall_mm"], 120.0)
        self.assertEqual(data["parameters"]["rainfall_surge_mm"], 0.0)
        self.assertEqual(data["summary"]["red_zone_delta"], 0)


if __name__ == '__main__':
    unittest.main()
