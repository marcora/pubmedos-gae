from datetime import datetime
import re
import time
import urllib
import hashlib
import hmac
import base64

from google.appengine.api import urlfetch

AWS_ACCESS_KEY_ID = '0192GNFCV8591E0MHVG2'
AWS_SECRET_ACCESS_KEY = 'lLnxrDkOb+KJhe1A08EfUfekjbzmrhz0rh4W0AbE'

def fetch(bucket, path, payload = None, method = 'GET', headers = {}, allow_truncated = False):
    FMT = '%a, %d %b %Y %H:%M:%S +0000'
    URLFETCH_HTTP_METHODS = { 'GET':urlfetch.GET, 'POST':urlfetch.POST, 'HEAD':urlfetch.HEAD, 'PUT':urlfetch.PUT, 'DELETE':urlfetch.DELETE }
    headers = headers.copy()
    headers['x-amz-date'] = datetime.datetime.utcnow().strftime(FMT)
    cresource = "/%s%s" % (bucket, path)
    canonheaders = {}
    for key in headers:
        canonheaders[key.lower()] = headers[key]
    cheaders = ''
    p = re.compile("^x-amz-")
    chkeys = canonheaders.keys()
    chkeys.sort()
    for key in chkeys:
        if p.match(key):
            cheaders = "%s%s:%s\n" % (cheaders, key, canonheaders[key])
    ctype = canonheaders.get('content-type', '')
    cmd5 = canonheaders.get('content-md5', '')
    cdate = ''
    cverb = method
    stringtosign = cverb + "\n" + cmd5 + "\n" + ctype + "\n" + cdate + "\n" + cheaders + cresource
    hm = hmac.new(AWS_SECRET_ACCESS_KEY, stringtosign, hashlib.sha1)
    hmac_b64 = base64.b64encode(hm.digest())
    headers["Authorization"] = "AWS %s:%s" % (AWS_ACCESS_KEY_ID, hmac_b64)
    url = "http://%s.s3.amazonaws.com%s" % (bucket, path)
    response = urlfetch.fetch(url, payload = payload, method = URLFETCH_HTTP_METHODS[method], headers = headers, allow_truncated = allow_truncated)
    return response

def url_for(bucket, path, expires_after=300):
    expires = int(time.mktime(datetime.utcnow().timetuple())) + expires_after
    cresource = "/%s%s" % (bucket, path)
    stringtosign = "GET" + "\n\n\n" + str(expires) + "\n" + cresource
    hm = hmac.new(AWS_SECRET_ACCESS_KEY, stringtosign, hashlib.sha1)
    hmac_b64 = base64.b64encode(hm.digest())
    signature = urllib.quote(hmac_b64)
    url = "http://%s.s3.amazonaws.com%s?AWSAccessKeyId=%s&Expires=%s&Signature=%s" % (bucket, path, AWS_ACCESS_KEY_ID, expires, signature)
    return url

