import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import User

class FlaskLoginTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True

        self.app = app.test_client()

        with app.app_context():
            db.create_all()
            user = User.query.filter_by(email='logintest1@sfsu.edu').first()
            if not user:
                user = User(name='Login Test User1', email='logintest1@sfsu.edu')
                db.session.add(user)


                user.set_password('password123')
                db.session.commit()
                #print(f"User ID: {user.id}, Password hash: {user.password_hash}")
                #print("SetUp: Password hash:", user.password_hash)

    def test_login_success(self):
        response = self.app.post('/api/login', json={
            'email': 'logintest1@sfsu.edu',
            'password': 'password123'
        })
        data = response.get_json()
        #print(data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Logging in user')

    def test_login_invalid_email(self):
        response = self.app.post('/api/login', json={
            'email': 'notreal@sfsu.edu',
            'password': 'password123'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'invalid email')

    def test_login_wrong_password(self):
        response = self.app.post('/api/login', json={
            'email': 'logintest1@sfsu.edu',
            'password': 'wrongpassword'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Invalid password')


if __name__ == '__main__':
    unittest.main()
