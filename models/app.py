import logging, re

from google.appengine.ext import db


## helpers
def transaction(wrapped):
    def wrapper(*args, **kwargs):
        return db.run_in_transaction(wrapped, *args, **kwargs)
    return wrapper

## base model
class Model(db.Model):
    pass
