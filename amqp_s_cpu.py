import pika
import time
import sys
import ConfigParser
import io
from optparse import OptionParser
from collections import namedtuple
from thread import start_new_thread
import psutil
import Queue

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
sec_test   = config.getint('amqp_general', 'cpu_duration')
results    = []
msg_pay_size = 0
plr        = '0%'                                               #Packet-Loss-Rate: Given with initial script call
t_receive  = 0                                                  #Message received (time): Set at on_message
t_send_b   = 0                                                  #Message send (time before)
t_send_a   = 0                                                  #Message send (time after)
results_structure = namedtuple('Results','msg_payload plr latency timestamp cpu')
flag_end = ' '
latency = 0

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

        ###Set the CPU measurement###
        q = Queue.Queue()
        start_new_thread(measure_cpu,(results, q))

	###Connect to the broker###
	parameters = pika.ConnectionParameters(host=br_host, port=br_port)
	connection = pika.SelectConnection(parameters=parameters, on_open_callback=on_connect)
	
	###Stay connected###
	connection.ioloop.start()

	if flag_end == 'X':
		return results

"""***********************************************************
Measure_Cpu:
***********************************************************"""
def measure_cpu(results, q):

        while flag_end != 'X':
                cpu = psutil.cpu_percent(interval=1)
                ts = int(round(time.time() * 1000 ))
                node = results_structure(msg_pay_size, plr, latency, ts, cpu)
                results.append(node)
                q.put(results)
        return results

"""***********************************************************
On_Connect: Behaviour after connection to the broker is set
Opens a channel to the broker
***********************************************************"""
def on_connect(connection):

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

        ###Send a initial message to start the test###
        channel.basic_publish(exchange = '', routing_key = ch_pub, body = msg_payload)

"""************************************************************
On_Callback: Behaviour after receiving a message
Send the message back
************************************************************"""
def on_callback(channel, method, header, body):

        global start_time
	global results	

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
	time.sleep(5)
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

        if input.msg_payload is None or input.plr is None and input.latency is None:
                print('Please enter a message, plr and latency')
        else:
                main(input.msg_payload, input.plr, input.latency)
