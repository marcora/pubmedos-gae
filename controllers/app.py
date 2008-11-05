import sys, os, logging, urllib, re
import mimetypes, base64
import simplejson
import Cookie

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import webapp

from models.user import User
from models.article import Article
from models.reprint import Reprint
from models.folder import Folder
from models.rating import Rating

from mako.lookup import TemplateLookup
from mako.template import Template

template_lookup = TemplateLookup(directories=[os.path.dirname(__file__).replace('/controllers', '/views')], output_encoding='utf-8', encoding_errors='replace')

SESSION_TIMEOUT = 2*(60*60) # two hours

## helpers
def url(*segments, **vars):
  base_url = "http://%s" % os.environ.get('HTTP_HOST')
  path = '/'.join([str(s) for s in segments])
  if not path.startswith('/'):
    path = '/' + path
  if vars:
    path += '?' + urllib.urlencode(vars)
  return base_url + path

def login_required(request_handler):
  def wrapper(self, *args, **kwargs):
    user = None
    cookie = Cookie.SimpleCookie(self.request.headers.get('Cookie'))
    if cookie.has_key('pubmedos_sid'):
      sid = cookie['pubmedos_sid'].value
      if sid:
        session = memcache.get(sid)
        if session:
          username = session.get('username')
          remote_addr = session.get('remote_addr')
          if username and self.request.remote_addr == remote_addr:
            user = User.get_by_username(username)
    self.current_user = user
    if not self.current_user:
      self.error(401)
    else:
      request_handler(self, *args, **kwargs)
  return wrapper


## base controller
class Controller(webapp.RequestHandler):

  def template(self, format):
    ext = mimetypes.guess_extension(format)
    if ext:
      template_name = self.__class__.__bases__[0].__name__.lower() + '/' + self.__class__.__name__.lower() + ext
      template_vars = self.__dict__
      self.response.headers["Content-Type"] = format
      template = template_lookup.get_template(template_name)
      self.response.out.write(template.render(**template_vars))
    else:
      raise

  def pdf(self, content):
    self.response.headers["Content-Type"] = 'application/pdf'
    self.response.out.write(content)

  def json(self, content):
    self.response.headers['Content-Type'] = 'application/json' # 'text/javascript'
    cb = self.request.get('callback')
    if cb:
      self.response.out.write(cb + '(' + simplejson.dumps(content) + ')')
    else:
      self.response.out.write(simplejson.dumps(content))

  def html(self, content=None):
    if content:
      self.response.headers["Content-Type"] = 'text/html'
      self.response.out.write(content.encode('utf-8'))
    else:
      self.template('text/html')

  def xml(self, content=None):
    if content:
      self.response.headers["Content-Type"] = 'text/xml'
      self.response.out.write(content.encode('utf-8'))
    else:
      self.template('text/xml')

  def text(self, content=None):
    if content:
      self.response.headers["Content-Type"] = 'text/plain'
      self.response.out.write(content.encode('utf-8'))
    else:
      self.template('text/plain')

