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
def get_users_db(value = None):
	''' returns var as a Gql object where username = value or '''
	if not value:
		var = db.GqlQuery ('SELECT * FROM user_db')
	else:
		var = db.GqlQuery('SELECT * FROM user_db WHERE username = :1',value)
	return var
class user_db(db.Model):
	username = db.StringProperty(required = True)
	password = db.StringProperty(required = True)
	email = db.StringProperty()
	created = db.DateTimeProperty(auto_now_add = True)
	modified = db.DateTimeProperty(auto_now = True)
class blog_db(db.Model):
	blogtitle = db.StringProperty(required = True)
	blogtext = db.TextProperty()
	created = db.DateTimeProperty(auto_now_add = True)
	modified = db.DateTimeProperty(auto_now = True)
	like = db.IntegerProperty()
	dislikes = db.IntegerProperty()
class pagehandler(webapp2.RequestHandler):
	''' This default class for displaying blog pages'''
	def write(self, *args, **kwargs):
		''' function to simply use write vs response.out'''
		self.response.write(*args, **kwargs)
	def render_template(self, template,**kwargs):
		''' function to render template '''
		t = jinja2_env.get_template(template)
		self.write(t.render(**kwargs))
class createblog(pagehandler):
	def get(self):
		self.render_template('createblog.html')
class signup(pagehandler):
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
			user_record = user_db(username = username, password = password, email = email)
			user_record.put()
			time.sleep(0.5)
			users = db.GqlQuery('SELECT * FROM user_db')
			self.render_template('main.html', users = users, blogs = blogs)
class mainpage(pagehandler):
	def get(self):
		self.render_template('main.html', users = get_users_db('user1'))
routes = [('/',mainpage),
		  ('/signup',signup),
		  ('/createblog',createblog)]
app = webapp2.WSGIApplication(routes = routes,
								debug = True)
