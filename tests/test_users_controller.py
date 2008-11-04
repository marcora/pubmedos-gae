from webtest import TestApp
from main import application
from models.user import User

app = TestApp(application())

user = User.get_or_insert_by_username(username='marcora', password='123456', email='marcora@caltech.edu', lastname='Marcora', forename='Edoardo')

def setup():
    res = app.post('/login', {'username':'marcora', 'password':'123456'})

def test_item_action():
    res = app.get('/users/marcora')
    assert 'Edoardo Marcora' in res

