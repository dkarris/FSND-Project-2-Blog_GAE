from google.appengine.ext import db

class Userdb(db.Model):
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)


class Blogdb(db.Model):
    blogtitle = db.StringProperty(required=True)
    blogtext = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

class Commentdb(db.Model):
    comment_type = db.StringProperty(required=True)
    comment = db.TextProperty(required=True)
    author = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)
