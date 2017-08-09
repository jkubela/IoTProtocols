import sys
from importlib import import_module
import time
import csv
import os
import msg_payload as create_msg
import ConfigParser
import io
from collections import namedtuple

"""*******************************************************************
Globals
*******************************************************************"""
###Read the config###
with open("config_framework.ini") as c:
        sample_config = c.read()
config = ConfigParser.RawConfigParser(allow_no_value = True)
config.readfp(io.BytesIO(sample_config))

###Set configs###
tmp_prot = config.get('general', 'protocols')
gl_protocols = tmp_prot.split(',')
tmp_test = config.get('general', 'tests')
gl_tests = tmp_test.split(',')
tmp_pay = config.get('general', 'payload')
gl_payload = tmp_pay.split(',')
tmp_plr = config.get('general', 'plr')
gl_plr = tmp_plr.split(',')
tmp_lat = config.get('general', 'latency')
gl_latency = tmp_lat.split(',')

###Set variables###
g_server_script = None
g_dir = None
g_protocol = None
g_test = None

"""*******************************************************************
MAIN:
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
	payload = None
	plr = None
	msg = None
	l_results = []

	broker_up = raw_input('Is the broker started?[Y/N] ')
	check_yn(broker_up)
	broker_clean = raw_input('Is the broker is clean?[Y/N] ')
	check_yn(broker_clean)
	client_script = raw_input('Is the script for ' + i_test + ' started at the client?[Y/N] ')
	check_yn(client_script)

	print('Preparing the test...')
	
	prepare()

	for payload in gl_payload:
		###Create the message###
		msg = 'test'

		for plr in gl_plr:

			for latency in gl_latency:

				settings = raw_input('Please set the PLR to ' + str(plr) + ' and the latency to ' + str(latency) + ' [Y/N] ')
				check_yn(settings)
				
				###Reset the globals of the script###
				reload(g_server_script)
                                
				###Start the test###
				i_results = g_server_script.main(msg, plr)

				###Create the output###
                                csvName = g_dir + '/' + i_protocol + '_' + i_test
                                create_csv(csvName, 'a+', i_results)

                                csvName = g_dir + '/' + i_protocol + '_' + i_test + '_' + str(g_plr) + '_' + str(g_payload) + '_' + str(time.strftime("%Y%m%d")) + '_' + str(time.strftime("%H%M%S"))
                                create_csv(csvName, 'a+', i_results)

"""*******************************************************************
CREATE_CSV: 
*******************************************************************"""
def create_csv(csv_name, method, list):

	with open(csv_name, method) as csvfile:
		writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

		if g_test == 'throughput':
			writer.writerow(('round', 'msg_payload', 'plr', 'time_before_sending', 'time_after_sending', 'time_received'))
			writer.writerows([(data.round, data.msg_payload, data.plr, data.time_before_sending, data.time_after_sending, data.time_received) for data in list])

		elif g_test == 'latency':
			writer.writerow(('msg', 'msg_payload', 'plr', 'time_before_sending', 'time_received'))
			writer.writerows([(data.msg, data.payload, data.plr, data.time_before_sending, data.time_received) for data in list])

		elif g_test == 'cpu':
                        if list is None:
				print('results is none')
				sys.exit()
			writer.writerow(('msg_payload', 'plr', 'ts', 'cpu'))
                        writer.writerows([(data.payload, data.plr, data.ts, data.cpu) for data in list])

		else:
			print('ATTENTION, CANNOT WRITE RESULTS - PLEASE EXPAND THE CREATE_CSV-METHOD')
			sys.exit()

"""*******************************************************************
*******************************************************************"""
def create_results_folder():

	###Globals###
	global g_dir

	###Locals###
	input = None

	g_dir = 'Results_' + g_protocol + '_' + time.strftime("%Y%m%d") + '_' + time.strftime("%H%M%S")
	try:
		os.makedirs(g_dir)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
		else:
			input = self.yn_choice('Attention: The results folder already exists! Continue? [Y/N]')
			check_yn(input)

"""*******************************************************************
PREPARE:
*******************************************************************"""
def prepare():
	###Globals###
	global g_server_script

	###Locals###
	server_script = g_protocol + '_s_' + g_test	

	g_server_script = import_module(server_script)

	"""
	if g_test == 'latency':
		if g_protocol == 'mqtt':	
			import mqtt_s_latency as g_server_script
                elif g_protocol == 'xmpp':
                        import xmpp_s_latency as g_server_script
                elif g_protocol == 'amqp':
                        import amqp_s_latency as g_server_script
		else:
			print('ATTENTION, CANNOT LOAD SERVER TEST SCRIPT - PLEASE EXPAND THE PREPARE-METHOD')
			sys.exit()
        elif g_test == 'throughput':
                if g_protocol == 'mqtt':
                        import mqtt_s_throughput as g_server_script
                elif g_protocol == 'xmpp':
                        import xmpp_s_throughput as g_server_script
                elif g_protocol == 'amqp':
                        import amqp_s_throughput as g_server_script
                else:
                        print('ATTENTION, CANNOT LOAD SERVER TEST SCRIPT - PLEASE EXPAND THE PREPARE-METHOD')
                        sys.exit()
        elif g_test == 'cpu':
                if g_protocol == 'mqtt':
                        import mqtt_s_cpu as g_server_script
                elif g_protocol == 'xmpp':
                        import xmpp_s_cpu as g_server_script
                elif g_protocol == 'amqp':
                        import amqp_s_cpu as g_server_script
                else:
                        print('ATTENTION, CANNOT LOAD SERVER TEST SCRIPT - PLEASE EXPAND THE PREPARE-METHOD')
                        sys.exit()
	else:
		print('ATTENTION, CANNOT LOAD SERVER TEST SCRIPT - PLEASE EXPAND THE PREPARE-METHOD')
                sys.exit()
	"""
	create_results_folder()

"""*******************************************************************
CHECK_YN:
*******************************************************************"""
def check_yn(i_value):
	###Locals###
	upper_value = None

	upper_value = i_value.upper()

	if upper_value == 'Y' or upper_value == 'YES':
		print('Ok')
	elif upper_value == 'N' or upper_value == 'NO':
		print('The test cannot be started!')
		sys.exit()
	else:
		print('Invalid input')
		sys.exit()

"""*******************************************************************
CHECK_PROTOCOLS: 
*******************************************************************"""
def check_protocol(i_protocol):
	###Locals###
	upper_protocol = None
	item = None	

	upper_protocol = i_protocol.upper()
	
	if upper_protocol in gl_protocols:
		return 'Y'
	else:
		print('Currently implemented protocols are: ')
		for item in gl_protocols:
			print('-' + item)
		return 'N'	
	
"""*******************************************************************
CHECK_TEST:
*******************************************************************"""
def check_test(i_test):
	###Locals###
	upper_test = None
	item = None

	upper_test = i_test.upper()

	if upper_test in gl_tests:
		return 'Y'
	else:
		print('Currently implemented tests are: ')
		for item in gl_tests:
			print('- ' + item)
		return 'N'


"""*******************************************************************
SCRIPT START: 
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
