#import psutil
import popen
import pipe

proc = Popen('wimic cpu', stdout=PIPE, stderr=PIPE)
print str(proc.communicate())


#while 1 == 1:
#	a = psutil.cpu_percent(interval = 1)
#	print (a)
