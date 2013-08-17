__author__ = 'Justin'

import os
import glob
import time
import datetime
from Adafruit_7Segment import SevenSegment
import RPi.GPIO as io
import subprocess

io.setmode(io.BCM)
switch_pin = 18
io.setup(switch_pin, io.IN)
segment = SevenSegment(address=0x70)

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
colon = 0

def read_temp_raw():
	catdata = subprocess.Popen(['cat',device_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out,err = catdata.communicate()
	out_decode = out.decode('utf-8')
	lines = out_decode.split('\n')
	return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

def display_temp():
	segment.setColon(False)
	temp = int(read_temp()[1]) # F
	# temp = int(read_temp()[0]) # C
	sign = (temp < 0)
	temp = abs(temp)
	digit_1 = temp % 10
	temp = temp / 10
	digit_2 = temp % 10
	temp = temp / 10
	digit_3 = temp % 10
	if sign :
		segment.writeDigitRaw(0, 0x40)       # - sign
	if digit_3 > 0 :
		segment.writeDigit(0, digit_3)       # Hundreds
	else:
		segment.writeDigitRaw(0, 0)
	if digit_2 > 0 :
		segment.writeDigit(1, digit_2)       # Tens
	else:
		segment.writeDigitRaw(1, 0)
	segment.writeDigit(3, digit_1)           # Ones
	segment.writeDigitRaw(4, 0x71) #F        # Temp units letter
	#segment.writeDigitRaw(4, 0x39) #C

def display_time():
	global colon
	now = datetime.datetime.now()
	hour = now.hour
	minute = now.minute
	second = now.second
	# Set hours
	segment.writeDigit(0, int(hour / 10))     # Tens
	segment.writeDigit(1, hour % 10)          # Ones
	# Set minutes
	segment.writeDigit(3, int(minute / 10))   # Tens
	segment.writeDigit(4, minute % 10)        # Ones
	# Toggle colon
	segment.writeDigitRaw(2, colon)
	colon = colon ^ 0x2


while True:
	if io.input(switch_pin):
		display_temp()
	else :
		display_time()
	time.sleep(0.5)