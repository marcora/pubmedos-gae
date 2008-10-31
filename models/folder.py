from google.appengine.ext import db

from models.user import User

# transaction decorator
def transaction(wrapped):
    def wrapper(*args, **kwargs):
        return db.run_in_transaction(wrapped, *args, **kwargs)
    return wrapper

class Folder(db.Model):
    ## datastore schema
    user = db.ReferenceProperty(User, required=True, collection_name='folders')
    title = db.CategoryProperty(required=True)
    # sup_folder = db.SelfReferenceProperty(collection_name='sub_folders')
    ratings_count_cache = db.IntegerProperty(required=True, default=0)
    updated_at = db.DateTimeProperty(required=True, auto_now=True)
    created_at = db.DateTimeProperty(required=True, auto_now_add=True)

    ## class methods
    @staticmethod
    def get_or_insert_by_user_and_title(user, title):
        folder = Folder.gql("WHERE user = :user AND title = :title AND ANCESTOR IS :user", user=user, title=title).get()
        if folder is None:
            folder = Folder(user=user, title=db.Category(title), parent=user)
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
        return { 'id': self.key().id(), 'title': self.title, 'ratings_count': self.ratings_count_cache }

    @property
    def ratings(self):
        return Rating.gql('WHERE folder_list = :1', self.key())

    def put(self):
        # ensure uniqueness based on user and title
        if not self.is_saved and Folder.get_by_user_and_title(self.user, self.title):
            raise db.NotSavedError()
        return super(Folder, self).put()

    def delete(self):
        # cleanup ratings folder list
        for rating in self.ratings:
            self.remove_rating(rating)
        return super(Folder, self).delete()

    @transaction
    def append_rating(self, rating):
        try:
            if self.user.key() != rating.user.key(): raise Exception()
            if not self.key() in rating.folder_list:
                rating.folder_list.append(self.key())
                rating.put()
                self.ratings_count_cache += 1
                self.put()
            return True
        except:
            return False

    @transaction
    def remove_rating(self, rating):
        try:
            if self.user.key() != rating.user.key(): raise Exception()
            if self.key() in rating.folder_list:
                rating.folder_list.remove(self.key())
                rating.put()
                self.ratings_count_cache -= 1
                self.put()
            return True
        except:
            return False


from models.rating import Rating
