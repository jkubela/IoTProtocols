import sys
import logging
import getpass
from optparse import OptionParser
import sleekxmpp
import time

if sys.version_info < (3, 0):
	reload(sys)
	sys.setdefaultencoding('utf8')
else:
	raw_input = input

class SendMsgBot(sleekxmpp.ClientXMPP):
	def __init__(self, jid, password):
		print('init')
		super(SendMsgBot, self).__init__(jid, password)	

		self.add_event_handler("session_start", self.start)
		self.add_event_handler("message", self.message)
		print('End Init')

	def start(self, event):
		print('Pre-started')
		self.send_presence()
		self.get_roster()
		print("Startdd")
		
	def message(self, msg):
		print("Message received")
		print(str(msg))

if __name__ == '__main__':
	#optp = OptionParser()

	#optp.add_option("-j", "--jid", dest="jid")
	#optp.add_option("-p", "--password", dest="password")
	#optp.add_option("-t", "--to", dest="to")
	#optp.add_option("-m", "--message", dest="message")

	#opts, args = optp.parse_args()

	xmpp = SendMsgBot('alice@rasp', 'root')
	#xmpp.register_plugin('xep_0030')
	#xmpp.register_plugin('xep_0199')
	#xmpp.ssl_version = ssl.PROTOCOL_SSLv3

	if xmpp.connect():
		xmpp.process(block=True)
		print("Done")
	else:
		print("Unable to connect.")
