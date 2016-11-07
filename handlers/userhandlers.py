import re
import time
import random
import hashlib
from string import letters

from handlers.blogpage import Blogpage
from models.models import Userdb
from google.appengine.ext import db

def make_salt(length=5):
    return ''.join(random.choice(letters) for x in xrange(length))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s|%s' % (salt, h)


def valid_pw(name, password, h):
    salt = h.split('|')[0]
    return h == make_pw_hash(name, password, salt)

# Regex validation functions:


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")


def valid_username(username):
    return username and USER_RE.match(username)


PASS_RE = re.compile(r"^.{3,20}$")


def valid_password(password):
    return password and PASS_RE.match(password)


EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


def valid_email(email):
    return not email or EMAIL_RE.match(email)


class Signup(Blogpage):
    def get(self):
        self.render_template('signup.html', user=self.user_obj)

    def post(self):
        error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')
        params = dict(username=self.username, email=self.email)
        if self.get_user_obj(self.username).get():
            params['error_username'] = "This user already exists"
            error = True
        else:
            if not valid_username(self.username):
                params['error_username'] = "That's not a valid username"
                error = True
            if not valid_password(self.password):
                params['error_password'] = "Password is not valid"
                error = True
            if self.password != self.verify:
                params['error_verify'] = "Passwords do not match"
                error = True
            if not valid_email(self.email):
                params['error_email'] = "Email is not valid"
                error = True
        if not error:
            self.hashed_password = make_pw_hash(self.username, self.password)
            user_record = Userdb(username=self.username,
                                 password=self.hashed_password,
                                 email=self.email)
            user_record.put()
            self.set_secure_cookie('name', str(self.username))
            time.sleep(0.4)
            self.redirect('/')
        else:
            self.render_template('signup.html', **params)


class Login(Blogpage):
    def get(self):
        self.render_template('login.html', user=self.user_obj)

    def post(self):
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        if self.get_user_obj(self.username).get():  # user exists check password
            self.hashed_password = self.get_user_obj(self.username).get().password
            if valid_pw(self.username, self.password, self.hashed_password):
                self.set_secure_cookie('name', str(self.username))
                self.redirect('/')
            else:
                self.error = "Password doesn't match the one that we have"
        else:
            self.error = 'No user found'
        self.render_template('login.html', error=self.error)


class Logout(Blogpage):
    def get(self):
        self.clear_cookie()
        self.write('You have been successfully logged out <BR>')
        self.write("Please go to <a href='/'>main page</a>" +
                   " or <a href='/login'>login page</a")


class Badcookie(Blogpage):
    def get(self):
        self.clear_cookie()
        self.write('Bad cookie. Possible cookie forging detected')
        self.write('Suspicious Cookie has been deleted from this client')
        self.write('<BR>Please use /signup or login pages to enter')


class Mainpage(Blogpage):
    def get(self):
        likes = []
        authors = []
        blogs = self.get_all_blogs().order('-modified')
        for blog in blogs:
            authors.append(self.get_blog_user(blog.key()).username)
            likes.append(self.get_likes(blog))
        self.render_template('show_blogs.html', blogs=blogs,
                             user=self.user_obj,
                             likes=likes, author=authors)
