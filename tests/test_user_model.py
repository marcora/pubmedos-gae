from models.user import User

def test():
    user = User(username='marcora', password='123456', email='marcora@caltech.edu', lastname='Marcora', forename='Edoardo')
    user.put()
    assert user.username == 'marcora'
