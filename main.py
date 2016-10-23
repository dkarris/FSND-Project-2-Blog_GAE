import webapp2
import re
import os
import random
import jinja2
from google.appengine.ext import db
# This is my magical SQL string
# SELECT * FROM blog_db WHERE __key__ HAS ANCESTOR Key(`user_db`,'testuser')

template_dir = os.getcwd()+'/templates'
jinja2_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

class user_db(db.Model):
	username = db.StringProperty(required = True)
	password = db.StringProperty(required = True)
	email = db.StringProperty()
	created = db.DateTimeProperty(auto_now_add = True)
	modified = db.DateTimeProperty(auto_now = True)
class blog_db(db.Model):
	bloghead = db.StringProperty(required = True)
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
class mainpage(pagehandler):
	def get(self):
		self.render_template('header.html')

routes = [('/',mainpage)]
app = webapp2.WSGIApplication(routes = routes,
								debug = True)
