from webtest import TestApp
from controllers.root import application

app = TestApp(application())

def test_index_action():
    res = app.get('/')
    assert 'root - index' in res

def test_login_action():
    res = app.post('/login', {'username':'marcora', 'password':'deddym369'})
    assert res.json == 'register'
