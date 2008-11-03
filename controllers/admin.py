import sys, os, logging, urllib, re, base64

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

## configon
DEBUG = True
SESSION_TIMEOUT = 2*(60*60) # two hours

from models.user import User
from models.reprint import Reprint
from models.folder import Folder
from models.article import Article
from models.rating import Rating

from controllers.app import *

## base request handler
class Admin(Controller):
  pass

## actions
class root(Admin):
  def get(self):
    admin = users.get_current_user()
    self.text(admin.nickname())

