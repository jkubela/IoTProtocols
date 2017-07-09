import paho.mqtt.client as mqtt
import time
import sys
import ConfigParser
import io

###############################################################
###########Set the globals and get them from the config file

#####################
###Read the config.ini
with open("config.ini") as c:
	sample_config = c.read()
config = ConfigParser.RawConfigParser(allow_no_value = True)
config.readfp(io.BytesIO(sample_config))

##################
###Set the globals
#Broker
br_host  = config.get('mqtt_address', 'broker_host')
br_port  = config.getint('mqtt_address', 'broker_port')
br_alive = config.getint('mqtt_broker', 'alive')

#Message characteristics
msg_qos    = config.getint('mqtt_general', 'qos')		#Quality of service
msg_retain = config.getboolean('mqtt_general', 'retain')
msg_payload = "TEST"

#Channels
ch_pub = config.get('mqtt_s_general', 'topic_pub')
ch_sub = config.get('mqtt_s_general', 'topic_sub')

#Helper
rounds     = 0
start_time = 0
sec_test   = config.getint('mqtt_general', 'duration')
results	   = []
client	   = mqtt.Client()
msg_pay	   = 0	 						#Message-Payload: Given with initial script call
plr	   = "0%"						#Packet-Loss-Rate: Given with initial script call
t_receive  = 0							#Message received (time): Set at on_message
t_send_b   = 0							#Message send (time before)
t_send_a   = 0							#Message send (time after)

###############################################################
###########Main-Method: Used after starting the script
#Connecting to the given host forever
def main():

	global client
	global t_send_a
	global t_send_b

	#Set globals
        try: sys.argv[1]
        except IndexError:
                print("No Message-Payload given")
        else:
                msg_pay = sys.argv[1]
                print("Message-Payload: " + msg_pay)

        try: sys.argv[2]
        except IndexError:
                print("No Packet-Loss-Rate given")
        else:
                plr = sys.argv[2]
                print("Packet-Los-Rate: " + plr)


	#Connect to the broker
	client.connect(br_host, br_port, br_alive)

	#Define MQTT-methods
	client.on_connect = on_connect
	client.on_message = on_message

	#Stay connected
	client.loop_forever()	

###############################################################
###########Behaviour after connection is set:
###########Connecting to the given channel

def on_connect(client, userdata, flags, rc):
        print("Connected to broker " + str(br_host) + ":" + str(br_port) + " with result code " + str(rc))
        client.subscribe(ch_sub, msg_qos)
	print("Subscribed to topic " + str(ch_sub) + " with QoS " + str(msg_qos))

        #Send initial message to start the test
        t_send_b = int(round(time.time() * 1000 ))
        client.publish(ch_pub, msg_payload, msg_qos, msg_retain)
        t_send_a = int(round(time.time() * 1000 ))


###############################################################
###########Behaviour after receiving a message:
###########Send the message back

def on_message(client, userdata, msg):
	global rounds
	global start_time
	global t_receive


	t_receive = int(round(time.time() * 1000 ))

	#Append the output-structure
        results.append([rounds, t_receive, t_send_b, t_send_a, msg_pay, plr])

	if start_time == 0:
		start_time = time.time()

	if ((start_time + sec_test) >= time.time()):
		on_answer(msg)
		rounds += 1
	else:
		on_stop_msg()
		client.unsubscribe(ch_sub)
		client.disconnect()
		print(rounds)
		print("END")
		del results[0]
		print(results)

###############################################################
###########Answer to a received message:
###########Send the given message back

def on_answer(msg):
	global results
	global t_send_a
	global t_send_b

	#Get the time before sending the message	
	t_send_b = int(round(time.time() * 1000 ))

	#Send the message
	client.publish(ch_pub,msg.payload,msg.qos,msg.retain)

	#Get the time after sending the message
	t_send_a = int(round(time.time() * 1000 ))

###############################################################
###########Send stop message
def on_stop_msg():
	client.publish(ch_pub, "STOP", 0, False)

###############################################################
###########Call the Main-Method when the script is called

if __name__ == "__main__":
	main()
