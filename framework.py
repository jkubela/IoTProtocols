import sys
import msg_payload

################################################################
###Globals
payload_size = 200

print("_______________________________________________________")
print("This is the test environment for the server")
print("_______________________________________________________")
print("")

################################################################
###Create the message payload
msg_payload = msg_payload.string_generator(payload_size)
print("Message Payload:") 
print(msg_payload)
print("_______________________________________________________")

################################################################
###Set the Packet-Loss-Rate of the network

################################################################
###Run the Latency-Test for MQTT
if "MQTT" in sys.argv:
	print("Starting Latency-Test for MQTT: ")


################################################################
###Run the Throughput-Test for MQTT
