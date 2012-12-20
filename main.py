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
import httplib
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.api import users
from survey_backend import  *
from model import *

#Handles the server-side requests
class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.generateSurvey()
        path = os.path.join(os.path.dirname(__file__), 'server.html')
        client_path = os.path.join(os.path.dirname(__file__), 'client.html')
        conn = httplib.HTTPConnection("yep.it")
        conn.request("GET", "/api.php?url=" + client_path)
        res = conn.getresponse()
        conn.close()
        short_url = res.read()
        tmp_value = {
            'url': client_path,
            'short_url' : short_url,
        }
        self.response.out.write(template.render(path, tmp_value))
        self.response.out.write(short_url)
        
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
        currentUser=''
        url=''
        url_linktext=''
        if users.get_current_user():
          allUser = User.all()
          allUser.filter("user_email =",users.get_current_user().email()) 
          if allUser.count() == 0:
            newUser = User(pid=1,user_email=users.get_current_user().email(),user_nickname=users.get_current_user().nickname())
            newUser.put()
          currentUser=users.get_current_user().nickname()
          url = users.create_logout_url(self.request.uri)
          url_linktext = 'Logout'
        else:
          self.redirect(users.create_login_url(self.request.uri)) 
        template_values = {
          'currentUser': currentUser,
          'url': url,
          'url_linktext': url_linktext,
        }   
        path = os.path.join(os.path.dirname(__file__), 'client.html')
        self.response.out.write(template.render(path, template_values))        

#Gives the current page of Server, used to synchronize between client and server
class Status(webapp2.RequestHandler):
    def get(self):
        hindex = cgi.escape(self.request.get('h'))
        vindex = cgi.escape(self.request.get('v'))
        if(hindex):
            memcache.set('hindex', hindex)
            memcache.set('vindex', vindex)
        self.response.out.write("%s %s"%(memcache.get('hindex'), memcache.get('vindex')))




app = webapp2.WSGIApplication([
    ('/server', MainHandler),
    ('/server_status', Status),
    ('/client', Client),
    ('/survey_vote', SurveyVote),
    ('/survey_result', Result)
], debug=True)
