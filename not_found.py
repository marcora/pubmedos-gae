from webob.exc import HTTPNotFound
from google.appengine.ext.webapp.util import run_wsgi_app

def main():
    response = HTTPNotFound()
    run_wsgi_app(response)

if __name__ == '__main__':
    main()
