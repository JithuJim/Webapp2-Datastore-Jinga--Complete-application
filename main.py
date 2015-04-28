import webapp2
import jinja2
import os
from google.appengine.ext import ndb

from webapp2_extras import sessions
import logging
jinja2_loader = jinja2.Environment(loader = jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),"templates")))

#For session management
config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}

class Person(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    password = ndb.StringProperty()
    about = ndb.StringProperty()

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()


class RegisterHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja2_loader.get_template('register.html')
        context = {}
        self.response.write(template.render(context))

class PostHandler(webapp2.RequestHandler):
    def post(self):
        person = Person()
        person.name = self.request.get('name')
        person.email = self.request.get('email')
        person.password = self.request.get('pwd')
        person.about = self.request.get('about')
        person.put()
        return self.redirect('/home')

class HomeHandler(BaseHandler):
    def get(self):
        if self.session.get('username'):
            user = self.session.get('username')
            template = jinja2_loader.get_template('home.html')
            q = Person.query()
            context = {'persons':q,'user':user}
            self.response.write(template.render(context))
        else:
            self.redirect('/')

class AboutHandler(BaseHandler):
    def get(self):
        if self.session.get('username'):
            user = self.session.get('username')
            template = jinja2_loader.get_template('about.html')
            q = Person.query()
            context = {'persons':q,'user':user}
            self.response.write(template.render(context))
        else:
            self.redirect('/')

class LoginHandler(BaseHandler):
    def get(self):
        template = jinja2_loader.get_template('login.html')
        context = {}
        self.response.write(template.render(context))

    def post(self):
        username = self.request.get('name')
        password = self.request.get('pwd')
        q= Person.query()
        r = q.filter(Person.name==username).filter(Person.password==password).get()
        logging.info(r)
        if r:
            self.session['username'] = self.request.get('name')
            self.redirect('/home')
        else:
            self.redirect('/register')

class LogoutHandler(BaseHandler):
    def get(self):
        if self.session.get('username'):
            del self.session['username']
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/register',RegisterHandler),
    ('/postData',PostHandler),
    ('/home',HomeHandler),
    ('/about',AboutHandler),
    ('/',LoginHandler),
    ('/logout',LogoutHandler)
], debug=True,config=config)
