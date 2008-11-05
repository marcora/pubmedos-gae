from models.user import User

def setup():
    for user in User.all():
        user.delete()

def test_create():
    user = User.get_or_insert_by_username(username='marcora', password='123456', email='marcora@caltech.edu', lastname='Marcora', forename='Edoardo')
    assert user.is_saved()
    assert user.key().name() == 'username:marcora'
    assert user.username == 'marcora'
    assert user.password == '123456'
    assert user.email == 'marcora@caltech.edu'
    assert user.lastname == 'Marcora'
    assert user.forename == 'Edoardo'
    assert user.suffix == ''

def test_name():
    user = User.get_or_insert_by_username(username='marcora')
    assert user.name == 'Edoardo Marcora'
