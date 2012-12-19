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
#Author:    Zekai Li
#           Xingyang Chen
#           Jinglun Dong    
#           Xin Zhang

import webapp2
import os
import cgi
import datetime
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.ext import db
from survey_backend import  *
from model import *

#Handles the server-side requests
class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.generateSurvey()
        path = os.path.join(os.path.dirname(__file__), 'server.html')
        tmp_value = {
            'url': os.path.join(os.path.dirname(__file__), 'client.html'),
        }
        self.response.out.write(template.render(path, tmp_value))
        
    def generateSurvey(self):
        q = db.GqlQuery("SELECT * FROM Survey WHERE sid=1")
        if q.count() == 0:
            a1 = Survey(sid=1,sname="What is your favorate programming language",aid=0,atext="PHP",count=0)
            a2 = Survey(sid=1,sname="What is your favorate programming language",aid=1,atext="Java",count=0)
            a3 = Survey(sid=1,sname="What is your favorate programming language",aid=2,atext="Python",count=0)
            a4 = Survey(sid=1,sname="What is your favorate programming language",aid=3,atext="C",count=0)
            a1.put();
            a2.put();
            a3.put();
            a4.put();

#Handles the client-side requests
class Client(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'client.html')
        self.response.out.write(template.render(path, None))        

#Gives the current page of Server, used to synchronize between client and server
class Status(webapp2.RequestHandler):
    def get(self):
        hindex = cgi.escape(self.request.get('h'))
        vindex = cgi.escape(self.request.get('v'))
        if(hindex):
            memcache.set('hindex', hindex)
            memcache.set('vindex', vindex)
        self.response.out.write("%s %s"%(memcache.get('hindex'), memcache.get('vindex')))


#generate survey results for server to display
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
