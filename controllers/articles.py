import logging
import urllib
import re

from sets import Set
from ncbi.eutils import epost

from postmarkup import postmarkup #from textile import textile

import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.ext import webapp

from models.article import Article
from models.rating import Rating
from models.folder import Folder
from models.filing import Filing
from models.reprint import Reprint

from controllers.app import *

# base request handler
class Articles(RequestHandler):
  pass


## helpers

def annotation_to_html(annotation):
  annotation_markup = postmarkup.create(use_pygments=False)
  annotation_markup.add_tag(u'pmid',
                            postmarkup.SearchTag,
                            u'pmid',
                            u"http://www.ncbi.nlm.nih.gov/pubmed/%s", u'pubmed.gov')
  annotation_markup.add_tag(u'sub', postmarkup.SimpleTag, u'sub', u'sub')
  annotation_markup.add_tag(u'sup', postmarkup.SimpleTag, u'sup', u'sup')
  return annotation_markup(annotation) #return textile.textile(annotation.encode('utf-8'), head_offset=3, sanitize=1, encoding='utf-8', output='utf-8')


## actions

class list(Articles):
  @login_required
  def get(self):
    current_user = self.current_user
    ret = []
    id = self.request.get('id', allow_multiple=True)
    if id:
      pmids = [pmid for pmid in Set(id)] # remove duplicates
      article_key_names = ['pmid:'+pmid for pmid in pmids]
      rating_key_names = ['username:'+current_user.username+'|'+'pmid:'+pmid for pmid in pmids]
      articles = Article.get_by_key_name(article_key_names)
      ratings = Rating.get_by_key_name(rating_key_names, parent=current_user)
      i = 0
      for article in articles:
        if article:
          rating = ratings[i]
          if rating:
            ret.append({ 'article_id':article.pmid, 'ratings_average_rating':article.ratings_average_rating_cache, 'ratings_count':article.ratings_count_cache, 'rating':rating.rating, 'file':rating.is_file, 'favorite':rating.is_favorite, 'read':rating.is_read, 'work':rating.is_work, 'author':rating.is_author })
          else:
            ret.append({ 'article_id':article.pmid, 'ratings_average_rating':article.ratings_average_rating_cache, 'ratings_count':article.ratings_count_cache })
        else:
          ret.append({ 'article_id': pmids[i] })
        i += 1
    self.render_json(ret)

