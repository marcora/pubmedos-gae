import re
from datetime import datetime
from google.appengine.ext import db
from google.appengine.api import urlfetch
from xml.etree.ElementTree import fromstring, tostring

# transaction decorator
def transaction(method):
  def wrapper(*args, **kwds):
    return db.run_in_transaction(method, *args, **kwds)
  return wrapper

class Article(db.Model):
    ## datastore schema
    pmid = db.IntegerProperty(required=True)
    xml = db.TextProperty(required=True)
    # ratings
    ratings_average_rating_cache = db.FloatProperty()
    ratings_count_cache = db.IntegerProperty(required=True, default=0)
    fetched_at = db.DateTimeProperty(required=True)
    updated_at = db.DateTimeProperty(required=True, auto_now=True)
    created_at = db.DateTimeProperty(required=True, auto_now_add=True)

    ## class methods
    @staticmethod
    def get_or_insert_by_pmid(pmid):
        pmid = int(pmid)
        key_name = 'pmid:'+str(pmid)
        article = Article.get_by_key_name(key_name)
        if article is None:
            url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&rettype=full&id="+str(pmid)
            res = urlfetch.fetch(url)
            if res.status_code == 200:
                xml = fromstring(res.content)
                if xml.findtext('.//MedlineCitation/PMID') == str(pmid):
                    xml = db.Text(res.content, encoding='utf-8')
                    article = Article.get_or_insert(key_name = key_name, pmid = pmid, xml = xml, fetched_at = datetime.utcnow())
        return article

    ## instance methods
    def get_raters(self):
        return [rating.user for rating in self.ratings]
    raters = property(get_raters)

    def get_ratings_count(self):
        return self.get_ratings_stats()[0]
    ratings_count = property(get_ratings_count)

    def get_ratings_average_rating(self):
        return self.get_ratings_stats()[1]
    ratings_average_rating = property(get_ratings_average_rating)

    def get_ratings_stats(self):
        count = 0
        sum = 0
        average = None
        for rating in self.ratings.filter('rating >', 0):
            count += 1
            sum += rating.rating
        if count:
            average = float(sum)/count
        return (count, average)

    def set_ratings_stats(self):
        count, average = self.get_ratings_stats()
        self.ratings_count_cache = count
        self.ratings_average_rating_cache = average
        self.put()

    def delete(self):
        # prevent deletion
        pass

#    def put(self):
#        key = super(Article, self).put()
#        query = Article.gql("WHERE pmid = :pmid", pmid=self.pmid)
#        if query.count() == 0:
#            return key
#        else:
#            Article.get(key).delete()
#            query.bind()
#            return query.get().key()

    def record(self):
        xml = fromstring(self.xml.encode('utf-8'))
        med = xml.find('.//MedlineCitation')
        title = med.findtext('./Article/ArticleTitle')
        journal = med.findtext('./MedlineJournalInfo/MedlineTA')
        year = med.findtext('./Article/Journal/JournalIssue/PubDate/Year')
        if not year:
            year = med.findtext('./Article/Journal/JournalIssue/MedlineDate', '')
        source = "%s (%s)" % (journal, year)
        abstract = med.findtext('./Article/Abstract/AbstractText', '')
        authors = med.findall('./Article/AuthorList/Author')
        def extract_author(author):
            last_name = author.findtext('./LastName')
            initials = author.findtext('./Initials', '')
            suffix = author.findtext('./Suffix', '')
            collective_name = author.findtext('./CollectiveName')
            if collective_name:
                author = "%s" % (collective_name)
            else:
                author = "%s %s %s" % (last_name, initials, suffix)
            return author.strip()
        authors = [extract_author(author) for author in authors]
        authors = ', '.join(authors)
        keywords = med.findall('./MeshHeadingList/MeshHeading')
        def extract_keyword(keyword):
            descriptor_name = keyword.findtext('./DescriptorName')
            qualifier_names = keyword.findall('./QualifierName')
            if qualifier_names:
                return ', '.join(["%s %s" % (descriptor_name, qualifier_name.findtext('.').capitalize()) for qualifier_name in qualifier_names])
            else:
                return "%s" % (descriptor_name)
        keywords = [extract_keyword(keyword) for keyword in keywords]
        keywords = ', '.join(keywords)
        return { 'title': title, 'source': source, 'abstract': abstract, 'authors': authors, 'keywords': keywords  }





#class Journal(db.Model):
#    nlmid = db.StringProperty(required=True)
#    title = db.StringProperty(required=True)
#    title_alt = db.StringProperty(required=True)
#    title_iso = db.StringProperty()
#    pissn = db.StringProperty()
#    eissn = db.StringProperty()
#
#    def get_or_insert_by_nlmid(cls, nlmid):
#        nlmid = str(nlmid)
#        key_name = 'nlmid:' + nlmid
#        journal = Journal.get_by_key_name(key_name)
#        if journal: return journal
#        url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=journals&term=%s[nlmid]" % nlmid
#        result = urlfetch.fetch(url)
#        if result.status_code == 200:
#            xml = fromstring(result.content).getroot()
#            if xml.findtext('Count') == '1':
#                id = xml.findtext('IdList/Id')
#            else:
#                return None
#        else:
#            return None
#        url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=journals&retmode=xml&rettype=full&id="+id
#        result = urlfetch.fetch(url)
#        if result.status_code == 200:
#            xml = fromstring(result.content).getroot()
#            xml = xml.find('.//Serial')
#            if xml and xml.findtext('NlmUniqueID') == nlmid:
#                title = xml.findtext('MedlineTA')
#                title_alt = xml.findtext('Title').replace('\n', ' ').strip()
#                title_iso = xml.findtext('ISOAbbreviation', default=None)
#                pissn = xml.findtext("ISSN[@IssnType='Print']", default=None)
#                eissn = xml.findtext("ISSN[@IssnType='Electronic']", default=None)
#                return Journal.get_or_insert(key_name = key_name, nlmid = nlmid, title = title, title_alt = title_alt, title_iso = title_iso, pissn = pissn, eissn = eissn)
#            else:
#                return None
#        else:
#            return None
#
#    get_or_insert_by_nlmid = classmethod(get_or_insert_by_nlmid)
#
#    def put(self):
#        key = super(Journal, self).put()
#        if Journal.gql("WHERE nlmid = :nlmid ", nlmid = self.nlmid).count() > 1:
#            Journal.get(key).delete()
#            raise 'duplicate entity exception'
