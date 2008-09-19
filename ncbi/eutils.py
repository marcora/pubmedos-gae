from xml.etree.ElementTree import fromstring

from google.appengine.api import urlfetch

def epost(ids=[], db='pubmed', retmode='xml', tool='pubmedos', email='marcora@caltech.edu'):
    url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/epost.fcgi?id=%s&db=%s&retmode=%s&tool=%s&email=%s" % ('%2C'.join([str(int(id)) for id in ids]), db, retmode, tool, email)
    result = urlfetch.fetch(url)
    if result.status_code == 200:
        xml = fromstring(result.content)
        env = xml.findtext('./WebEnv')
        key = xml.findtext('./QueryKey')
        if env and key:
            return (env, key)
        else:
            return (None, None)
    else:
        return (None, None)
