import re
from webtest import TestApp
from controllers.root import application
from models.user import User

app = TestApp(application())

def test_index_action():
    res = app.get('/')
    assert 'root - index' in res

def test_help_action():
    res = app.get('/help')
    assert 'root - help' in res

def test_about_action():
    res = app.get('/about')
    assert 'root - about' in res

def test_terms_action():
    res = app.get('/terms')
    assert 'root - terms' in res

def test_privacy_action():
    res = app.get('/privacy')
    assert 'root - privacy' in res

def test_login_action_before_registration():
    res = app.post('/login', {'username':'marcora', 'password':'123456'})
    assert res.json == 'register'

def test_login_action_after_registration():
    res = app.post('/register', {'username':'marcora', 'password':'123456', 'email':'marcora@caltech.edu', 'lastname':'Marcora', 'forename':'Edoardo'})
    res = app.post('/login', {'username':'marcora', 'password':'123456'})
    assert res.json == 'activate'

def test_login_action_after_activation():
    user = User.get_by_username('marcora')
    assert user.activation_code
    res = app.get('/activate/' + user.activation_code)
    res = res.follow() # redirect to pubmed
    user = User.get_by_username('marcora')
    assert not user.activation_code
    res = app.post('/login', {'username':'marcora', 'password':'654321'})
    assert res.json == 'authenticate'
    res = app.post('/login', {'username':'marcora', 'password':'123456'})
    assert res.json == 'authenticated'

def test_login_action_with_wrong_credentials():
    res = app.post('/login', {'username':'marcora', 'password':'654321'})
    assert res.json == 'authenticate'

def test_login_action_with_right_credentials():
    res = app.post('/login', {'username':'marcora', 'password':'123456'})
    assert res.json == 'authenticated'

def test_logout_action():
    res = app.get('/logout')

