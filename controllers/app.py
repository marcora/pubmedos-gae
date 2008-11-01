import os
import logging

import urllib
import mimetypes
from django.utils import simplejson as json
import Cookie

from google.appengine.api import memcache
from google.appengine.ext import webapp

from mako.lookup import TemplateLookup
from mako.template import Template

from utils.sessions import Session

from models.user import User

template_lookup = TemplateLookup(directories=[os.path.dirname(__file__).replace('/controllers', '/views')], output_encoding='utf-8', encoding_errors='replace')

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
    username = self.session['username']
    if username:
      user = User.get_by_username(username)
    self.current_user = user
    if not self.current_user:
      self.error(401)
    else:
      request_handler(self, *args, **kwargs)
  return wrapper

## base request handler
class RequestHandler(webapp.RequestHandler):

  def __init__(self):
    self.session = Session()

  def json(self, content):
    self.response.headers['Content-Type'] = 'text/javascript'
    cb = self.request.get('callback')
    if cb:
      self.response.out.write(cb + '(' + json.dumps(content) + ')')
    else:
      self.response.out.write(json.dumps(content))

  def template(self, format='text/html'):
    ext = mimetypes.guess_extension(format)
    if ext:
      template_name = self.__class__.__bases__[0].__name__.lower() + '/' + self.__class__.__name__.lower() + ext
      template_vars = self.__dict__
      self.response.headers["Content-Type"] = format
      template = template_lookup.get_template(template_name)
      self.response.out.write(template.render(**template_vars))
    else:
      raise

  def text(self, text, format='text/plain'):
    ext = mimetypes.guess_extension(format)
    if ext:
      self.response.headers["Content-Type"] = format
      self.response.out.write(unicode(text))
    else:
      raise

  def xml(self, xml, format='text/xml'):
    ext = mimetypes.guess_extension(format)
    if ext:
      self.response.headers["Content-Type"] = format
      self.response.out.write(unicode(xml))
    else:
      raise
