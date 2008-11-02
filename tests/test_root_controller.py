import unittest

from webtest import TestApp

import controllers.root as controller

class ControllerTest(unittest.TestCase):

    def setUp(self):
        self.app = controller.main(test=True)

    def test_index_action(self):
        app = TestApp(self.app)
        res = app.get('/')
        self.assertTrue('root - index' in res)

    def test_login_action(self):
        app = TestApp(self.app)
        res = app.post('/login', {'username':'marcora', 'password':'deddym369'})
        self.assertTrue(res.json == 'register')
