#!/usr/bin/env python

import webapp2
import os
import cgi
import datetime
from model import *

#Handles a vote from clients
class SurveyVote(webapp2.RequestHandler):
    def get(self):
        _sid = cgi.escape(self.request.get('sid'))
        _aid = cgi.escape(self.request.get('aid'))
        vote = Vote(sid=int(_sid),
                    aid=int(_aid),
                    uid=0,
                    time=datetime.datetime.now())
        vote.put()
        q = db.GqlQuery("SELECT * FROM Survey WHERE sid="+_sid+" AND aid="+_aid)
        obj = q.get()
        obj.count +=1
        obj.put()
        
#generate survey results for server to display
class Result(webapp2.RequestHandler):
    def get(self):
        _sid = cgi.escape(self.request.get('sid'))
        q = db.GqlQuery("SELECT count FROM Survey ORDER BY aid ASC")
        total=[]
        for aCount in q:
            total.append(str(aCount.count))
        self.response.out.write(",".join(total))
        