# This code calls the functions defined in ble_scanner.py which scans beacons and if beacon is recognized eddystone beacons then it decodes the information from the packet

import ble_scanner
import sys

import bluetooth._bluetooth as bluez

dev_id = 0
try:
	sock = bluez.hci_open_dev(dev_id)
	print "Beacon Scanning Started"
	print ("\n")

except:
	print "error accessing bluetooth device..."
    	sys.exit(1)

ble_scanner.hci_le_set_scan_parameters(sock)
ble_scanner.hci_enable_le_scan(sock)

while True:
	# Fuction to scan beacons
	ble_scanner.parse_events(sock, 10)
	#print("--------------------------------------")

