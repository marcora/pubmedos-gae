from controllers.app import *

## base request handler
class Admin(Controller):
  pass

## actions
class root(Admin):
  def get(self):
    admin = users.get_current_user()
    self.text(admin.nickname())
