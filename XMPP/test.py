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

import re

cmdStart = 'python ' + 'mqtt_c_throughput.py'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='127.0.0.1', port=22, username='pi', password='raspberry')
stdin, stdout, stderr = ssh.exec_command('cd ~/Desktop/Testszenario; python mqtt_c_throughput.py')
#stdin, stdout, stderr = ssh.exec_command(cmdStart)
ssh.close()

