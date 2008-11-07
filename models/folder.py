from models.app import *

from models.user import User


class Folder(Model):
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
        folder = Folder.get_by_user_and_title(user, title)
        if folder is None:
            folder = Folder(user=user, title=db.Category(title), parent=user)
            folder.put()
        if folder.is_saved():
            return folder
        else:
            return None

    @staticmethod
    def get_by_user_and_title(user, title):
        title = title.decode('utf-8')
        return Folder.gql("WHERE user = :user AND title = :title AND ANCESTOR IS :user", user=user, title=title).get()

    ## instance methods
    def to_hash(self):
        return {'id': self.key().id(),
                'title': self.title,
                'ratings_count': self.ratings_count_cache }

    @property
    def ratings(self):
        from models.rating import Rating
        return Rating.gql('WHERE folder_list = :1', self.key())

    def put(self):
        # ensure uniqueness based on user and title
        if not self.is_saved() and Folder.get_by_user_and_title(self.user, self.title):
            raise db.NotSavedError()
        return super(Folder, self).put()

