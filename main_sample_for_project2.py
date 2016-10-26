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
class User(db.Model):
	username = db.StringProperty(required = True)
class Blog(db.Model):
	blogtitle = db.StringProperty(required = True)
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
		self.render_template('maindbtest.html')
	def post(self):
#This chunk of code is for display each blog of each user
		blogs = []
		users = User.all()
		x = 0
		for user in users:
			blogs.append([user.username])
			records = Blog.all().ancestor(user.key())
			for blog in records:
				blogs[x].append(blog.blogtitle)
			x += 1
#End of chunk
#This chunk of code is for display of blog and obtaining user of the code
		blogs2 = []
		all_records = Blog.all()
		x = 0
		for record in all_records:
			blogs2.append([record.blogtitle])
			uid = record.key().parent() # get parent id
			name = User.get_by_id(uid.id()).username
			blogs2[x].append(name)
			x += 1
#End of chunk
		username = self.request.get('username')
		blogtitle = self.request.get('blogtitle')
#if user exists then get id, else create user
		user = User.all().filter('username =',username).get()
		if not user:
			user = User(username = username)
			user.put()
#Create child record in blog db
		blog = Blog(parent = user , blogtitle = blogtitle)
		blog.put()
		time.sleep(0.4)
		self.render_template('maindbtest.html', records = blogs, blogs2 = blogs2)
#below comments are for basic put / get procedures		
		# time.sleep(0.4)
		# self.write('This is user.key().id(): ' + str(user.key().id()))
		# q = db.GqlQuery ('SELECT * FROM User WHERE username =:1',username).get()
		# key_path = db.Key.from_path('User', user.key().id())
		# self.write('<BR> This key.from_path:')
		# self.write(key_path)
		# self.write('<BR> This is key.name():<BR>')
		# self.write(user.key().name())
		# self.write ('<BR> This is GQL returned username :  ')
		# self.write (q.username)
		# self.write ('<BR> This search by key ID from path: db.get(key.from_path):<BR>')
		# self.write (db.get(key_path).username)
		# self.write('<BR> This is Model.get by id <BR>')
		# self.write(User.get_by_id(user.key().id()).username)
		# query = User.all().filter('username =', username).get()
		# self.write('<BR><BR> Here is filter method<BR>')
		# self.write(query.username)
routes = [('/',mainpage)]
app = webapp2.WSGIApplication(routes = routes,
								debug = True)
