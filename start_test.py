"""######################################################################################################
#########################################################################################################

#########################################################################################################
######################################################################################################"""

import sys
from importlib import import_module
import time
import csv
import os
import msg_payload as create_msg
import ConfigParser
import io
from collections import namedtuple
import subprocess

"""*******************************************************************
Globals
*******************************************************************"""
###Read the config###
with open("config_framework.ini") as c:
        sample_config = c.read()
config = ConfigParser.RawConfigParser(allow_no_value = True)
config.readfp(io.BytesIO(sample_config))

###Set configs###
tmp_prot     = config.get('general', 'protocols')
gl_protocols = tmp_prot.split(',')
tmp_test     = config.get('general', 'tests')
gl_tests     = tmp_test.split(',')
tmp_pay      = config.get('general', 'payload')
gl_payload   = tmp_pay.split(',')
tmp_plr      = config.get('general', 'plr')
gl_plr       = tmp_plr.split(',')
tmp_lat      = config.get('general', 'latency')
gl_latency   = tmp_lat.split(',')

###Set variables###
g_server_script = None
g_dir           = None
g_protocol      = None
g_test          = None
g_cmd_setnet = None

###Set constants###
gc_cmd_delnet = 'sudo tcdel --device eth0'
gc_cmd_setnet = 'sudo tcset --device eth0'

"""*******************************************************************
MAIN: Is called after the script has been started.
Performs test preperations and the test itself.
*******************************************************************"""
def main(i_protocol, i_test):
	###Globals###
	global g_protocol
	global g_test

	g_protocol = i_protocol.lower()
	g_test = i_test.lower()

	###Locals###
	broker_up = None
	broker_clean = None
	time_synch = None
	payload = None
	plr = None
	msg = None
	l_results = []

	###Check if the user has set the test environment###
	broker_up = raw_input('Is the broker started?[Y/N] ')
	check_yn(broker_up)
	broker_clean = raw_input('Is the broker is clean?[Y/N] ')
	check_yn(broker_clean)
	client_script = raw_input('Is the script for ' + i_test + ' started at the client?[Y/N] ')
	check_yn(client_script)
	time_sync = raw_input('Is the time synced for all devices? [Y/N] ')
	check_yn(time_sync)

	###Prepare everthing for the test###
	print('*' * 100)
	print('Preparing the test...')
	
	prepare()

	###Create payload, network plr and network plr for the current test. Then perform the test and print the results###
	for payload in gl_payload:

		###Create the message###
		print('Creating the message...')
		msg = create_msg.main(payload)

		for plr in gl_plr:

			for latency in gl_latency:
				
				###Set the given network characteristics###
				g_cmd_setnet = gc_cmd_setnet + ' --loss ' + plr +  ' --delay ' + latency
				try:
					subprocess.call([gc_cmd_delnet], shell=True)
				except:
					print('Error while deleting network settings')
				try:
					subprocess.call([g_cmd_setnet], shell=True)
				except:
					print('Error while setting network settings')
		
				print('*' * 50)
			        print('Test started with the following settings: ')
				print('Payload: ' + str(payload))
				print('PLR: ' + str(plr))
				print('Latency: ' + str(latency))

				###Reset the globals of the script###
				reload(g_server_script)
                                
				###Start the test###
				i_results = g_server_script.main(msg, plr, latency)
	
				###Create the output###
                                csvName = g_dir + '/' + i_protocol + '_' + i_test
                                create_csv(csvName, 'a+', i_results)

                                csvName = g_dir + '/' + g_protocol + '_' + g_test + '_' + str(plr) + '_' + str(payload) + '_' + str(time.strftime("%Y%m%d")) + '_' + str(time.strftime("%H%M%S"))
                                create_csv(csvName, 'a+', i_results)
				
				print('Test finished')

