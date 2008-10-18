# from datetime import datetime
# import iso8601
import os
import logging
import uuid
import base64
import hashlib
import re
import Cookie
from sets import Set

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
from google.appengine.api import mail

from models.user import User

from controllers.app import *

## base request handler
class Root(RequestHandler):
  pass

## helpers
def b64_sha1(s):
  return base64.standard_b64encode(hashlib.sha1(s).digest())

def unique(list): # Fast and order preserving
    set = {}
    return [set.setdefault(e,e) for e in list if e not in set]

def decrypt_password_hash(encrypted_password_hash, username):
  # keyed Caesar cipher
  b64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
  key_chars = ''.join(unique(list(b64_sha1(username)+b64_chars)))
  if len(key_chars) == len(b64_chars):
    password_hash = [ b64_chars[key_chars.index(encrypted_password_hash[i])] for i in range(0,len(encrypted_password_hash)) ]
  else:
    raise
  return ''.join(password_hash)

def wsse_password_digest(nonce, created, password):
  # wsse password digest = Base64 (SHA1 (Nonce + Created + Password))
  s = hashlib.sha1()
  s.update(nonce)
  s.update(created)
  s.update(password)
  return base64.standard_b64encode(s.digest())

## actions
class index(Root):
  def get(self):
#    self.title = 'Home'
#    self.render_template()
    self.render_text('root - index')

class help(Root):
  def get(self):
    self.render_template()

class about(Root):
  def get(self):
    self.render_template()

class terms(Root):
  def get(self):
    self.render_template()

class register(Root):
  def post(self):
    username = self.request.get('username')
    password_hash = self.request.get('password')
    email = self.request.get('email')
    last_name = self.request.get('last_name')
    first_name = self.request.get('first_name', '')
    middle_name = self.request.get('middle_name', '')
    affiliation = self.request.get('affiliation', '')
    if username and \
          password_hash and \
          last_name and \
          first_name and \
          email and \
          re.match('^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$', email):
      activation_code = uuid.uuid4().urn[9:]
      last_name = last_name.decode('utf-8')
      first_name = first_name.decode('utf-8')
      middle_name = middle_name.decode('utf-8')
      affiliation = affiliation.decode('utf-8')
      user = User.get_or_insert_by_username(username, password = password_hash, last_name = last_name, first_name = first_name, middle_name = middle_name, affiliation = affiliation, email = email, activation_code = activation_code)
      if user:
        mail.send_mail(sender="help@pubmedos.appspot.com",
                       to="%s <%s>" % (last_name, email),
                       subject="Please activate your PubMed On Steroids account",
                       body="""
Dear %s:

Your PubMed On Steroids account has been created. In order to activate your account, please visit:

https://pubmedos.appspot.com/activate/%s

Please let us know if you have any problems activating your account or if you have any questions about the registration/activation process.

The PubMed On Steroids Team :)
""" % (last_name, activation_code))
        logging.info(activation_code)
      else:
        self.error(404)
    else:
      self.error(404)

class activate(Root):
  def get(self, activation_code):
    user = User.gql("WHERE activation_code = :1",
                    activation_code).get()
    if user:
      user.activation_code = None
      user.put()
      self.success = True
    else:
      self.success = False
    self.render_template()

class login(Root):
  def get(self):
    try:
##      authentication = os.environ['HTTP_AUTHORIZATION']
##      (meth, auth) = authentication.split(' ', 1)
##      if meth.lower() != 'basic':
##        raise
##      auth = auth.strip().decode('base64')
##      username, password = auth.split(':', 1)
      username = self.request.get('username')
      password = self.request.get('password')
      user = User.get_by_key_name('username:'+username)
      if user:
        if user.activation_code:
          self.render_json('activate')
        else:
          if password == user.password:
            cookie = Cookie.SimpleCookie(self.request.headers.get('Cookie'))
            if cookie.has_key('sid'):
              sid = cookie['sid'].value
              if sid:
                memcache.delete(sid)
            sid = str(uuid.uuid4())
            timeout = 60*60 # 1 hour timeout
            cookie['sid'] = sid
            cookie['sid']['max-age'] = timeout
            # store username and http_referrer in session id
            memcache.set(sid, user.username + '|' + self.request.remote_addr, timeout+60) # set memcache to last 1 min longer than cookie to ensure memcache exists when cookie does!
            self.response.headers['Set-Cookie'] = cookie.output(header='')
            self.render_json('authenticated')
          else:
            raise
      else:
        self.render_json('register')
    except:
      ## self.response.headers['WWW-Authenticate'] = 'Basic realm="pubmedos"'
      ## self.response.set_status(401)
      self.render_json('authenticate')

class logout(Root):
  def get(self):
    cookie = Cookie.SimpleCookie(self.request.headers.get('Cookie'))
    if cookie.has_key('sid'):
      sid = cookie['sid'].value
      if sid:
        memcache.delete(sid)
    self.response.headers['Set-Cookie'] = 'sid=; expires=Sat, 29-Mar-1969 00:00:00 GMT;'

## routes
def main():
  urls = [('/', index),
          ('/terms', terms),
          ('/help', help),
          ('/about', about),
          ('/register', register),
          ('/activate/(\S+)', activate),
          ('/login', login),
          ('/logout', logout)]
  application = webapp.WSGIApplication(urls, debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
