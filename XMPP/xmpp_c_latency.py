import sys
from optparse import OptionParser
import sleekxmpp
from sleekxmpp.plugins.xep_0323.device import Device
import time

if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding

    setdefaultencoding('utf8')
else:
    raw_input = input

"""**********************************************************************
Globals
**********************************************************************"""
jid = 'bob@raspberrypi'
pw = 'root'
nodeid = 'test'
commTimeout = 10
msg = None
jid_to = 'alice@raspberrypi'
jid_node = 'alice@raspberrypi/' + nodeid
jid_to = jid_node
ts_send = 0

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
		global ts_send
		ts_send = str(int(round(time.time() * 1000 ))) 
		session = self['xep_0323'].request_data(self.boundjid.full, jid_to, self.datacallback, flags={"momentary": "true"})

        def datacallback(self, from_jid, result, nodeId=None, timestamp=None, fields=None, error_msg=None):
              	if results == 'done':
			ts_receive = str(int(round(time.time() * 1000 )))           
		        self.send_message(mto = jid_to, mbody = ts_receive + '|' + ts_send)

	def session_start(self, event):
        	self.send_presence()
        	self.get_roster()

        	session = self['xep_0323'].request_data(self.boundjid.full, jid_node,
                                                self.datacallback, flags={"momentary": "true"})

def main(i_msg):
        ###Set globals###
        global msg
        msg = i_msg

        xmpp = IoT_Server(jid + "/" + nodeid, pw)
        xmpp.register_plugin('xep_0323')

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
