import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

from app import app

load_dotenv()


class HackerTestCase(unittest.TestCase):
    """This class represents the hacker news test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = app
        self.client = self.app.test_client
        self.database_path = os.environ.get('SQLALCHEMY_DATABASE_URI')
        self.news_item = {
            'title': 'test news item',
            'text': 'technology will transform Africa',
        }
        self.bad_news_item = {
            'text': 'this is bad test sample, it should have a title',
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_items(self):
        res = self.client().get('/api/v1/items')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['items']))
        self.assertTrue(type(data['items']), list)

    def test_405_get_items(self):
        res = self.client().post('/api/v1/items', json=self.news_item)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_get_single_item(self):
        res = self.client().get('/api/v1/item/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['id'])
        self.assertTrue(data['type'])

    def test_404_get_item(self):
        res = self.client().get('/api/v1/item/100000000000000000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_item(self):
        res = self.client().delete('/api/v1/item/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['id'])
        self.assertEqual(data['success'], True)

    def test_422_if_news_does_not_exist(self):
        res = self.client().delete('/api/v1/item/10000000000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_create_news(self):
        res = self.client().post('/api/v1/item', json=self.news_item)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['id'])

    def test_422__news_creation_not_allowed(self):
        res = self.client().post('/api/v1/item', json=self.bad_news_item)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_422_update_item(self):
        res = self.client().patch('/api/v1/item/4', json=self.news_item)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
