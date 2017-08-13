import pika
import ConfigParser
import io

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
ch_ack = config.get('amqp_c_general', 'ch_ack')

#Channels
ch_pub = config.get('amqp_c_general', 'topic_pub')
ch_sub = config.get('amqp_c_general', 'topic_sub')
channel = None

#User
user = config.get('amqp_server', 'user1')
pw = config.get('amqp_server', 'pw1')


"""************************************************************
Main-Method: Used after starting the script
Connecting to the given host forever
************************************************************"""
def main():

	###Connect to the broker###
        credentials = pika.PlainCredentials(user, pw)
        parameters = pika.ConnectionParameters(br_host, br_port, '/', credentials)
        connection = pika.SelectConnection(parameters=parameters, on_open_callback=on_connect)
#	connection.RequestHeartbeat = 600
	
	###Stay connected###
        connection.ioloop.start()

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

        ###Subscribe to the given queue###
        channel.basic_consume(on_callback, queue=ch_sub, no_ack=ch_ack)
        print('Subscribed to topic ' + str(ch_sub))

"""************************************************************
On_Callback: Behaviour after receiving a message
Send the message back
************************************************************"""
def on_callback(channel, method, header, body):
	print('Message received ' + body)
	channel.basic_publish(exchange ='', routing_key = ch_pub, body = body)

"""***********************************************************
Call the Main-Method when the script is called
***********************************************************"""
if __name__ == "__main__":
        main()

