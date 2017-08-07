import sys
import logging
import getpass
from optparse import OptionParser
import sleekxmpp
from sleekxmpp.xmlstream import ET, tostring

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
		self.add_event_handler("pubsub_publish", self.pub)
		self.add_event_handler("pubsub_subscription", self.sub)
	
	def start(self, event):
		self.send_presence()
		self.get_roster()

		#self.send_message(mto=self.recipient, mbody=self.msg,mtype='chat')
		#print("Message send")
		#try:
		#	self['xep_0060'].create_node('raspberrypi', 'node2')
		#except:
		#	print("Node already exists")
		#result = self['xep_0060'].get_nodes('raspberrypi', 'node1')
		#for item in result['disco_items']['items']:
		#	print(str(item))
		#self['xep_0060'].subscribe('raspberrypi', 'node1')
		#payload = ET.fromstring("<test xmlns='test'>%s</test>" % 'Hallo')
		#self['xep_0060'].publish('raspberrypi', 'node1', payload)
		self.disconnect(wait=True)

	def message(self, msg):
		print("Message received")
		#print(str(msg))
		#self.disconnect(wait=True)

	def pub(self, msg):
		print('Published')
		self.disconnect(wait=True)

	def sub(self, msg):
		print('Subscribed')

if __name__ == '__main__':
	optp = OptionParser()

	optp.add_option("-j", "--jid", dest="jid")
	optp.add_option("-p", "--password", dest="password")
	optp.add_option("-t", "--to", dest="to")
	optp.add_option("-m", "--message", dest="message")


	opts, args = optp.parse_args()

	xmpp = SendMsgBot('bob@raspberrypi', 'root', 'bob@raspberrypi', 'HI')
	xmpp.register_plugin('xep_0030')
	xmpp.register_plugin('xep_0060')
	xmpp.register_plugin('xep_0199')
	xmpp.register_plugin('xep_0323')
	xmpp.register_plugin('xep_0325')
	#xmpp.ssl_version = ssl.PROTOCOL_SSLv3

	try:
        	self['xep_0060'].create_node('raspberrypi', 'node2')
        except:
                print("Node already exists")

	try:
		result = xmpp['xep_0060'].get_nodes('raspberrypi', 'node1')
       		for item in result['disco_items']['items']:
                	print(str(item))
	except:
		print('error')


	if xmpp.connect():
		print('connected')
		xmpp.process(block=True)
		print("Done")
	else:
		print("Unable to connect.")
