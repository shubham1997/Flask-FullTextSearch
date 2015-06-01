#http://flask.pocoo.org/docs/0.10/testing/
#http://www.diveintopython3.net/unit-testing.html
#http://werkzeug.pocoo.org/docs/0.10/test/#testing-api

import unittest
from app import create_app
from app.users.models import Users

app = create_app('config')

class TestUsers(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()


    def test_01_list(self):
      self.app = app.test_client()
      rv = self.app.get('/users/')
      assert "Users" in rv.data.decode('utf-8')


    def test_05_add(self):
        rv = self.app.post('/users/add', data=dict(name = 'test name', email = 'test@email.com',
                           password="qwe765", is_enabled=True, role="None"), follow_redirects=True)
        assert 'Add was successful' in rv.data.decode('utf-8')



    def test_10_Update(self):

         with app.app_context():
            user = Users.query.filter_by(email='test@email.com').first()
            id = user.id
            rv = self.app.post('/users/update/{}'.format(id), data=dict(name = 'test name update',
                               email = 'test@email.update', password="qwe75", is_enabled=False, role="admin"),
                               follow_redirects=True)
            assert 'Update was successful' in rv.data.decode('utf-8')

    def test_15_delete(self):
                     with app.app_context():
                       id = Users.query.first().id
                       rv = self.app.post('/users/delete/{}'.format(id), follow_redirects=True)
                       assert 'Delete was successful' in rv.data.decode('utf-8')






if __name__ == '__main__':
    unittest.main()