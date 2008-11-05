from webtest import TestApp
from main import application

from models.user import User
from models.folder import Folder

app = TestApp(application())

folder_hash = { 'id': 1, 'title':'Spam', 'ratings_count': 0 }

def setup():
    res = app.post('/login', {'username':'marcora', 'password':'123456'})

def test_index_action():
    res = app.get('/folders')
    assert res.json == []

def test_create_action():
    res = app.post('/folders', {'title':'Spam'})
    assert res.json == [folder_hash]

def test_create_dup_action():
    res = app.post('/folders', {'title':'Spam'})
    assert res.json == [folder_hash]

def test_show_action():
    other_user = User.get_or_insert_by_username(username='marcorae', password='123456', email='edoardo.marcora@gmail.com', lastname='Marcora', forename='Edoardo')
    other_folder = Folder.get_or_insert_by_user_and_title(other_user, 'Foo')
    res = app.get('/folders/3', status=404) # no folder
    res = app.get('/folders/2', status=404) # other folder
    res = app.get('/folders/1')
    assert res.json == folder_hash

def test_update_action():
    res = app.post('/folders/3', {'title':'Poo'}, status=404) # no folder
    res = app.post('/folders/2', {'title':'Poo'}, status=404) # other folder
    res = app.post('/folders/1', {'title':'Poo'})
    folder_hash = { 'id': 1, 'title':'Poo', 'ratings_count': 0 }
    assert res.json == folder_hash

def test_dialog():
    res = app.get('/folders/dialog')

def test_delete_action():
    res = app.delete('/folders/3', status=404) # no folder
    res = app.delete('/folders/2', status=404) # other folder
    res = app.delete('/folders/1')
    res = app.get('/folders')
    assert res.json == []

