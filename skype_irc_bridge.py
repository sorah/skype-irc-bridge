#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim: noet sts=4:ts=4:sw=4
# author: takano32 <tak at no32.tk>
# modified-by: sorah <her at sorah.jp>
# Distributed under the terms of the GNU General Public License v2

import Skype4Py
import os
import time
from SimpleXMLRPCServer import SimpleXMLRPCServer
from socket import error as socket_error
from configobj import ConfigObj
import sys, xmlrpclib, socket

if len(sys.argv) == 2:
	CONFIG = ConfigObj(sys.argv[1])
else:
	CONFIG = ConfigObj("bridge.conf")


class SkypeIrcBridge():
	xmlrpc_host = CONFIG['irc']['xmlrpc_host']
	xmlrpc_port = CONFIG['irc']['xmlrpc_port']
	irc = xmlrpclib.ServerProxy('http://%s:%s' % (xmlrpc_host, xmlrpc_port))
	def __init__(self):
		self.skype = Skype4Py.Skype()
		self.start()

	def handler(self, msg, event):
		if len(msg.Body) == 0:
			return
		if event == u"RECEIVED":
			self._pass_to_irc(msg)

	def _pass_to_irc(self, msg, deleted=False, body=False):
			said = False
			for key in CONFIG:
				if key == 'skype' or key == 'irc':
					continue
				if CONFIG[key].has_key('skype') and msg.ChatName == CONFIG[key]['skype'] and CONFIG[key].has_key('irc'):
					said = True
					self._pass_to_irc_core(CONFIG[key]['irc'], msg, deleted=deleted, body=body)
			if not said:
				self._pass_to_irc_core(False, msg, deleted=deleted, body=body)

	@staticmethod
	def _pass_to_irc_core(channel, msg, deleted=False, body=False):
		name = msg.Sender.FullName
		if len(name) == 0 or len(name) > 16:
			name = msg.Sender.Handle

		body = (body or msg.Body).splitlines()
		if msg.Type == "SETTOPIC" and channel:
			topic = u' '.join(body)
			print 'Skype(%s)->IRC %s [TOPIC] %s' % (msg.ChatName, channel, topic)
			SkypeIrcBridge.irc.set_topic(channel, topic)
			print 'done'

		for line in body:
			if msg.Type != 'SAID':
				name = '[%s] %s' % (msg.Type, name)

			if deleted:
				if (not msg.EditedBy) or msg.EditedBy == msg.Sender.Handle:
					name = '[DELETED] ' + name
				else:
					name = '[DELETED BY %s] %s' % (msg.EditedBy, name)
			elif msg.EditedBy:
				if msg.EditedBy == msg.Sender.Handle:
					name = '[EDITED] ' + name
				else:
					name = '[EDITED BY %s] %s' % (msg.EditedBy, name)


			name = unicode(name, 'UTF-8')
			if channel:
				text = u'%s: %s' % (name, line)
				print u'Skype(%s)->IRC %s: %s' % (msg.ChatName, channel, text)
			else:
				topic = unicode(msg.Chat.Topic, 'UTF-8')
				text = u'(%s) %s: %s [%s]' % (topic, name, line, msg.ChatName)
				print u'Skype(%s)->IRC DEFAULT: %s' % (msg.ChatName,  text)

			SkypeIrcBridge.irc.say(channel, text)
			print 'done'

			if CONFIG['irc'].has_key('wait'):
				time.sleep(float(CONFIG['irc']['wait']))
			else:
				time.sleep(len(text) / 20.0)

	def handler_notify(self, notification):
		payload = notification.split(' ')
		if payload[0] == 'CHATMESSAGE' and payload[2] == 'BODY':
			self._pass_to_irc(self.skype.Message(payload[1]), deleted=(not payload[3]), body=payload[3])
		elif CONFIG['irc'].has_key('dump_all_notification'):
			print '[RAW] ' + notification
			try:
				SkypeIrcBridge.irc.say(False, notification)
				print 'done'
			except socket_error:
				print 'fail'

	def say(self, channel, msg):
		room = self.skype.Chat(channel)
		print u"Skype(%s)<-IRC: %s" % (channel, msg)
		room.SendMessage(msg)
		return True

	def get_topic(self, chatname):
		return self.skype.Chat(chatname).Topic

	def set_topic(self, chatname, topic):
		print "[SETTOPIC] Skype(%s)<-IRC: %s" % (chatname, topic)
		self.skype.Chat(chatname).Topic = topic
		return True


	def start(self):
		self.skype.OnMessageStatus = self.handler
		self.skype.OnNotify = self.handler_notify
		self.skype.Attach()

if __name__ == "__main__":
	host = CONFIG['skype']['xmlrpc_host']
	port = CONFIG['skype']['xmlrpc_port']
	sv = SimpleXMLRPCServer((host, int(port)))
	sv.register_instance(SkypeIrcBridge())
	sv.serve_forever()

