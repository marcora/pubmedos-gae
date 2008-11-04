from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from controllers import *

## routes
def application():
  urls = [('/', root.index),
          ('/help', root.help),
          ('/about', root.about),
          ('/terms', root.terms),
          ('/privacy', root.privacy),
          ('/register', root.register),
          ('/activate/(\S+)', root.activate),
          ('/login', root.login),
          ('/logout', root.logout),
          ('/users/(\w+)', users.item),
          ('/articles/?', articles.root),
          ('/articles/file/redirect', articles.root_file_redirect),
          ('/articles/toprated/redirect', articles.root_toprated_redirect),
          ('/articles/favorite/redirect', articles.root_favorite_redirect),
          ('/articles/work/redirect', articles.root_work_redirect),
          ('/articles/read/redirect', articles.root_read_redirect),
          ('/articles/author/redirect', articles.root_author_redirect),
          ('/articles/(\d+)', articles.item),
          ('/articles/(\d+)/file', articles.item_file),
          ('/articles/(\d+)/favorite', articles.item_favorite),
          ('/articles/(\d+)/work', articles.item_work),
          ('/articles/(\d+)/read', articles.item_read),
          ('/articles/(\d+)/author', articles.item_author),
          ('/articles/(\d+)/rating', articles.item_rating),
          ('/articles/(\d+)/annotation', articles.item_annotation),
          ('/articles/(\d+)/reprint', articles.item_reprint),
          ('/articles/(\d+)/sponsored_links', articles.item_sponsored_links),
          ('/articles/(\d+)/xml', articles.item_xml),
          ('/folders/?', folders.root),
          ('/folders/(\d+)', folders.item),
          ('/folders/(\d+)/articles/?', folders.item_articles),
          ('/folders/(\d+)/articles/redirect', folders.item_articles_redirect),
          ('/folders/dialog', folders.root_dialog),
          ('/articles/(\d+)/folders/?', articles_folders.root),
          ('/articles/(\d+)/folders/(\d+)', articles_folders.item),
          ('/articles/(\d+)/folders/dialog', articles_folders.root_dialog),
          ('/admin/?', admin.root)]

  return webapp.WSGIApplication(urls, debug=True)

def main():
  run_wsgi_app(application())

if __name__ == '__main__':
  main()
