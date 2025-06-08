import os
import sys
import unittest
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import User, Items, Message, Categories

class ChatAPITestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        with app.app_context():
            db.create_all()

            # Ensure sender & receiver users exist
            if not User.query.get(1):
                u1 = User(id=1, name='Alice', email='alice@sfsu.edu')
                u1.set_password('password')
                db.session.add(u1)
            if not User.query.get(2):
                u2 = User(id=2, name='Bob', email='bob@sfsu.edu')
                u2.set_password('password')
                db.session.add(u2)

            # Ensure test category and item exist
            if not Categories.query.get(1):
                db.session.add(Categories(category_id=1, category_name='Tech'))
            if not Items.query.get(1):
                db.session.add(Items(
                    item_id=1,
                    title='MacBook Pro',
                    item_description='Testing item',
                    category_id=1,
                    price=1200.00,
                    item_condition='Used - Good',
                    seller_id=1
                ))

            db.session.commit()

    def test_send_message(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1  # sender

        res = self.app.post('/api/message', json={
            "receiver_id": 2,
            "content": "Hello, is this still available?",
            "item_id": 1
        })

        self.assertEqual(res.status_code, 200)
        self.assertIn('Message sent successfully', res.get_data(as_text=True))

    def test_inbox_messages(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1

        # Ensure there's at least one message
        self.app.post('/api/message', json={
            "receiver_id": 2,
            "content": "Follow-up message",
            "item_id": 1
        })

        res = self.app.get('/api/inbox')
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(isinstance(data, list))
        self.assertGreater(len(data), 0)
        self.assertIn('messages', data[0])
        self.assertGreater(len(data[0]['messages']), 0)

    def test_mark_messages_as_read(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = 2  # receiver

        # Send unread message to user_id=2
        with app.app_context():
            msg = Message(sender_id=1, receiver_id=2, content='Unread test', item_id=1, is_read=False)
            db.session.add(msg)
            db.session.commit()

        # Mark as read
        res = self.app.post('/api/mark-read', json={"sender_id": 1})
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('marked as read', data['message'])


if __name__ == '__main__':
    unittest.main()
