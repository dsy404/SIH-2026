"""
Automated Test Suite for Phase 10: Alert Engine.

Verifies:
1. Automatic event-driven alert triggers (road blocked, conflict, risk escalation, capacity, simulation).
2. Database persistence with complete required schema:
   - id, type, severity (INFO, WARNING, HIGH, CRITICAL), title, description,
   - habitation/site reference, created timestamp, source event,
   - acknowledged status, resolved status, resolution timestamp.
3. Filtering alerts by severity, status, and source.
4. Acknowledge and resolve lifecycle transitions.
5. End-to-end integration with Field Verification cascading pipeline.
"""
import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.db.database import get_session_factory
from app.db.repository import Repository
from app.engines.alert_engine import AlertEngine


class AlertEngineTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.Session = get_session_factory()
        self.session = self.Session()

    def tearDown(self):
        self.session.close()

    def test_alert_schema_and_persistence(self):
        """Verify that an alert has all required fields persisted in the database."""
        alert = AlertEngine.create_alert(
            db=self.session,
            alert_type="TEST_CRITICAL_EVENT",
            severity="CRITICAL",
            title="Severe Hazard Spike",
            description="Test description of catastrophic flood inundation.",
            source_event="TEST_SUITE",
            habitation_id="HAB001",
            habitation_name="Achanakmar A",
            site_id="SITE001",
            site_name="Shivtar Safe Plateau",
            rpi=82.5,
            deduplicate=False
        )
        self.session.commit()

        # Check required properties
        self.assertTrue(alert.id.startswith("ALR-"))
        self.assertEqual(alert.type, "TEST_CRITICAL_EVENT")
        self.assertEqual(alert.severity, "CRITICAL")
        self.assertEqual(alert.title, "Severe Hazard Spike")
        self.assertIn("catastrophic", alert.description)
        self.assertEqual(alert.habitation_id, "HAB001")
        self.assertEqual(alert.site_id, "SITE001")
        self.assertEqual(alert.source_event, "TEST_SUITE")
        self.assertFalse(alert.is_acknowledged)
        self.assertFalse(alert.is_resolved)
        self.assertIsNone(alert.resolved_at)
        self.assertIsNotNone(alert.created_at)

        # Retrieve through Repository dict serializer
        retrieved = Repository.get_alert(self.session, alert.id)
        self.assertIsNotNone(retrieved)
        d = Repository.alert_to_dict(retrieved)
        self.assertEqual(d["id"], alert.id)
        self.assertEqual(d["severity"], "CRITICAL")
        self.assertEqual(d["habitation_name"], "Achanakmar A")

    def test_event_triggers(self):
        """Verify distinct automated event triggers produce corresponding alert types."""
        # 1. Road blocked trigger
        rb = AlertEngine.trigger_road_blocked(
            self.session, "HAB003", "Test Hamlet", verifier="Field Officer A", source_event="FIELD_VERIFICATION"
        )
        self.assertEqual(rb.type, "ROAD_BLOCKED")
        self.assertEqual(rb.severity, "HIGH")
        self.assertIn("Test Hamlet", rb.title)

        # 2. Verification conflict trigger
        vc = AlertEngine.trigger_verification_conflict(
            self.session, "HAB003", "Test Hamlet", notes="Bridge reported destroyed contrary to satellite data."
        )
        self.assertEqual(vc.type, "FIELD_VERIFICATION_CONFLICT")
        self.assertEqual(vc.severity, "WARNING")

        # 3. Critical risk trigger
        cr = AlertEngine.trigger_risk_critical(
            self.session, "HAB003", "Test Hamlet", rpi=78.2, risk_category="Critical"
        )
        self.assertEqual(cr.type, "RISK_CRITICAL")
        self.assertEqual(cr.severity, "CRITICAL")

        # 4. Immediate relocation trigger
        ir = AlertEngine.trigger_immediate_relocation(
            self.session, "HAB003", "Test Hamlet", urgency="Immediate"
        )
        self.assertEqual(ir.type, "IMMEDIATE_RELOCATION")
        self.assertEqual(ir.severity, "CRITICAL")

        # 5. Site capacity low trigger
        sc = AlertEngine.trigger_site_capacity_low(
            self.session, "SITE002", "North Valley Site", remaining_capacity=250, initial_capacity=2000
        )
        self.assertEqual(sc.type, "CANDIDATE_SITE_CAPACITY_LOW")
        self.assertEqual(sc.severity, "WARNING")
        self.assertEqual(sc.site_id, "SITE002")

        # 6. No feasible capacity trigger
        nfc = AlertEngine.trigger_no_feasible_capacity(
            self.session, unassigned_count=2, total_deficit=950, habitation_names=["Hamlet X", "Hamlet Y"]
        )
        self.assertEqual(nfc.type, "NO_FEASIBLE_CAPACITY")
        self.assertEqual(nfc.severity, "HIGH")

        # 7. Simulation escalation trigger
        sim = AlertEngine.trigger_simulation_escalation(
            self.session, rainfall_surge_mm=90.0, red_zone_delta=3, escalated_hab_names=["Hamlet A", "Hamlet B"]
        )
        self.assertEqual(sim.type, "SIMULATION_RISK_ESCALATION")
        self.assertEqual(sim.severity, "HIGH")

        self.session.commit()

    def test_lifecycle_acknowledge_and_resolve(self):
        """Verify alert acknowledge and resolve lifecycle transitions."""
        alert = AlertEngine.create_alert(
            db=self.session,
            alert_type="LIFECYCLE_TEST",
            severity="HIGH",
            title="Lifecycle Transition Alert",
            description="Testing acknowledge and resolve state transitions.",
            deduplicate=False
        )
        self.session.commit()
        alert_id = alert.id

        # 1. Initial State
        self.assertFalse(alert.is_acknowledged)
        self.assertFalse(alert.is_resolved)

        # 2. Acknowledge via API
        res_ack = self.client.patch(f"/api/alerts/{alert_id}/acknowledge")
        self.assertEqual(res_ack.status_code, 200)
        data_ack = res_ack.get_json()
        self.assertTrue(data_ack["alert"]["is_acknowledged"])
        self.assertIsNotNone(data_ack["alert"]["acknowledged_at"])
        self.assertFalse(data_ack["alert"]["is_resolved"])

        # 3. Resolve via API
        res_res = self.client.patch(f"/api/alerts/{alert_id}/resolve")
        self.assertEqual(res_res.status_code, 200)
        data_res = res_res.get_json()
        self.assertTrue(data_res["alert"]["is_resolved"])
        self.assertIsNotNone(data_res["alert"]["resolved_at"])

    def test_alerts_api_filtering(self):
        """Verify API filters alerts by severity and status."""
        # Create test alerts
        AlertEngine.create_alert(self.session, "FILTER_TEST", "CRITICAL", "Crit Alert", "Desc", deduplicate=False)
        AlertEngine.create_alert(self.session, "FILTER_TEST", "INFO", "Info Alert", "Desc", deduplicate=False)
        self.session.commit()

        # Query CRITICAL only
        res_crit = self.client.get("/api/alerts?severity=CRITICAL")
        self.assertEqual(res_crit.status_code, 200)
        data_crit = res_crit.get_json()
        self.assertTrue(all(a["severity"] == "CRITICAL" for a in data_crit["alerts"]))

        # Query active/unacknowledged
        res_active = self.client.get("/api/alerts?status=ACTIVE")
        self.assertEqual(res_active.status_code, 200)
        data_active = res_active.get_json()
        self.assertTrue(all(not a["is_resolved"] and not a["is_acknowledged"] for a in data_active["alerts"]))

    def test_recalculation_pipeline_emits_alerts(self):
        """Verify that submitting a field verification with road blocked automatically generates an alert."""
        hab = Repository.get_habitation(self.session, "HAB001")
        if not hab:
            self.skipTest("HAB001 not found")

        # Submit verification with blocked road
        payload = {
            "habitation_id": "HAB001",
            "verifier_name": "Alert Engine Integration Tester",
            "road_status": "BLOCKED",
            "road_accessible": False,
            "verification_status": "CONFLICTING_DATA",
            "notes": "Landslide severely damaged the only bridge access."
        }

        res = self.client.post("/api/field-verification/submit", json=payload)
        self.assertEqual(res.status_code, 200)

        # Check that alerts table received ROAD_BLOCKED and CONFLICT alerts for HAB001
        alerts = Repository.get_alerts(self.session, habitation_id="HAB001")
        types = [a.type for a in alerts]
        self.assertIn("ROAD_BLOCKED", types)
        self.assertIn("FIELD_VERIFICATION_CONFLICT", types)


if __name__ == '__main__':
    unittest.main()
