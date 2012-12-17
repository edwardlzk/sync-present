#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import cgi
import datetime
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
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

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.generateSurvey()
        path = os.path.join(os.path.dirname(__file__), 'server.html')
        self.response.out.write(template.render(path, None))
        
    def generateSurvey(self):
        q = db.GqlQuery("SELECT * FROM Survey WHERE sid="+_sid)
        if(not q):
            a1 = Survey(sid=1,sname="What is your favorate programming language",aid=0,atext="PHP",count=0)
            a2 = Survey(sid=1,sname="What is your favorate programming language",aid=1,atext="Java",count=0)
            a3 = Survey(sid=1,sname="What is your favorate programming language",aid=2,atext="Python",count=0)
            a4 = Survey(sid=1,sname="What is your favorate programming language",aid=3,atext="C",count=0)
            a1.put();
            a2.put();
            a3.put();
            a4.put();
        
class Client(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'client.html')
        self.response.out.write(template.render(path, None))        

class Status(webapp2.RequestHandler):
    def get(self):
        hindex = cgi.escape(self.request.get('h'))
        vindex = cgi.escape(self.request.get('v'))
        if(hindex):
            memcache.set('hindex', hindex)
            memcache.set('vindex', vindex)
        self.response.out.write("%s %s"%(memcache.get('hindex'), memcache.get('vindex')))
        
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

class Result(webapp2.RequestHandler):
    def get(self):
        _sid = cgi.escape(self.request.get('sid'))
        q = db.GqlQuery("SELECT count FROM Survey ORDER BY aid ASC")
        total=[]
        for aCount in q:
            total.append(str(aCount.count))
        self.response.out.write(",".join(total))

app = webapp2.WSGIApplication([
    ('/server', MainHandler),
    ('/server_status', Status),
    ('/client', Client),
    ('/survey_vote', SurveyVote),
    ('/survey_result', Result)
], debug=True)
