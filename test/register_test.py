import io
import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import User


class FlaskAPITestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Create test user if not exists
        with app.app_context():
            db.create_all()
            if not User.query.filter_by(email='test@sfsu.edu').first():
                user = User(name='Test User', email='test@sfsu.edu')
                user.set_password('password123')
                db.session.add(user)
                db.session.commit()

    def test_register_success(self):
        response = self.app.post('/api/register', json={
            'name': 'New Tester',
            'email': 'newtester@sfsu.edu',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('User registered successfully', response.get_data(as_text=True))

    def test_register_invalid_email(self):
        response = self.app.post('/api/register', json={
            'name': 'Invalid Email',
            'email': 'notallowed@gmail.com',
            'password': 'abc'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('@sfsu.edu', response.get_data(as_text=True))

    def test_create_item_success(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1  # Make sure user with ID 1 exists

        data = {
            'title': 'Test Chair',
            'description': 'Comfortable mesh chair',
            'category_id': '1',  # Ensure this category exists
            'price': '79.99',
            'condition': 'Used - Good'
        }

        image_path = 'chair.jpeg'  # Adjust path if needed

        with open(image_path, 'rb') as image_file:
            response = self.app.post('/api/item', data={
                **data,
                'image': (image_file, 'chair.jpeg')
            }, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Item posted successfully', response.get_data(as_text=True))

    def test_create_item_missing_field(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1

        response = self.app.post('/api/item', data={
            'title': 'Missing Image',
            'description': 'No image here',
            'category_id': '1',
            'price': '50.00',
            'condition': 'Brand New'
        }, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 400)
        self.assertIn('Exactly one image must be uploaded', response.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
