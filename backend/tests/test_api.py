import json
import unittest
from app import create_app
from app.extensions import db
from app.models.student import Student
from app.models.institution import Institution
from seed import seed_database

class BackendApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        with self.app.app_context():
            seed_database()

    def test_login_success(self):
        res = self.client.post('/api/v1/auth/login', json={
            'username': 'institute_demo',
            'password': 'Demo123!'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('token', data)
        self.assertEqual(data['user']['role'], 'institute')
        self.assertIsNotNone(data['user']['institution_id'])

    def test_login_invalid_credentials(self):
        res = self.client.post('/api/v1/auth/login', json={
            'username': 'institute_demo',
            'password': 'WrongPassword!'
        })
        self.assertEqual(res.status_code, 401)

    def test_institute_isolation_cannot_access_other_institution(self):
        login_res = self.client.post('/api/v1/auth/login', json={
            'username': 'institute_demo',
            'password': 'Demo123!'
        })
        token = login_res.get_json()['token']
        headers = {'Authorization': f'Bearer {token}'}

        with self.app.app_context():
            inst2 = Institution.query.filter_by(code='AICTE-1-004812').first()
            inst2_id = inst2.id

        res = self.client.get(f'/api/v1/institutions/{inst2_id}', headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_csv_template_download(self):
        res = self.client.get('/api/v1/uploads/template')
        self.assertEqual(res.status_code, 200)
        content = res.get_data(as_text=True)
        self.assertIn('student_id', content)
        self.assertIn('apaar_id', content)

    def test_dashboard_metrics_for_institute(self):
        login_res = self.client.post('/api/v1/auth/login', json={
            'username': 'institute_demo',
            'password': 'Demo123!'
        })
        token = login_res.get_json()['token']
        headers = {'Authorization': f'Bearer {token}'}

        res = self.client.get('/api/v1/dashboard/metrics', headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['role'], 'institute')
        self.assertIn('kpis', data)
        self.assertGreaterEqual(data['kpis']['total_students'], 5)

if __name__ == '__main__':
    unittest.main()
