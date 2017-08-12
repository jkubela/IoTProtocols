import psutil
import time
from collections import namedtuple
import csv
import os

node = None
results = []
results_structure = namedtuple('Results','timestamp cpu')

try:
	while (True):
		cpu = psutil.cpu_percent(interval=1)
		ts = int(round(time.time() * 1000 ))
		node = results_structure(ts, cpu)
		results.append(node)

except KeyboardInterrupt:
	filename = 'CPU_' + str(time.strftime("%Y%m%d")) + '_' + str(time.strftime("%H%M%S"))
	try:	
		with open(filename, 'a+') as csvfile:
			writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
 			writer.writerow(('timestamp', 'CPU'))
			writer.writerows([(data.timestamp, data.cpu) for data in results])
		
		print('File was created')
	except:
		print('Error create the file, so here is the result: ')
		print results	
