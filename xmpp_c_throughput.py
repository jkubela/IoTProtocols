import sleekxmpp
import sys
from sleekxmpp.xmlstream import ET, tostring
from optparse import OptionParser
import ConfigParser
import io

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

user = config.get('xmpp_server', 'user1')
host = config.get('xmpp_server', 'host')
pubSubServer = config.get('xmpp_server', 'pubsub')
jid = user + '@' + host
pubNode = config.get('xmpp_c_general', 'node_pub')
subNode = config.get('xmpp_c_general', 'node_sub')
pw = config.get('xmpp_server', 'pw1')

"""*******************************************************************
Main-Method: Set handlers and  a connection to the broker
*******************************************************************"""
def main(i_msg):

	global xmpp
	global payload
	
        payload = ET.fromstring("<test xmlns = 'test'>%s</test>" % i_msg)

	xmpp = sleekxmpp.ClientXMPP(jid, pw)
	xmpp.add_event_handler("session_start", on_start)
	xmpp.add_event_handler("pubsub_publish", on_receive)

        xmpp.register_plugin('xep_0004') ###Dataforms
	xmpp.register_plugin('xep_0060') ###PubSub

	xmpp.connect()
	xmpp.process(block=True)

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
	xmpp['xep_0060'].subscribe(pubSubServer, subNode)
	
"""*******************************************************************
Receive-Handler: Is called when a message at the sub channel is pub'ed.
Anwser it by published a message by yourself.
*******************************************************************"""
def on_receive(i_msg):
	xmpp['xep_0060'].publish(pubSubServer, pubNode, payload = payload)
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

