import webapp2
import re
import os
import random
import jinja2
import time
from google.appengine.ext import db
# This is my magical SQL string
# SELECT * FROM blog_db WHERE __key__ HAS ANCESTOR Key(`user_db`,'testuser')
#Jinja2 environment setup
template_dir = os.getcwd()+'/templates'
loader = jinja2.FileSystemLoader(template_dir)
jinja2_env = jinja2.Environment(loader = loader, trim_blocks = True,
								autoescape = True)
#Note. Should later clear why lstrip_blocks = True doesn't work.
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
class Userdb(db.Model):
	username = db.StringProperty(required = True)
	password = db.StringProperty(required = True)
	email = db.StringProperty()
	created = db.DateTimeProperty(auto_now_add = True)
class Blogdb(db.Model):
	blogtitle = db.StringProperty(required = True)
	blogtext = db.TextProperty()
	created = db.DateTimeProperty(auto_now_add = True)
class Blogpage(webapp2.RequestHandler):
	check_login = False
	''' This default class for displaying blog pages'''
	def write(self, *args, **kwargs):
		''' function to simply use write vs response.out'''
		self.response.write(*args, **kwargs)
	def render_template(self, template,**kwargs):
		''' function to render template '''
		t = jinja2_env.get_template(template)
		self.write(t.render(**kwargs))
	def check_login(self):
		''' returns login user object or none if not logged in '''
		user = self.request.cookies.get('user')
		if user:
			user = str(user.split('|')[0])
			user_obj = Userdb.all().filter('username =',user).get()
		else:
			user_obj = None
		return user_obj
class Createblog(Blogpage):
	def get(self):
		self.render_template('createblog.html')
	def post(self):
		blogtitle = self.request.get('blogtitle')
		blogtext = self.request.get('blogtext')
		parent = Userdb.all().filter('username =', 'testuser2').get()
		blog_record = Blogdb(parent = parent, blogtitle = blogtitle, blogtext = blogtext)
		blog_record.put()
		time.sleep(0.4)
		self.redirect('/')		
class Signup(Blogpage):
	def get(self):
		self.render_template('signup.html')
	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		verify = self.request.get('verify')
		email = self.request.get('email')
# Later put here username and password regex validation
		regex_validation = True
		if not regex_validation:
#Later insert handler for username/password resubmission
			somevariable = True
		else:
			user_record = Userdb(username = username, password = password, email = email)
			user_record.put()
			time.sleep(0.5)
class Mainpage(Blogpage):
	def get(self):
		user_obj = self.check_login()
		users = get_user_obj(user_obj.username)
		#blogs = get_all_blogs(user_obj.username)
		blogs = get_all_blogs()
		self.render_template('main.html', user = user_obj, users = users, blogs = blogs)
routes = [('/',Mainpage),
		  ('/signup',Signup),
		  ('/createblog',Createblog)]
app = webapp2.WSGIApplication(routes = routes,
								debug = True)
