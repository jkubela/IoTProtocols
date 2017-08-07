import sys
import logging
import getpass
from optparse import OptionParser
import sleekxmpp

if sys.version_info < (3, 0):
	reload(sys)
	sys.setdefaultencoding('utf8')
else:
	raw_input = input

class SendMsgBot(sleekxmpp.ClientXMPP):
	def __init__(self, jid, password, recipient, message):
		
		super(SendMsgBot, self).__init__(jid, password)	

		self.recipient = recipient
		self.msg = message

		self.add_event_handler("session_start", self.start)
		self.add_event_handler("message", self.message)

	def start(self, event):
		self.send_presence()
		self.get_roster()

		self.send_message(mto=self.recipient, mbody=self.msg,mtype='chat')
		print("Message send")
		self.disconnect(wait=True)

	def message(self, msg):
		print("Message received")
		print(str(msg))

if __name__ == '__main__':
	optp = OptionParser()

	optp.add_option("-j", "--jid", dest="jid")
	optp.add_option("-p", "--password", dest="password")
	optp.add_option("-t", "--to", dest="to")
	optp.add_option("-m", "--message", dest="message")

	opts, args = optp.parse_args()

	xmpp = SendMsgBot('bob@rasp', 'root', 'alice@rasp', 'test')
	xmpp.register_plugin('xep_0030')
	xmpp.register_plugin('xep_0199')
	#xmpp.ssl_version = ssl.PROTOCOL_SSLv3

	xmpp.connect()
	print('connected')
	xmpp.process(block=True)
	print("Done")
	
