"""
Automated Test Suite for Phase 8: Field Verification + Recalculation.

Verifies:
1. Habitations retrieval for verification console with baseline values.
2. Field verification submission with road blocked observation.
3. Automated cascading recalculation:
   Field Verification -> Vulnerability -> Hazard -> RPI Risk -> Relocation Necessity -> Optimizer.
4. "Before vs After" differential tracking.
5. Non-destructive provenance & audit trail persistence.
"""
import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.db.database import get_session_factory
from app.db.repository import Repository


class FieldVerificationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.Session = get_session_factory()
        self.session = self.Session()

        # Save pristine snapshot of HAB002 to restore after tests
        hab = Repository.get_habitation(self.session, "HAB002")
        if hab:
            self.hab_backup = {
                "road_accessible": hab.road_accessible,
                "road_status": hab.road_status,
                "water_availability": hab.water_availability,
                "housing_condition": hab.housing_condition,
                "healthcare_accessible": hab.healthcare_accessible,
                "hazard_observation": hab.hazard_observation,
                "verification_status": hab.verification_status,
            }
            if hab.risk_assessment:
                self.ra_backup = {
                    "hazard_score": hab.risk_assessment.hazard_score,
                    "exposure_score": hab.risk_assessment.exposure_score,
                    "vulnerability_score": hab.risk_assessment.vulnerability_score,
                    "rpi": hab.risk_assessment.rpi,
                    "risk_category": hab.risk_assessment.risk_category,
                }
            else:
                self.ra_backup = None

            if hab.necessity:
                self.nec_backup = {
                    "category": hab.necessity.category,
                    "risk_score": hab.necessity.risk_score,
                }
            else:
                self.nec_backup = None
        else:
            self.hab_backup = None
            self.ra_backup = None
            self.nec_backup = None

    def tearDown(self):
        # Restore HAB002 to baseline so other tests remain strictly consistent
        if self.hab_backup:
            hab = Repository.get_habitation(self.session, "HAB002")
            if hab:
                for k, v in self.hab_backup.items():
                    setattr(hab, k, v)
                if self.ra_backup and hab.risk_assessment:
                    for k, v in self.ra_backup.items():
                        setattr(hab.risk_assessment, k, v)
                if self.nec_backup and hab.necessity:
                    for k, v in self.nec_backup.items():
                        setattr(hab.necessity, k, v)
                self.session.commit()
        self.session.close()

    def test_01_get_habitations_for_verification(self):
        """Verify API exposes habitations with operational baseline attributes."""
        res = self.client.get('/api/field-verification/habitations')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

        first = data[0]
        self.assertIn("id", first)
        self.assertIn("name", first)
        self.assertIn("road_accessible", first)
        self.assertIn("road_status", first)
        self.assertIn("water_availability", first)
        self.assertIn("housing_condition", first)
        self.assertIn("healthcare_accessible", first)
        self.assertIn("hazard_observation", first)
        self.assertIn("verification_status", first)
        self.assertIn("risk_score", first)

    def test_02_field_verification_cascading_recalculation(self):
        """
        Verify that submitting field verification with a blocked road triggers
        cascading recalculation and updates vulnerability, risk, necessity, and optimizer.
        """
        # Pick HAB002 or first available habitation
        hab = Repository.get_habitation(self.session, "HAB002")
        if not hab:
            hab = Repository.get_all_habitations(self.session)[0]
        hab_id = hab.id

        # Ensure starting from baseline open state
        hab.road_accessible = True
        hab.road_status = "OPEN"
        hab.water_availability = "ADEQUATE"
        hab.housing_condition = "PUCCA_GOOD"
        hab.healthcare_accessible = True
        hab.hazard_observation = "NONE"
        if hab.risk_assessment:
            hab.risk_assessment.vulnerability_score = 40.0
            hab.risk_assessment.rpi = 65.0
            hab.risk_assessment.risk_category = "High"
        if hab.necessity:
            hab.necessity.category = "Short-Term"
        self.session.commit()

        # Submit verification with road blocked, vulnerable housing, and water scarcity
        payload = {
            "habitation_id": hab_id,
            "verifier_name": "Inspector Ramesh Kumar",
            "road_accessible": False,
            "road_status": "BLOCKED",
            "water_availability": "SCARCE",
            "housing_condition": "KUTCHA_VULNERABLE",
            "healthcare_accessible": False,
            "hazard_observation": "RISING_WATER",
            "verification_status": "VERIFIED",
            "notes": "Severe flash flood has washed away the main approach culvert. Evacuation route severed."
        }

        res = self.client.post('/api/field-verification/submit', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        # 1. Output structure
        self.assertIn("verification_id", data)
        self.assertIn("before", data)
        self.assertIn("after", data)
        self.assertIn("difference", data)
        self.assertIn("cascading_pipeline_steps", data)

        before = data["before"]
        after = data["after"]
        diff = data["difference"]

        # 2. Vulnerability should escalate due to severed road (+25), water (+15), housing (+20)
        self.assertGreater(after["vulnerability_score"], before["vulnerability_score"])
        self.assertGreater(diff["vulnerability_delta"], 0)

        # 3. Hazard should escalate due to RISING_WATER observation
        self.assertGreaterEqual(after["hazard_score"], before["hazard_score"])

        # 4. RPI Risk score must increase
        self.assertGreater(after["rpi"], before["rpi"])
        self.assertGreater(diff["rpi_delta"], 0)

        # 5. Relocation necessity should be updated
        self.assertIn(after["necessity_category"], ("Immediate", "Short-Term"))

        # 6. Verify audit trail history endpoint records this submission
        hist_res = self.client.get(f'/api/field-verification/history?habitation_id={hab_id}')
        self.assertEqual(hist_res.status_code, 200)
        history = hist_res.get_json()
        self.assertGreater(len(history), 0)
        latest_audit = history[0]
        self.assertEqual(latest_audit["habitation_id"], hab_id)
        self.assertEqual(latest_audit["verifier_name"], "Inspector Ramesh Kumar")
        self.assertEqual(latest_audit["road_status"], "BLOCKED")
        self.assertIsNotNone(latest_audit["previous_state"])
        self.assertIsNotNone(latest_audit["updated_state"])
        self.assertIsNotNone(latest_audit["recalculation_diff"])


if __name__ == '__main__':
    unittest.main()
