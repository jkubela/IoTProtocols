import paho.mqtt.client as mqtt
import time
import sys
import ConfigParser
import io

###############################################################
###########Set the globals and get them from the config file

#####################
###Read the config.ini
with open("config_mqtt.ini") as c:
        sample_config = c.read()
config = ConfigParser.RawConfigParser(allow_no_value = True)
config.readfp(io.BytesIO(sample_config))

##################
###Set the globals
#Broker
br_host  = config.get('mqtt_address', 'broker_host')
br_port  = config.getint('mqtt_address', 'broker_port')
br_alive = config.getint('mqtt_broker', 'alive')

#Channels
ch_pub = config.get('mqtt_c_general', 'topic_pub')
ch_sub = config.get('mqtt_c_general', 'topic_sub')

#Message details
msg_qos = config.getint('mqtt_general', 'qos')

#Helper
g_client     = mqtt.Client()

###############################################################
###########Main-Method: Used after starting the script
#Connecting to the given broker forever
def main():

        global g_client

        ###Connect to the broker###
        g_client.connect(br_host, br_port, br_alive)

        ###Define MQTT-methods###
        g_client.on_connect = on_connect
        g_client.on_message = on_message

        ###Stay connected###
        g_client.loop_forever()

###############################################################
###########Behaviour after connection is set:
###########Connecting to the given channel

def on_connect(client, userdata, flags, rc):
        print("Connected to broker " + str(br_host) + ":" + str(br_port) + " with result code " + str(rc))
        g_client.subscribe(ch_sub, msg_qos)
        print("Subscribed to topic " + str(ch_sub) + " with QoS " + str(msg_qos))

###############################################################
###########Behaviour after receiving a message:
###########Send the message back

def on_message(client, userdata, msg):
       
	global g_client

	#Encode the message
	rec_payload = msg.payload.decode()

	#Timestamp after encoding the message
	ts_receive = int(round(time.time() * 1000))

	if rec_payload == 'Stop':
		print('Disconnecting...')
		g_client.disconnect()
		g_client = mqtt.Client()
		rec_payload = None
		ts_receive = 0
		print('Reconnecting...')
		main()
	else:
		###return the timestamp to the server###	
		send_payload = str(ts_receive)
		client.publish(ch_pub,send_payload,0,False)

###############################################################
###########Call the Main-Method when the script is called

if __name__ == "__main__":
        main()
