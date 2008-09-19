from google.appengine.ext import db

from models.user import User
# from models.filing import Filing

class Folder(db.Model):
    ## datastore schema
    title = db.StringProperty(required=True)
    description = db.TextProperty()
    user = db.ReferenceProperty(User, required=True, collection_name='folders')
    sup_folder = db.SelfReferenceProperty(collection_name='sub_folders')
    path_cache = db.StringProperty() # required=True?
    # filings

    ## class methods
    @staticmethod
    def get_or_insert_by_user_and_title(user, title, description=None, sup_folder=None):
        folder = Folder.gql("WHERE user = :user AND title = :title AND sup_folder = :sup_folder AND ANCESTOR IS :user", user=user, title=title, sup_folder=sup_folder).get()
        if not folder:
            folder = Folder(user=user, title=title, description=description, sup_folder=sup_folder, parent=user)
            folder.put()
        if folder.is_saved():
            return folder
        else:
            return None

    @staticmethod
    def get_or_insert_by_user_and_path(user, path):
        titles = [title.strip() for title in path.split('/') if title.strip()]
        if not titles: return None
        sup_folder = None
        for title in titles:
            folder = Folder.get_or_insert_by_user_and_title(user, title, sup_folder=sup_folder)
            if not folder: break
            sup_folder = folder
        return folder

    ## instance methods
    def to_hash(self):
        if self.sup_folder:
            return { 'id': self.key().id(), 'title': self.title, 'parent_id': self.sup_folder.key().id(), 'path': self.path_cache }
        else:
            return { 'id': self.key().id(), 'title': self.title, 'parent_id': None }

    def get_ratings(self):
        return [filing.rating for filing in self.filings]
    ratings = property(get_ratings)

    def add_rating(self, rating):
        from models.filing import Filing
        try:
            Filing.get_or_insert_by_folder_and_rating(self, rating)
            return True
        except:
            return False

    def remove_rating(self, rating):
        from models.filing import Filing
        try:
            filing = Filing.get_or_insert_by_folder_and_rating(self, rating)
            filing.delete()
            return True
        except:
            return False

    def get_descendant_ratings(self):
        descendant_ratings = []
        for folder in self.descendant_folders:
            descendant_ratings + [filing.rating for filing in folder.filings]
        return descendant_ratings
    descendant_ratings = property(get_descendant_ratings)


    def get_or_insert_sub_folder(self, title, description=None):
        return Folder.get_or_insert_by_user_and_title(self.user, title=title, description=description, sup_folder=self)

    def get_self_and_ancestor_folders(self):
        folder, ancestor_folders = (self, [])
        while folder.sup_folder:
            ancestor_folders.append(folder)
            folder = folder.sup_folder
        ancestor_folders.append(folder)
        return ancestor_folders
    self_and_ancestor_folders = property(get_self_and_ancestor_folders)

    def get_ancestor_folders(self):
        return self.self_and_ancestor_folders.remove(self)
    ancestor_folders = property(get_ancestor_folders)

    def get_root_folder(self):
        root_folder = self
        while root_folder.sup_folder:
            root_folder = root_folder.sup_folder
        return root_folder
    root_folder = property(get_root_folder)

    def get_self_and_sibling_folders(self):
        if self.sup_folder:
            return self.sup_folder.sub_folders
        else:
            return self.user.root_folders
    self_and_sibling_folders = property(get_self_and_sibling_folders)

    def get_sibling_folders(self):
        return self.self_and_sibling_folders.remove(self)
    sibling_folders = property(get_sibling_folders)

    def get_descendant_folders(self):
        descendant_folders = [folder for folder in self.sub_folders]
        for sub_folder in self.sub_folders:
            descendant_folders + sub_folder.descendant_folders
        return descendant_folders
    descendant_folders = property(get_descendant_folders)

    def get_path(self):
        return '/'.join([folder.title for folder in self.self_and_ancestor_folders])
    path = property(get_path)

    def put(self):
        self.path_cache = self.path
        return super(Folder, self).put()

    def set_title(self, title):
        self.title = title
        self.put()
        for descendant_folder in self.descendant_folders:
            descendant_folder.put()
