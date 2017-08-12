import sleekxmpp
import sys
import time
from sleekxmpp.xmlstream import ET, tostring
from optparse import OptionParser
from collections import namedtuple
import io
import gc
import ConfigParser

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
###Read the config.ini###
with open("config_xmpp.ini") as c:
        sample_config = c.read()
config = ConfigParser.RawConfigParser(allow_no_value = True)
config.readfp(io.BytesIO(sample_config))

###Set xmpp globals and constans###
xmpp    = None
payload = None

user 	     = config.get('xmpp_server', 'user2')
touser 	     = config.get('xmpp_server', 'user1')
host 	     = config.get('xmpp_server', 'host')
pubSubServer = config.get('xmpp_server', 'pubsub')
jid          = user + '@' + host
tojid 	     = touser + '@' + host
pubNode      = config.get('xmpp_s_general', 'node_pub')
subNode      = config.get('xmpp_s_general', 'node_sub')
pw           = config.get('xmpp_server', 'pw2')

###Set analysis globals and constans###
rounds     = 0
startTime  = 0
results    = []
tReceive   = 0
tSendB     = 0
flagEnd = ' '

secTest    	 = config.getint('xmpp_general', 'duration')
msgPaySize	 = 0
plr        	 = 0
latency		 = 0
resultsStructure = namedtuple('Results','round msg_payload plr latency time_before_sending time_received')
g_msg 		 = None

"""*******************************************************************
MAIN:
-Set handlers 
-Connect to the broker
*******************************************************************"""
def main(i_msg, i_plr, i_latency):

	###Globals###
	global payload
	global msgPaySize
	global plr
	global xmpp
	global g_msg
	global latency

        payload    = ET.fromstring("<test xmlns = 'test'>%s</test>" % i_msg)
        msgPaySize = len(i_msg)
        plr 	   = i_plr
	g_msg	   = i_msg
	latency	   = i_latency

	###Connect to the broker and set handlers###
	xmpp = sleekxmpp.ClientXMPP(jid, pw)
	xmpp.add_event_handler("session_start", on_start)
	xmpp.add_event_handler("pubsub_publish", on_receive)

	xmpp.register_plugin('xep_0004') ###Dataforms
	xmpp.register_plugin('xep_0060') ###PubSub

	try:
		xmpp.connect()
	except:
		print('Cannot connect to the broker. Test failed!')
		sys.exit()

	xmpp.process(block=True)

	if flagEnd == 'X':
		return results

"""*******************************************************************
ON_START: Is called when the connection is set.
-Try to create the sub and pub channel.
-Subscribe to the sub channel.
*******************************************************************"""
def on_start(event):

	xmpp.send_presence()
	xmpp.get_roster()	

        ###Send a message with the payload to the client, so that it can be send back###
        xmpp.send_message(mto = tojid, mbody = g_msg, mtype='chat')

	###Set the publish model of the nodes to open so every user can publish content###
	form	     = xmpp['xep_0004'].stanza.Form()
	form['type'] = 'submit'
	form.add_field(var='pubsub#publish_model', value='open')
	
	###Try to create the used nodes###
	try:
                xmpp['xep_0060'].create_node(pubSubServer, pubNode, config=form)
        except:
                print('PubNode cannot be created')
        try:
                xmpp['xep_0060'].create_node(pubSubServer, subNode, config=form)
        except:
                print('SubNode cannot be created')
	
	###Subscribe to a node###
	xmpp['xep_0060'].subscribe(pubSubServer, subNode, callback = on_sub)

"""*******************************************************************
ON_SUB: Is called when we subscribed successfully.
-Publish a message at the pub channel.
*******************************************************************"""
def on_sub(i_msg):

	###Globals###	
	global tSendB

	tSendB = int(round(time.time() * 1000 ))

	try: 
		xmpp['xep_0060'].publish(pubSubServer, pubNode, payload = payload)
	except:
		print('Cannot publish at ' + pubNode + '. Test failed!')

"""*******************************************************************
ON_RECEIVE: Is called when a message at the sub channel is pub'ed.
-Anwser it by published a message by yourself.
*******************************************************************"""
def on_receive(i_msg):
	###Globals###
	global rounds
	global flagEnd
	global startTime
	global results
	global node
	global tSendB
	global tSendA

	tReceive = int(round(time.time() * 1000 ))
	rounds = rounds + 1
        
	node = resultsStructure(rounds, msgPaySize, plr, latency, tSendB, tReceive)
        results.append(node)
	
	if startTime == 0:
		startTime = time.time()
	
	if ((startTime + secTest) >= time.time()):
       		tSendB = int(round(time.time() * 1000 ))
		xmpp['xep_0060'].publish(pubSubServer, pubNode, payload = payload)
	else:
		del results[0]
		print('Finished')
		flagEnd = 'X'
		xmpp.disconnect()	

"""*******************************************************************
INIT: Get userinput and call the Main-Method.
*******************************************************************"""
if __name__ == '__main__':

        ###Get input-parameters###
        parser = OptionParser()
        parser.add_option('-m', '--message', dest='msg_payload', help='Payload of the message')
        parser.add_option('-p', '--plr', dest='plr', help='Packet-Loss-Rate of the network')
        parser.add_option('-l', '--latency', dest='latency', help='Latency of the network')
        input, args = parser.parse_args()

        ###Check if input-parameters are valid and call the main-method###
        if (input.msg_payload is None) or (input.plr is None) or (input.latency is None):
                print('Please enter a message, plr and latency')
        else:
                main(input.msg_payload, input.plr, input.latency)

