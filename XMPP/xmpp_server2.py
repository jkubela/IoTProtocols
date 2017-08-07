import sys
from optparse import OptionParser
import sleekxmpp
from sleekxmpp.plugins.xep_0323.device import Device
import time
from collections import namedtuple

if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding

    setdefaultencoding('utf8')
else:
    raw_input = input

"""**********************************************************************
Globals
**********************************************************************"""
jid = 'alice@raspberrypi'
pw = 'root'
nodeid = 'test'
commTimeout = 10
msg = None
jid_to = 'bob@raspberrypi'
jid_node = 'bob@raspberrypi/' + nodeid
jid_to = jid_node

ts_send = None
ts_received = None
msg_nr = 0
results_structure = namedtuple('Results','msg time_before_sending time_received')
results = []

"""-----------------------------------------------------------------------
Class of the server: Handle events that are not related to xep_0323
-----------------------------------------------------------------------"""
class IoT_Server(sleekxmpp.ClientXMPP):
   	"""*****************************************************
   	Set initial values and register event handlers
	*****************************************************"""
   	def __init__(self, jid, password):

        	sleekxmpp.ClientXMPP.__init__(self, jid, password)
        	self.add_event_handler("session_start", self.session_start)
		self.add_event_handler("message", self.message)
		self.device = None

        def message(self, msg):
 		ts_received = str(int(round(time.time() * 1000 )))
		node = results_structure(msg_nr, ts_send, ts_received)
	        results.append(node)

		print('Received Message - Starting Request at ' + str(int(round(time.time() * 1000 ))))
               	session = self['xep_0323'].request_data(self.boundjid.full, jid_node, self.datacallback, flags={"momentary": "true"})

        def datacallback(self, from_jid, result, nodeId=None, timestamp=None, fields=None, error_msg=None):
		global msg_nr
		global ts_send

		if result == 'done':
                	print('Request completed - Sending Message at ' + str(int(round(time.time() * 1000 ))))

                	###Data received: Tell the server###
			if msg_nr <= 30:
				msg_nr = msg_nr + 1
				ts_send = str(int(round(time.time() * 1000 )))
                		self.send_message(mto = jid_to, mbody = '1')
			else:
				print(str(results))
				self.disconnect()
        """*****************************************************
        Handle the initialisation of a new connection
        *****************************************************"""
   	def session_start(self, event):
        	self.send_presence()
        	self.get_roster()
 
"""-----------------------------------------------------------------------
Class of the IoT Device: Creates an IoT device that holds data
-----------------------------------------------------------------------"""
class IoT_Device(Device):
        """*****************************************************
        Set initial values
        *****************************************************"""
    	def __init__(self, nodeId):

        	Device.__init__(self, nodeId)
    
		###Set a default attribute value###
        	self.attribute = msg
        	self.update_sensor_data()

        """*****************************************************
        Update the data of the IoT device
        *****************************************************"""
	def update_sensor_data(self):
        
        	self._add_field(name="Attribute", typename="string", unit="C")
       	 	self._set_momentary_timestamp(self._get_timestamp())
        	self._add_field_momentary_data("Attribute", self.attribute,
                                       flags={"automaticReadout": "true"})

def main(i_msg):
	###Set globals###
	global msg
	msg = i_msg

	xmpp = IoT_Server(jid + "/" + nodeid, pw)
	xmpp.register_plugin('xep_0323')

 	myDevice = IoT_Device(nodeid)
  	xmpp['xep_0323'].register_node(nodeId=nodeid, device=myDevice, commTimeout=commTimeout)
	
	xmpp.connect()
  	xmpp.process(block=True)

if __name__ == '__main__':

	###Get the input###
  	optp = OptionParser()
  	optp.add_option("-m", "--message", dest="msg", help="Message")
  	opts, args = optp.parse_args()

	###If the input is correct: Call the Main-Method###
  	if opts.msg is None:
    		print("Please enter a message")
		exit()
	main(opts.msg)
