import webapp2
import re
import os
import random
import jinja2
import time
import hmac
import hashlib
from string import letters
from google.appengine.ext import db

# Jinja2 environment setup
# The following function replaces \n with <br> tage
# Borrowed from udacity forums.


def letitpass(s):
    return s.replace('\n', '<br>')

template_dir = os.getcwd()+'/templates'
loader = jinja2.FileSystemLoader(template_dir)
jinja2_env = jinja2.Environment(loader=loader, trim_blocks=True,
                                autoescape=True)
jinja2_env.filters['letitpass'] = letitpass
# Hashing block begin

SECRET = 'MySeCR5tMe55a6E'

# DB functions to retrieve user/blog/likes records


def get_blog_user(blog_key):
    ''' returns user who created the blog record with blog_id'''
    user_id = Blogdb.get(blog_key).parent()
    return user_id


def get_user_obj(username=None):
        ''' Returns all users  object or object with username'''
        if username:
            return Userdb.all().filter('username =', username)
        else:
            return Userdb.all()


def get_all_blogs(username=None):
    if not username:
        return Blogdb.all()
    else:
        key = db.Key.from_path(
            'Userdb', Userdb.all().filter('username =',
                                          username).get().key().id())
        bloglist = Blogdb.all().ancestor(key)
        return bloglist


def get_likes(blog):
    ''' returns number of likes for blog class'''
    likes = Commentdb.all().ancestor(blog).filter("comment_type =",
                                                  'vote').count()
    if not likes:
        likes = 0
    return likes

# Cookies functions


def make_secure_val(val):
        return '%s|%s' % (val, hmac.new(SECRET, val).hexdigest())


def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

# Password hashing functions


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

# DB classes


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

# Web page classes


class Blogpage(webapp2.RequestHandler):
    ''' This default class for displaying blog pages'''
    def __init__(self, *args, **kwargs):
        webapp2.RequestHandler.__init__(self, *args, **kwargs)
        self.user_obj = self.check_login()

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie', '%s=%s; Path=/' % (str(name), (cookie_val)))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        if cookie_val and not check_secure_val(cookie_val):
            self.redirect('/badcookie')
        return cookie_val
        # return cookie_val and check_secure_val(cookie_val)

    def write(self, *args, **kwargs):
        ''' function to simply use write vs response.out'''
        self.response.write(*args, **kwargs)

    def render_template(self, template, **kwargs):
        ''' function to render template '''
        t = jinja2_env.get_template(template)
        self.write(t.render(**kwargs))

    def check_login(self):
        ''' returns login user object or none if not logged in '''
        user = self.read_secure_cookie('name')
        if user:
            user = str(user.split('|')[0])
            user_obj = get_user_obj(user).get()
        else:
            user_obj = None
        return user_obj

    def blog_author(self, blog_id):
        author_key = Blogdb.get(blog_id).parent().key()
        if not self.user_obj or self.user_obj.key() != author_key:
            return False
        return True

    def clear_cookie(self):
        self.response.headers.add_header('Set-Cookie', 'name=; Path=/')


class Createblog(Blogpage):
    def get(self):
        # Check if logged in
        if not self.user_obj:
            self.write('You are not logged in! <BR>')
            self.write('Please <a href="/">click here</a> to go the main page')
        else:
            self.render_template('createblog.html', user=self.user_obj)

    def post(self):
        blogtitle = self.request.get('blogtitle')
        blogtext = self.request.get('blogtext')
        blog_record = Blogdb(parent=self.user_obj, blogtitle=blogtitle,
                             blogtext=blogtext)
        blog_record.put()
        time.sleep(0.4)
        self.redirect('/')


class Displayblog(Blogpage):
    def get(self, blog_id):
        blog_id = blog_id[4:]  # delete show from the parameter
        try:
            blog = db.get(blog_id)
            # load comments
            comments = Commentdb.all().ancestor(blog).filter(
                'comment_type =', 'comment').order('-modified')
            self.render_template(
                'displayblog.html', user=self.user_obj,
                blogtitle=blog.blogtitle, blogtext=blog.blogtext,
                blog_id=blog_id, comments=comments)
        except:
            self.write('Error. Something wrong with blog link.' +
                       ' Please try again! <BR>')
            self.write('Please <a href="/">click here</a> to go the main page')

    def post(self, blog_id):
        ''' we use post method for commentary posting, so need
                define post method in display blog page as well '''
        if self.user_obj:
            blog_id = blog_id[4:]
            blog = db.get(blog_id)
            comments = Commentdb.all().ancestor(blog).filter(
                'comment_type =', 'comment').order('-modified')
            commenttext = self.request.get('new_comment')
            if not commenttext:
                error = "Comments can't be blank"
                self.render_template('displayblog.html', user=self.user_obj,
                                     blogtitle=blog.blogtitle,
                                     blogtext=blog.blogtext, blog_id=blog_id,
                                     comments=comments, error=error)
            else:
                comment = Commentdb(
                    comment_type='comment', comment=commenttext,
                    author=self.user_obj.username, parent=blog)
                comment.put()
                time.sleep(0.4)
                self.render_template(
                    'displayblog.html', user=self.user_obj,
                    blogtitle=blog.blogtitle, blogtext=blog.blogtext,
                    blog_id=blog_id, comments=comments)
        else:
            self.write('Sorry, you must be logged in' +
                       ' order to comment blogs <BR>')
            self.write('Please <a href="/">click here</a>' +
                       ' to go to the main page')


