import paho.mqtt.client as mqtt
import time
import sys
import ConfigParser
import io
from optparse import OptionParser
from collections import namedtuple

"""************************************************************
Globals
************************************************************"""
###Read the config.ini###
with open("config_mqtt.ini") as c:
        sample_config = c.read()
config = ConfigParser.RawConfigParser(allow_no_value = True)
config.readfp(io.BytesIO(sample_config))

###Set the configs###
br_host    = config.get('mqtt_address', 'broker_host')
br_port    = config.getint('mqtt_address', 'broker_port')
br_alive   = config.getint('mqtt_broker', 'alive')
msg_qos    = config.getint('mqtt_general', 'qos')
msg_retain = config.getboolean('mqtt_general', 'retain')
msg_amount = config.getint('mqtt_general', 'msg_amount')
ch_pub     = config.get('mqtt_s_general', 'topic_pub')
ch_sub     = config.get('mqtt_s_general', 'topic_sub')

###Set variables###
msg_payload 	  = None
plr		  = None
latency 	  = None
msg_pay_size 	  = 0
client 		  = mqtt.Client()
results_structure = namedtuple('Results','msg payload plr time_before_sending time_received')
t_send 		  = 0
counter 	  = 0
flag_end 	  = None
results 	  = []

"""************************************************************
MAIN: Is called after the script has been started.
-Set connection characteristics.
-Connect to the broker.
************************************************************"""
def main(i_payload, i_plr, i_latency):

	###Globals###
        global client
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

	if flag_end == 'X':
		return results

"""***********************************************************
ON_CONNECT: Is called when connection is set.
-Subscribe to the given channel.
-Publish a message at the channel.
***********************************************************"""
def on_connect(client, userdata, flags, rc):

	try:
                client.subscribe(ch_sub, msg_qos)
        except:
                ('Cannot subscribe to ' + ch_sub + '. Test failed!')
                sys.exit()
	
	###Publish the message###
	send_msg()

"""************************************************************
ON_MESSAGE: Is called when message is published to the sub channel.
-Get statistical data.
-Publish a new  message.
************************************************************"""
def on_message(client, userdata, msg):

	###Globals###
	global counter
	global results

	if counter <= msg_amount: 

		counter = counter + 1

		###Append the output structure###
		t_received = msg.payload.decode()
        	node 	   = results_structure(counter, msg_pay_size, plr, t_send, t_received)
        	results.append(node)
		
		###Publish a new message###
		send_msg()

	else:
		stop_test()

"""************************************************************
SEND_MSG: Helper method.
-Publish a message. 
************************************************************"""
def send_msg(): 

	###Globals###
	global t_send

	###Get the current time and set the payload###
	t_send = int(round(time.time() * 1000 ))
        payload = msg_payload

        client.publish(ch_pub, payload, msg_qos, msg_retain)

"""************************************************************
STOP_TEST: Helper method.
-Ends the current test by disconnecting.
************************************************************"""
def stop_test():

	###Globals###
	global flag_end

	client.publish(ch_pub, "Stop")
	client.unsubscribe(ch_sub)
	client.disconnect()
	flag_end = 'X'
        del results[0]
	print('Finished successful')

"""************************************************************
Call the Main-Method when the script is called
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
