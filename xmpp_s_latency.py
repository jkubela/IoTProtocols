import sleekxmpp
import sys
import time
from sleekxmpp.xmlstream import ET, tostring
from optparse import OptionParser
from collections import namedtuple
import io
import gc

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
"""
with open("config_xmpp.ini") as c:
        sample_config = c.read()
config = ConfigParser.RawConfigParser(allow_no_value = True)
config.readfp(io.BytesIO(sample_config))
"""

###Set xmpp globals and constans###
xmpp = None
payload = None

user = 'alice'
server = 'localhost'
jid = user + '@' + server
pubNode = 'node2'
subNode = 'node1'
pw = 'root'

###Set analysis globals and constans###
rounds     = 0
results    = []
tSend   = 0

roundsTotal = 10  #config.getint('mqtt_general', 'duration')
msgPaySize = 0
plr        = 0
resultsStructure = namedtuple('Results','round msg_payload plr time_before_sending time_received')

"""*******************************************************************
Main-Method: Set handlers and  a connection to the broker
*******************************************************************"""
def main(i_msg, i_plr):

	global payload
	global msgPaySize
	global plr
	global xmpp

	###Set global variables and constants###
        payload = ET.fromstring("<test xmlns = 'test'>%s</test>" % i_msg)
        msgPaySize = len(i_msg)
        plr = i_plr

	###Connect to the broker and set handlers###
	xmpp = sleekxmpp.ClientXMPP(jid, pw)
	xmpp.add_event_handler("session_start", on_start)
	xmpp.add_event_handler("message", on_message)

	xmpp.register_plugin('xep_0060') #PubSub

	xmpp.connect()
	xmpp.process(block=True)

"""*******************************************************************
Start-Handler: Is called when tThe connection is set.
Try to create the sub and pub channel. Subscribe to the sub channel.
*******************************************************************"""
def on_start(event):

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

	xmpp['xep_0060'].subscribe(jid, subNode, callback = on_sub)

"""*******************************************************************
Message-Handler: Is called when a message is received.
Gets the confirmation from the client that the message arrived at ts.
*******************************************************************"""
def on_message(msg):
###message received:
	
        global rounds
        global results
        global tSend

	tReceive = msg['body']
	rounds = rounds + 1
	
        node = resultsStructure(rounds, msgPaySize, plr, tSend, tReceive)
        results.append(node)

        if rounds <= roundsTotal:
		tSend = int(round(time.time() * 1000 ))
                xmpp['xep_0060'].publish(jid, pubNode, payload = payload)
	else:
                xmpp.disconnect()
                del results[0]
                print('Finished')
                print results

"""*******************************************************************
Sub-Handler: Is called when we subscribed successfully.
Publish a message at the pub channel.
*******************************************************************"""
def on_sub(i_msg):
        global tSend

	tSend = int(round(time.time() * 1000 ))
	xmpp['xep_0060'].publish(jid, pubNode, payload = payload)

"""*******************************************************************
Init: Get userinput and call the Main-Method.
*******************************************************************"""
if __name__ == '__main__':
        optp = OptionParser()
        optp.add_option("-m", "--message", dest="msg")
        optp.add_option("-p", "--plr", dest="plr")
        opts, args = optp.parse_args()

        if opts.msg is not None and opts.plr:
                main(opts.msg, opts.plr)
        else:
                print('Please enter a message and a PLR')
