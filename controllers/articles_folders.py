from controllers.app import *

## base request handler
class ArticlesFolders(Controller):
  pass

## actions
class root(ArticlesFolders):
  @login_required
  def get(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      selected = self.request.get('selection')
      if selected:
        folders = []
        for folder in current_user.folders.order('title'):
          if folder.key() in rating.folder_list:
            record = folder.to_hash()
            record.update({ 'selected': True })
            folders.append(record)
          else:
            record = folder.to_hash()
            record.update({ 'selected': False })
            folders.append(record)
      else:
        folders = [folder.to_hash() for folder in rating.folders if folder]
      self.json(folders)

class root_dialog(ArticlesFolders):
  @login_required
  def get(self, pmid):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if article and rating:
      self.pmid = pmid
      self.template()
    else:
      self.error(404)

class item(ArticlesFolders):
  @login_required
  def post(self, pmid, folder_id):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      folder = Folder.get_by_id(int(folder_id), parent=current_user)
      if folder:
        self.json(folder.append_rating(rating))
      else:
        self.error(400)

  @login_required
  def delete(self, pmid, folder_id):
    current_user = self.current_user
    article = Article.get_or_insert_by_pmid(pmid)
    rating = Rating.get_or_insert_by_user_and_article(current_user, article)
    if not (article and rating):
      self.error(404)
    else:
      folder = Folder.get_by_id(int(folder_id), parent=current_user)
      if folder:
        self.json(folder.remove_rating(rating))
      else:
        self.error(400)

