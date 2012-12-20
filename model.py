#!/usr/bin/env python
from google.appengine.ext import db

class Vote(db.Model):
    sid = db.IntegerProperty();
    aid = db.IntegerProperty();
    uid = db.IntegerProperty();
    time = db.DateTimeProperty();

class Survey(db.Model):
    sid = db.IntegerProperty();
    sname = db.StringProperty();
    aid = db.IntegerProperty();
    atext = db.StringProperty();
    count = db.IntegerProperty();

class User(db.Model):
    pid = db.IntegerProperty();
    user_email = db.StringProperty();
    user_nickname = db.StringProperty();