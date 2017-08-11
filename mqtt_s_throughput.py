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
msg_payload = 'default'

#Channels
ch_pub = config.get('mqtt_s_general', 'topic_pub')
ch_sub = config.get('mqtt_s_general', 'topic_sub')

#Helper
rounds     = 0
start_time = 0
sec_test   = config.getint('mqtt_general', 'duration')
results	   = []
client	   = mqtt.Client()
msg_pay_size = 0
plr	   = 0
t_receive  = 0
t_send_b   = 0
t_send_a   = 0
results_structure = namedtuple('Results','round msg_payload plr time_before_sending time_after_sending time_received')
flag_end = ' '

"""************************************************************
Main-Method: Used after starting the script
Connecting to the given host forever
************************************************************"""
def main(i_payload, i_plr):

	global client
	global t_send_a
	global t_send_b
	global msg_payload
	global plr
	global msg_pay_size

	###Set the globals###
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
		return results

"""***********************************************************
On_Connect: Behaviour after connection is set
Connecting to the given channel
***********************************************************"""
def on_connect(client, userdata, flags, rc):

	global t_send_b
	global t_send_a
   
	print('Connected to broker ' + str(br_host) + ':' + str(br_port) + ' with result code ' + str(rc))
        client.subscribe(ch_sub, msg_qos)
	print('Subscribed to topic ' + str(ch_sub) + ' with QoS ' + str(msg_qos))

	###Send a initial message to start the test###
        t_send_b = int(round(time.time() * 1000 ))
        client.publish(ch_pub, msg_payload, msg_qos, msg_retain)
        t_send_a = int(round(time.time() * 1000 ))

"""************************************************************
On_Message: Behaviour after receiving a message:
Send the message back
************************************************************"""
def on_message(client, userdata, msg):

	global rounds
	global start_time
	global t_receive
	global results
	global flag_end

	###Set the current timestamp: Message received###	
	t_receive = int(round(time.time() * 1000 ))

	###Append the output-structure###
     	node = results_structure(rounds, msg_pay_size, plr, t_send_b, t_send_a, t_receive)
	results.append(node)

	###Check if the start time is already set. Else: Set it###
	if start_time == 0:
		start_time = time.time()

	###Check if the time running this test is over###
	if ((start_time + sec_test) >= time.time()):
		on_answer(msg)
		rounds += 1
	else:
		on_stop_msg()
		client.unsubscribe(ch_sub)
		client.disconnect()
		flag_end = 'X'
		del results[0]
		print("Finished")

"""*************************************************************
Answer to a received message:
Send the given message back
*************************************************************"""
def on_answer(msg):

	global t_send_a
	global t_send_b

	###Get the time before sending the message###	
	t_send_b = int(round(time.time() * 1000 ))

	###Send the message###
	client.publish(ch_pub,msg.payload,msg.qos,msg.retain)

	###Get the time after sending the message###
	t_send_a = int(round(time.time() * 1000 ))

"""************************************************************
On_Stop_Msg: Called at the end of the roundtrip 
Send stop message
************************************************************"""
def on_stop_msg():
	client.publish(ch_pub, "STOP", 0, False)

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
