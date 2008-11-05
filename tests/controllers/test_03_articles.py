from webtest import TestApp
from main import application

from models.user import User

app = TestApp(application())

def setup():
    res = app.post('/login', {'username':'marcora', 'password':'123456'})

def test_index_action():
    res = app.get('/articles')
    assert res.json == []

def test_index_action_with_id():
    res = app.get('/articles?id=16159402')
    assert type(res.json) == type([])
    assert len(res.json) == 1

def test_index_action_with_ids():
    res = app.get('/articles?id=16159402&id=123456')
    assert type(res.json) == type([])
    assert len(res.json) == 2

def test_item_action():
    res = app.get('/articles/16159402')
    assert res.json['id'] == 16159402

def test_item_update_rating_action():
    res = app.get('/articles/16159402')
    assert res.json['rating'] == 0
    res = app.post('/articles/16159402/rating', {'value':'3'})
    res = app.get('/articles/16159402')
    assert res.json['rating'] == 3

def test_item_update_annotation_action():
    res = app.get('/articles/16159402')
    assert res.json['annotation'] == None
    res = app.post('/articles/16159402/annotation', {'value':'foo'})
    res = app.get('/articles/16159402')
    print str(res)
    assert res.json['annotation'] == 'foo'

def test_item_toggle_favorite_action():
    res = app.get('/articles/16159402')
    assert res.json['favorite'] == False
    res = app.post('/articles/16159402/favorite')
    res = app.get('/articles/16159402')
    assert res.json['favorite'] == True

def test_item_toggle_file_action():
    res = app.get('/articles/16159402')
    assert res.json['file'] == False
    res = app.post('/articles/16159402/file')
    res = app.get('/articles/16159402')
    assert res.json['file'] == True

def test_item_toggle_work_action():
    res = app.get('/articles/16159402')
    assert res.json['work'] == False
    res = app.post('/articles/16159402/work')
    res = app.get('/articles/16159402')
    assert res.json['work'] == True

def test_item_toggle_read_action():
    res = app.get('/articles/16159402')
    assert res.json['read'] == False
    res = app.post('/articles/16159402/read')
    res = app.get('/articles/16159402')
    assert res.json['read'] == True

def test_item_toggle_author_action():
    res = app.get('/articles/16159402')
    assert res.json['author'] == False
    res = app.post('/articles/16159402/author')
    res = app.get('/articles/16159402')
    assert res.json['author'] == True

def test_item_sponsored_links_action():
    res = app.get('/articles/16159402/sponsored_links')
    assert "Huntington's disease" in res

def test_item_xml_action():
    res = app.get('/articles/16159402/xml')
    assert "Huntington's disease" in res
