import logging, urllib, re

from ncbi.eutils import epost

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from config import *

from models.reprint import Reprint
from models.folder import Folder
from models.article import Article
from models.rating import Rating

from controllers.app import *

## base request handler
class Articles(RequestHandler):
  pass

## actions
class root(Articles):
  @login_required
  def get(self):
    current_user = self.current_user
    records = []
    id = self.request.get('id', allow_multiple=True)
    if id:
      pmids = [pmid for pmid in set(id)] # remove duplicates
      article_key_names = ['pmid:'+pmid for pmid in pmids]
      rating_key_names = ['username:'+current_user.username+'|'+'pmid:'+pmid for pmid in pmids]
      articles = Article.get_by_key_name(article_key_names)
      ratings = Rating.get_by_key_name(rating_key_names, parent=current_user)
      i = 0
      for article in articles:
        if article:
          rating = ratings[i]
          if rating:
            record = article.to_hash()
            record.update(rating.to_hash())
            records.append(record)
          else:
            records.append(article.to_hash)
        else:
          records.append({ 'id': pmids[i] })
        i += 1
    self.json(records)

class item(Articles):
  @login_required
  def get(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      record = article.to_hash()
      record.update(rating.to_hash_plus())
      self.json(record)

class item_rating(Articles):
  @login_required
  def post(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      value = self.request.get('value')
      if not (value and range(-1,6).count(int(value))):
        self.error(400)
      else:
        rating.update_rating(value)
        record = article.to_hash()
        record.update(rating.to_hash())
        self.json(record)

class item_annotation(Articles):
  @login_required
  def post(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      value = self.request.get('value')
      rating.update_annotation(value)
      record = rating.to_hash_plus()
      self.json(record)

class item_reprint(Articles):
  @login_required
  def get(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating and rating.has_reprint()):
      self.error(404)
    else:
      self.response.headers['Content-Type'] = 'application/pdf'
      self.response.out.write(rating.reprint.filedata);

  @login_required
  def post(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      filedata = self.request.body
      # check size and if pdf
      max_filesize = 10*1048576; # 10 megabytes
      if not (re.compile('^%PDF-1\.\d{1}').match(filedata) and (len(filedata) <= max_filesize)):
        self.error(403)
      else:
        reprint = Reprint.get_or_insert_by_filedata(filedata)
        if not reprint:
          self.error(400)
        else:
          rating.reprint = reprint
          rating.put()
        if not rating.has_reprint():
          self.error(400)

class item_file(Articles):
  @login_required
  def post(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      self.json(rating.toggle_file())

class item_favorite(Articles):
  @login_required
  def post(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      self.json(rating.toggle_favorite())

class item_work(Articles):
  @login_required
  def post(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      self.json(rating.toggle_work())

class item_read(Articles):
  @login_required
  def post(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      self.json(rating.toggle_read())

class item_author(Articles):
  @login_required
  def post(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      self.json(rating.toggle_author())

class root_file_redirect(Articles):
  @login_required
  def get(self):
    current_user = self.current_user
    ratings = Rating.gql("WHERE is_file = TRUE AND ANCESTOR IS :parent", parent=current_user)
    env, key = epost(ids=[rating.pmid for rating in ratings])
    if not (env and key):
      self.error(500)
    else:
      self.redirect("http://www.ncbi.nlm.nih.gov/sites/entrez?Db=pubmed&Cmd=DetailsSearch&term=%%23%s&WebEnv=%s&WebEnvRq=1&CmdTab=File" % (key, urllib.quote_plus(env)))

class root_toprated_redirect(Articles):
  @login_required
  def get(self):
    current_user = self.current_user
    ratings = Rating.gql("WHERE rating > 2 AND ANCESTOR IS :parent", parent=current_user)
    env, key = epost(ids=[rating.pmid for rating in ratings])
    if not (env and key):
      self.error(500)
    else:
      self.redirect("http://www.ncbi.nlm.nih.gov/sites/entrez?Db=pubmed&Cmd=DetailsSearch&term=%%23%s&WebEnv=%s&WebEnvRq=1&CmdTab=TopRated" % (key, urllib.quote_plus(env)))

class root_favorite_redirect(Articles):
  @login_required
  def get(self):
    current_user = self.current_user
    ratings = Rating.gql("WHERE is_favorite = TRUE AND ANCESTOR IS :parent", parent=current_user)
    env, key = epost(ids=[rating.pmid for rating in ratings])
    if not (env and key):
      self.error(500)
    else:
      self.redirect("http://www.ncbi.nlm.nih.gov/sites/entrez?Db=pubmed&Cmd=DetailsSearch&term=%%23%s&WebEnv=%s&WebEnvRq=1&CmdTab=Favorite" % (key, urllib.quote_plus(env)))

class root_work_redirect(Articles):
  @login_required
  def get(self):
    current_user = self.current_user
    ratings = Rating.gql("WHERE is_work = TRUE AND ANCESTOR IS :parent", parent=current_user)
    env, key = epost(ids=[rating.pmid for rating in ratings])
    if not (env and key):
      self.error(500)
    else:
      self.redirect("http://www.ncbi.nlm.nih.gov/sites/entrez?Db=pubmed&Cmd=DetailsSearch&term=%%23%s&WebEnv=%s&WebEnvRq=1&CmdTab=Work" % (key, urllib.quote_plus(env)))

class root_read_redirect(Articles):
  @login_required
  def get(self):
    current_user = self.current_user
    ratings = Rating.gql("WHERE is_read = TRUE AND ANCESTOR IS :parent", parent=current_user)
    env, key = epost(ids=[rating.pmid for rating in ratings])
    if not (env and key):
      self.error(500)
    else:
      self.redirect("http://www.ncbi.nlm.nih.gov/sites/entrez?Db=pubmed&Cmd=DetailsSearch&term=%%23%s&WebEnv=%s&WebEnvRq=1&CmdTab=Read" % (key, urllib.quote_plus(env)))

class root_author_redirect(Articles):
  @login_required
  def get(self):
    current_user = self.current_user
    ratings = Rating.gql("WHERE is_author = TRUE AND ANCESTOR IS :parent", parent=current_user)
    env, key = epost(ids=[rating.pmid for rating in ratings])
    if not (env and key):
      self.error(500)
    else:
      self.redirect("http://www.ncbi.nlm.nih.gov/sites/entrez?Db=pubmed&Cmd=DetailsSearch&term=%%23%s&WebEnv=%s&WebEnvRq=1&CmdTab=Author" % (key, urllib.quote_plus(env)))

class item_xml(Articles):
  @login_required
  def get(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      content = rating.xml or article.xml
      self.xml(content)

class item_sponsored_links(Articles):
  def get(self, pmid):
    article = Article.get_or_insert_by_pmid(pmid)
    if article:
      record = article.record()
      self.pmid = pmid
      self.title = record['title']
      self.authors = record['authors']
      self.source = record['source']
      self.abstract = record['abstract']
      self.keywords = record['keywords']
      self.template()
    else:
      self.error(404)


def application():
  urls = [('/articles/?', root),
          ('/articles/file/redirect', root_file_redirect),
          ('/articles/toprated/redirect', root_toprated_redirect),
          ('/articles/favorite/redirect', root_favorite_redirect),
          ('/articles/work/redirect', root_work_redirect),
          ('/articles/read/redirect', root_read_redirect),
          ('/articles/author/redirect', root_author_redirect),
          ('/articles/(\d+)', item),
          ('/articles/(\d+)/file', item_file),
          ('/articles/(\d+)/favorite', item_favorite),
          ('/articles/(\d+)/work', item_work),
          ('/articles/(\d+)/read', item_read),
          ('/articles/(\d+)/author', item_author),
          ('/articles/(\d+)/rating', item_rating),
          ('/articles/(\d+)/annotation', item_annotation),
          ('/articles/(\d+)/reprint', item_reprint),
          ('/articles/(\d+)/sponsored_links', item_sponsored_links)]
  return webapp.WSGIApplication(urls, debug=DEBUG)

def main():
  run_wsgi_app(application())

if __name__ == '__main__':
  main()