"""*******************************************************************
CREATE_CSV: Creates a csv-file for the given list.
Attenting: The list has to follow the following hard-coded structure.
*******************************************************************"""
def create_csv(csv_name, method, list):

	with open(csv_name, method) as csvfile:
		###Create a csv file following the given test specifications###
		writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

		if g_test == 'throughput':
                        writer.writerow(('round', 'msg_payload', 'plr', 'latency', 'time_before_sending', 'time_received', 'time_diff'))
                        writer.writerows([(data.round, data.msg_payload, data.plr, data.latency,  data.time_before_sending, data.time_received, str(int(data.time_received) - int(data.time_before_sending))) for data in list])

		elif g_test == 'latency':
			writer.writerow(('msg', 'msg_payload', 'plr', 'latency', 'time_before_sending', 'time_received'))
			writer.writerows([(data.msg, data.payload, data.plr, data.latency, data.time_before_sending, data.time_received, str(int(data.time_received) - int(data.time_before_sending))) for data in list])

		elif g_test == 'cpu':
                        if list is None:
				print('results is none')
				sys.exit()
			writer.writerow(('msg_payload', 'plr', 'ts', 'latency', 'cpu'))
                        writer.writerows([(data.msg_payload, data.plr, data.latency, data.timestamp, data.cpu) for data in list])

		else:
			print('ATTENTION, CANNOT WRITE RESULTS - PLEASE EXPAND THE CREATE_CSV-METHOD')
			sys.exit()

"""*******************************************************************
CREATE_RESULTS_FOLDER: Creates a directory at the current directory.
*******************************************************************"""
def create_results_folder():

	###Globals###
	global g_dir

	###Locals###
	input = None

	###Create the name of the directory###
	g_dir = 'Results_' + g_protocol + '_' + time.strftime("%Y%m%d") + '_' + time.strftime("%H%M%S")
	
	###Create the directory. If it exists already: Throw a warning###
	try:
		os.makedirs(g_dir)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
		else:
			input = self.yn_choice('Attention: The results folder already exists! Continue? [Y/N]')
			check_yn(input)

"""*******************************************************************
PREPARE: Tasks:
-Imports the server-script for the current protocol and test.
-Creates a folder for to save the test results.
*******************************************************************"""
def prepare():
	###Globals###
	global g_server_script

	###Locals###
	server_script = g_protocol + '_s_' + g_test	

	###Import the needed scripts###
	g_server_script = import_module(server_script)
	
	###Create a folder to save the results###
	create_results_folder()

"""*******************************************************************
CHECK_YN: Checks if the user typed in Yes or No.
Yes: Continue
No: Exit the script-
*******************************************************************"""
def check_yn(i_value):
	###Locals###
	upper_value = None

	upper_value = i_value.upper()

	###Case: Yes or No?###
	if upper_value == 'Y' or upper_value == 'YES':
		print('Ok')
	elif upper_value == 'N' or upper_value == 'NO':
		print('The test cannot be started!')
		sys.exit()
	else:
		print('Invalid input')
		sys.exit()

"""*******************************************************************
CHECK_PROTOCOLS: Checks if the given protocol is valid.
Yes: Continue
No: Exit
*******************************************************************"""
def check_protocol(i_protocol):
	###Locals###
	upper_protocol = None
	item = None	

	upper_protocol = i_protocol.upper()
	
	###Case: valid or not?###
	if upper_protocol in gl_protocols:
		return 'Y'
	else:
		print('Currently implemented protocols are: ')
		for item in gl_protocols:
			print('-' + item)
		return 'N'	
	
"""*******************************************************************
CHECK_TEST: Checks if the given test is valid.
Yes: Continue
No: Exit
*******************************************************************"""
def check_test(i_test):
	###Locals###
	upper_test = None
	item = None

	upper_test = i_test.upper()

	###Case: Valid or not?###
	if upper_test in gl_tests:
		return 'Y'
	else:
		print('Currently implemented tests are: ')
		for item in gl_tests:
			print('- ' + item)
		return 'N'


"""*******************************************************************
SCRIPT START: Ask for a protocol and a test type - also check if they
are valid. Continue by calling Main-Method if the input is valid.
*******************************************************************"""
if __name__ == '__main__':
	###Locals###
	protocol = None
	test = None
	b_protocol = None
	b_test = None

	###Ask for the protocol###
	protocol = raw_input('Please enter a protocol: ')
	b_protocol = check_protocol(protocol)
	check_yn(b_protocol)

	###Ask for testtype###
	test = raw_input('Please enter a test: ')
	b_test = check_test(test)
	check_yn(b_test)

	main(protocol, test)
