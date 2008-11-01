from google.appengine.ext import db

from models.user import User
from models.article import Article
from models.reprint import Reprint
from models.folder import Folder

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
    annotation = db.TextProperty()
    xml = db.TextProperty()
    reprint = db.ReferenceProperty(Reprint, collection_name='ratings')
    folder_list = db.ListProperty(db.Key)
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
    def to_hash(self):
        return { 'id': self.pmid,
                 'rating': self.rating,
                 'file': self.is_file,
                 'favorite': self.is_favorite,
                 'read': self.is_read,
                 'work': self.is_work,
                 'author': self.is_author,
                 'reprint': self.has_reprint() }

    @property
    def folders(self):
        return Folder.get(self.folder_list)

    def has_reprint(self):
        return not self.reprint is None

    def update_rating(self, rating):
        try:
            if self.rating == int(rating): raise
            self.rating = int(rating)
            self.put()
            self.article.cache_ratings_stats()
            return True
        except:
            return False

    def update_annotation(self, annotation):
        try:
            self.annotation = db.Text(annotation)
            self.put()
            return True
        except:
            return False

    def toggle_file(self):
        value = not self.is_file
        self.is_file = value
        if not self.is_file:
            self.folder_list = []
        self.put()
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
        pass
