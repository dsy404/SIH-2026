import unittest
import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

class TestEndpoints(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_health_check(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_action_plan(self):
        response = self.client.get('/api/dashboard/action-plan')
        self.assertEqual(response.status_code, 200)

    def test_tracking_post_relocation(self):
        response = self.client.post('/api/tracking/post-relocation', json={})
        self.assertEqual(response.status_code, 200)

    def test_simulation_run(self):
        response = self.client.post('/api/simulation/run', json={"rainfall_mm": 100})
        self.assertEqual(response.status_code, 200)

    def test_reports_csv(self):
        response = self.client.get('/api/reports/csv')
        self.assertEqual(response.status_code, 200)

    def test_ml_feature_importance(self):
        response = self.client.get('/api/ml/feature-importance')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
