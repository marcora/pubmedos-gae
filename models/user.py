import operator
import re

from google.appengine.ext import db

class User(db.Model):
    ## datastore schema
    username = db.StringProperty(required=True, validator=lambda v: re.match('^\w+$', v))
    password = db.StringProperty(required=True)
    email = db.EmailProperty(required=True, validator=lambda v: re.match('^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$', v))
    lastname = db.StringProperty(required=True, validator=lambda v: type(v) == type(u''))
    forename = db.StringProperty(required=True, validator=lambda v: type(v) == type(u''))
    suffix = db.StringProperty(default=u'', choices=set([u'',u'Jr',u'Sr',u'2nd',u'3rd',u'4th',u'5th']))
    activation_code = db.StringProperty()
    # ratings
    # folders
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

    ## instance methods
    @property
    def name(self):
        name = "%s %s %s" % (self.forename, self.lastname, self.suffix)
        re.sub('\s+', ' ', name)
        return name.strip()

    @property
    def authored_articles(self):
        return [ rating.article for rating in self.ratings if rating.is_author ]

    @property
    def reprints(self):
        return [ rating.reprint for rating in self.ratings if rating.has_reprint() ]

    @property
    def reprints_filesize_sum(self):
        reprints = self.reprints
        if reprints:
            return reduce(operator.add, [reprint.filesize for reprint in reprints])
        else:
            return 0
