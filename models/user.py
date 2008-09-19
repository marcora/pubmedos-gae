import operator
import re

from google.appengine.ext import db

class User(db.Model):
    ## datastore schema
    username = db.StringProperty(required=True, validator=lambda v: re.match('^\w+$', v))
    password = db.StringProperty(required=True)
    email = db.EmailProperty(required=True, validator=lambda v: re.match('^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$', v))
    salutation = db.StringProperty(default=u'', choices=set([u'',u'Mr',u'Ms',u'Dr',u'Prof']))
    last_name = db.StringProperty(required=True, validator=lambda v: type(v) == type(u''))
    first_name = db.StringProperty(required=True, validator=lambda v: type(v) == type(u''))
    middle_name = db.StringProperty(default=u'', validator=lambda v: type(v) == type(u''))
    suffix = db.StringProperty(default=u'', choices=set([u'',u'Jr',u'Sr',u'2nd',u'3rd',u'4th',u'5th']))
    affiliation = db.StringProperty(default=u'', validator=lambda v: type(v) == type(u''))
    activation_code = db.StringProperty()
    authentication_code = db.StringProperty()
    # ratings
    # folders
    # articles
    # reprints
    updated_at = db.DateTimeProperty(required=True, auto_now=True)
    created_at = db.DateTimeProperty(required=True, auto_now_add=True)

    ## class methods
    @staticmethod
    def get_or_insert_by_username(username, **kwds):
        username = str(username).strip()
        key_name = 'username:'+username
        user = User.get_by_key_name(key_name)
        if user is None:
            kwds.update({'username':username})
            user = User.get_or_insert(key_name, **kwds)
        return user

    @staticmethod
    def get_by_username(username):
        username = str(username).strip()
        key_name = 'username:'+username
        return User.get_by_key_name(key_name)

#    @staticmethod
#    def get_by_email(email):
#        return User.gql("WHERE email = :1", email).get()

    ## instance methods
    def get_rated_articles(self):
        return [rating.article for rating in self.ratings]
    rated_articles = property(get_rated_articles)

    def get_long_name(self):
        name = "%s %s %s %s %s" % (self.salutation, self.first_name, self.middle_name, self.last_name, self.suffix)
        re.sub('\s+', ' ', name)
        return name.strip()
    long_name = property(get_long_name)

    def get_short_name(self):
        pass
    short_name = property(get_short_name)

    def get_authored_articles(self):
        return [ rating.article for rating in self.ratings.order('-pmid') if rating.is_author ]
    authored_articles = property(get_authored_articles)

    def get_reprints(self):
        return [ rating.reprint for rating in self.ratings if rating.has_reprint ]
    reprints = property(get_reprints)

    def reprints_filesize_sum(self):
        reprints = self.reprints
        if reprints:
            return reduce(operator.add, [reprint.filesize for reprint in reprints])
        else:
            return 0

#    def put(self):
#        # ensure uniqueness based on email
#        if not self.is_saved and User.get_by_email(self.email):
#            raise db.NotSavedError()
#        return super(User, self).put()

    def delete(self):
        # prevent deletion
        pass
