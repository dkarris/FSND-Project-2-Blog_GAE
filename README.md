### **Udacity Project 2 blog**

### Installation

Download Google App SDK from [https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python]

Download or clone app repository to your computer, run 'dev_appserver.py .'' from the project dictory and go
to localhost:8080 in your browser.

Otherwise you can simply go to [https://guestbook-44.appspot.com/] to check this app running on GAE.

### How to use

App allows registred and logged in users to create/edit/delete their own blogs, post/edit/delete comments and like /unline blogs made by other users.

To create a new blog click the button at the top right corner under username.

From the main screen you can view recent blogs sorted by modified date. You can like (only one like per user, blog authors can't
like their own posts) or unlike previously liked post

You can edit blog or post a comment by clicking on the blog title link and going to the blog page, where you can add/edit/delete
comments.

### Security

User passwords are stored in hashed format. Cookies are validated with HMAC hashing algorithm.

### Notes to Udacity reviewer:

I choose parent/child DB structure without using 'dbReference' properties since google claims that queries made by using
ANCESTOR key are preferrable over 'WHERE parent is foo' because of full consistency. That's why my blog records are placed with
parent key (user object) and I don't have 'dbReference' property.

Later on, because of this model I ran into problem that blog.key().id() (numerical similar to what is used in lessons) doesn't work as expected. In this case ,when using parent object, numeric id is not unique and it is not possible to use it as a permalink.

So, my approach was to take original key() object and use it as permalink. Since key() uses ascii characters and doesn't have a fixed lenght, my regex would just confuse these links with common 'display', 'edit', etc. common types of links. As a workaround I
added addiitonal keywords like: 'blog', 'show'. etc, in the perm link, so that I could create a regex expression capturing these links.

#### Future releases, to do

Add bootstrap and mobile versions, JS and modals to improve usability.

#### 11/07/2016 Implemented suggestions from Udacity after submitting the first version of the project 

- Fixed security bugs
- Refactored model and page handlers
- Removed <table> tags from signin and login forms
- Changed jinja template structure from using {% include %} to {% extends %}








