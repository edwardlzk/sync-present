#!/usr/bin/env python
from google.appengine.ext import db

class Vote(db.Model):
    sid = db.IntegerProperty();
    aid = db.IntegerProperty();
    user_nickname = db.StringProperty();
    time = db.DateTimeProperty();

class Survey(db.Model):
    sid = db.IntegerProperty(); #slides id
    sname = db.StringProperty();
    aid = db.IntegerProperty(); #sequence of this choice in the suite
    atext = db.StringProperty();
    count = db.IntegerProperty();

class User(db.Model):
    pid = db.IntegerProperty();
    user_email = db.StringProperty();
    user_nickname = db.StringProperty();
    
class Presentation(db.Model):
    time  = db.DateTimeProperty();
    user_count = db.IntegerProperty();

class Slides(db.Model):
    pid = db.IntegerProperty();
    stype = db.IntegerProperty();
    scontent = db.StringProperty(multiline=True);
    order = db.IntegerProperty();