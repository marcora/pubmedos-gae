import logging

import wsgiref.handlers

from google.appengine.api import mail
from google.appengine.ext import webapp

from models.user import User

from controllers.app import *

# base request handler
class Users(RequestHandler):
  pass


## actions

class item(Users):
  def get(self, username):
    self.username = username
    self.current_user = self.get_current_user()
    self.user = User.get_by_username(username)
    self.render_template()
#    user = User.get_by_username(username)
#    if user:
#      self.render_template()
#    else:
#      self.error(404)


## routes

def main():
  urls = [('/users/(\w+)/?', item)]
  application = webapp.WSGIApplication(urls ,debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
