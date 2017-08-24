import os
import signal
import subprocess
import argparse
import sys
import time
import RPi.GPIO as GPIO
import dht11


#initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()


schemes = ["http://www.",
	"https://www.",
	"http://",
	"https://",
	]


extensions = [ ".com/", ".org/", ".edu/", ".net/", ".info/", ".biz/", ".gov/",".com", ".org", ".edu", ".net", ".info", ".biz", ".gov" ]


data=[0xed]
url=sys.argv[1]
i=0


for s in range(len(schemes)):
	scheme = schemes[s]
	if url.startswith(scheme):
		data.append(s)
		i += len(scheme)
		break
else:
	raise Exception("Invalid url scheme")


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


while len(data)<19:
	data.append(0x00)


data=map(lambda x: "%02x" % x, data)


message=" ".join(data)
#print message


#subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x0008 17 02 01 06 03 03 aa fe 0f 16 aa fe 10 00 02 67 6f 6f 67 6c 65 2e 63 6f 6d 00 00 00 00 00 00 00",shell=True,stdout=None)


while True:
	sensor_data1=[0x00]
	instance=dht11.DHT11(pin=4)
        result=instance.read()
        if result.is_valid():
        #        print("Temperature: %d C" % result.temperature)
        #        print("Humidity: %d %%" % result.humidity)
                print("Temp: ",result.temperature)
                print("Humidity: ",result.humidity)


	sensor_data1.append(int(result.temperature))
	sensor_data1.append(0x00)
	sensor_data1.append(int(result.humidity))

	while len(sensor_data1)<19:
        	sensor_data1.append(0x00)

	sensor_data2=map(lambda x: "%02x" % x,sensor_data1)
	sensor_data=" ".join(sensor_data2)

	subprocess.call("sudo hciconfig hci0 up",shell=True, stdout=None)
	subprocess.call("sudo hciconfig hci0 leadv 3",shell=True, stdout=None)
	
	subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x0008 17 02 01 06 03 03 aa fe 0f 16 aa fe 10 " + message,shell=True,stdout=None)	

	time.sleep(2)

	subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x000a 00",shell=True,stdout=None)

	subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x0008 17 02 01 06 03 03 aa fe 0f 16 aa fe 20 " + sensor_data,shell=True,stdout=None)

	time.sleep(2)
	
	subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x000a 00",shell=True,stdout=None)
	print("_______________________________________________________________")
	

