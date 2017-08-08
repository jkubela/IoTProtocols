import sleekxmpp
import sys
from sleekxmpp.xmlstream import ET, tostring
import time

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
jid = user + '@' + server 
pubNode = 'node1'
subNode = 'node2'
pw = 'root'

"""*******************************************************************
Main-Method: Set handlers and  a connection to the broker
*******************************************************************"""
def main():

	global xmpp

	xmpp = sleekxmpp.ClientXMPP(jid, pw)
	xmpp.add_event_handler("session_start", on_start)
	xmpp.add_event_handler("pubsub_publish", on_receive)
	#xmpp.add_event_handler("message", message)
	xmpp.register_plugin('xep_0060') #PubSub

	xmpp.connect()
	xmpp.process(block=True)

def message(msg):
	print('MESSAGE')
"""*******************************************************************
Start-Handler: Is called when tThe connection is set.
Try to create the sub and pub channel. Subscribe to the sub channel.
*******************************************************************"""
def on_start(event):
	global xmpp

	xmpp.send_presence()
	xmpp.get_roster()	
	
	try:
		xmpp['xep_0060'].create_node(jid, PubNode)
	except:
		print('PubNode cannot be created')
        try:
                xmpp['xep_0060'].create_node(jid, SubNode)
        except:
                print('SubNode cannot be created')

	xmpp['xep_0060'].subscribe(jid, subNode)

"""*******************************************************************
Receive-Handler: Is called when a message at the sub channel is pub'ed.
Anwser it by published a message by yourself.
*******************************************************************"""
def on_receive(i_msg):
	#data = i_msg['pubsub_event']['items']['item']['payload']
	#print(tostring(data))
	t_receive = int(round(time.time() * 1000 ))
	msg = str(t_receive)
	xmpp.send_message(mto=jid, mbody=msg, mtype='chat')

"""*******************************************************************
Init: Get userinput and call the Main-Method.
*******************************************************************"""
if __name__ == '__main__':
	main()
