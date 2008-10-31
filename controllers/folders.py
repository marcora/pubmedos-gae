import logging

import base64
import urllib

from ncbi.eutils import epost

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from models.folder import Folder

from controllers.app import *

## base request handler
class Folders(RequestHandler):
  pass

## actions
class root(Folders):
  def get(self): # index
    current_user = self.get_current_user()
    if current_user:
      self.render_json([folder.to_hash() for folder in current_user.folders.order('title')])
    else:
      self.error(401)

  def post(self): # create
    current_user = self.get_current_user()
    if current_user:
      title = self.request.get('title')
      if title:
        title = title.decode('utf-8')
        folder = Folder.get_or_insert_by_user_and_title(current_user, title)
        if folder:
          self.render_json([folder.to_hash() for folder in current_user.folders.order('title')])
        else:
          self.error(404)
      else:
        self.error(404)
    else:
      self.error(401)

class item(Folders):
  def get(self, id): # show
    current_user = self.get_current_user()
    if current_user:
      folder = Folder.get_by_id(int(id), parent=current_user)
      if folder:
        env, key = epost(ids=[rating.pmid for rating in folder.ratings])
        if env and key:
          self.redirect("http://www.ncbi.nlm.nih.gov/sites/entrez?Db=pubmed&Cmd=DetailsSearch&term=%%23%s&WebEnv=%s&WebEnvRq=1&CmdTab=Folder_%s" % (key, urllib.quote_plus(env), urllib.quote_plus(base64.standard_b64encode(folder.title.encode('utf-8')))))
        else:
          self.error(404)
      else:
        self.error(404)
    else:
      self.error(401)

  def post(self, id): # update
    current_user = self.get_current_user()
    if current_user:
      title = self.request.get('title')
      if title:
        title = title.decode('utf-8')
        folder = Folder.get_by_user_and_title(current_user, title)
        if folder:
          self.error(400)
        else:
          folder = Folder.get_by_id(int(id), parent=current_user)
          if folder:
            folder.title = title
            folder.put()
          else:
            self.error(404)
      else:
        self.error(400)
    else:
      self.error(401)

  def delete(self, id): # destroy
    current_user = self.get_current_user()
    if current_user:
      folder = Folder.get_by_id(int(id), parent=current_user)
      if folder:
        folder.delete()
      else:
        self.error(404)
    else:
      self.error(401)

class root_dialog(Folders):
  def get(self):
    current_user = self.get_current_user()
    if current_user:
      self.folders = current_user.folders.order('title')
      self.render_template()
    else:
      self.error(401)

## routes
def main():
  urls = [('/folders', root),
          ('/folders/(\d+)', item),
          ('/folders/dialog', root_dialog)]
  application = webapp.WSGIApplication(urls, debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
