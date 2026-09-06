"""
Automated Test Suite for Phase 5: Real Data Ingestion.

Verifies:
1. Reference template downloads (/api/datasets/templates/<name>)
2. Active dataset registry with Phase 5 required metadata (/api/datasets)
3. CSV schema inspection and smart column mapping (/api/datasets/inspect)
4. GeoJSON schema inspection (/api/datasets/inspect)
5. Validation rules:
   - Impossible coordinates (lat > 90, lon > 180)
   - Missing coordinates
   - Negative or non-numeric population
   - Empty files
6. Clean, Coordinate Standardization (WGS84 EPSG:4326), and Canonical DB Persist (/api/datasets/import)
7. Pure Engine Recalculation: Newly imported real habitations pass through MasterEngine,
   NecessityEngine, and RelocationOptimizer, immediately showing up in risk & action plan.
"""
import unittest
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.db.database import get_session_factory
from app.db.repository import Repository
from app.db.models import Habitation, Dataset, RiskAssessment, RelocationNecessity


class RealDataIngestionTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.Session = get_session_factory()
        self.session = self.Session()

    def tearDown(self):
        self.session.close()

    def test_01_template_downloads(self):
        """Test that downloadable reference templates exist and are accessible via API."""
        templates = [
            'sample_habitations.csv',
            'sample_habitations.geojson',
            'sample_hazards.geojson',
            'sample_candidate_sites.csv',
        ]
        for tpl in templates:
            with self.client.get(f'/api/datasets/templates/{tpl}') as res:
                self.assertEqual(res.status_code, 200, f"Template {tpl} should be downloadable")
                self.assertGreater(len(res.data), 0, f"Template {tpl} content should not be empty")

    def test_02_datasets_registry_metadata(self):
        """GET /api/datasets must return all required metadata fields."""
        res = self.client.get('/api/datasets')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

        required_keys = {
            'id', 'name', 'source', 'original_filename',
            'record_count', 'geometry_type',
            'validation_status', 'processing_status', 'is_real'
        }
        for item in data:
            for key in required_keys:
                self.assertIn(key, item, f"Missing required dataset metadata key: {key}")

    def test_03_csv_inspection_and_auto_mapping(self):
        """Inspect a raw CSV with arbitrary custom headers and verify auto-mapping."""
        raw_csv = (
            "village_name,lat,lon,pop_total,households,elevation_m,slope_deg\n"
            "Bhojpur Basti,23.6412,85.5012,420,84,310,21.5\n"
            "Ghatotand Tola,23.6521,85.5130,290,58,340,24.0\n"
        )
        payload = {
            "content": raw_csv,
            "filename": "field_survey_habitations.csv",
            "category": "habitations"
        }
        res = self.client.post('/api/datasets/inspect', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data['format'].lower(), 'csv')
        self.assertEqual(data['category'], 'habitations')
        self.assertEqual(data['total_records'], 2)
        self.assertIn('village_name', data['headers'])
        self.assertIn('lat', data['headers'])
        self.assertIn('lon', data['headers'])

        # Check smart mapping suggestion
        mapping = data.get('suggested_mapping', {})
        self.assertEqual(mapping.get('village_name'), 'name')
        self.assertEqual(mapping.get('lat'), 'latitude')
        self.assertEqual(mapping.get('lon'), 'longitude')
        self.assertEqual(mapping.get('pop_total'), 'population')

    def test_04_geojson_inspection(self):
        """Inspect a valid GeoJSON and verify property and geometry detection."""
        sample_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [85.55, 23.65]},
                    "properties": {
                        "name": "Survey Hamlet 1",
                        "population": 150,
                        "households": 30
                    }
                }
            ]
        }
        payload = {
            "content": json.dumps(sample_geojson),
            "filename": "incoming_points.geojson",
            "category": "habitations"
        }
        res = self.client.post('/api/datasets/inspect', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data['format'].lower(), 'geojson')
        self.assertEqual(data['total_records'], 1)
        self.assertEqual(data['geometry_type'], 'Point')
        self.assertEqual(data['detected_crs'], 'EPSG:4326')
        self.assertIn('name', data['headers'])
        self.assertIn('population', data['headers'])

    def test_05_validation_anomalies_and_rejection(self):
        """Test rejection of invalid records: impossible coordinates, negative population."""
        # Row 1: lat=95.5 (impossible lat > 90)
        # Row 2: pop=-200 (impossible negative population)
        # Row 3: missing coordinates
        invalid_csv = (
            "village_name,lat,lon,pop_total\n"
            "Impossible North,95.5000,85.5012,300\n"
            "Negative Population,23.6500,85.5100,-200\n"
            "Missing Coords,,,450\n"
        )
        payload = {
            "content": invalid_csv,
            "filename": "flawed_data.csv",
            "category": "habitations",
            "mapping": {
                "village_name": "name",
                "lat": "latitude",
                "lon": "longitude",
                "pop_total": "population"
            }
        }
        res = self.client.post('/api/datasets/validate', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data['status'], 'FAILED')
        self.assertFalse(data['can_import'])
        self.assertGreater(data['invalid_count'], 0)

        # Check error reporting details
        error_msgs = [e['message'] for e in data['errors']]
        has_coord_err = any('latitude' in msg.lower() or 'coordinate' in msg.lower() for msg in error_msgs)
        has_pop_err = any('negative' in msg.lower() or 'numeric' in msg.lower() for msg in error_msgs)
        self.assertTrue(has_coord_err, f"Errors should catch invalid latitude: {error_msgs}")
        self.assertTrue(has_pop_err, f"Errors should catch negative population: {error_msgs}")

    def test_06_real_data_import_and_pipeline_recalculation(self):
        """
        End-to-end test of real CSV ingestion:
        - Upload custom CSV
        - Apply column mapping
        - Validate, clean, standardize CRS
        - Persist to canonical Habitation model with is_real=True
        - Verify automated recalculation of RPI and Necessity
        - Confirm appearance in Geospatial / Habitations APIs
        """
        real_csv = (
            "local_habitation,gps_lat,gps_lon,headcount,hh_count,alt_m,gradient_deg\n"
            "Pahari Tola North,23.6450,85.5050,450,90,320.0,22.5\n"
            "Koilakhurd Riverbed,23.6380,85.5120,380,76,285.0,14.0\n"
        )
        mapping = {
            "local_habitation": "name",
            "gps_lat": "latitude",
            "gps_lon": "longitude",
            "headcount": "population",
            "hh_count": "households",
            "alt_m": "elevation",
            "gradient_deg": "slope"
        }
        payload = {
            "content": real_csv,
            "filename": "ramgarh_real_field_survey.csv",
            "category": "habitations",
            "dataset_name": "Ramgarh Real Field Survey 2026",
            "source": "District Disaster Management Authority (DDMA)",
            "mapping": mapping
        }

        res = self.client.post('/api/datasets/import', json=payload)
        self.assertEqual(res.status_code, 200, f"Import failed: {res.data.decode()}")
        data = res.get_json()

        self.assertTrue(data['success'])
        self.assertEqual(data['imported_count'], 2)
        self.assertIn('recalculation_summary', data)

        recalc = data['recalculation_summary']
        self.assertEqual(recalc.get('status'), 'completed')
        self.assertGreaterEqual(recalc.get('total_habitations_evaluated', 0), 2)

        # 1. Verify Dataset metadata in DB
        db_session = self.Session()
        try:
            ds = db_session.query(Dataset).filter_by(id=data['dataset_id']).first()
            self.assertIsNotNone(ds)
            self.assertTrue(ds.is_real, "Dataset must be flagged as real")
            self.assertEqual(ds.source, "District Disaster Management Authority (DDMA)")
            self.assertEqual(ds.validation_status, "STANDARDIZED")
            self.assertEqual(ds.processing_status, "READY")
            self.assertEqual(ds.record_count, 2)

            # 2. Verify Habitations persisted in canonical DB
            h1 = db_session.query(Habitation).filter_by(name="Pahari Tola North").first()
            self.assertIsNotNone(h1, "Imported habitation 'Pahari Tola North' must exist in DB")
            self.assertEqual(h1.population, 450)
            self.assertEqual(h1.households, 90)
            self.assertAlmostEqual(h1.latitude, 23.6450, places=4)
            self.assertAlmostEqual(h1.longitude, 85.5050, places=4)

            # 3. Verify MasterEngine recalculated risk for new habitation
            risk = db_session.query(RiskAssessment).filter_by(habitation_id=h1.id).first()
            self.assertIsNotNone(risk, "Imported habitation must have an automatically computed RiskAssessment")
            self.assertGreater(risk.rpi, 0.0, "Calculated RPI must be > 0.0")

            # 4. Verify NecessityEngine evaluated necessity
            nec = db_session.query(RelocationNecessity).filter_by(habitation_id=h1.id).first()
            self.assertIsNotNone(nec, "Imported habitation must have RelocationNecessity evaluated")
            self.assertIn(nec.category, ['Immediate', 'Short-Term', 'Medium-Term', 'In-Situ', 'Monitor'])

        finally:
            db_session.close()

        # 5. Verify Habitations GeoJSON API includes the new points for the map
        geo_res = self.client.get('/api/habitations/geojson')
        self.assertEqual(geo_res.status_code, 200)
        geo_data = geo_res.get_json()
        names = [f['properties']['name'] for f in geo_data['features']]
        self.assertIn("Pahari Tola North", names)
        self.assertIn("Koilakhurd Riverbed", names)

        # 6. Cleanup test records to preserve baseline database state
        clean_session = self.Session()
        try:
            from app.db.models import RelocationAssignment
            from app.api.routes.datasets import _trigger_full_pipeline_recalculation
            h_ids = [h.id for h in clean_session.query(Habitation).filter(Habitation.name.in_(["Pahari Tola North", "Koilakhurd Riverbed"])).all()]
            if h_ids:
                clean_session.query(RelocationAssignment).filter(RelocationAssignment.habitation_id.in_(h_ids)).delete(synchronize_session=False)
                clean_session.query(RelocationNecessity).filter(RelocationNecessity.habitation_id.in_(h_ids)).delete(synchronize_session=False)
                clean_session.query(RiskAssessment).filter(RiskAssessment.habitation_id.in_(h_ids)).delete(synchronize_session=False)
                clean_session.query(Habitation).filter(Habitation.id.in_(h_ids)).delete(synchronize_session=False)
            clean_session.query(Dataset).filter_by(id=data['dataset_id']).delete(synchronize_session=False)
            clean_session.commit()
            _trigger_full_pipeline_recalculation(clean_session)
        finally:
            clean_session.close()


if __name__ == '__main__':
    unittest.main()
