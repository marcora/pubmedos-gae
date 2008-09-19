import logging
import wsgiref.handlers

from google.appengine.ext import webapp

from models.article import Article
from models.rating import Rating
from models.folder import Folder
from models.filing import Filing

from controllers.app import *

class ArticlesFolders(RequestHandler):
  pass

class list(ArticlesFolders):
  def get(self, pmid):
    current_user = self.get_current_user()
    if current_user:
      article = Article.get_or_insert_by_pmid(pmid)
      rating = Rating.get_or_insert_by_user_and_article(current_user, article)
      if article and rating:
        selected = self.request.get('selected')
        if selected:
          selected_folders = [str(folder.key()) for folder in rating.folders]
          folders = []
          for folder in current_user.folders.order('title'):
            if str(folder.key()) in selected_folders:
              hash = folder.to_hash()
              hash['is_selected'] = True
              folders.append(hash)
            else:
              hash = folder.to_hash()
              hash['is_selected'] = False
              folders.append(hash)
        else:
          folders = [folder.to_hash() for folder in rating.folders]
        self.render_json(folders)
      else:
        self.error(404)
    else:
      self.error(401)

  def post(self, pmid): # add article to folder
    current_user = self.get_current_user()
    if current_user:
      article = Article.get_or_insert_by_pmid(pmid)
      rating = Rating.get_or_insert_by_user_and_article(current_user, article)
      if article and rating:
        title = self.request.get('title')
        if title:
          title = title.decode('utf-8')
          folder = Folder.get_or_insert_by_user_and_title(current_user, title)
          if folder:
            rating.add_folder(folder)
        else:
          self.error(404)
      else:
        self.error(404)
    else:
      self.error(401)

class item(ArticlesFolders):
  def post(self, pmid, id): # add article to folder
    current_user = self.get_current_user()
    if current_user:
      article = Article.get_or_insert_by_pmid(pmid)
      rating = Rating.get_or_insert_by_user_and_article(current_user, article)
      if article and rating:
        folder = Folder.get_by_id(int(id), parent=current_user)
        if folder:
          rating.add_folder(folder)
      else:
        self.error(404)
    else:
      self.error(401)

  def delete(self, pmid, id): # remove article from folder
    current_user = self.get_current_user()
    if current_user:
      article = Article.get_or_insert_by_pmid(pmid)
      rating = Rating.get_or_insert_by_user_and_article(current_user, article)
      if article and rating:
        folder = Folder.get_by_id(int(id), parent=current_user)
        if folder:
          rating.remove_folder(folder)
      else:
        self.error(404)
    else:
      self.error(401)

class dialog(ArticlesFolders):
  def get(self, pmid):
    current_user = self.get_current_user()
    if current_user:
      article = Article.get_or_insert_by_pmid(pmid)
      rating = Rating.get_or_insert_by_user_and_article(current_user, article)
      if article and rating:
        self.pmid = pmid
        self.render_template()
      else:
        self.error(404)
    else:
      self.error(401)



def main():
  urls = [('/articles/(\d+)/folders', list),
          ('/articles/(\d+)/folders/(\d+)', item),
          ('/articles/(\d+)/folders/dialog', dialog)]
  application = webapp.WSGIApplication(urls, debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
