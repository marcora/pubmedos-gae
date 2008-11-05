import uuid

from controllers.app import *

## controller
class Root(Controller):
  pass

## actions
class index(Root):
  def get(self):
    self.text('root - index')

class help(Root):
  def get(self):
    self.text('root - help')

class about(Root):
  def get(self):
    self.text('root - about')

class terms(Root):
  def get(self):
    self.text('root - terms')

class privacy(Root):
  def get(self):
    self.text('root - privacy')

class register(Root):
  def post(self):
    username = str(self.request.get('username')).strip()
    password_hash = str(self.request.get('password')).strip()
    email = str(self.request.get('email')).strip()
    lastname = self.request.get('lastname').decode('utf-8').strip()
    forename = self.request.get('forename').decode('utf-8').strip()
    suffix = self.request.get('suffix')
    if suffix: suffix = decode('utf-8').strip()
    if username and \
          password_hash and \
          lastname and \
          forename and \
          email and \
          re.match('^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$', email):
      activation_code = uuid.uuid4().urn[9:]
      user = User.get_or_insert_by_username(username, password = password_hash, lastname = lastname, forename = forename, suffix = suffix, email = email, activation_code = activation_code)
      if user:
        mail.send_mail(sender= "edoardo.marcora@gmail.com",# "help@pubmedos.appspot.com",
                       to="%s %s <%s>" % (lastname, forename, email),
                       subject="Please activate your PubMed On Steroids account",
                       body="""
Dear %s %s:

Goto <https://pubmedos.appspot.com/activate/%s> to activate your PubMed On Steroids account!

The PubMed On Steroids Team :)
""" % (lastname, forename, activation_code))
      else:
        self.error(403)
    else:
      self.error(403)

class activate(Root):
  def get(self, activation_code):
    user = User.gql("WHERE activation_code = :1", activation_code).get()
    if user:
      user.activation_code = None
      user.put()
      self.success = True
    else:
      self.success = False
    self.html()

class login(Root):
  def post(self):
      username = str(self.request.get('username')).strip()
      password = str(self.request.get('password')).strip()
      user = None
      sid = None
      cookie = Cookie.SimpleCookie(self.request.headers.get('Cookie'))
      if cookie.has_key('pubmedos_sid'):
        sid = cookie['pubmedos_sid'].value
      if sid:
        session = memcache.get(sid)
        if session:
          un = session.get('username')
          pw = session.get('password')
          ra = session.get('remote_addr')
          if username == un and password == pw and self.request.remote_addr == ra:
            # store username, password and remote_addr in session
            cookie['pubmedos_sid']['max-age'] = SESSION_TIMEOUT
            memcache.set(sid, { 'username':un, 'password':pw, 'remote_addr':ra }, SESSION_TIMEOUT+(SESSION_TIMEOUT/10))
            self.response.headers['Set-Cookie'] = cookie.output(header='')
            self.json('authenticated')
            return
      user = User.get_by_username(username)
      if user:
        if user.activation_code:
          self.json('activate')
        else:
          if password == user.password:
            sid = str(uuid.uuid4())
            cookie['pubmedos_sid'] = sid
            cookie['pubmedos_sid']['max-age'] = SESSION_TIMEOUT
            # store username, password and remote_addr in session
            memcache.set(sid, { 'username': user.username, 'password': user.password, 'remote_addr': self.request.remote_addr }, SESSION_TIMEOUT+(SESSION_TIMEOUT/10))
            self.response.headers['Set-Cookie'] = cookie.output(header='')
            self.json('authenticated')
            return
          else:
            self.json('authenticate')
      else:
        self.json('register')

class logout(Root):
  def get(self):
    cookie = Cookie.SimpleCookie(self.request.headers.get('Cookie'))
    if cookie.has_key('pubmedos_sid'):
      sid = cookie['pubmedos_sid'].value
      if sid:
        memcache.delete(sid)
    self.response.headers['Set-Cookie'] = 'pubmedos_sid=; expires=Sat, 29-Mar-1969 00:00:00 GMT;'

