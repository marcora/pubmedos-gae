from datetime import datetime
from xml.etree.ElementTree import fromstring, tostring

from google.appengine.ext import db
from google.appengine.api import urlfetch


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
                    xml = db.Text(res.content)
                    article = Article.get_or_insert(key_name = key_name, pmid = pmid, xml = xml, fetched_at = datetime.utcnow())
        return article

    ## instance methods
    def to_hash(self):
        return { 'id': self.pmid, 'ratings_count': self.ratings_count_cache, 'ratings_average_rating': self.ratings_average_rating_cache }

    @property
    def ratings_count(self):
        return self.ratings_stats[0]

    @property
    def ratings_average_rating(self):
        return self.ratings_stats[1]

    @property
    def ratings_stats(self):
        count = 0
        sum = 0
        average = None
        for rating in self.ratings.filter('rating >', 0):
            count += 1
            sum += rating.rating
        if count:
            average = float(sum)/count
        return (count, average)

    def cache_ratings_stats(self):
        count, average = self.ratings_stats
        self.ratings_count_cache = count
        self.ratings_average_rating_cache = average
        self.put()

    def delete(self):
        pass

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
