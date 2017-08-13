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

#Channels
ch_pub = config.get('amqp_c_general', 'topic_pub')
ch_sub = config.get('amqp_c_general', 'topic_sub')
ch_ack = config.get('amqp_c_general', 'ch_ack')
channel = None
connection = None

#User
user = config.get('amqp_server', 'user1') 
pw = config.get('amqp_server', 'pw1')

"""************************************************************
Main-Method: Used after starting the script
Connecting to the given host forever
************************************************************"""
def main():
	global connection

	###Connect to the broker###
	credentials = pika.PlainCredentials(user, pw)
	parameters = pika.ConnectionParameters(br_host, br_port, '/', credentials)
	connection = pika.SelectConnection(parameters=parameters, on_open_callback=on_connect)

	###Stay connected###
	connection.ioloop.start()

"""***********************************************************
On_Connect: Behaviour after connection to the broker is set
Opens a channel to the broker
***********************************************************"""
def on_connect(connection):

        connection.channel(on_channel_open)

"""***********************************************************
On_Channel_Open: Behaviour after the channel is opened
Declare the queue
***********************************************************"""
def on_channel_open(new_channel):

	global channel

	channel = new_channel
	channel.queue_declare(queue=ch_pub, callback=on_queue_declared)

"""***********************************************************
On_Queue_Declared / On_Reversequeue_Declared:
Consume the reverse-queue
***********************************************************"""
def on_queue_declared(frame):

	###Before we can consume the reverse-queue
	#we got to make sure that the queue exisits###
	channel.queue_declare(queue=ch_sub, callback=on_reversequeue_declared)

def on_reversequeue_declared(frame):

	###Subscribe to the given queue###
	channel.basic_consume(on_callback, queue=ch_sub, no_ack=ch_ack)        

"""************************************************************
On_Callback: Behaviour after receiving a message
Append the results and send a new  message
************************************************************"""
def on_callback(channel, method, header, body):

	global connection
	
	msg_payload = body
	t_received = int(round(time.time() * 1000))
	
	if msg_payload == 'Stop':
		#print('Deconnecting...')
		#connection.close()
		#connection = None
		#print('Reconnecting...')
		#main()
		print('New test')
	else:
		send_payload = str(t_received)
		print(send_payload)
		channel.basic_publish(exchange = '', routing_key = ch_pub, body = send_payload)
	       
"""**********************************************************************
Call the Main-Method when the script is called
*********************************************************************"""
if __name__ == "__main__":
	main()
