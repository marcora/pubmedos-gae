from webtest import TestApp
from main import application
from models.user import User
from models.folder import Folder

app = TestApp(application())

user = User.get_or_insert_by_username(username='marcora', password='123456', email='marcora@caltech.edu', lastname='Marcora', forename='Edoardo')
other_user = User.get_or_insert_by_username(username='marcorae', password='123456', email='edoardo.marcora@gmail.com', lastname='Marcora', forename='Edoardo')

folder = Folder.get_or_insert_by_user_and_title(user, "Spam")
other_folder = Folder.get_or_insert_by_user_and_title(other_user, "Foo")

folder_hash = { 'id': 1, 'title':'Spam', 'ratings_count': 1 }

def setup():
    res = app.post('/login', {'username':'marcora', 'password':'123456'})

def test_index_action():
    res = app.get('/articles/16159402/folders')
    assert res.json == []

def test_create_action():
    res = app.post('/articles/16159402/folders/3', status=400) # no folder
    res = app.get('/articles/16159402/folders')
    res = app.post('/articles/16159402/folders/2', status=400) # other folder
    res = app.get('/articles/16159402/folders')
    assert res.json == []
    res = app.post('/articles/16159402/folders/1')
    res = app.get('/articles/16159402/folders')
    assert res.json == [folder_hash]

def test_destroy_action():
    res = app.delete('/articles/16159402/folders/3', status=400) # no folder
    res = app.get('/articles/16159402/folders')
    res = app.delete('/articles/16159402/folders/2', status=400) # other folder
    res = app.get('/articles/16159402/folders')
    assert res.json == [folder_hash]
    res = app.delete('/articles/16159402/folders/1')
    res = app.get('/articles/16159402/folders')
    assert res.json == []

def teardown():
    folder.delete()
    other_folder.delete()
