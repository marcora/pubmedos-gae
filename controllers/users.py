from controllers.app import *

## base request handler
class Users(Controller):
  pass

## actions
class item(Users):
  @login_required
  def get(self, username):
    user = User.get_by_username(username)
    if user:
      pass
    else:
      self.error(404)

