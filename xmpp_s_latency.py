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
xmpp = None
payload = None

user = config.get('xmpp_server', 'user2')
host = config.get('xmpp_server', 'host')
pubSubServer = config.get('xmpp_server', 'pubsub')
jid = user + '@' + host
pubNode = config.get('xmpp_s_general', 'node_pub')
subNode = config.get('xmpp_s_general', 'node_sub')
pw = config.get('xmpp_server', 'pw2')

###Set analysis globals and constans###
rounds     = 0
results    = []
tSend   = 0
flagEnd = None

roundsTotal = config.getint('xmpp_general', 'msg_amount')
msgPaySize = 0
plr        = 0
resultsStructure = namedtuple('Results','msg payload plr latency time_before_sending time_received')
latency = 0

"""*******************************************************************
Main-Method: Set handlers and  a connection to the broker
*******************************************************************"""
def main(i_msg, i_plr, i_latency):

	global payload
	global msgPaySize
	global plr
	global xmpp
	global latency

	###Set global variables and constants###
        payload = ET.fromstring("<test xmlns = 'test'>%s</test>" % i_msg)
        msgPaySize = len(i_msg)
        plr = i_plr
	latency = i_latency

	###Connect to the broker and set handlers###
	xmpp = sleekxmpp.ClientXMPP(jid, pw)
	xmpp.add_event_handler("session_start", on_start)
	xmpp.add_event_handler("message", on_message)

        xmpp.register_plugin('xep_0004') ###Dataforms
	xmpp.register_plugin('xep_0060') #PubSub

	xmpp.connect()
	xmpp.process(block=True)

	if flagEnd == 'X':
		return results

"""*******************************************************************
Start-Handler: Is called when tThe connection is set.
Try to create the sub and pub channel. Subscribe to the sub channel.
*******************************************************************"""
def on_start(event):

	xmpp.send_presence()
        xmpp.get_roster()

        ###Set the publish model of the nodes to open so every user can publish content###
        form = xmpp['xep_0004'].stanza.Form()
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
Message-Handler: Is called when a message is received.
Gets the confirmation from the client that the message arrived at ts.
*******************************************************************"""
def on_message(msg):
###message received:
	
        global rounds
        global results
        global tSend
	global flagEnd	

	tReceive = msg['body']
	rounds = rounds + 1
	t = int(tReceive) - tSend	

	node = resultsStructure(rounds, msgPaySize, plr, latency, tSend, tReceive)
        results.append(node)
	
        if rounds <= roundsTotal:
		tSend = int(round(time.time() * 1000 ))
        	xmpp['xep_0060'].publish(pubSubServer, pubNode, payload = payload)
	else:
                del results[0]
                print('Finished successful')
                flagEnd = 'X'
		xmpp.disconnect()

"""*******************************************************************
Sub-Handler: Is called when we subscribed successfully.
Publish a message at the pub channel.
*******************************************************************"""
def on_sub(i_msg):
        global tSend

	tSend = int(round(time.time() * 1000 ))
        xmpp['xep_0060'].publish(pubSubServer, pubNode, payload = payload)

"""*******************************************************************
Init: Get userinput and call the Main-Method.
*******************************************************************"""
if __name__ == '__main__':
        optp = OptionParser()
        optp.add_option("-m", "--message", dest="msg")
        optp.add_option("-p", "--plr", dest="plr")
        optp.add_option("-l", "--latency", dest="latency")

        opts, args = optp.parse_args()

        if (opts.msg is not None) and (opts.plr is not None) and (opts.latency is not None):
                main(opts.msg, opts.plr, opts.latency)
        else:
                print('Please enter a message, PLR and latency')
