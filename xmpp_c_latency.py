import sleekxmpp
import sys
from sleekxmpp.xmlstream import ET, tostring
import time
import io
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

user = config.get('xmpp_server', 'user1')
userTo = config.get('xmpp_server', 'user2')
host = config.get('xmpp_server', 'host')
pubSubServer = config.get('xmpp_server', 'pubsub')
jid = user + '@' + host
toId = userTo + '@' + host
pubNode = config.get('xmpp_s_general', 'node_pub')
subNode = config.get('xmpp_s_general', 'node_sub')
pw = config.get('xmpp_server', 'pw2')

"""*******************************************************************
Main-Method: Set handlers and a connection to the broker
*******************************************************************"""
def main():

	global xmpp

	xmpp = sleekxmpp.ClientXMPP(jid, pw)
	xmpp.add_event_handler("session_start", on_start)
	xmpp.add_event_handler("pubsub_publish", on_receive)

        xmpp.register_plugin('xep_0004') ###Dataforms
	xmpp.register_plugin('xep_0060') #PubSub

	xmpp.connect()
	xmpp.process(block=True)

"""*******************************************************************
Start-Handler: Is called when the connection is set.
Try to create the sub and pub channel. Subscribe to the sub channel.
*******************************************************************"""
def on_start(event):
	print("started")
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
Sub-Handler: Is called when a message at the sub channel is pub'ed.
Anwser it by sending a message with the receive TS back.
*******************************************************************"""
def on_receive(i_msg):
	data = i_msg['pubsub_event']['items']['item']['payload']

	t_receive = int(round(time.time() * 1000 ))
	msg = str(t_receive)
	xmpp.send_message(mto=toId, mbody=msg, mtype='chat')
	print("received")

"""*******************************************************************
Init: Get userinput and call the Main-Method.
*******************************************************************"""
if __name__ == '__main__':
	main()
