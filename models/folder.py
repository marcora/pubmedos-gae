from google.appengine.ext import db
from models.user import User
# from models.filing import Filing

class Folder(db.Model):
    ## datastore schema
    user = db.ReferenceProperty(User, required=True, collection_name='folders')
    title = db.StringProperty(required=True, validator=lambda v: type(v) == type(u''))
    sup_folder = db.SelfReferenceProperty(collection_name='sub_folders')
    # filings
    filings_count_cache = db.IntegerProperty(required=True, default=0)
    updated_at = db.DateTimeProperty(required=True, auto_now=True)
    created_at = db.DateTimeProperty(required=True, auto_now_add=True)

    ## class methods
    @staticmethod
    def get_or_insert_by_user_and_title(user, title):
        folder = Folder.gql("WHERE user = :user AND title = :title AND ANCESTOR IS :user", user=user, title=title).get()
        if folder is None:
            folder = Folder(user=user, title=title, parent=user)
            folder.put()
        if folder.is_saved():
            return folder
        else:
            return None

    @staticmethod
    def get_by_user_and_title(user, title):
        return Folder.gql("WHERE user = :user AND title = :title AND ANCESTOR IS :user", user=user, title=title).get()

    ## instance methods
    def to_hash(self):
        return { 'id': self.key().id(), 'title': self.title, 'filings_count_cache': self.filings_count_cache }

    def get_ratings(self):
        return [filing.rating for filing in self.filings]
    ratings = property(get_ratings)

    def add_rating(self, rating):
        from models.filing import Filing
        filing = Filing.get_or_insert_by_folder_and_rating(self, rating)
        if filing:
            return True
        else:
            return False

    def remove_rating(self, rating):
        from models.filing import Filing
        filing = Filing.get_or_insert_by_folder_and_rating(self, rating)
        try:
            filing.delete()
            return True
        except:
            return False

    def put(self):
        # ensure uniqueness based on user and title
        if not self.is_saved and Folder.get_by_user_and_title(self.user, self.title):
            raise db.NotSavedError()
        return super(Folder, self).put()

    def delete(self):
        # cascade delete filings
        filings = [filing for filing in self.filings]
        db.delete([self]+filings)
