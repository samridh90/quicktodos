import webapp2
import jinja2
import os
import Cookie
import json
import hashlib
import random
import string
from datetime import datetime

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


def make_salt(length = 5):
    return ''.join(random.choice(string.letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

#Models
class TodoCollection(db.Model):
    timestamp = db.DateTimeProperty(auto_now_add=True)
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)

    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(uid)

    @classmethod
    def by_name(cls, name):
        u = cls.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw):
        pw_hash = make_pw_hash(name, pw)
        return TodoCollection(name=name, pw_hash=pw_hash)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u


class TodoItem(db.Model):
    collection = db.ReferenceProperty(TodoCollection)
    priority = db.IntegerProperty()
    content = db.StringProperty()
    due = db.StringProperty()
    done = db.BooleanProperty()

    def toDict(self):
        todoItem = {
            'id': self.key().id(),
            'priority': self.priority,
            'content': self.content,
            'due': self.due,
            'done': self.done
        }
        return todoItem


#Handlers
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class  MainPage(Handler):
    def add_cookie(self, todocoll):
        cookie = Cookie.SimpleCookie()
        cookie['todos'] = todocoll.key().__str__()
        cookie['todos']['expires'] = datetime(2014, 1, 1).strftime("%a, %d %b %Y %H:%M:%S")
        cookie['todos']['path'] = '/'
        self.response.headers.add_header('Set-Cookie', cookie['todos'].OutputString())

    def get(self):
        cookie = self.request.cookies.get('todos', None)
        if cookie == None:
            self.render("index.html", loggedIn=False)
        else:
            self.render("index.html", loggedIn=True)

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        if not (username and password):
            msg = "Please enter a valid username and password."
            self.render("index.html", loggedIn=False, error = msg)
            return
        t = TodoCollection.by_name(username)
        if t:
            u = TodoCollection.login(username, password)
            if u:
                self.add_cookie(u)
                self.render("index.html", loggedIn=True)
            else:
                msg = "Username exists. Invalid username/password combination."
                self.render("index.html", loggedIn=False, error=msg)
        else:
            u = TodoCollection.register(username, password)
            u.put()
            self.add_cookie(u)
            self.render("index.html", loggedIn=True)


class TodoCollectionHandler(Handler):
    def get_todocollection_key(self):
        key = self.request.cookies['todos']
        todocollection = db.get(key)
        return todocollection.key()

    def get(self):
        key = self.get_todocollection_key()
        query = TodoItem.all()
        query.filter("collection =", key)
        todos = []
        for todo in query:
            todos.append(todo.toDict())
        self.write(json.dumps(todos))

    def post(self):
        key = self.get_todocollection_key()
        todo = json.loads(self.request.body)
        todo = TodoItem(collection=key, content=todo['content'], done=todo['done'],
                        priority=todo['priority'], due=todo['due'])
        todo.put()
        todo = json.dumps(todo.toDict())
        self.write(todo)


class TodoItemHandler(Handler):
    def get_todocollection_key(self):
        key = self.request.cookies['todos']
        todocollection = db.get(key)
        return todocollection.key()

    def put(self, id):
        key = self.get_todocollection_key()
        todo = TodoItem.get_by_id(int(id))
        if todo.collection.key() == key:
            data = json.loads(self.request.body)
            todo.content = data["content"]
            todo.done = data["done"]
            todo.put()
            todo = json.dumps(todo.toDict())
            self.write(todo)

    def delete(self, id):
        key = self.get_todocollection_key()
        todo = TodoItem.get_by_id(int(id))
        if todo.collection.key() == key:
            todo.delete()
        else:
            self.error(403)


class LogoutHandler(Handler):
    def get(self):
        cookie = Cookie.SimpleCookie()
        cookie['todos'] = ""
        cookie['todos']['expires'] = datetime(2010, 1, 1).strftime("%a, %d %b %Y %H:%M:%S")
        cookie['todos']['path'] = '/'
        self.response.headers.add_header('Set-Cookie', cookie['todos'].OutputString())
        self.redirect("/")

application = webapp2.WSGIApplication([('/', MainPage),
                                       ('/todos', TodoCollectionHandler),
                                       ('/todos/(\d+)', TodoItemHandler),
                                       ('/logout', LogoutHandler)], debug=True)
