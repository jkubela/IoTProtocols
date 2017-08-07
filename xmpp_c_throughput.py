import sleekxmpp
import sys
from sleekxmpp.xmlstream import ET, tostring
from optparse import OptionParser

"""*******************************************************************
Python version lower than 2 does not use UTF-8 encode as default, so
we have to set it.
*******************************************************************"""
if sys.version_info < (3, 0):
        reload(sys)
        sys.setdefaultencoding('utf8')
else:
        raw_input = input

"""*******************************************************************
Globals
*******************************************************************"""
xmpp = None
user = 'alice'
server = 'localhost'
jidFrom = user + '@' + server 
pubNode = 'node1'
subNode = 'node2'
pw = 'root'
payload = None

"""*******************************************************************
Main-Method: Set handlers and  a connection to the broker
*******************************************************************"""
def main(i_msg):

	global xmpp
	global payload
	
        payload = ET.fromstring("<test xmlns = 'test'>%s</test>" % i_msg)

	xmpp = sleekxmpp.ClientXMPP(jidFrom, pw)
	xmpp.add_event_handler("session_start", on_start)
	xmpp.add_event_handler("pubsub_publish", on_receive)

	xmpp.register_plugin('xep_0060') #PubSub

	xmpp.connect()
	xmpp.process(block=True)

"""*******************************************************************
Start-Handler: Is called when tThe connection is set.
Try to create the sub and pub channel. Subscribe to the sub channel.
*******************************************************************"""
def on_start(event):
	global xmpp

	xmpp.send_presence()
	xmpp.get_roster()	
	
	try:
		xmpp['xep_0060'].create_node(jidFrom, PubNode)
	except:
		print('PubNode cannot be created')
        try:
                xmpp['xep_0060'].create_node(jidFrom, SubNode)
        except:
                print('SubNode cannot be created')

	xmpp['xep_0060'].subscribe(jidFrom, subNode)

"""*******************************************************************
Receive-Handler: Is called when a message at the sub channel is pub'ed.
Anwser it by published a message by yourself.
*******************************************************************"""
def on_receive(i_msg):
	xmpp['xep_0060'].publish(jidFrom, pubNode, payload = payload)
	print('received')
"""*******************************************************************
Init: Get userinput and call the Main-Method.
*******************************************************************"""
if __name__ == '__main__':
        optp = OptionParser()
        optp.add_option("-m", "--message", dest="msg")
        opts, args = optp.parse_args()

	if opts.msg is not None:
        	main(opts.msg)
	else:
		print('Please enter a message')

