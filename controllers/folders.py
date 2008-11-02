import logging

import base64
import urllib

from ncbi.eutils import epost

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from config import *

from models.folder import Folder

from controllers.app import *

## base request handler
class Folders(RequestHandler):
  pass

## actions
class root(Folders):
  @login_required
  def get(self): # index
    current_user = self.current_user
    self.json([folder.to_hash() for folder in current_user.folders.order('title')])

  @login_required
  def post(self): # create
    current_user = self.current_user
    title = self.request.get('title')
    if title:
      title = title.decode('utf-8')
      folder = Folder.get_or_insert_by_user_and_title(current_user, title)
      if folder:
        self.json([folder.to_hash() for folder in current_user.folders.order('title')])
      else:
        self.error(500)
    else:
      self.error(400)

class item(Folders):
  @login_required
  def get(self, id): # show
    current_user = self.current_user
    folder = Folder.get_by_id(int(id), parent=current_user)
    if folder:
      self.json(folder.to_hash())
    else:
      self.error(404)

  @login_required
  def post(self, id): # update
    current_user = self.current_user
    title = self.request.get('title')
    if title:
      title = title.decode('utf-8')
      folder = Folder.get_by_user_and_title(current_user, title)
      if folder:
        self.error(403) # can't rename with title of existing folder
      else:
        folder = Folder.get_by_id(int(id), parent=current_user)
        if folder:
          folder.title = title
          folder.put()
          self.json(folder.to_hash())
        else:
          self.error(404)
    else:
      self.error(400)

  @login_required
  def delete(self, id): # destroy
    current_user = self.current_user
    folder = Folder.get_by_id(int(id), parent=current_user)
    if folder:
      folder.delete()
    else:
      self.error(404)

class item_articles(Folders):
  @login_required
  def get(self, id):
    current_user = self.current_user
    folder = Folder.get_by_id(int(id), parent=current_user)
    if folder:
      records = []
      for rating in folder.ratings:
        record = rating.article.to_hash()
        record.update(rating.to_hash())
        records.append(record)
      self.json(records)
    else:
      self.error(404)

class item_articles_redirect(Folders):
  @login_required
  def get(self, id):
    current_user = self.current_user
    folder = Folder.get_by_id(int(id), parent=current_user)
    if folder:
      env, key = epost(ids=[rating.pmid for rating in folder.ratings])
      if env and key:
        self.redirect("http://www.ncbi.nlm.nih.gov/sites/entrez?Db=pubmed&Cmd=DetailsSearch&term=%%23%s&WebEnv=%s&WebEnvRq=1&CmdTab=Folder_%s" % (key, urllib.quote_plus(env), urllib.quote_plus(base64.standard_b64encode(folder.title.encode('utf-8')))))
      else:
        self.error(500)
    else:
      self.error(404)

class root_dialog(Folders):
  @login_required
  def get(self):
    current_user = self.current_user
    self.folders = current_user.folders.order('title')
    self.template()


def application():
  urls = [('/folders/?', root),
          ('/folders/(\d+)', item),
          ('/folders/(\d+)/articles/?', item_articles),
          ('/folders/(\d+)/articles/redirect', item_articles_redirect),
          ('/folders/dialog', root_dialog)]
  return webapp.WSGIApplication(urls, debug=DEBUG)

def main():
  run_wsgi_app(application())

if __name__ == '__main__':
  main()
