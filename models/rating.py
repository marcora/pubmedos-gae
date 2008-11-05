from models.user import User
from models.article import Article
from models.reprint import Reprint

from models.app import *

from postmarkup import postmarkup

class Rating(Model):
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
    annotation = db.TextProperty(validator=lambda v: isinstance(v, unicode))
    xml = db.TextProperty(validator=lambda v: isinstance(v, unicode))
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
    def to_hash(self, include_annotation=False, include_folders=False):
        hash = {'id': self.pmid,
                'rating': self.rating,
                'file': self.is_file,
                'favorite': self.is_favorite,
                'read': self.is_read,
                'work': self.is_work,
                'author': self.is_author,
                'reprint': self.has_reprint() }
        if include_annotation:
            hash.update({'annotation': self.annotation, 'annotation_html': self.annotation_html })
        if self.is_file and include_folders:
            folders = [folder.to_hash() for folder in self.folders if folder]
            hash.update({'folders': folders })
        return hash

    @property
    def folders(self):
      from models.folder import Folder
      return Folder.get(self.folder_list)

    def has_reprint(self):
        return not self.reprint is None

    @property
    def annotation_html(self):
      if self.annotation:
        annotation_markup = postmarkup.create(use_pygments=False)
        annotation_markup.add_tag(u'pubmed',
                                  postmarkup.SearchTag,
                                  u'pubmed',
                                  u"http://www.ncbi.nlm.nih.gov/pubmed/%s", u'pubmed.gov')
        annotation_markup.add_tag(u'sub', postmarkup.SimpleTag, u'sub', u'sub')
        annotation_markup.add_tag(u'sup', postmarkup.SimpleTag, u'sup', u'sup')
        return annotation_markup(self.annotation)
      else:
        return '<img class="annotation_img" alt="[annotation]" src="chrome://pubmedos/skin/pencil.png" />&nbsp;Click here to add a private annotation to this article'

    def update_annotation(self, annotation):
        try:
            self.annotation = db.Text(annotation.decode('utf-8'))
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

    def update_rating(self, rating):
        try:
            if self.rating == int(rating): raise
            self.rating = int(rating)
            self.put()
            self.article.cache_ratings_stats()
            return True
        except:
            return False

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
