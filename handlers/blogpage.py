import webapp2
import hmac
import jinja2
import os
import time

from models.models import Userdb, Blogdb, Commentdb
from google.appengine.ext import db

SECRET = 'MySeCR5tMe55a6E'

# Jinja2 environment setup

# The following function replaces \n with <br> tag.
# Borrowed from udacity forums.


def letitpass(s):
    return s.replace('\n', '<br>')

template_dir = os.getcwd()+'/templates'
loader = jinja2.FileSystemLoader(template_dir)
jinja2_env = jinja2.Environment(loader=loader, trim_blocks=True,
                                autoescape=True)
jinja2_env.filters['letitpass'] = letitpass

class Blogpage(webapp2.RequestHandler):
    ''' This default class for displaying blog pages'''
    def __init__(self, *args, **kwargs):
        webapp2.RequestHandler.__init__(self, *args, **kwargs)
        self.user_obj = self.check_login()

# Cookies functions

    def clear_cookie(self):
        self.response.headers.add_header('Set-Cookie', 'name=; Path=/')

    def make_secure_val(self, val):
        return '%s|%s' % (val, hmac.new(SECRET, val).hexdigest())

    def check_secure_val(self, secure_val):
        val = secure_val.split('|')[0]
        if secure_val == self.make_secure_val(val):
            return val

    def set_secure_cookie(self, name, val):
        cookie_val = self.make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie', '%s=%s; Path=/' % (str(name), (cookie_val)))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        if cookie_val and not self.check_secure_val(cookie_val):
            self.redirect('/badcookie')
        return cookie_val

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
            user_obj = self.get_user_obj(user).get()
        else:
            user_obj = None
        return user_obj

    def blog_author(self, blog_id):
        author_key = Blogdb.get(blog_id).parent().key()
        if not self.user_obj or self.user_obj.key() != author_key:
            return False
        return True
    
    def check_valid_record(self, record_id, db_name):
        ''' Checks if record with record_id exists in db_name datastore object
            returns false if record does not exist '''
        try:
            record_id = db_name.get(record_id)
            return True
        except:
            return False

    def get_blog_user(self, blog_key):
        ''' returns user who created the blog record with blog_id'''
        user_id = Blogdb.get(blog_key).parent()
        return user_id


    def get_user_obj(self, username=None):
        ''' Returns all users  object or object with username'''
        if username:
            return Userdb.all().filter('username =', username)
        else:
            return Userdb.all()


    def get_all_blogs(self, username=None):
        if not username:
            return Blogdb.all()
        else:
            key = db.Key.from_path(
                'Userdb', Userdb.all().filter('username =',
                                              username).get().key().id())
            bloglist = Blogdb.all().ancestor(key)
            return bloglist

    def get_likes(self, blog):
        ''' returns number of likes for blog class'''
        likes = Commentdb.all().ancestor(blog).filter("comment_type =",
                                                      'vote').count()
        if not likes:
            likes = 0
        return likes

class Createblog(Blogpage):
    def get(self):
        # Check if logged in
        if not self.user_obj:
            self.write('You are not logged in! <BR>')
            self.write(
                'Please <a href="/">click here</a> to go to the main page')
        else:
            self.render_template('createblog.html', user=self.user_obj)

    def post(self):
        if not self.user_obj:
            self.write('You are not logged in! <BR>')
            self.write(
                'Please <a href="/">click here</a> to go to the main page')
        else:
            blogtitle = self.request.get('blogtitle')
            blogtext = self.request.get('blogtext')
            if blogtitle and blogtext:
                blog_record = Blogdb(parent=self.user_obj, blogtitle=blogtitle,
                                     blogtext=blogtext)
                blog_record.put()
                time.sleep(0.4)
                self.redirect('/')
            else:
                error = 'Either blog title or blog text are empty'
                self.render_template(
                    'createblog.html', user=self.user_obj, blogtitle=blogtitle,
                    blogtext=blogtext, error=error)
class Displayblog(Blogpage):
    def get(self, blog_id):
        blog_id = blog_id[4:]
        if self.check_valid_record(blog_id, Blogdb):
            blog = db.get(blog_id)
            # load comments
            blog = db.get(blog_id)
            comments = Commentdb.all().ancestor(blog).filter(
                'comment_type =', 'comment').order('-modified')
            self.render_template(
                'displayblog.html', user=self.user_obj,
                blogtitle=blog.blogtitle, blogtext=blog.blogtext,
                blog_id=blog_id, comments=comments)
        else:
            self.write('Error. Something wrong with blog link.' +
                       ' Please try again! <BR>')
            self.write('Please <a href="/">click here</a> to go the main page')

    def post(self, blog_id):
        ''' we use post method for commentary posting, so need
                to define post method in display blog page as well '''
        if self.user_obj:
            blog_id = blog_id[4:]
            if self.check_valid_record(blog_id, Blogdb):
                blog = db.get(blog_id)
                comments = Commentdb.all().ancestor(blog).filter(
                    'comment_type =', 'comment').order('-modified')
                commenttext = self.request.get('new_comment')
                if not commenttext:
                    error = "Comments can't be blank"
                    self.render_template(
                        'displayblog.html', user=self.user_obj,
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
                self.write('Error. Something wrong with blog link.' +
                           ' Please try again! <BR>')
                self.write(
                    'Please <a href="/">click here</a> to go the main page')
        else:
            self.write('Sorry, you must be logged in' +
                       ' order to comment blogs <BR>')
            self.write('Please <a href="/">click here</a>' +
                       ' to go to the main page')
class Editblog(Blogpage):
    def get(self, blog_id):
        blog_id = blog_id[4:]  # clear key
        if self.check_valid_record(blog_id, Blogdb):
            if not self.blog_author(blog_id):
                self.render_template('error_user.html', user=self.user_obj)
            else:
                blog = db.get(blog_id)
                self.render_template(
                    'editblog.html', user=self.user_obj,
                    blogtitle=blog.blogtitle, blogtext=blog.blogtext,
                    blog_id=blog_id)
        else:
            self.write('Error. Something wrong with blog link.' +
                       ' Please try again! <BR>')
            self.write('Please <a href="/">click here</a> to go the main page')

    def post(self, blog_id):
        blog_id = blog_id[4:]
        if self.check_valid_record(blog_id, Blogdb):
            blogtitle = self.request.get('blogtitle')
            blogtext = self.request.get('blogtext')
            if not self.blog_author(blog_id):
                self.render_template('error_user.html', user=self.user_obj)
            else:
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
        else:
            self.write('Error. Something wrong with blog link.' +
                       ' Please try again! <BR>')
            self.write('Please <a href="/">click here</a> to go the main page')

class Deleteblog(Blogpage):
    def get(self, blog_id):
        blog_id = blog_id[4:]
        if not self.check_valid_record(blog_id, Blogdb):
            self.write('Error. Something wrong with blog link.' +
                       ' Please try again! <BR>')
            self.write('Please <a href="/">click here</a> to go the main page')
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
    
    