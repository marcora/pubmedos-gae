import logging

import urllib, re

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.api import users

from config import *

from controllers.app import *

## base request handler
class Admin(RequestHandler):
  pass

## actions
class root(Admin):
  def get(self):
    admin = users.get_current_user()
    self.text(admin.nickname())


def application():
  urls = [('/admin/?', root),]
  return webapp.WSGIApplication(urls, debug=DEBUG)

def main():
  run_wsgi_app(application())

if __name__ == '__main__':
  main()
