import sys
from optparse import OptionParser
import sleekxmpp
import time
from sleekxmpp.plugins.xep_0323.device import Device
from sleekxmpp.xmlstream import ET, tostring

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
		self.add_event_handler("pubsub_subscription", self.pubsub_subscription)
		self.device = None	

	def pubsub_subscription(self, msg):
		print("Subscribtion")
		#print('Subscription change for node %s:' % (msg['pubsub_event']['subscription']['node']))
		#print(msg['pubsub_event']['subscription'])
		print(str(msg))
		#self.disconnect(wait=True)
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
		result = self['xep_0060'].subscribe('bob@raspberrypi', node, callback = self.callback)
		print(str(result))
		#self['xep_0060'].publish('raspberrypi', node, payload = payload)
		
		
	def callback(self, msg):
		print('Callback')
		print(str(msg))
	"""***************************************************************************
	***************************************************************************"""
	def message(self, msg):
        	print("Message received")
        	print(str(msg))
	
class Thermometer(Device):

	def __init__(self, nodeId):
		Device.__init__(self, nodeId)
		self.temperature = 25
		self.update_sensor_data()

	def refresh(self, fields):
		self.temperature = self.temperature + 1
		self._set_momentary_timestamp(self._get_timestamp())
		self._add_field_momentary_data('Temperature', self.get_temperature(), flags={"automaticReadout": "true"})

	def update_sensor_data(self):
		self._add_field(name="Temperature", typename="numeric", unit="C")
                self._set_momentary_timestamp(self._get_timestamp())
                self._add_field_momentary_data('Temperature', self.get_temperature(), flags={"automaticReadout": "true"})

	def get_temperature(self):
		return str(self.temperature)

def main():
	xmpp = IoT_Device('bob@raspberrypi', 'root')
	myDevice = Thermometer('test')
	xmpp['xep_0323'].register_node(nodeid, myDevice, 10)
	xmpp.connect()
	xmpp.process(block=True)

if __name__ == '__main__':
	main()
