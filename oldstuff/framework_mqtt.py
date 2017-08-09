import sys
import msg_payload as payload_generator
import ConfigParser
import io
import subprocess
import psutil
import paramiko
import sshtunnel
import mqtt_s_throughput as throughput

################################################################
###Output: Script started
print("This is the test environment for the server")
print("_______________________________________________________")
print("")

################################################################
###Set globals

###Read the config file
with open("config_framework.ini") as c:
        sample_config = c.read()
config = ConfigParser.RawConfigParser(allow_no_value = True)
config.readfp(io.BytesIO(sample_config))

###Set the globals from the config
tmpPayloadList = config.get('message', 'sizeList')
payloadList = tmpPayloadList.split(',')
network_device = config.get('network', 'device')

###Set other globals
msg_payload = 0
plr = 0
nr_loops = 0

###SSH
ssh_host_b = config.get('ssh', 'host_b')
ssh_port_b = config.getint('ssh', 'port_b')
ssh_user_b = config.get('ssh', 'user_b')
ssh_pw_b   = config.get('ssh', 'pw_b')

ssh_host_c = config.get('ssh', 'host_c')
ssh_port_c = config.getint('ssh', 'port_c')
ssh_user_c = config.get('ssh', 'user_c')
ssh_pw_c   = config.get('ssh', 'pw_c')

###CMDs to manipulate the network parameters
cmd_set_np = 'default'
cmd_set_np_alt = 'default'
cmd_del_np = 'sudo tcdel --device ' + network_device

################################################################
###Start the testszenario
while payloadList:
	###############################################################
	#Create the message payload
	payload_size = int(payloadList.pop(0))
	msg_payload = payload_generator.string_generator(payload_size)

    
	#Get the Packet-Loss-Rate list for the next loop
	tmpPlrList = config.get('plr', 'plrList')
	plrList = tmpPlrList.split(',')
	
	while plrList:
		#Increase the counter
		nr_loops = nr_loops + 1

		#Set the Packet-Loss-Rate
		plr = plrList.pop(0)
    
		################################################################
		###
		cmd_set_np_alt = 'sudo tcset --device eth0 --loss ' + str(plr)
		cmd_set_np = cmd_set_np_alt + ' --overwrite'
		################################################################
		###Set the Packet-Loss-Rate of the network
		if int(plr) != 0:
			#str_network_settings_alt = 'sudo tcset --device eth0 --loss ' + str(plr)
			#str_network_settings = str_network_settings_alt + ' --overwrite'
			try:
				subprocess.check_call([cmd_set_np], shell=True)         
			except:
				try:
					subprocess.check_call([cmd_set_np_alt], shell=True)
				except:
					system.exit(str(sys.exc_info()[0]))
		else:
			try:
				subprocess.call([cmd_del_np], shell=True)
			except:
				print("")
		###############################################################
		#Tell the user what happend
		print ("Test " + str(nr_loops) + " started with the following settings:")
		print("")
		print"Message Payload: " + str(payload_size)
		print"Packet-Loss-Rate: " + str(plr)
		print("_______________________________________________________")

		
		###############################################################
		###Set the Packet-Loss-Rate for the Broker and the Client
		
		###Broker###
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hostname=ssh_host_b, port=ssh_port_b, username=ssh_user_b, password=ssh_pw_b)
		stdin, stdout, stderr = ssh.exec_command(cmd_del_np)
                stdin, stdout, stderr = ssh.exec_command(cmd_set_np_alt)
		print stdout.readlines()
		ssh.close()

                ###Client###
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=ssh_host_c, port=ssh_port_c, username=ssh_user_c, password=ssh_pw_c)
                stdin, stdout, stderr = ssh.exec_command(cmd_del_np)
                stdin, stdout, stderr = ssh.exec_command(cmd_set_np_alt)
                print stdout.readlines()
                ssh.close()


		################################################################
		###Run the Throughput test
		print("Starting Throughput test for MQTT: ")
		throughput.main(msg_payload, plr)

		###############################################################
		###Run the Latency test

		################################################################
		###Run the CPU measurement test
