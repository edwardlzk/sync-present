#!/usr/bin/env python

import webapp2
import os
import cgi
import datetime
from model import *
from google.appengine.ext.webapp import template

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


class SlidesContent(webapp2.RequestHandler):
    def get(self):
        type = cgi.escape(self.request.get('type'))
        num = cgi.escape(self.request.get('num'))
        data = {}
        data['type'] = type
        data['num'] = num
        path = os.path.join(os.path.dirname(__file__), 'type'+type+'.html')
        self.response.out.write(template.render(path, data))

class PAdmin(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'slides_create.html')
        self.response.out.write(template.render(path, None))