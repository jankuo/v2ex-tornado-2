#!/usr/bin/env python
# coding=utf-8

import os
import datetime

import tornado.web
from v2ex.babel.memcached import mc as memcache
import urlfetch


import tornado.ioloop
from jinja2 import Template, Environment, FileSystemLoader


from v2ex.babel import Member
from v2ex.babel import Counter
from v2ex.babel import Section
from v2ex.babel import Node
from v2ex.babel import Topic
from v2ex.babel import Reply

from v2ex.babel.da import *

from v2ex.babel.handlers import BaseHandler
import pytz
#template.register_template_library('v2ex.templatetags.filters')

class FeedHomeHandler(BaseHandler):
    def head(self):
        self.write('')
        
    def get(self):
        output = memcache.get('feed_index')
        if output is None:
            self.values['site_domain'] = self.site.domain
            self.values['site_name'] = self.site.title
            self.values['site_slogan'] = self.site.slogan
            self.values['feed_url'] = 'http://' + self.values['site_domain'] + '/index.xml'
            self.values['site_updated'] = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
            topics = memcache.get('feed_home')
            if topics is None:
                #q = db.GqlQuery("SELECT * FROM Topic ORDER BY created DESC LIMIT 10")
                q = Topic.select(orderBy='-created').limit(10)
                topics = []
                IGNORED = ['newbie', 'in', 'flamewar', 'pointless', 'tuan', '528491', 'chamber', 'autistic', 'blog', 'love', 'flood', 'fanfou', 'closed']
                for topic in q:
                    if topic.node.name not in IGNORED:
                        topics.append(topic)
                memcache.set('feed_home', topics, 3600)
            self.values['topics'] = topics
            self.values['feed_title'] = self.site.title
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'feed')
            t=self.get_template(path, 'index.xml')
            output = t.render(self.values)
            memcache.set('feed_index', output, 3600)
        self.set_header('Content-type', 'application/xml;charset=UTF-8')
        self.write(output)
        
class FeedReadHandler(BaseHandler):
    def head(self):
        self.write('')
        
    def get(self):
        output = memcache.get('feed_read_output')
        if output is None:
            self.values['site_domain'] = self.site.domain
            self.values['site_name'] = self.site.title
            self.values['site_slogan'] = self.site.slogan
            self.values['feed_url'] = 'http://' + self.values['site_domain'] + '/read.xml'
            self.values['site_updated'] = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
            topics = memcache.get('feed_home')
            if topics is None:
                #q = db.GqlQuery("SELECT * FROM Topic ORDER BY created DESC LIMIT 10")
                q = Topic.select(orderBy='-created').limit(10)
                topics = []
                IGNORED = ['newbie', 'in', 'flamewar', 'pointless', 'tuan', '528491', 'chamber', 'autistic', 'blog', 'love', 'flood']
                for topic in q:
                    if topic.node.name not in IGNORED:
                        topics.append(topic)
                memcache.set('feed_home', topics, 3600)
            self.values['topics'] = topics
            self.values['feed_title'] = self.site.title
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'feed')
            t=self.get_template(path, 'read.xml')
            output = t.render(self.values)
            memcache.set('feed_read_output', output, 3600)
        self.set_header('Content-type', 'application/xml;charset=UTF-8')
        self.write(output)


class FeedNodeHandler(BaseHandler):
    def head(self):
        self.write('')
    
    def get(self, node_name):
        node_name = node_name.lower()
        site = GetSite()
        node = GetKindByName('Node', node_name)
        if node is False:
            return self.write('node not found')
        output = memcache.get('feed_node_' + node_name)
        if output is None:
            template_values = {}
            template_values['site'] = site
            template_values['site_domain'] = site.domain
            template_values['site_name'] = site.title
            template_values['site_slogan'] = site.slogan
            template_values['feed_url'] = 'http://' + template_values['site_domain'] + '/index.xml'
            template_values['site_updated'] = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
            #q = db.GqlQuery("SELECT * FROM Topic WHERE node = :1 ORDER BY created DESC LIMIT 10", node)
            q = Topic.selectBy(node=node).orderBy('-created').limit(10)
            topics = []
            for topic in q:
                topics.append(topic)
            template_values['topics'] = topics
            template_values['feed_title'] = site.title + u' › ' + node.title
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'feed')
            t=self.get_template(template_values)
            output = t.render(self.values)
            memcache.set('feed_node_' + node.name, output, 7200)
        self.set_header('Content-type', 'application/xml;charset=UTF-8')
        self.write(output)

