import sys
import msg_payload as payload_generator
import ConfigParser
import io
import subprocess
import psutil
import paramiko
import sshtunnel
import csv
import time
from optparse import OptionParser
import os
import errno

class TestScenario():
	"""************************************************************
	Define global variables
	************************************************************"""
	###CMDs to manipulate the network parameters###
	cmdSetNp = None
        cmdSetNpAlt = None
        cmdDelNp = None
	
	throughput = None
	latency = None
	results_dir = None

	"""************************************************************
	Constructor
	************************************************************"""
	def __init__(self, protocol):	
	
		global cmdDelNp

		self.payloadList = []
		self.networkDevice = None
		self.msgPayload = 0
		self.plr = 0
		self.payloadSize = 0
		self.protocol = protocol 	
		self.clientScript = protocol.lower() + '_c_'

		###SSH###
		self.ssh_host_b = None
		self.ssh_port_b = None
		self.ssh_user_b = None
		self.ssh_pw_b = None
		self.ssh_host_c = None
		self.ssh_port_c = None
		self.ssh_user_c = None
		self.ssh_pw_c = None

		self.read_config()

		###Shell commands###
		cmdDelNp =  'sudo tcdel --device ' + self.networkDevice

	"""************************************************************
	Method: Read the config file
	************************************************************"""
	def read_config(self):	
		###Local variables###
		tmpPayloadList = []
		
               ###Read the config file###
                with open("config_framework.ini") as c:
                        sample_config = c.read()
                	config = ConfigParser.RawConfigParser(allow_no_value = True)
                	config.readfp(io.BytesIO(sample_config))

		###Set the globals from the config
		tmpPayloadList = config.get('message', 'sizeList')
		self.payloadList = tmpPayloadList.split(',')
		self.networkDevice = config.get('network', 'device')

		###SSH
		self.ssh_host_b = config.get('ssh', 'host_b')
		self.ssh_port_b = config.getint('ssh', 'port_b')
		self.ssh_user_b = config.get('ssh', 'user_b')
		self.ssh_pw_b   = config.get('ssh', 'pw_b')

		self.ssh_host_c = config.get('ssh', 'host_c')
		self.ssh_port_c = config.getint('ssh', 'port_c')
		self.ssh_user_c = config.get('ssh', 'user_c')
		self.ssh_pw_c   = config.get('ssh', 'pw_c')

	"""************************************************************
	Method:
	************************************************************"""	
	def run(self):

		self.check_input(self.protocol)
		self.check_parameters()

                print('*' * 50)
                print('The test has been started for ' + self.protocol)
                print('This device is defined as the server')
                print('*' *50)

		self.create_results_folder()

                print('*' * 50)
                print('Perform the througput test')
                print('*' *50)
		self.run_throughput_test()	

                print('*' * 50)
                print('Perform the latency test')
                print('*' *50)
		self.read_config()
		self.run_latency_test()

        """************************************************************
        Method:
        ************************************************************"""
	def run_throughput_test(self):

		###Local variables###
		nrLoops = 0
		clientScript = self.clientScript + 'throughput.py'

		self.start_client_script(clientScript, '')

		while self.payloadList:
	        	self.payloadSize = int(self.payloadList.pop(0))
			self.msgPayload = payload_generator.string_generator(self.payloadSize)

			self.set_plr_list()

			while self.plrList:
				nrLoops = nrLoops + 1
				self.plr = self.plrList.pop(0)
				
				if nrLoops != 1:
					print('_' * 40)
				print('Started test ' + str(nrLoops) + ' with ')
				print('Payload size: ' + str(self.payloadSize))
				print('Packet-Loss-Rate: ' + str(self.plr))

				self.create_shell_commands()
				self.set_network_settings()
				self.set_network_settings_ssh(self.ssh_host_b, self.ssh_port_b, self.ssh_user_b, self.ssh_pw_b)
				self.set_network_settings_ssh(self.ssh_host_c, self.ssh_port_c, self.ssh_user_c, self.ssh_pw_c)

				reload(throughput)
				results = throughput.main(self.msgPayload, self.plr)			

				csvName = results_dir + '/' + self.protocol + '_throughput'
				self.create_csv(csvName, 'a+', results)
				
				csvName = results_dir + '/' + self.protocol + '_throughput_' + str(self.plr) + '_' + str(self.payloadSize) + '_' + str(time.strftime("%Y%m%d")) + '_' + str(time.strftime("%H%M%S"))
                                self.create_csv(csvName, 'a+', results)
		
		self.kill_client_script(clientScript)
		
        """************************************************************
        Method:
        ************************************************************"""
	def run_latency_test(self):
		
		###Local Variables###
		nrLoops = 0
                clientScript = self.clientScript + 'latency.py'

                while self.payloadList:
                        self.payloadSize = int(self.payloadList.pop(0))
                        self.msgPayload = payload_generator.string_generator(self.payloadSize)

                        self.set_plr_list()

                        while self.plrList:
		                self.start_client_script(clientScript,'')
                                nrLoops = nrLoops + 1
                                self.plr = self.plrList.pop(0)

                                if nrLoops != 1:
                                        print('_' * 40)
                                print('Started test ' + str(nrLoops) + ' with ')
                                print('Payload size: ' + str(self.payloadSize))
                                print('Packet-Loss-Rate: ' + str(self.plr))

                                self.create_shell_commands()
                                self.set_network_settings()
                                self.set_network_settings_ssh(self.ssh_host_b, self.ssh_port_b, self.ssh_user_b, self.ssh_pw_b)
                                self.set_network_settings_ssh(self.ssh_host_c, self.ssh_port_c, self.ssh_user_c, self.ssh_pw_c)

                                reload(latency)
                                results = latency.main(self.msgPayload, self.plr)
				
                                csvName = results_dir + '/' + self.protocol + '_latency'
                                self.create_csv_latency(csvName, 'a+', results)

                                csvName = results_dir + '/' + self.protocol + '_latency_' + str(self.plr) + '_' + str(self.payloadSize) + '_' + str(time.strftime("%Y%m%d")) + '_' + str(time.strftime("%H%M%S"))
                                self.create_csv_latency(csvName, 'a+', results)
				self.kill_client_script(clientScript)
				
        """************************************************************
        Method:
        ************************************************************"""
	def start_client_script(self, scriptname, scriptparams):
               
		###Create the Shell command###
		cmdStart = 'cd ~/Desktop/Testszenario; python ' + scriptname
		
		ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=self.ssh_host_c, port=self.ssh_port_c, username=self.ssh_user_c, password=self.ssh_pw_c)
                stdin, stdout, stderr = ssh.exec_command(cmdStart)
                ssh.close()

        """************************************************************
        Method:
        ************************************************************"""
	def kill_client_script(self, scriptname):

                ###Create the Shell command###
		cmdPid = "ps -ef | grep 'python " + scriptname + "' | grep -v 'grep' | awk '{ print $2}'"

		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hostname=self.ssh_host_c, port=self.ssh_port_c, username=self.ssh_user_c, password=self.ssh_pw_c)
		stdin, stdout, stderr = ssh.exec_command(cmdPid)
		for line in stdout.read().splitlines():
			stdin2, stdout2, stderr2 = ssh.exec_command('kill -9 ' + line)
		ssh.close()

	"""************************************************************
	Method: Check the protocoltype
	************************************************************"""
	def check_input(self, protocol):
		
		global throughput
		global latency

		if protocol == 'MQTT':
			import mqtt_s_throughput as throughput
			import mqtt_s_latency as latency
		elif protocol == 'AMQP':
			import amqp_s_throughput as throughput
			import amqp_s_latency as latency
		elif protocol == 'XMPP':
			print('Not implemented yet')
		elif protocol == 'COAP':
			print('Not implemented yet')
		elif protocol == 'DDS':
			print('Not implemented yet')
		else:
			print('This protocol is unknown. Known protocols are:')
			print('- MQTT')
			print('- AMQP')
			print('- COAP')
			print('- DDS')
			sys.exit()
        """************************************************************
        Method:
        ************************************************************"""
	def check_parameters(self):

		###Local variables###
		abort = ''

		if not self.payloadList:
			abort = 'X'
			print('Please enter a payload list at the config file!')
		if not self.networkDevice:
			abort = 'X'
			print('Please enter a network device at the config file!')
			
		if abort == 'X':
			print('Test scenario aborted')
			sys.exit()

        """************************************************************
        Method:
        ************************************************************"""
	def create_results_folder(self):

		global results_dir

		###Local variable###
		input = ''

		results_dir = 'Results_' + self.protocol + '_' + time.strftime("%Y%m%d") + '_' + time.strftime("%H%M%S")
                try:
                	os.makedirs(results_dir)
                except OSError as e:
               		if e.errno != errno.EEXIST:
                       		raise
			else:
				input = self.yn_choice('Attention: The results folder already exists! Continue? [y/n]')

		if input == 'y':
			print('Test continued')
		elif input == 'n':
			print('Test aborted')
			sys.exit()

        """************************************************************
        Method:
        ************************************************************"""
	def yn_choice(self, out_text):

		input = raw_input(out_text).lower()
		
		if input == 'n' or input == 'y':
			return input
		else:
			print(input + 'is no valid input')
			self.yn_choice(out_text)	 				


	"""************************************************************
	Method:
	************************************************************"""
	def set_plr_list(self):

		###Read the config file###
		with open("config_framework.ini") as c:
			sample_config = c.read()
                	config = ConfigParser.RawConfigParser(allow_no_value = True)
                	config.readfp(io.BytesIO(sample_config))

		tmpPlrList = config.get('plr', 'plrList')
		self.plrList = tmpPlrList.split(',')

	"""************************************************************
	Method:
	************************************************************"""
	def create_shell_commands(self):
		global cmdSetNpAlt
		global cmdSetNp
		
		cmdSetNpAlt = 'sudo tcset --device eth0 --loss ' + str(self.plr)
		cmdSetNp = cmdSetNpAlt + ' --overwrite'

	"""************************************************************
	Method:
	************************************************************"""
	def set_network_settings(self):
		try:
			subprocess.check_all([cmdDelNp], shell=True)
		except:
			print('Error while deleting network settings')

		try:
			subprocess.check_call([cmdSetNpAlt], shell=True)	
		except:
			print('Error while setting network settings')

	"""************************************************************
	Method:
	************************************************************"""
	def set_network_settings_ssh(self, host, port, user, pw):
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hostname=host, port=port, username=user, password=pw)
		stdin, stdout, stderr = ssh.exec_command(cmdDelNp)
		stdin, stdout, stderr = ssh.exec_command(cmdSetNpAlt)
		#print stdout.readlines()
		ssh.close()

	"""************************************************************
	Method:
	************************************************************"""
	def create_csv(self, csv_name, method, list):

		with open(csv_name, method) as csvfile:
			writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
			writer.writerow(('round', 'msg_payload', 'plr', 'time_before_sending', 'time_after_sending', 'time_received'))
			writer.writerows([(data.round, data.msg_payload, data.plr, data.time_before_sending, data.time_after_sending, data.time_received) for data in list])

        """************************************************************
        Method:
        ************************************************************"""
        def create_csv_latency(self, csv_name, method, list):

                with open(csv_name, method) as csvfile:
                        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
                        writer.writerow(('msg', 'msg_payload', 'plr', 'time_before_sending', 'time_received'))
                        writer.writerows([(data.msg, data.payload, data.plr, data.time_before_sending, data.time_received) for data in list])

"""************************************************************
Method: Main
************************************************************"""
def main(protocol):
	test = TestScenario(protocol)
	test.run()

"""************************************************************
Call the Main-Method when the script is called
************************************************************"""
if __name__ == "__main__":

        parser = OptionParser()
        parser.add_option('-p', '--protocol', dest='protocol', help='Protocol that should be tested')
        input, args = parser.parse_args()

        if input.protocol is None:
               # print('Please enter a protocol')
		input.protocol = raw_input('Please enter a protocol: ')
        else:
                main(input.protocol)
