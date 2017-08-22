import pika
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

with open("config_amqp.ini") as c:
        sample_config = c.read()
config = ConfigParser.RawConfigParser(allow_no_value = True)
config.readfp(io.BytesIO(sample_config))

###Set the globals###

#Broker
br_host  = config.get('amqp_address', 'broker_host')
br_port  = config.getint('amqp_address', 'broker_port')
br_alive = config.getint('amqp_broker', 'alive')

#Message characteristics
msg_payload = 'default'                                         #Message payload: Given with initial script call

#Channels
ch_pub = config.get('amqp_s_general', 'topic_pub')
ch_sub = config.get('amqp_s_general', 'topic_sub')
ch_ack = config.get('amqp_s_general', 'ch_ack')
channel = None
connection = None

#Helper
rounds     = 0
start_time = 0
sec_test   = config.getint('amqp_general', 'duration')
results    = []
msg_pay_size = 0
plr        = '0%'                                               #Packet-Loss-Rate: Given with initial script call
t_receive  = 0                                                  #Message received (time): Set at on_message
t_send_b   = 0                                                  #Message send (time before)
t_send_a   = 0                                                  #Message send (time after)
results_structure = namedtuple('Results','round msg_payload plr latency time_before_sending time_received')
flag_end = ' '
latency = None

#User
user = config.get('amqp_server', 'user2')
pw = config.get('amqp_server', 'pw2')

"""************************************************************
Main-Method: Used after starting the script
Connecting to the given host forever
************************************************************"""
def main(i_payload, i_plr, i_latency):

        global msg_payload
        global plr
        global msg_pay_size
	global connection
	global latency

        ###Set the globals###
        msg_payload = i_payload
        msg_pay_size = len(msg_payload)
        plr = i_plr
	latency = i_latency

	###Connect to the broker###
        credentials = pika.PlainCredentials(user, pw)
        parameters = pika.ConnectionParameters(br_host, br_port, '/', credentials)
        connection = pika.SelectConnection(parameters=parameters, on_open_callback=on_connect)
	
	###Stay connected###
	connection.ioloop.start()

	if flag_end == 'X':
		return results

"""***********************************************************
On_Connect: Behaviour after connection to the broker is set
Opens a channel to the broker
***********************************************************"""
def on_connect(connection):

        print('Connected to broker ' + str(br_host) + ':' + str(br_port))
        connection.channel(on_channel_open)

"""***********************************************************
On_Channel_Open: Behaviour after the channel is opened
Subscribes to the queue
***********************************************************"""
def on_channel_open(new_channel):

	global channel

	channel = new_channel
	channel.queue_declare(queue=ch_pub, callback=on_queue_declared)

"""***********************************************************
On_Queue_Declared / On_Reversequeue_Declared:
Behaviour after the queue is subscribed
Consume the reverse-queue
***********************************************************"""
def on_queue_declared(frame):

	###Before we can consume the reverse-queue
	### we got to make sure that the queue exisits###
	channel.queue_declare(queue=ch_sub, callback=on_reversequeue_declared)

def on_reversequeue_declared(frame):

	global t_send_b

	###Subscribe to the given queue###
	channel.basic_consume(on_callback, queue=ch_sub, no_ack=ch_ack)        
        print('Subscribed to topic ' + str(ch_sub))

        ###Send a initial message to start the test###
        t_send_b = int(round(time.time() * 1000 ))
        channel.basic_publish(exchange = '', routing_key = ch_pub, body = msg_payload)

"""************************************************************
On_Callback: Behaviour after receiving a message
Send the message back
************************************************************"""
def on_callback(channel, method, header, body):

        global rounds
        global start_time
        global t_receive
        global results
	
	#print('Message received: ' + body)
        t_receive = int(round(time.time() * 1000 ))

	###Append the output-structure###
        node = results_structure(rounds, str(msg_pay_size), str(plr), str(latency), t_send_b, t_receive)
        results.append(node)

        if start_time == 0:
                start_time = time.time()

        if ((start_time + sec_test) >= time.time()):
                on_answer(body)
                rounds += 1
        else:
             	del results[0]
		on_stop_msg()

"""*************************************************************
Answer to a received message:
Send the given message back
*************************************************************"""
def on_answer(body):

        global t_send_b

        ###Get the time before sending the message###
        t_send_b = int(round(time.time() * 1000 ))

        ###Send the message###
        channel.basic_publish(exchange ='', routing_key = ch_pub, body = body)

"""************************************************************
On_Stop_Msg: Called at the end of the roundtrip
Send stop message
************************************************************"""
def on_stop_msg():
	
	global flag_end
       
	#channel.basic_publish(exchange ='', routing_key = ch_pub, body = "Stop")	
        channel.close()
        connection.close()
        connection.ioloop.start()
        print("Done")
	flag_end = 'X'

"""**********************************************************************
Call the Main-Method when the script is called
*********************************************************************"""
if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option('-m', '--message', dest='msg_payload', help='Payload of the message')
        parser.add_option('-p', '--plr', dest='plr', help='Packet-Loss-Rate of the network')
	parser.add_option('-l', '--latency', dest='latency')
        input, args = parser.parse_args()

        if input.msg_payload is None or input.plr is None:
                print('Please enter a message, plr and latency')
        else:
                main(input.msg_payload, input.plr, input.latency)
