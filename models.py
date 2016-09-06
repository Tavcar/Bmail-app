from google.appengine.ext import ndb


class Sporocilo(ndb.Model):
    prejemnik = ndb.StringProperty()
    posiljatelj = ndb.StringProperty()
    zadeva = ndb.StringProperty()
    vnos = ndb.StringProperty()
    nastanek = ndb.StringProperty()