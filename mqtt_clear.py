import paho.mqtt.client as mqtt
import time
import sys
import ConfigParser
import io
from optparse import OptionParser
from collections import namedtuple
import gc

"""************************************************************
Set the globals and get data from the config file
************************************************************"""
###Read the config###
with open("config_mqtt.ini") as c:
        sample_config = c.read()
config = ConfigParser.RawConfigParser(allow_no_value = True)
config.readfp(io.BytesIO(sample_config))

###Set the globals###
#Broker
br_host  = config.get('mqtt_address', 'broker_host')
br_port  = config.getint('mqtt_address', 'broker_port')
br_alive = config.getint('mqtt_broker', 'alive')

#Message characteristics
msg_qos    = config.getint('mqtt_general', 'qos')
msg_retain = config.getboolean('mqtt_general', 'retain')

#Channels
ch_pub = config.get('mqtt_s_general', 'topic_pub')
ch_sub = config.get('mqtt_s_general', 'topic_sub')

#Helper
client     = mqtt.Client()

"""************************************************************
Main-Method: Used after starting the script
Connecting to the given host forever
************************************************************"""
def main():

        global client

        ###Connect to the broker###
	try:
        	client.connect(br_host, br_port, br_alive)
	except:
		print('Cannot connect to ' + br_host)

        ###Define MQTT-methods###
        client.on_connect = on_connect
        client.on_message = on_message

        ###Stay connected###
        client.loop_forever()

"""***********************************************************
On_Connect: Behaviour after connection is set
Connecting to the given channel
***********************************************************"""
def on_connect(client, userdata, flags, rc):

	msg_payload = 'Test'

	try:
        	client.subscribe(ch_sub, msg_qos)
		print('sub')
	except:
		print('Cannot subscribe to ' + ch_sub)	

	try:
        	client.publish(ch_pub, msg_payload, msg_qos, msg_retain)
		print('pub')
	except:
		print('Cannot publish at ' + ch_pub)

	ts = int(round(time.time() * 1000))

	if ts + 1000 < int(round(time.time() * 1000)):
		print('FAIL')

"""************************************************************
On_Message: Behaviour after receiving a message:
Send the message back
************************************************************"""
def on_message(client, userdata, msg):
	
	print(str(msg))

	###Clear the channels
	client.publish(ch_pub, bytearray([0]), 0, True)
	client.publish(ch_sub, bytearray([0]), 0, True)

	###Unsubscribe and disconnect
	client.unsubscribe(ch_sub)
	client.unsubscribe(ch_pub)
	client.disconnect()


if __name__ == '__main__':
	main()
