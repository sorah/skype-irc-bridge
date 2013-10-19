#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim: noet sts=4:ts=4:sw=4
# author: takano32 <tak at no32.tk>
# modified-by: sorah <her at sorah.jp>
# Distributed under the terms of the GNU General Public License v2

from irc.bot import SingleServerIRCBot
from configobj import ConfigObj
from SimpleXMLRPCServer import SimpleXMLRPCServer

import sys, xmlrpclib, threading

CONFIG = ConfigObj("bridge.conf")

class IrcSkypeBridge(SingleServerIRCBot):
	def __init__(self, server = 'localhost'):
		self.channel = CONFIG['irc']['default_channel']
		SingleServerIRCBot.__init__(self, [(CONFIG['irc']['host'], int(CONFIG['irc']['port']))], CONFIG['irc']['nick'], CONFIG['irc']['nick'])

		xmlrpc_host = CONFIG['skype']['xmlrpc_host']
		xmlrpc_port = CONFIG['skype']['xmlrpc_port']
		self.skype = xmlrpclib.ServerProxy('http://%s:%s' % (xmlrpc_host, xmlrpc_port))

	def on_nicknameinuse(self, c, e):
		c.nick(c.get_nickname() + "_")

	def on_welcome(self, c, e):
		c.join(self.channel)
		for key in CONFIG:
			if key == 'skype' or key == 'irc':
				continue
			if CONFIG[key].has_key('irc'):
				channel = CONFIG[key]['irc']
				c.join(channel)
				c.topic(channel, self.skype.get_topic(CONFIG[key]['skype']))

	def on_topic(self, c, e):
		if e.source.nick == c.get_nickname():
			return
		for key in CONFIG:
			if key == 'skype' or key == 'irc':
				continue
			if CONFIG[key].has_key('irc'):
				channel = CONFIG[key]['irc']
				if channel == e.target:
					if CONFIG[key].has_key('irc_with_nick'):
						topic = '%s (by IRC %s)' % (e.arguments[0], e.source.nick)
						self.skype.set_topic(CONFIG[key]['skype'], topic)
					else:
						topic = e.arguments[0]
						self.skype.set_topic(CONFIG[key]['skype'], topic)
		return True

	def say(self, channel, msg):
		if channel == False:
			channel = self.channel
		print "IRC<-Skype %s %s" % (channel, msg)
		self.connection.privmsg(channel, msg)
		return True

	def set_topic(self, channel, topic):
		print "[TOPIC] IRC<-Skype %s %s" % (channel, topic)
		self.connection.topic(channel, topic)
		return True

	def do_command(self, c, e):
		msg = e.arguments[0]
		self.say(self.channel, msg.encode('utf-8'))

	def handler(self, c, e):
		nick = e.source.nick
		msg = e.arguments[0]
		text_with_nick = '%s: %s' % (nick, msg)
		for key in CONFIG:
			if key == 'skype' or key == 'irc':
				continue
			if CONFIG[key].has_key('irc'):
				channel = CONFIG[key]['irc']
				if channel == e.target:
					if CONFIG[key].has_key('irc_with_nick'):
						self.skype.say(CONFIG[key]['skype'], text_with_nick)
					else:
						self.skype.say(CONFIG[key]['skype'], msg)

	on_pubnotice = do_command
	on_privnotice = do_command
	on_pubmsg = handler
	on_privmsg = do_command

if __name__ == "__main__":
	host = CONFIG['irc']['xmlrpc_host']
	port = CONFIG['irc']['xmlrpc_port']
	sv = SimpleXMLRPCServer((host, int(port)))
	bridge = IrcSkypeBridge()
	th = threading.Thread(None, bridge.start, 'ircbot')
	th.daemon = True
	th.start()
	sv.register_instance(bridge)
	sv.serve_forever()

