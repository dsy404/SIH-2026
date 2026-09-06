import sys
import os
import unittest
import json

# Add backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.db.database import get_session_factory
from app.db.repository import Repository

class TestDataConsistency(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()
        # Find the first habitation to test
        Session = get_session_factory()
        session = Session()
        habs = Repository.get_all_habitations(session)
        self.test_hab = habs[0] if habs else None
        session.close()

    def test_single_source_of_truth(self):
        if not self.test_hab:
            self.skipTest("No habitations in DB")
            
        hab_id = self.test_hab.id
        expected_pop = self.test_hab.population
        
        # 1. Test /habitations endpoint
        res = self.client.get(f'/api/habitations/{hab_id}')
        data = res.get_json()
        self.assertEqual(data['id'], hab_id)
        self.assertEqual(data['population'], expected_pop)
        
        # 2. Test /dashboard/action-plan
        res = self.client.get('/api/dashboard/action-plan')
        data = res.get_json()
        table = data['priority_table']
        row = next((r for r in table if r['habitation_id'] == hab_id), None)
        self.assertIsNotNone(row)
        self.assertEqual(row['population'], expected_pop)
        
        # 3. Test /optimizer/run
        res = self.client.post('/api/optimizer/run')
        data = res.get_json()
        assignments = data['assignments']
        unassigned = data['unassigned']
        all_habs = assignments + unassigned
        row = next((r for r in all_habs if r['habitation_id'] == hab_id), None)
        self.assertIsNotNone(row)
        self.assertEqual(row['population'], expected_pop)
        
if __name__ == '__main__':
    unittest.main()
