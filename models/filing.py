from google.appengine.ext import db
from models.folder import Folder
from models.rating import Rating

class Filing(db.Model):
    ## datastore schema
    folder = db.ReferenceProperty(Folder, required=True, collection_name='filings')
    rating = db.ReferenceProperty(Rating, required=True, collection_name='filings')

    ## class methods
    @staticmethod
    def get_or_insert_by_folder_and_rating(folder, rating):
        if folder.user.key() != rating.user.key(): raise 'folder and rating must belong to the same user'
        filing = Filing.gql("WHERE folder = :folder AND rating = :rating AND ANCESTOR IS :folder", folder=folder, rating=rating).get()
        if filing is None:
            filing = Filing(folder=folder, rating=rating, parent=folder)
            filing.put()
        if filing.is_saved():
            return filing
        else:
            return None

    ## instance methods
    def put(self):
        ret = super(Filing, self).put()
        # update folder filings count cache when filing is created
        self.folder.filings_count_cache = self.folder.filings.count()
        self.folder.put()
        return ret

    def delete(self):
        ret = super(Filing, self).delete()
        # update folder filings count cache when filing is deleted
        self.folder.filings_count_cache = self.folder.filings.count()
        self.folder.put()
        return ret
