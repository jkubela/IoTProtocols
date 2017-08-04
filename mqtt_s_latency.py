import paho.mqtt.client as mqtt
import time
import sys
import ConfigParser
import io
from optparse import OptionParser
from collections import namedtuple

"""************************************************************
Set the globals and get data from the config file
************************************************************"""

###Read the config.ini###
with open("config_mqtt.ini") as c:
        sample_config = c.read()
config = ConfigParser.RawConfigParser(allow_no_value = True)
config.readfp(io.BytesIO(sample_config))

###Set the globals###
#Broker
br_host  = config.get('mqtt_address', 'broker_host')
br_port  = config.getint('mqtt_address', 'broker_port')
br_alive = config.getint('mqtt_broker', 'alive')

#Message and network characteristics
msg_qos    = config.getint('mqtt_general', 'qos')
msg_retain = config.getboolean('mqtt_general', 'retain')
msg_payload = None
plr = None
msg_pay_size = 0
msg_amount = config.getint('mqtt_general', 'msg_amount')

#Channels and client
ch_pub = config.get('mqtt_s_general', 'topic_pub')
ch_sub = config.get('mqtt_s_general', 'topic_sub')
client = mqtt.Client()

#Helper
results_structure = namedtuple('Results','msg payload plr time_before_sending time_received')
t_send = 0
counter = 0
flag_end = ' '
results = []

"""************************************************************
Main-Method: Used after starting the script
Connecting to the given host forever
************************************************************"""
def main(i_payload, i_plr):

        global client
	global msg_payload
	global plr
	global msg_pay_size

	###Set the message and network characteristics###
	msg_payload = i_payload
	msg_pay_size = len(msg_payload)
	plr = i_plr

        ###Connect to the broker###
        client.connect(br_host, br_port, br_alive)

        ###Define MQTT-methods###
        client.on_connect = on_connect
        client.on_message = on_message

        ###Stay connected###
        client.loop_forever()

	if flag_end == 'X':
		print(results)
		return results

"""***********************************************************
On_Connect: Behaviour after connection is set
Connecting to the given channel and send the first message
***********************************************************"""
def on_connect(client, userdata, flags, rc):

        print('Connected to broker ' + str(br_host) + ':' + str(br_port) + ' with result code ' + str(rc))
        client.subscribe(ch_sub, msg_qos)
        print('Subscribed to topic ' + str(ch_sub) + ' with QoS ' + str(msg_qos))
	
	send_msg()

"""************************************************************
On_Message: Behaviour after receiving a message:
Get the receiving timestamp and send a new message
************************************************************"""
def on_message(client, userdata, msg):

	global counter
	global results
	print('Received MSG: ' + str(msg.payload.decode()))
	if counter <= msg_amount: 

		counter = counter + 1

		###Append the output structure###
		t_received = msg.payload.decode()
        	node = results_structure(counter, msg_pay_size, plr, t_send, t_received)
        	results.append(node)
		
		send_msg()

	else:
		stop_test()

"""************************************************************
Send_Msg: Publishing a message at the connected broker 
************************************************************"""
def send_msg(): 

	global t_send

	t_send = int(round(time.time() * 1000 ))
        payload = msg_payload

        client.publish(ch_pub, payload, msg_qos, msg_retain)

"""************************************************************
Stop_Test:
************************************************************"""
def stop_test():

	global flag_end

	client.publish(ch_pub, "Stop")
	client.disconnect()
	print("Done")
	flag_end = 'X'
"""************************************************************
Call the Main-Method when the script is called
************************************************************"""
if __name__ == "__main__":

        parser = OptionParser()
        parser.add_option('-m', '--message', dest='msg_payload', help='Payload of the message')
        parser.add_option('-p', '--plr', dest='plr', help='Packet-Loss-Rate of the network')
        input, args = parser.parse_args()

        if input.msg_payload is None or input.plr is None:
                print('Please enter a message and the plr')
        else:
                main(input.msg_payload, input.plr)
