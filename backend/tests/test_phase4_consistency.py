"""
Automated Consistency Test Suite for Phase 4: Full Synthetic Dataset Pipeline.

Verifies:
1. Population Conservation (GeoJSON == DB == Dashboard API)
2. Pure Engine Derivation (No synthetic random numbers downstream)
3. Risk Score (RPI) calculation: 0.40*H + 0.30*E + 0.30*V
4. Necessity Category thresholds based strictly on calculated RPI
5. Red-zone counts and affected population consistency
6. RelocationOptimizer site capacity constraints (no site over-allocated)
7. Dashboard KPI aggregation correctness and rank ordering
"""
import unittest
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.db.database import get_session_factory
from app.db.repository import Repository
from app.engines.relocation.carrying_capacity import CapacityCalculator


class Phase4ConsistencyTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.Session = get_session_factory()
        self.session = self.Session()

    def tearDown(self):
        self.session.close()

    def test_population_conservation(self):
        """Sum of habitation populations in DB matches GeoJSON and Dashboard API."""
        geojson_path = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'synthetic', 'habitations.geojson'
        )
        with open(geojson_path, 'r') as f:
            geojson_data = json.load(f)

        expected_total = sum(
            feat['properties'].get('population', 0) for feat in geojson_data['features']
        )
        self.assertEqual(expected_total, 28930)

        habitations = Repository.get_all_habitations(self.session)
        db_total = sum(h.population for h in habitations)
        self.assertEqual(db_total, expected_total, "DB population sum must equal GeoJSON raw sum")

        # Verify Dashboard API matches
        res = self.client.get('/api/dashboard/action-plan')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['stats']['total_population'], db_total)
        self.assertEqual(data['stats']['total_habitations'], len(habitations))

    def test_rpi_mathematical_derivation(self):
        """Verify RPI is strictly calculated from H/E/V engines with 0.4/0.3/0.3 weights."""
        habitations = Repository.get_all_habitations(self.session)
        self.assertEqual(len(habitations), 20)

        for hab in habitations:
            ra = hab.risk_assessment
            self.assertIsNotNone(ra, f"Habitation {hab.id} must have a RiskAssessment")

            expected_rpi = min(
                100.0,
                (ra.hazard_score * 0.40) + (ra.exposure_score * 0.30) + (ra.vulnerability_score * 0.30)
            )
            self.assertAlmostEqual(
                ra.rpi,
                expected_rpi,
                places=1,
                msg=f"RPI for {hab.id} must match mathematical weighted sum"
            )

            # Check category bracket
            if ra.rpi >= 76:
                expected_cat = "Critical / Red Zone Candidate"
            elif ra.rpi >= 56:
                expected_cat = "High"
            elif ra.rpi >= 31:
                expected_cat = "Moderate"
            else:
                expected_cat = "Low"

            self.assertEqual(
                ra.risk_category,
                expected_cat,
                f"Category for {hab.id} with RPI={ra.rpi} must be {expected_cat}"
            )

    def test_necessity_derivation(self):
        """Verify necessity category strictly derives from calculated RPI score."""
        habitations = Repository.get_all_habitations(self.session)
        for hab in habitations:
            self.assertIsNotNone(hab.necessity, f"Habitation {hab.id} must have a necessity classification")
            rpi = hab.risk_assessment.rpi

            if rpi > 85:
                expected_nec = "Immediate"
            elif rpi >= 70:
                expected_nec = "Short-Term"
            elif rpi >= 50:
                expected_nec = "Medium-Term"
            elif rpi >= 30:
                expected_nec = "In-Situ"
            else:
                expected_nec = "Monitor"

            self.assertEqual(
                hab.necessity.category,
                expected_nec,
                f"Necessity category for {hab.id} (RPI={rpi}) must be {expected_nec}"
            )

    def test_red_zone_and_affected_population(self):
        """Verify red-zone counts and affected population in DB strictly equal Dashboard API."""
        habitations = Repository.get_all_habitations(self.session)

        manual_red_zones = 0
        manual_affected_pop = 0
        for h in habitations:
            if h.necessity and h.necessity.category in ["Immediate", "Short-Term"]:
                manual_red_zones += 1
                manual_affected_pop += h.population

        res = self.client.get('/api/dashboard/action-plan')
        self.assertEqual(res.status_code, 200)
        stats = res.get_json()['stats']

        self.assertEqual(stats['red_zones'], manual_red_zones)
        self.assertEqual(stats['affected_population'], manual_affected_pop)

    def test_optimizer_site_capacity_constraints(self):
        """Verify optimizer assignments never exceed any site's feasible additional capacity."""
        sites = Repository.get_all_sites(self.session)
        assignments = Repository.get_all_assignments(self.session)

        # Map site capacities
        capacities = {}
        for s in sites:
            cap_analysis = CapacityCalculator.analyze_capacity(s.id, 0)
            capacities[s.id] = cap_analysis.get('feasible_additional_capacity', 0)

        # Sum assigned population per site
        site_load = {s.id: 0 for s in sites}
        for a in assignments:
            if a.site_id is not None:
                self.assertIn(a.site_id, site_load, f"Assigned site {a.site_id} must be valid")
                site_load[a.site_id] += a.population
            else:
                self.assertEqual(a.status, "unassigned")


        for site_id, total_assigned in site_load.items():
            max_feasible = capacities[site_id]
            self.assertLessEqual(
                total_assigned,
                max_feasible,
                f"Site {site_id} has assigned population {total_assigned} exceeding feasible capacity {max_feasible}"
            )

    def test_priority_table_ordering(self):
        """Verify priority table is strictly sorted by risk score descending with no rank gaps."""
        res = self.client.get('/api/dashboard/action-plan')
        self.assertEqual(res.status_code, 200)
        table = res.get_json()['priority_table']

        self.assertEqual(len(table), 20, "Priority table must include all 20 habitations")

        for idx, row in enumerate(table):
            self.assertEqual(row['rank'], idx + 1, f"Rank must be sequential at index {idx}")
            if idx > 0:
                prev_score = table[idx - 1]['risk_score']
                self.assertLessEqual(
                    row['risk_score'],
                    prev_score,
                    f"Table must be sorted descending: row {idx} ({row['risk_score']}) > prev ({prev_score})"
                )


if __name__ == '__main__':
    unittest.main()
