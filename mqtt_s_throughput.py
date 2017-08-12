
import paho.mqtt.client as mqtt
import time
import sys
import ConfigParser
import io
from optparse import OptionParser
from collections import namedtuple
import gc

"""************************************************************
Globals
************************************************************"""
###Read the config###
with open("config_mqtt.ini") as c:
	sample_config = c.read()
config = ConfigParser.RawConfigParser(allow_no_value = True)
config.readfp(io.BytesIO(sample_config))

###Set configs###
#Broker
br_host    = config.get('mqtt_address', 'broker_host')
br_port    = config.getint('mqtt_address', 'broker_port')
br_alive   = config.getint('mqtt_broker', 'alive')
msg_qos    = config.getint('mqtt_general', 'qos')
msg_retain = config.getboolean('mqtt_general', 'retain')
ch_pub     = config.get('mqtt_s_general', 'topic_pub')
ch_sub     = config.get('mqtt_s_general', 'topic_sub')
sec_test   = config.getint('mqtt_general', 'duration')

###Set variables###
msg_payload  = 'default'
rounds       = 0
start_time   = 0
results	     = []
client	     = mqtt.Client()
msg_pay_size = 0
plr	     = 0
latency      = 0
t_send_b     = 0
flag_end     = None
results_structure = namedtuple('Results','round msg_payload plr latency time_before_sending time_received')

"""************************************************************
MAIN: Is called after the script has been started.
-Set connection characteristics.
-Connect to the broker.
************************************************************"""
def main(i_payload, i_plr, i_latency):

	###Globals###
	global client
	global t_send_a
	global t_send_b
	global msg_payload
	global plr
	global msg_pay_size

	msg_payload  = i_payload
	msg_pay_size = len(msg_payload)
	plr	     = i_plr
	latency      = i_latency

	###Connect to the broker###
	try:
		client.connect(br_host, br_port, br_alive)
	except:
		print('Cannot connect to the broker. Test failed!')
		sys.exit()

	###Define MQTT-methods###
	client.on_connect = on_connect
	client.on_message = on_message

	###Stay connected###
	client.loop_forever()	

	###Return the results when the test is over###
	if flag_end == 'X':
		return results

"""***********************************************************
ON_CONNECT: Is called when connection is set.
-Subscribe to the given channel.
-Publish a message at the channel.
***********************************************************"""
def on_connect(client, userdata, flags, rc):

	####Globals###
	global t_send_b
   
	try:
		client.subscribe(ch_sub, msg_qos)
	except:
		('Cannot subscribe to ' + ch_sub + '. Test failed!')
		sys.exit()

	###Send a initial message to start the test###
        t_send_b = int(round(time.time() * 1000 ))
	try:
        	client.publish(ch_pub, msg_payload, msg_qos, msg_retain)
	except:
		print('Cannot publish at ' + ch_pub + '. Test failed!')
		sys.exit()

"""************************************************************
ON_MESSAGE: Is called when message is published to the sub channel.
-Get statistical data.
-Publish the message again.
************************************************************"""
def on_message(client, userdata, msg):

	###Globals###
	global rounds
	global start_time
	global results
	global flag_end
	
	###Locals###
	#Set the current timestamp
	t_receive = int(round(time.time() * 1000 ))

	###Append the output-structure###
     	node = results_structure(rounds, msg_pay_size, plr, latency, t_send_b, t_receive)
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
		print('Finished successful')

"""*************************************************************
ON_ANSWER: Helper method.
-Publish the given message.
*************************************************************"""
def on_answer(msg):

	global t_send_a
	global t_send_b

	###Get the time before sending the message###	
	t_send_b = int(round(time.time() * 1000 ))

	###Send the message###
	client.publish(ch_pub,msg.payload,msg.qos,msg.retain)

"""************************************************************
ON_STOP_MSG: Helper method.
-Published the message "Stop".
************************************************************"""
def on_stop_msg():
	client.publish(ch_pub, "STOP", 0, False)

"""************************************************************
INIT: Call the Main-Method when the script is called.
************************************************************"""
if __name__ == "__main__":

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
