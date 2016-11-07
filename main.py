import webapp2

from models.models import Userdb, Blogdb, Commentdb
from handlers.blogpage import Blogpage, Createblog, Displayblog, Editblog
from handlers.blogpage import Deleteblog
from handlers.comments import Updatecomment, Deletecomment
from handlers.likes import Likepost, Unlikepost
from handlers.userhandlers import Signup, Login, Logout, Badcookie, Mainpage



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
