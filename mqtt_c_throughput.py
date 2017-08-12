import paho.mqtt.client as mqtt
import ConfigParser
import io

"""***********************************************************
Globals
***********************************************************"""
###Read the config###
with open("config_mqtt.ini") as c:
        sample_config = c.read()
config = ConfigParser.RawConfigParser(allow_no_value = True)
config.readfp(io.BytesIO(sample_config))

###Set configs###
br_host    = config.get('mqtt_address', 'broker_host')
br_port    = config.getint('mqtt_address', 'broker_port')
br_alive   = config.getint('mqtt_broker', 'alive')
msg_qos    = config.getint('mqtt_general', 'qos')
msg_retain = config.getboolean('mqtt_general', 'retain')
ch_pub     = config.get('mqtt_c_general', 'topic_pub')
ch_sub     = config.get('mqtt_c_general', 'topic_sub')

###Set variables###
client = mqtt.Client()

"""************************************************************
MAIN: Is called after the script has been started.
-Set connection characteristics.
-Connect to the broker.
***********************************************************"""
def main():

	###Globals###
        global client
        
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

"""***********************************************************
ON_CONNECT: Is called when connection is set.
-Subscribe to the given channel.
**********************************************************"""
def on_connect(client, userdata, flags, rc):

        try:
                client.subscribe(ch_sub, msg_qos)
        except:
                ('Cannot subscribe to ' + ch_sub + '. Test failed!')
                sys.exit()

"""************************************************************
ON_MESSAGE: Is called when message is published to the sub channel.
-Send the message back.
************************************************************"""
def on_message(client, userdata, msg):

	client.publish(ch_pub,msg.payload,msg.qos,msg.retain)

"""***********************************************************
INIT: Call the Main-Method when the script is called
***********************************************************"""
if __name__ == "__main__":
        main()
