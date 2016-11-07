import time

from handlers.blogpage import Blogpage
from models.models import Userdb, Blogdb, Commentdb
from google.appengine.ext import db


class Likepost(Blogpage):
    def get(self, blog_id):
        blog_id = blog_id[4:]  # clear key
        if self.check_valid_record(blog_id, Blogdb):
            if self.blog_author(blog_id):
                self.write('Seems that you are the one who wrote this.<BR>')
                self.write("You can't like your own post <BR>")
                self.write("Click <a href='/'>here</a> to go to the main page")
            else:
                if not self.user_obj:
                    self.write('You must login to like posts!<BR>')
                    self.write("Click <a href='/'>here</a> to" +
                               'go to the main page')
                else:
                    blog = db.get(blog_id)
                    like_record = Commentdb.all().filter(
                        'comment_type =', 'vote').filter(
                            'author =', self.user_obj.username).ancestor(
                                blog).get()
                    if like_record:
                        self.write('You already liked this post!<BR>')
                        self.write("Click <a href='/'>here</a> to go to" +
                                   " the main page")
                    else:
                        like = Commentdb(comment_type='vote', comment='vote',
                                         author=self.user_obj.username,
                                         parent=blog)
                        like.put()
                        time.sleep(0.2)
                        self.redirect('/')
        else:
            self.write('Bad blog id. Please try again <BR>')
            self.write("Click <a href='/'>here</a> to go to the main page")


class Unlikepost(Blogpage):
    def get(self, blog_id):
        if not self.user_obj:
            self.write('You must login to unlike posts!<BR>')
            self.write("Click <a href='/'>here</a> to go to the main page")
        else:
            blog_id = blog_id[6:]  # Dislike comment key is 'dislike' - 6 chars
            if self.check_valid_record(blog_id, Blogdb):
                blog = db.get(blog_id)
                like_record = Commentdb.all().filter(
                    'comment_type =', 'vote').filter(
                    'author =', self.user_obj.username).ancestor(blog).get()
                if not like_record:
                    self.write("You haven't liked this post." +
                               " Nothing to unlike <BR>")
                    self.write("Click <a href='/'>here</a> to " +
                               "go to the main page")
                else:
                    like_record.delete()
                    time.sleep(0.2)
                    self.redirect('/')
            else:
                self.write('Bad blog id. Please try again <BR>')
                self.write("Click <a href='/'>here</a> to go to the main page")