class Editblog(Blogpage):
    def get(self, blog_id):
        blog_id = blog_id[4:]  # clear key
        if not self.blog_author(blog_id):
            self.render_template('error_user.html')
        else:
            blog = db.get(blog_id)
            if not blog:
                self.render_template('error_link.html')
            self.render_template(
                'editblog.html', user=self.user_obj, blogtitle=blog.blogtitle,
                blogtext=blog.blogtext, blog_id=blog_id)

    def post(self, blog_id):
        blogtitle = self.request.get('blogtitle')
        blogtext = self.request.get('blogtext')
        blog_id = blog_id[4:]
        if not self.blog_author(blog_id):
            self.write('Wrong user')
        if blogtitle and blogtext:
            blog = db.get(blog_id)
            blog.blogtext = blogtext
            blog.blogtitle = blogtitle
            blog.put()
            time.sleep(0.4)
            self.redirect('/')
        else:
            error = 'Either blog title or blog text are empty'
            self.render_template(
                'editblog.html', user=self.user_obj, blogtitle=blogtitle,
                blogtext=blogtext, blog_id=blog_id, error=error)


class Deleteblog(Blogpage):
    def get(self, blog_id):
        blog_id = blog_id[4:]
        if not self.blog_author(blog_id):
            self.render_template('error_user.html')
        else:
            blog = db.get(blog_id)
            if not blog:
                self.render_template('error_link.html')
            else:
                # delete all child comments
                comments = Commentdb.all().ancestor(blog)
                for comment in comments:
                    comment.delete()
                # delete blog
                blog.delete()
                time.sleep(0.4)
                self.redirect('/')


class Updatecomment(Blogpage):
    def get(self):
        id = self.request.get('comment_id')
        comment = Commentdb.get(id)
        if not self.user_obj or self.user_obj.username != comment.author:
            self.write('Looks like you are either not' +
                       'logged in or authorized to edit this comment. <BR>')
            self.write("Click <a href = '/'>here</a> " +
                       "to go back to the main page")
        else:
            self.render_template('post_comment.html',
                                 old_comment=comment.comment, comment_key=id)

    def post(self):
        commenttext = self.request.get('new_comment')
        if not commenttext:
            error = "Comments can't be blank"
            self.render_template('post_comment.html', error=error)
        else:
            id = self.request.get('comment_id')
            comment = Commentdb.get(id)
            comment.comment = commenttext
            comment.put()
            time.sleep(0.4)
            redirect_blog_link = '/show'+str(comment.parent().key())
            self.redirect(redirect_blog_link)


class Deletecomment(Blogpage):
    def post(self):
        id = self.request.get('comment_id')
        comment = Commentdb.get(id)
        if not self.user_obj or self.user_obj.username != comment.author:
            self.write('Looks like you are either not logged in or' +
                       'authorized to edit this comment. <BR>')
            self.write("Click <a href = '/'>here</a>" +
                       " to go back to the main page")
        else:
            comment.delete()
            time.sleep(0.3)
            redirect_blog_link = '/show'+str(comment.parent().key())
            self.redirect(redirect_blog_link)


class Likepost(Blogpage):
    def get(self, blog_id):
        blog_id = blog_id[4:]  # clear key
        if self.blog_author(blog_id):
            self.write('Seems that you are the one who wrote this.<BR>')
            self.write("You can't like your own post <BR>")
            self.write("Click <a href='/'>here</a> to go to the main page")
        else:
            blog = db.get(blog_id)
            like_record = Commentdb.all().filter(
                'comment_type =', 'vote').filter(
                    'author =', self.user_obj.username).ancestor(blog).get()
            if like_record:
                self.write('You already liked this post!<BR>')
                self.write("Click <a href='/'>here</a> to go to the main page")
            else:
                like = Commentdb(comment_type='vote', comment='vote',
                                 author=self.user_obj.username, parent=blog)
                like.put()
                time.sleep(0.2)
                self.redirect('/')


class Unlikepost(Blogpage):
    def get(self, blog_id):
        blog_id = blog_id[6:]  # Dislike comment key is 'dislike' - 6 chars
        blog = db.get(blog_id)
        like_record = Commentdb.all().filter(
            'comment_type =', 'vote').filter(
                'author =', self.user_obj.username).ancestor(blog).get()
        if not like_record:
            self.write("You haven't liked this post. Nothing to unlike <BR>")
            self.write("Click <a href='/'>here</a> to go to the main page")
        else:
            like_record.delete()
            time.sleep(0.2)
            self.redirect('/')


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
        if get_user_obj(self.username).get():
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
        if get_user_obj(self.username).get():  # user exists check password
            self.hashed_password = get_user_obj(self.username).get().password
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
        blogs = get_all_blogs().order('-modified')
        for blog in blogs:
            authors.append(get_blog_user(blog.key()).username)
            likes.append(get_likes(blog))
        self.render_template('main.html', blogs=blogs,
                             user=self.user_obj,
                             likes=likes, author=authors)
routes = [('/', Mainpage),
          ('/(show[a-zA-Z0-9-_]+)', Displayblog),
          ('/(edit[a-zA-Z0-9-_]+)', Editblog),
          ('/(kill[a-zA-Z0-9-_]+)', Deleteblog),
          ('/(like[a-zA-Z0-9-_]+)', Likepost),
          ('/(unlike[a-zA-Z0-9-_]+)', Unlikepost),
          ('/updatecomment', Updatecomment),
          ('/deletecomment', Deletecomment),
          ('/signup', Signup),
          ('/createblog', Createblog),
          ('/badcookie', Badcookie),
          ('/login', Login),
          ('/logout', Logout)]
app = webapp2.WSGIApplication(routes=routes,
                              debug=True)
