from models.user import User

def test_create():
    for user in User.all():
        user.delete()
    user = User.get_or_insert_by_username(username='marcora', password='123456', email='marcora@caltech.edu', lastname='Marcora', forename='Edoardo')
    assert user.key().name() == 'username:marcora'
    assert user.username == 'marcora'
    assert user.password == '123456'
    assert user.email == 'marcora@caltech.edu'
    assert user.lastname == 'Marcora'
    assert user.forename == 'Edoardo'
    assert user.suffix == ''
    assert user.ratings
    assert user.folders
    assert user.name == 'Edoardo Marcora'
    assert user.authored_articles
    assert user.reprints
    assert user.reprints_filesize_sum

