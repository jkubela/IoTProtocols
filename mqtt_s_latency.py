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
msg_qos    = config.getint('mqtt_general', 'qos')               #Quality of service
msg_retain = config.getboolean('mqtt_general', 'retain')
msg_payload = "TEST"
msg_amount = config.getint('mqtt_general', 'msg_amount')

#Channels
ch_pub = config.get('mqtt_s_general', 'topic_pub')
ch_sub = config.get('mqtt_s_general', 'topic_sub')

#Helper
client     = mqtt.Client()
counter	   = 0

###############################################################
###########Main-Method: Used after starting the script
#Connecting to the given broker forever
def main():

        global client

        #Connect to the broker
        client.connect(br_host, br_port, br_alive)

        #Define MQTT-methods
        client.on_connect = on_connect
        client.on_message = on_message

	print(str(msg_amount) + " messages will be send")

        #Stay connected
        client.loop_forever()

###############################################################
###########Behaviour after connection is set:
###########Connecting to the given channel

def on_connect(client, userdata, flags, rc):
        print("Connected to broker " + str(br_host) + ":" + str(br_port) + " with result code " + str(rc))
        client.subscribe(ch_sub, msg_qos)
        print("Subscribed to topic " + str(ch_sub) + " with QoS " + str(msg_qos))
        print("Publishing at " + ch_pub)
	
	on_send_msg()

###############################################################
###########Behaviour after receiving a message:

def on_message(client, userdata, msg):
	global counter

	if counter <= msg_amount: 

		if  msg.payload.decode() == "ready":
			on_send_msg()
			counter = counter + 1
			print("Message " + str(counter) + " send")
		elif msg.payload.decode() == "error":
			print("An Error occured")
	else:
	        client.publish(ch_pub, "stop", msg_qos, msg_retain)

		print("Done")
		client.disconnect()

###############################################################
###########Send messages:
def on_send_msg():
        payload = str(int(round(time.time()))) + ";" +  msg_payload

        client.publish(ch_pub, payload, msg_qos, msg_retain)

###############################################################
###########Call the Main-Method when the script is called

if __name__ == "__main__":
        main()

