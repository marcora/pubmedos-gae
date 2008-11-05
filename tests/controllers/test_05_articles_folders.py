from webtest import TestApp
from main import application

from models.user import User
from models.folder import Folder

app = TestApp(application())

folder_hash = { 'id': 3, 'title':'Foo', 'ratings_count': 1 }

def setup():
    user = User.get_by_username('marcora')
    folder = Folder.get_or_insert_by_user_and_title(user, 'Foo')
    res = app.post('/login', {'username':'marcora', 'password':'123456'})

def test_index_action():
    res = app.get('/articles/16159402/folders')
    assert res.json == []

def test_create_action():
    res = app.post('/articles/16159402/folders/1', status=400) # no folder
    res = app.get('/articles/16159402/folders')
    res = app.post('/articles/16159402/folders/2', status=400) # other folder
    res = app.get('/articles/16159402/folders')
    assert res.json == []
    res = app.post('/articles/16159402/folders/3')
    res = app.get('/articles/16159402/folders')
    assert res.json == [folder_hash]

def test_dialog():
    res = app.get('/articles/16159402/folders/dialog')

def test_destroy_action():
    res = app.delete('/articles/16159402/folders/1', status=400) # no folder
    res = app.get('/articles/16159402/folders')
    res = app.delete('/articles/16159402/folders/2', status=400) # other folder
    res = app.get('/articles/16159402/folders')
    assert res.json == [folder_hash]
    res = app.delete('/articles/16159402/folders/3')
    res = app.get('/articles/16159402/folders')
    assert res.json == []
