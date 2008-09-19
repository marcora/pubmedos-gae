import re
from google.appengine.ext import db
from models.article import Article
from models.user import User
from models.reprint import Reprint
# from models.filing import Filing

class Rating(db.Model):
    ## datastore schema
    user = db.ReferenceProperty(User, required=True, collection_name='ratings')
    article = db.ReferenceProperty(Article, required=True, collection_name='ratings')
    pmid = db.IntegerProperty(required=True)
    rating = db.IntegerProperty(required=True, default=0, choices=set(range(-1,6)))
    is_file = db.BooleanProperty(required=True, default=False)
    is_favorite = db.BooleanProperty(required=True, default=False)
    is_work = db.BooleanProperty(required=True, default=False)
    is_read = db.BooleanProperty(required=True, default=False)
    is_author = db.BooleanProperty(required=True, default=False)
    reprint = db.ReferenceProperty(Reprint, collection_name='ratings')
    annotation = db.TextProperty()
    # filings
    updated_at = db.DateTimeProperty(required=True, auto_now=True)
    created_at = db.DateTimeProperty(required=True, auto_now_add=True)

    ## class methods
    @staticmethod
    def get_or_insert_by_user_and_article(user, article):
        key_name = 'username:'+user.username+'|'+'pmid:'+str(article.pmid)
        rating = Rating.get_by_key_name(key_name)
        if rating is None:
            rating = Rating.get_or_insert(key_name, pmid=article.pmid, user=user, article=article, parent=user)
        return rating

    ## instance methods
    def has_reprint(self):
        return not self.reprint is None
    has_reprint = property(has_reprint)

    def get_folders(self):
        return [filing.folder for filing in self.filings]
    folders = property(get_folders)

    def add_folder(self, folder):
        from models.filing import Filing
        filing = Filing.get_or_insert_by_folder_and_rating(folder, self)
        if filing:
            return True
        else:
            return False

    def remove_folder(self, folder):
        from models.filing import Filing
        filing = Filing.get_or_insert_by_folder_and_rating(folder, self)
        try:
            filing.delete()
            return True
        except:
            return False

    def toggle_file(self):
        value = not self.is_file
        self.is_file = value
        self.put()
        # delete filings if rating is not file
        if not self.is_file:
            filings = [filing for filing in self.filings]
            if filings:
                db.delete(filings)
        return self.is_file

    def toggle_favorite(self):
        value = not self.is_favorite
        self.is_favorite = value
        self.put()
        return self.is_favorite

    def toggle_work(self):
        value = not self.is_work
        self.is_work = value
        self.put()
        return self.is_work

    def toggle_read(self):
        value = not self.is_read
        self.is_read = value
        self.put()
        return self.is_read

    def toggle_author(self):
        value = not self.is_author
        self.is_author = value
        self.put()
        return self.is_author

    def delete(self):
        # cascade delete filings
        filings = [filing for filing in self.filings]
        db.delete([self]+filings)

#    def put(self):
#        # delete filings if rating is not file
#        key = super(Rating, self).put()
#        filings = [filing for filing in self.filings]
#        if filings and not self.is_file:
#            db.delete(filings)
#        return key
