import sleekxmpp
import sys
import time
from sleekxmpp.xmlstream import ET, tostring
from optparse import OptionParser
from collections import namedtuple
import io
import gc
import ConfigParser
from thread import start_new_thread
import psutil
import Queue

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
startTime = 0
results    = []
tReceive  = 0
tSendB   = 0
tSendA   = 0
flagEnd = ' '

secTest   = config.getint('xmpp_general', 'duration')
msgPaySize = 0
plr        = 0
resultsStructure = namedtuple('Results','msg_payload plr timestamp cpu')

"""*******************************************************************
Main-Method: Set handlers and a connection to the broker
*******************************************************************"""
def main(i_msg, i_plr):

	global payload
	global msgPaySize
	global plr
	global xmpp
	global results

        ###Set the CPU measurement###
        q = Queue.Queue()
        start_new_thread(measure_cpu,(results, q))

	###Set global variables and constants###
        payload = ET.fromstring("<test xmlns = 'test'>%s</test>" % i_msg)
        msgPaySize = len(i_msg)
        plr = i_plr

	###Connect to the broker and set handlers###
	xmpp = sleekxmpp.ClientXMPP(jid, pw)
	xmpp.add_event_handler("session_start", on_start)
	xmpp.add_event_handler("pubsub_publish", on_receive)

	xmpp.register_plugin('xep_0004') ###Dataforms
	xmpp.register_plugin('xep_0060') ###PubSub

	xmpp.connect()
	xmpp.process(block=True)

"""***********************************************************
Measure_Cpu:
***********************************************************"""
def measure_cpu(results, q):

        while flagEnd != 'X':
                cpu = psutil.cpu_percent(interval=1)
                ts = int(round(time.time() * 1000 ))
                node = resultsStructure(msgPaySize, plr, ts, cpu)
                results.append(node)
                q.put(results)
        return results

"""*******************************************************************
Start-Handler: Is called when the connection is set.
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
Sub-Handler: Is called when we subscribed successfully.
Publish a message at the pub channel.
*******************************************************************"""
def on_sub(i_msg):
	
	global tSendB
	global tSendA

	tSendB = int(round(time.time() * 1000 ))
	xmpp['xep_0060'].publish(pubSubServer, pubNode, payload = payload)
	tSendA = int(round(time.time() * 1000 ))

"""*******************************************************************
Receive-Handler: Is called when a message at the sub channel is pub'ed.
Anwser it by published a message by yourself.
*******************************************************************"""
def on_receive(i_msg):
	global rounds
	global flagEnd
	global startTime
	global results
	global node
	global tSendB
	global tSendA

	rounds = rounds + 1
	
	if startTime == 0:
		startTime = time.time()
	
	if ((startTime + secTest) >= time.time()):
		xmpp['xep_0060'].publish(pubSubServer, pubNode, payload = payload)
	else:
		xmpp.disconnect()
		del results[0]
		print('Finished')
		flagEnd = 'X'
		time.sleep(5)
		print results
		
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


