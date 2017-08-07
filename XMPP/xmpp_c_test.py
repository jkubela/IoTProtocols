import sys
from optparse import OptionParser
import sleekxmpp
import time
from sleekxmpp.xmlstream import ET, tostring

if sys.version_info < (3, 0):
        reload(sys)
        sys.setdefaultencoding('utf8')
else:
        raw_input = input

xmpp = None
to = 'alice@raspberrypi'
msg = 'IoTDevice'
nodeid = 'node1'
dev_timeout = 10
device = None
releaseMe = False
	
def pubsub_publish(msg):
	print("published")
	print('Published item %s to %s:' %(msg['pubsub_event']['items']['item']['id'], msg['pubsub_event']['items']['node']))
	data = msg['pubsub_event']['items']['item']['payload']
	if data is not None:
		print(tostring(data))
	else:
		print('No item content')

def pubsub_subscription(msg):
	print("Subscribtion")
	print('Subscription change for node %s:' % (msg['pubsub_event']['subscription']['node']))
	print(msg['pubsub_event']['subscription'])
	xmpp.disconnect(wait=True)
	"""***************************************************************************
	***************************************************************************"""

def session_start(event):

	global xmpp

	print('Started')
        self.send_presence()
        self.get_roster()

        node = 'node1'
        try:
                xmpp['xep_0060'].create_node('raspberrypi', node)
        except:
                print('Node %s already exists' % node)
        result = xmpp['xep_0060'].subscribe('raspberrypi', node) #callback = message)
	print(str(result))
    	
	"""***************************************************************************
	***************************************************************************"""
def message(msg):
       	print("Message received")
       	print(str(msg))

def main():

	global xmpp

	xmpp = sleekxmpp.ClientXMPP('bob@raspberrypi', 'root')
        
	xmpp.register_plugin('xep_0030')
        xmpp.register_plugin('xep_0060') #PubSub

        xmpp.add_event_handler("session_start", session_start)
        xmpp.add_event_handler("message", message)
        xmpp.add_event_handler("pubsub_publish", pubsub_publish)
        xmpp.add_event_handler("pubsub_subscription", pubsub_subscription)
	
        if xmpp.connect():
	        xmpp.process(block=True)

if __name__ == '__main__':
	main()
