import time
from google.appengine.ext import db

from handlers.blogpage import Blogpage
from models.models import Commentdb, Blogdb


class Updatecomment(Blogpage):
    def get(self):
        id = self.request.get('comment_id')
        back_link = self.request.get('blog_id')
        #  Check if id exists
        if self.check_valid_record(id, Commentdb):
            comment = Commentdb.get(id)
            if not self.user_obj or self.user_obj.username != comment.author:
                self.write('Looks like you are either not' +
                           'logged in or authorized to edit this comment.<BR>')
                self.write("Click <a href = '/'>here</a> " +
                           "to go back to the main page")
            else:
                self.render_template(
                    'post_comment.html', old_comment=comment.comment,
                    comment_key=id)
        else:
            self.write("""Comment does not exist. Wrong comment link <BR>
                       Click <a href="/%s">here <a/>to go back to display 
                       blog""" % back_link)

    def post(self):
        id = self.request.get('comment_id')
        back_link = self.request.get('blog_id')
        if self.check_valid_record(id, Commentdb):
            commenttext = self.request.get('new_comment')
            if not commenttext:
                error = "Comments can't be blank"
                self.render_template('post_comment.html', error=error)
            else:
                comment = Commentdb.get(id)
                if comment.author == self.user_obj.username:
                    comment.comment = commenttext
                    comment.put()
                    time.sleep(0.4)
                    redirect_blog_link = '/show'+str(comment.parent().key())
                    self.redirect(redirect_blog_link)
                else:
                    self.write('You are not the comment author <BR>')
                    self.write(
                        'Click <a href="/">here <a/>to go to the main page')

        else:
            self.write("""Comment does not exist. Wrong comment link <BR>
                       Click <a href="/%s">here <a/>to
                       go back to display blog""" % back_link)


class Deletecomment(Blogpage):
    def post(self):
        id = self.request.get('comment_id')
        back_link = self.request.get('blog_id')
        if self.check_valid_record(id, Commentdb):
            comment = Commentdb.get(id)
            if not self.user_obj or self.user_obj.username != comment.author:
                self.write('Looks like you are either not logged in or ' +
                           'authorized to edit this comment. <BR>')
                self.write("""Click <a href = '/%s'>here</a>
                           to go back to display blog""" % back_link)
            else:
                comment.delete()
                time.sleep(0.3)
                redirect_blog_link = '/show'+str(comment.parent().key())
                self.redirect(redirect_blog_link)
        else:
            self.write("""Comment does not exist. Wrong comment link <BR>
                       Click <a href="/%s">here <a/>to 
                       go back to display blog""" % back_link)