class item(Articles):
  @login_required
  def get(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      if rating.annotation:
        annotation_html = annotation_to_html(rating.annotation)
      else:
        annotation_html = '<img class="annotation_img" alt="[annotation]" src="chrome://pubmedos/skin/pencil.png" />&nbsp;Click here to add a private annotation to this article'
      if rating.is_file:
        folders = [folder.to_hash() for folder in rating.folders]
      else:
        folders = []
      self.render_json({ 'article_id': article.pmid,
                         'ratings_average_rating': article.ratings_average_rating_cache,
                         'ratings_count': article.ratings_count_cache,
                         'rating': rating.rating,
                         'file': rating.is_file,
                         'favorite': rating.is_favorite,
                         'work': rating.is_work,
                         'read': rating.is_read,
                         'author': rating.is_author,
                         'reprint': rating.has_reprint,
                         'annotation': rating.annotation,
                         'annotation_html': annotation_html,
                         'folders': folders,
                         })

class update_rating(Articles):
  @login_required
  def post(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      value = self.request.get('rating')
      if not (value and range(-1,6).count(int(value))):
        self.error(400)
      else:
        rating.rating = int(value)
        rating.put()
        article.set_ratings_stats()
        self.render_json({
            'ratings_average_rating': article.ratings_average_rating_cache,
            'ratings_count': article.ratings_count_cache,
            'rating': rating.rating,
            })

class update_annotation(Articles):
  @login_required
  def post(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      value = self.request.get('annotation')
      if not value:
        self.error(400)
      else:
        rating.annotation = db.Text(value, encoding='utf-8')
        rating.put()
        if rating.annotation:
          annotation_html = annotation_to_html(rating.annotation)
        else:
          annotation_html = '<img class="annotation_img" alt="[annotation]" src="chrome://pubmedos/skin/pencil.png" />&nbsp;Click here to add a private annotation to this article'
        self.render_json({
            'annotation': rating.annotation,
            'annotation_html': annotation_html,
            })

class reprint(Articles):
  @login_required
  def get(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating and rating.has_reprint):
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
        self.error(400)
      else:
        reprint = Reprint.get_or_insert_by_filedata(filedata)
        if not reprint:
          self.error(400)
        else:
          rating.reprint = reprint
          rating.put()
        if not rating.has_reprint:
          self.error(400)
        else:
          self.response.headers['Content-Type'] = 'application/pdf'
          self.response.out.write(rating.reprint.filedata);

class toggle_file(Articles):
  @login_required
  def post(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      self.render_json(rating.toggle_file())

class toggle_favorite(Articles):
  @login_required
  def post(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      self.render_json(rating.toggle_favorite())

class toggle_work(Articles):
  @login_required
  def post(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      self.render_json(rating.toggle_work())

class toggle_read(Articles):
  @login_required
  def post(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      self.render_json(rating.toggle_read())

class toggle_author(Articles):
  @login_required
  def post(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      self.render_json(rating.toggle_author())

class redirect_file(Articles):
  @login_required
  def get(self):
    current_user = self.current_user
    ratings = Rating.gql("WHERE is_file = TRUE AND ANCESTOR IS :parent", parent=current_user)
    env, key = epost(ids=[rating.pmid for rating in ratings])
    if not (env and key):
      self.error(404)
    else:
      self.redirect("http://www.ncbi.nlm.nih.gov/sites/entrez?Db=pubmed&Cmd=DetailsSearch&term=%%23%s&WebEnv=%s&WebEnvRq=1&CmdTab=File" % (key, urllib.quote_plus(env)))

class redirect_toprated(Articles):
  @login_required
  def get(self):
    current_user = self.current_user
    ratings = Rating.gql("WHERE rating > 2 AND ANCESTOR IS :parent", parent=current_user)
    env, key = epost(ids=[rating.pmid for rating in ratings])
    if not (env and key):
      self.error(404)
    else:
      self.redirect("http://www.ncbi.nlm.nih.gov/sites/entrez?Db=pubmed&Cmd=DetailsSearch&term=%%23%s&WebEnv=%s&WebEnvRq=1&CmdTab=TopRated" % (key, urllib.quote_plus(env)))

class redirect_favorite(Articles):
  @login_required
  def get(self):
    current_user = self.current_user
    ratings = Rating.gql("WHERE is_favorite = TRUE AND ANCESTOR IS :parent", parent=current_user)
    env, key = epost(ids=[rating.pmid for rating in ratings])
    if not (env and key):
      self.error(404)
    else:
      self.redirect("http://www.ncbi.nlm.nih.gov/sites/entrez?Db=pubmed&Cmd=DetailsSearch&term=%%23%s&WebEnv=%s&WebEnvRq=1&CmdTab=Favorite" % (key, urllib.quote_plus(env)))

class redirect_work(Articles):
  @login_required
  def get(self):
    current_user = self.current_user
    ratings = Rating.gql("WHERE is_work = TRUE AND ANCESTOR IS :parent", parent=current_user)
    env, key = epost(ids=[rating.pmid for rating in ratings])
    if not (env and key):
      self.error(404)
    else:
      self.redirect("http://www.ncbi.nlm.nih.gov/sites/entrez?Db=pubmed&Cmd=DetailsSearch&term=%%23%s&WebEnv=%s&WebEnvRq=1&CmdTab=Work" % (key, urllib.quote_plus(env)))

class redirect_read(Articles):
  @login_required
  def get(self):
    current_user = self.current_user
    ratings = Rating.gql("WHERE is_read = TRUE AND ANCESTOR IS :parent", parent=current_user)
    env, key = epost(ids=[rating.pmid for rating in ratings])
    if not (env and key):
      self.error(404)
    else:
      self.redirect("http://www.ncbi.nlm.nih.gov/sites/entrez?Db=pubmed&Cmd=DetailsSearch&term=%%23%s&WebEnv=%s&WebEnvRq=1&CmdTab=Read" % (key, urllib.quote_plus(env)))

class redirect_author(Articles):
  @login_required
  def get(self):
    current_user = self.current_user
    ratings = Rating.gql("WHERE is_author = TRUE AND ANCESTOR IS :parent", parent=current_user)
    env, key = epost(ids=[rating.pmid for rating in ratings])
    if not (env and key):
      self.error(404)
    else:
      self.redirect("http://www.ncbi.nlm.nih.gov/sites/entrez?Db=pubmed&Cmd=DetailsSearch&term=%%23%s&WebEnv=%s&WebEnvRq=1&CmdTab=Author" % (key, urllib.quote_plus(env)))

class ads(Articles):
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
      self.render_template()
    else:
      self.error(404)


## routes

def main():
  urls = [('/articles/?', list),
          ('/articles/file/?', redirect_file),
          ('/articles/toprated/?', redirect_toprated),
          ('/articles/favorite/?', redirect_favorite),
          ('/articles/work/?', redirect_work),
          ('/articles/read/?', redirect_read),
          ('/articles/author/?', redirect_author),
          ('/articles/(\d+)/?', item),
          ('/articles/(\d+)/file/?', toggle_file),
          ('/articles/(\d+)/favorite/?', toggle_favorite),
          ('/articles/(\d+)/work/?', toggle_work),
          ('/articles/(\d+)/read/?', toggle_read),
          ('/articles/(\d+)/author/?', toggle_author),
          ('/articles/(\d+)/rating/?', update_rating),
          ('/articles/(\d+)/annotation/?', update_annotation),
          ('/articles/(\d+)/reprint/?', reprint),
          ('/articles/(\d+)/ads/?', ads)]
  application = webapp.WSGIApplication(urls, debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
