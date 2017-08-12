import paho.mqtt.client as mqtt
import time
import sys
import ConfigParser
import io

"""************************************************************
Globals
************************************************************"""
###Read the config###
with open("config_mqtt.ini") as c:
        sample_config = c.read()
config = ConfigParser.RawConfigParser(allow_no_value = True)
config.readfp(io.BytesIO(sample_config))

###Set configs###
br_host  = config.get('mqtt_address', 'broker_host')
br_port  = config.getint('mqtt_address', 'broker_port')
br_alive = config.getint('mqtt_broker', 'alive')
ch_pub = config.get('mqtt_c_general', 'topic_pub')
ch_sub = config.get('mqtt_c_general', 'topic_sub')
msg_qos = config.getint('mqtt_general', 'qos')

###Set variables###
g_client     = mqtt.Client()

"""************************************************************
MAIN: Is called after the script has been started.
-Set connection characteristics.
-Connect to the broker.
************************************************************"""
def main():

	###Globals###
        global g_client
        
	###Connect to the broker###
        try:
                g_client.connect(br_host, br_port, br_alive)
        except:
                print('Cannot connect to the broker. Test failed!')
                sys.exit()

        ###Define MQTT-methods###
        g_client.on_connect = on_connect
        g_client.on_message = on_message

        ###Stay connected###
        g_client.loop_forever()

"""***********************************************************
ON_CONNECT: Is called when connection is set.
-Subscribe to the given channel.
***********************************************************"""
def on_connect(client, userdata, flags, rc):

        try:
                client.subscribe(ch_sub, msg_qos)
        except:
                ('Cannot subscribe to ' + ch_sub + '. Test failed!')
                sys.exit()

"""************************************************************
ON_MESSAGE: Is called when message is published to the sub channel.
-Get statistical data and send it back.
************************************************************"""
def on_message(client, userdata, msg):
 
	###Globals###      
	global g_client

	###Encode the message###
	rec_payload = msg.payload.decode()

	###Fetch timestamp####
	ts_receive = int(round(time.time() * 1000))

	###Check if the test is finished###
	if rec_payload == 'Stop':
		#reconnect
		print('Disconnecting...')
		g_client.unsubscribe(ch_sub)
		g_client.disconnect()
		g_client = mqtt.Client()
		rec_payload = None
		ts_receive = 0
		print('Reconnecting...')
		main()
	else:
		#return the timestamp	
		send_payload = str(ts_receive)
		client.publish(ch_pub,send_payload,0,False)

"""************************************************************
INIT: Call the Main-Method when the script is called.
************************************************************"""
if __name__ == "__main__":
        main()
