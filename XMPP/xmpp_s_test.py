import sys
from optparse import OptionParser
import sleekxmpp
import time
from sleekxmpp.plugins.xep_0323.device import Device
from sleekxmpp.xmlstream import ET, tostring
import sleekxmpp.xmlstream

if sys.version_info < (3, 0):
        reload(sys)
        sys.setdefaultencoding('utf8')
else:
        raw_input = input

xmpp = None
to = 'alice@raspberrypi'
msg = 'IoTDevice'
nodeid = 'test'
dev_timeout = 10
device = None
releaseMe = False

class IoT_Device(sleekxmpp.ClientXMPP):

	"""***************************************************************************
	***************************************************************************"""
        def __init__(self, jid, password):
                sleekxmpp.ClientXMPP.__init__(self, jid, password)
                self.add_event_handler("session_start", self.session_start)
                self.add_event_handler("message", self.message)
		self.register_plugin('xep_0030')
	        self.register_plugin('xep_0060') #PubSub
       		self.register_plugin('xep_0323')
	        self.register_plugin('xep_0325')
		self.add_event_handler("pubsub_publish", self.pubsub_publish)
		self.device = None
		
	def pubsub_publish(self, msg):
		print("published")
		#print(str(msg))
		print('Published item %s to %s:' %(msg['pubsub_event']['items']['item']['id'], msg['pubsub_event']['items']['node']))
		data = msg['pubsub_event']['items']['item']['payload']
		if data is not None:
			print(tostring(data))
		else:
			print('No item content')
		#self.disconnect()

	"""***************************************************************************
	***************************************************************************"""
	def session_start(self, event):
	        print('Started')
        	self.send_presence()
        	self.get_roster()
	
		node = 'node1'
		payload = ET.fromstring("<test xmlns='test'>%s</test>" % 'message')
		try:
			self['xep_0060'].create_node('raspberrypi', node)
		except:
			print("")
		self['xep_0060'].publish('raspberrypi', node, payload = payload)
		result = self['xep_0060'].get_nodes('raspberrypi', node)
                for item in result['disco_items']['items']:    
			print(str(item)) 
		print(str(result))		
	"""***************************************************************************
	***************************************************************************"""
	def message(self, msg):
        	print("Message received")
        	print(str(msg))
def main():
	xmpp = IoT_Device('bob@raspberrypi', 'root')
	xmpp.connect()
	xmpp.process(block=True)

if __name__ == '__main__':
	main()
