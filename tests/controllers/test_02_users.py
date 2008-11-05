from webtest import TestApp
from main import application

from models.user import User

app = TestApp(application())

def setup():
    res = app.post('/login', {'username':'marcora', 'password':'123456'})

def test_item_action():
    res = app.get('/users/marcora')
    assert 'Edoardo Marcora' in res

