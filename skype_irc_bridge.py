#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim: noet sts=4:ts=4:sw=4
# author: takano32 <tak at no32.tk>
#

import Skype4Py
import os
import time
from SimpleXMLRPCServer import SimpleXMLRPCServer
from configobj import ConfigObj
import sys, xmlrpclib, socket

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
			said = False
			for key in CONFIG:
				if key == 'skype' or key == 'irc':
					continue
				if CONFIG[key].has_key('skype') and msg.ChatName == CONFIG[key]['skype'] and CONFIG[key].has_key('irc'):
					said = True
					self._pass_to_irc(CONFIG[key]['irc'], msg)
			if not said:
				self._pass_to_irc(False, msg)

	@staticmethod
	def _pass_to_irc(channel, msg):
		name = msg.Sender.FullName
		if len(name) == 0 or len(name) > 16:
			name = msg.Sender.Handle

		if msg.Type == "SETTOPIC" and channel:
			topic = u' '.join(msg.Body.splitlines()).encode('utf-8')
			print '%s Skype->IRC %s [TOPIC] %s' % (msg.ChatName, channel, topic)
			SkypeIrcBridge.irc.set_topic(channel, topic)
			print 'done'

		for line in msg.Body.splitlines():
			if msg.Type != 'SAID':
				name = '[%s] %s' % (msg.Type, name)

			if channel:
				text = '%s: %s' % (name, line)
				text = text.encode('utf-8')
				print '%s Skype->IRC %s: %s' % (msg.ChatName, channel, text)
			else:
				topic = msg.Chat.Topic
				text = '(%s) %s: %s [%s]' % (topic, name, line, msg.ChatName)
				text = text.encode('utf-8')
				print '%s (%s) Skype->IRC DEFAULT: %s' % (msg.ChatName, topic, text)

			SkypeIrcBridge.irc.say(channel, text)
			print 'done'

			if CONFIG['irc'].has_key('wait'):
				time.sleep(float(CONFIG['irc']['wait']))
			else:
				time.sleep(len(text) / 20.0)

	def say(self, channel, msg):
		room = self.skype.Chat(channel)
		print "IRC->Skype %s %s" % (channel, msg)
		room.SendMessage(msg)
		return True

	def get_topic(self, chatname):
		return self.skype.Chat(chatname).Topic

	def start(self):
		self.skype.OnMessageStatus = self.handler
		self.skype.Attach()

if __name__ == "__main__":
	host = CONFIG['skype']['xmlrpc_host']
	port = CONFIG['skype']['xmlrpc_port']
	sv = SimpleXMLRPCServer((host, int(port)))
	sv.register_instance(SkypeIrcBridge())
	sv.serve_forever()

