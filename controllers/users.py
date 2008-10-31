import logging

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail

from models.user import User

from controllers.app import *

## base request handler
class Users(RequestHandler):
  pass

## actions
class item(Users):
  @login_required
  def get(self, username):
    user = User.get_by_username(username)
    if user:
      self.current_user = self.current_user
      self.username = username
      self.user = user
      self.template()
    else:
      self.error(404)

## routes
def main():
  urls = [('/users/(\w+)', item)]
  application = webapp.WSGIApplication(urls, debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
