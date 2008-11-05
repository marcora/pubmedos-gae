from models.app import *

import base64, hashlib
def b64_sha1(s):
  return base64.standard_b64encode(hashlib.sha1(s).digest())

def really_urlsafe_b64encode(s):
     return base64.urlsafe_b64encode(s).strip('=')

def really_urlsafe_b64decode(s):
     return base64.urlsafe_b64decode(s + '=' * (len(s) % 4))


class Reprint(Model):
    ## datastore schema
    checksum = db.StringProperty(required=True)
    filedata = db.BlobProperty(required=True)
    filesize = db.IntegerProperty(required=True)
    updated_at = db.DateTimeProperty(required=True, auto_now=True)
    created_at = db.DateTimeProperty(required=True, auto_now_add=True)
    # ratings

    ## class methods
    @staticmethod
    def get_or_insert_by_filedata(filedata):
        checksum = really_urlsafe_b64encode(hashlib.sha1(filedata).digest())
        key_name = 'checksum:'+checksum
        reprint = Reprint.get_by_key_name(key_name)
        if reprint is None:
            reprint = Reprint.get_or_insert(key_name, checksum=checksum, filedata=db.Blob(filedata), filesize=len(filedata))
        return reprint

    @staticmethod
    def get_by_checksum(checksum):
        key_name = 'checksum:'+checksum
        reprint = Reprint.get_by_key_name(key_name)
        return reprint

    ## instance methods
