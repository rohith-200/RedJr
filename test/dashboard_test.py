import unittest 
from urllib.parse import urlparse
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import User

class FlaskDashboardTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'
        self.client1 = app.test_client()
        self.client2 = app.test_client()
        self.client3 = app.test_client()
        with app.app_context():
            db.create_all()

    def test_no_login(self):
        response = self.client1.get('/api/dashboard', follow_redirects=False)
        expectedPath = '/login'
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.headers['Location']).path, expectedPath)

    def test_user_1(self):
        with self.client2.session_transaction() as session:
            session['user_id'] = 1
        response = self.client2.get('api/dashboard')
        sample_response = {
            'selling_listings': 
            [
                {'item_id': 2, 
                 'title': 'HP Laptop', 
                 'price': 1000.0, 
                 'condition': 'Used - Like New', 
                 'created_at': '2025-05-08T02:13:47',
                 'image_id': 2}, 
                 {'item_id': 1, 
                  'title': 'Macbook Pro', 
                  'price': 1000.0, 
                  'condition': 'Brand New', 
                  'created_at': '2025-05-08T02:13:13', 
                  'image_id': 1}
            ],
            'sold_items': [],
            'saved_items': []
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), sample_response)

    def test_user_2(self):
        with self.client3.session_transaction() as session:
            session['user_id'] = 2
        
        response = self.client3.get('/api/dashboard')
        sample_response = {
            'selling_listings':
            [
                {
                    "item_id": 5,
                    "title": 'Couch',
                    "price": 100.0,
                    "condition": 'Brand New',
                    "created_at": "2025-05-08T02:16:01",
                    "image_id": 5
                },
                {
                    "item_id": 4,
                    "title": 'Data Science Textbook',
                    "price": 5.0,
                    "condition": 'Used - Acceptable',
                    "created_at": "2025-05-08T02:15:09",
                    "image_id": 4
                },
                {
                    "item_id": 3,
                    "title": 'Bible',
                    "price": 1.0,
                    "condition": 'Used - Good',
                    "created_at": "2025-05-08T02:14:33",
                    "image_id": 3
                }
            ],
            'sold_items': [
                {
                    "item_id": 6,
                    "title": 'Chair',
                    "price": 50.0,
                    "condition": 'Used - Good',
                    "created_at": "2025-05-08T02:16:24",
                    "image_id": 6
                }
            ],
            'saved_items': []
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), sample_response)

if __name__ == '__main__':
    unittest.main(verbosity=2) # Increased verbosity
