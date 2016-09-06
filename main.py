#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import jinja2
import webapp2
from google.appengine.api import users
from google.appengine.api import urlfetch
import json
from models import Sporocilo
from operator import attrgetter
from datetime import datetime

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            logiran = True
            logout_url = users.create_logout_url('/')
            user = users.get_current_user()
            seznam = Sporocilo.query(Sporocilo.prejemnik == user.email()).fetch()
            urejen = sorted(seznam, key=attrgetter("nastanek"), reverse=True)
            params = {"logiran": logiran, "logout_url": logout_url, "user": user, "seznam": urejen}

        else:
            logiran = False
            login_url = users.create_login_url('/')
            params = {"logiran": logiran, "login_url": login_url, "user": user}

        return self.render_template("base.html", params=params)


class PosljiHandler(BaseHandler):
    def get(self):
        return self.render_template("poslji.html")

    def post(self):
        user = users.get_current_user()

        prejemnik = self.request.get("prejemnik")
        zadeva = self.request.get("zadeva")
        vnos = self.request.get("vnos")
        posiljatelj = user.email()
        nastanek = datetime.now().strftime("%d-%m-%Y ob %H:%M")

        sporocilo = Sporocilo(prejemnik=prejemnik, zadeva=zadeva, vnos=vnos, posiljatelj=posiljatelj, nastanek=nastanek)
        sporocilo.put()

        return self.redirect_to("poslano")


class PoslanaHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if hasattr(user, 'email'):
            seznam = Sporocilo.query(Sporocilo.posiljatelj == user.email()).fetch()
            urejen = sorted(seznam, key=attrgetter("nastanek"), reverse=True)
            params = {"seznam": urejen}
            return self.render_template("poslano.html", params=params)
        else:
            return self.render_template("poslano.html")

class SporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}

        return self.render_template("sporocilo.html", params=params)


class WeatherHandler(BaseHandler):
    def get(self):
        url = "http://api.openweathermap.org/data/2.5/weather?q=Novomesto,si&units=metric&appid=aac9d0d9a922db2181138031c1346214"
        result = urlfetch.fetch(url)
        podatki = json.loads(result.content)
        params = {"podatki": podatki}

        self.render_template("vreme.html", params)


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="prva"),
    webapp2.Route('/poslano', PoslanaHandler, name="poslano"),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>', SporociloHandler),
    webapp2.Route('/poslji', PosljiHandler),
    webapp2.Route('/vreme', WeatherHandler),
], debug=True)
