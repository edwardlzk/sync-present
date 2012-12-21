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
from google.appengine.api import mail

class SendEmail(webapp2.RequestHandler):
  def get(self):
    sender_addr = "edwardlzk@gmail.com"
    result = db.GqlQuery("SELECT user_email FROM User WHERE pid=1")
    user_email=""
    for uemail in result:
    	user_email=user_email+","+uemail.user_email
    to_addr = user_email
    if not mail.is_email_valid(to_addr):
        # Return an error message...
        pass
    subject = "Thanks for attending the presentation"
    body = """
Thanks for attending the presentation
Regards,

""" 
    mail.send_mail(sender_addr, to_addr, subject, body)

#Handles the server-side requests
class MainHandler(webapp2.RequestHandler):
    def get(self):
        pid = cgi.escape(self.request.get('pid'))
        if not pid:
            self.generateSurvey()
            
            client_path = os.path.join(os.path.dirname(__file__), 'client.html')
            conn = httplib.HTTPConnection("is.gd")
            conn.request("GET", "/create.php?format=simple&url=" + client_path)
            res = conn.getresponse()
            conn.close()
            short_url = res.read()
            tmp_value = {
                'url': client_path,
                'short_url' : short_url,
                }
            path = os.path.join(os.path.dirname(__file__), 'server.html')
            self.response.out.write(template.render(path, tmp_value))
            self.response.out.write(short_url)
        else:
            q = db.GqlQuery("SELECT * FROM Slides WHERE pid="+str(pid)+" ORDER BY order ASC")
            slides=''
            contents={}
            for s in q.run():
                type = s.stype
                data={}
                if type == 1:
                    content=s.scontent
                    data['content'] = content
                    path = os.path.join(os.path.dirname(__file__), 'type1_display.html')
                    slides+=template.render(path, data)
                elif type == 2:
                    sid=s.key().id()
                    survey = db.GqlQuery("SELECT * FROM Survey WHERE sid="+str(sid)+" ORDER BY aid ASC")
                    first = survey.get()
                    data['survey'] = survey.run()
                    data['sid'] = sid
                    data['title'] = first.sname
                    data['init_data']=','.join(['0']*survey.count())
                    path = os.path.join(os.path.dirname(__file__), 'type2_display_server.html')
                    slides+=template.render(path, data)
            contents['pid']=pid
            contents['slides']=slides
            client_path = os.path.join(os.path.dirname(__file__), '/client?pid='+str(pid))
            conn = httplib.HTTPConnection("is.gd")
            conn.request("GET", "/create.php?format=simple&url=" + client_path)
            res = conn.getresponse()
            conn.close()
            short_url = res.read()
            contents['url'] = client_path
            contents['short_url'] = short_url
            path = os.path.join(os.path.dirname(__file__), 'server_dynamic.html')
            self.response.out.write(template.render(path, contents))
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
        pid = cgi.escape(self.request.get('pid'))
        currentUser=''
        url=''
        url_linktext=''
        if users.get_current_user():
            #add pid filtering
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
        if not pid :
            path = os.path.join(os.path.dirname(__file__), 'client.html')
            self.response.out.write(template.render(path, template_values))
        else:
            q = db.GqlQuery("SELECT * FROM Slides WHERE pid="+str(pid)+" ORDER BY order ASC")
            slides=''
            contents={}
            for s in q.run():
                type = s.stype
                data={}
                if type == 1:
                    content=s.scontent
                    data['content'] = content
                    path = os.path.join(os.path.dirname(__file__), 'type1_display.html')
                    slides+=template.render(path, data)
                elif type == 2:
                    sid=s.key().id()
                    survey = db.GqlQuery("SELECT * FROM Survey WHERE sid="+str(sid)+" ORDER BY aid ASC")
                    first = survey.get()
                    data['survey'] = survey.run()
                    data['sid'] = sid
                    data['title'] = first.sname
                    path = os.path.join(os.path.dirname(__file__), 'type2_display_client.html')
                    slides+=template.render(path, data)
            template_values['pid']=pid
            template_values['slides']=slides
            path = os.path.join(os.path.dirname(__file__), 'client_dynamic.html')
            self.response.out.write(template.render(path, template_values))

#Gives the current page of Server, used to synchronize between client and server
class Status(webapp2.RequestHandler):
    def get(self):
        hindex = cgi.escape(self.request.get('h'))
        vindex = cgi.escape(self.request.get('v'))
        pid = cgi.escape(self.request.get('pid'))
        if not pid :
            if(hindex):
                memcache.set('hindex', hindex)
                memcache.set('vindex', vindex)
            self.response.out.write("%s %s"%(memcache.get('hindex'), memcache.get('vindex')))
        else:
            if(hindex):
                memcache.set('hindex'+str(pid), hindex)
                memcache.set('vindex'+str(pid), vindex)
            self.response.out.write("%s %s"%(memcache.get('hindex'+str(pid)), memcache.get('vindex'+str(pid))))




app = webapp2.WSGIApplication([
    ('/server', MainHandler),
    ('/server_status', Status),
    ('/client', Client),
    ('/survey_vote', SurveyVote),
    ('/survey_result', Result),
    ('/presentation_admin', PAdmin),
    ('/slides_content', SlidesContent),
    ('/email',SendEmail),
    ('/present_controller', PresentController),
    ('/presentation_list', PresentationList)
], debug=True)
