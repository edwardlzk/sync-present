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
                    user_nickname="test",
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
        q = db.GqlQuery("SELECT count FROM Survey WHERE sid="+_sid+" ORDER BY aid ASC")
        total=[]
        for aCount in q:
            total.append(str(aCount.count))
        self.response.out.write(",".join(total))


class SlidesContent(webapp2.RequestHandler):
    def get(self):
        type = cgi.escape(self.request.get('type'))
        num = cgi.escape(self.request.get('num'))
        seq = cgi.escape(self.request.get('seq'))
        data = {}
        data['type'] = type
        data['num'] = num
        data['seq'] = seq
        path = os.path.join(os.path.dirname(__file__), 'type'+type+'.html')
        self.response.out.write(template.render(path, data))

class PAdmin(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'slides_create.html')
        self.response.out.write(template.render(path, None))
        
class PresentController(webapp2.RequestHandler):
    #Create a new presentation, coming from PAdmin
    def post(self):
        #add presentation first
        p = Presentation(time = datetime.datetime.now(), user_count = 0)
        p.put()
        _pid = p.key().id()
        #add slides one by one
        slide_total = int(cgi.escape(self.request.get('sCounts')))
        for i in range(1, slide_total+1):
            type = int(cgi.escape(self.request.get('s'+str(i)+'type')))
            if type == 1:
                #Standard slides
                content = self.request.get('s'+str(i)+'content')
                s=Slides(pid=_pid,
                         stype=type,
                         scontent=content,
                         order=i)
                s.put()
            elif type == 2:
                #Survey slides
                #add Choice first
                choiceTotal = int(cgi.escape(self.request.get('s'+str(i)+'ChoiceNum')))
                title = cgi.escape(self.request.get('s'+str(i)+'Title'))
                s=Slides(pid=_pid,
                         stype=type,
                         scontent="",
                         order=i)
                s.put()
                _sid = s.key().id()
                for j in range(1, choiceTotal+1):
                    choiceText = cgi.escape(self.request.get('s'+str(i)+'Choice'+str(j)+'Text'))
                    obj=Survey(sid=_sid,
                             sname=title,
                             aid=j,
                             atext=choiceText,
                             count=0)
                    obj.put()
        self.redirect("/presentation_list")
    #def get(self):

class PresentationList(webapp2.RequestHandler):
    def get(self):
        q = db.GqlQuery("SELECT * FROM Presentation ORDER BY time DESC")
        data = {}
        list = []
        for p in q.run():
            current = {}
            current['pid'] = p.key().id()
            current['time'] = p.time
            current['user_count'] = p.user_count
            list.append(current)
        data['presentation'] = list
        path = os.path.join(os.path.dirname(__file__), 'presentation_list.html')
        self.response.out.write(template.render(path, data))