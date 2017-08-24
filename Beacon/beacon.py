# This code is used to make a RPi act as an eddystone beacon. Code is written in a way such that Eddystone URL packet and Eddystone TLM packet are send alternately. The packet format is as follows:
# 0x02 - Flags length, 0x01 - Flags data type value, 0x06 - Flags data, 0x03 - Service UUID length, 0x03 - Service UUID data type value, 0xaa - 16bit Eddystone UUID, 0xfe - 16bit Eddystone UUID, 
# 0x0f - Service data length(this may change), 0x16 - Service Data Type value, 0xaa - 16bit Eddystone UUID, 0xfe - 16bit Eddystone UUID, 0x10/0x20 - Frame Type(10 - URL, 20 - TLM), 0xed - txpower
# dht11.py file is included as we obtain the temperature and humidity value from dht11 sensor and send it in the TLM packet

import os
import signal
import subprocess
import argparse
import sys
import time
import RPi.GPIO as GPIO
import dht11


# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

# List of possible ways in which a url could start
schemes = ["http://www.",
	"https://www.",
	"http://",
	"https://",
	]

# List of possible ways in which a url could end
extensions = [ ".com/", ".org/", ".edu/", ".net/", ".info/", ".biz/", ".gov/",".com", ".org", ".edu", ".net", ".info", ".biz", ".gov" ]


# Tx power is the first element of list data which will be appended later to message
data=[0xed]

# taking url as commandline arguement
url=sys.argv[1]

i=0

# Appending data on the basis of scheme used
for s in range(len(schemes)):
	scheme = schemes[s]
	if url.startswith(scheme):
		data.append(s)
		i += len(scheme)
		break
else:
	raise Exception("Invalid url scheme")


# Appending data on the basis of extension and converting the rest of the ascii characters into integers using ord function for URL packet
# ord - Converts ascii into integer
while i < len(url):
	if url[i] == '.':
		for e in range(len(extensions)):
			expansion = extensions[e]
			if url.startswith(expansion, i):
				data.append(e)
				i += len(expansion)
				break
		else:
			data.append(0x2E)
			i += 1
 	else:
		data.append(ord(url[i]))
		i += 1

# Padding for a total of 32 bytes for URL packet
while len(data)<19:
	data.append(0x00)

# This converts the data from integer into hex as we need to send hex data for URL packet
data=map(lambda x: "%02x" % x, data)

# This converts the list into a string
message=" ".join(data)
#print message


#subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x0008 17 02 01 06 03 03 aa fe 0f 16 aa fe 10 00 02 67 6f 6f 67 6c 65 2e 63 6f 6d 00 00 00 00 00 00 00",shell=True,stdout=None)


while True:
	# Reading sensor data from dht11.py file
	sensor_data1=[0x00]
	instance=dht11.DHT11(pin=4)
        result=instance.read()

        if result.is_valid():
                print("Temp: ",result.temperature)
                print("Humidity: ",result.humidity)

	# Appending sensor data for TLM packet
	sensor_data1.append(int(result.temperature))
	sensor_data1.append(0x00)
	sensor_data1.append(int(result.humidity))

	# Appending sensor data for a total of 32 for TLM packet
	while len(sensor_data1)<19:
        	sensor_data1.append(0x00)

	# This converts integer data into hex as we need to send hex data for TLM packet
	sensor_data2=map(lambda x: "%02x" % x,sensor_data1)

	# This converts list into string
	sensor_data=" ".join(sensor_data2)

	# Used to turn on the device on hci0
	subprocess.call("sudo hciconfig hci0 up",shell=True, stdout=None)

	# Used to send a non connectable advertisement
	subprocess.call("sudo hciconfig hci0 leadv 3",shell=True, stdout=None)
	
	# Advertising URL packet
	subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x0008 17 02 01 06 03 03 aa fe 0f 16 aa fe 10 " + message,shell=True,stdout=None)	

	time.sleep(2)

	# Stop advertising
	subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x000a 00",shell=True,stdout=None)

	# Advertising TLM packet
	subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x0008 17 02 01 06 03 03 aa fe 0f 16 aa fe 20 " + sensor_data,shell=True,stdout=None)

	time.sleep(2)
	
	# Stop Advertising
	subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x000a 00",shell=True,stdout=None)
	print("_______________________________________________________________")
	

