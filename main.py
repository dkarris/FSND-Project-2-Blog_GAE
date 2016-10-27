import webapp2
import re
import os
import random
import jinja2
import time
import hmac
import hashlib
from google.appengine.ext import db
# This is my magical SQL string
# SELECT * FROM blog_db WHERE __key__ HAS ANCESTOR Key(`user_db`,'testuser')
#Jinja2 environment setup
template_dir = os.getcwd()+'/templates'
loader = jinja2.FileSystemLoader(template_dir)
jinja2_env = jinja2.Environment(loader = loader, trim_blocks = True,
								autoescape = True)
#Note. Should later clear why lstrip_blocks = True doesn't work.
#Hashing block begin

SECRET = 'MySeCR5tMe55a6E'

# DB functions to retrieve user and blog
def get_blog_user(blog_id):
	''' returns user who created the blog record with blog_id'''
	user_id = Blogdb.get_by_id(blog_id).key.parent()
	return user_id
def get_user_obj(username=None):
		''' Returns all user  object or object with username'''
		if username:
			return Userdb.all().filter('username =', username)
		else:
			return Userdb.all()
def get_all_blogs(username = None):
	if not username:
		return Blogdb.all()
	else:
		key = db.Key.from_path('Userdb',Userdb.all().filter('username =', username).get().key().id())
 		bloglist = Blogdb.all().ancestor(key)
		return bloglist
#Cookies functions
def make_secure_val(val):
		return '%s|%s' % (val, hmac.new(SECRET, val).hexdigest())
def check_secure_val(secure_val):
	val = secure_val.split('|')[0]
	if secure_val == make_secure_val(val):
		return val
#DB classes
class Userdb(db.Model):
	username = db.StringProperty(required = True)
	password = db.StringProperty(required = True)
	email = db.StringProperty()
	created = db.DateTimeProperty(auto_now_add = True)
class Blogdb(db.Model):
	blogtitle = db.StringProperty(required = True)
	blogtext = db.TextProperty()
	created = db.DateTimeProperty(auto_now_add = True)
#Web page classes
class Blogpage(webapp2.RequestHandler):
	''' This default class for displaying blog pages'''
	def __init__(self, *args, **kwargs):
		webapp2.RequestHandler.__init__(self, *args, **kwargs)
		self.user_obj = self.check_login()
	def set_secure_cookie(self, name, val):
		cookie_val = make_secure_val(val)
		self.response.headers.add_header(
			'Set-Cookie','%s=%s; Path=/' % (str(name), (cookie_val)))
	def read_secure_cookie(self, name):
		cookie_val = self.request.cookies.get(name)
		if cookie_val and not check_secure_val(cookie_val):
				self.redirect('/badcookie')
		return cookie_val
		#return cookie_val and check_secure_val(cookie_val)
	def write(self, *args, **kwargs):
		''' function to simply use write vs response.out'''
		self.response.write(*args, **kwargs)
	def render_template(self, template,**kwargs):
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
	def logout(self):
		self.response.headers.add_header('Set-Cookie','user=; Path=/')
		self.redirect('/logout')
class Createblog(Blogpage):
	def get(self):
		self.render_template('createblog.html', user = self.user_obj)
	def post(self):
		blogtitle = self.request.get('blogtitle')
		blogtext = self.request.get('blogtext')
		parent = Userdb.all().filter('username =', 'testuser2').get()
		blog_record = Blogdb(parent = parent, blogtitle = blogtitle,
			 blogtext = blogtext)
		blog_record.put()
		time.sleep(0.4)
		self.redirect('/')		
class Signup(Blogpage):
	def get(self):
		self.render_template('signup.html', user = self.user_obj)
	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		verify = self.request.get('verify')
		email = self.request.get('email')
# Later put here username and password regex validation
		regex_validation = True
		if not regex_validation:
#Later insert handler for username/password resubmission
			pass
		else:
			user_record = Userdb(username = username, password = password, email = email)
			user_record.put()
			self.set_secure_cookie('name',str(username))
			self.redirect('/')
class Login(Blogpage):
	def get(self):
		self.render_template('login.html', user = self.user_obj)
	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		if get_user_obj(username).get(): # user exists check password
#password checking block here
			self.set_secure_cookie('name', str(username))
			self.redirect('/')
		else:
			msg = 'No user found'
			self.render_template('login.html', error = msg)
class Logout(webapp2.RequestHandler):
	def get(self):
		self.response.headers.add_header('Set-Cookie','name=; Path=/')
		self.response.write('You have been successfully logged out <BR>')
		self.response.write("Please go to '/' or 'login'")
class Badcookie(webapp2.RequestHandler):
	def get(self):
		self.response.write('Bad cookie. Possible cookie forging detected')
		self.response.write('<BR>Please use /signup or login pages to enter')
class Mainpage(Blogpage):
	def get(self):
		users = get_user_obj()
		blogs = get_all_blogs()
		self.render_template('main.html', users = users, blogs = blogs,
			 user = self.user_obj)
routes = [('/',Mainpage),
		  ('/signup',Signup),
		  ('/createblog',Createblog),
		  ('/badcookie',Badcookie),
		  ('/login',Login),
		  ('/logout',Logout)]
app = webapp2.WSGIApplication(routes = routes,
								debug = True)
