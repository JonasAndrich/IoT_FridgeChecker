#! /usr/bin/python3
# -*- coding: utf-8 -*-
#

import time
import sqlite3
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import datetime

#configure GPIO of raspberry pi
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use BCM pin numbering
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set pin 16 to be an input pin and set initial value to be pulled low (off)

dbPath = "/home/pi/Sensors_Database/sensorsData.db"

# delay of state changes. State changes taking less than this are not recorded
# Change as you think
delay = datetime.timedelta(seconds =0.4)


# log sensor data to sqlite3 database
def logData (state):
	
	conn=sqlite3.connect(dbPath)
	curs=conn.cursor()
	curs.execute("INSERT INTO BUTTON_data VALUES(datetime('now'), (?))",(state,))
	#curs.execute("INSERT INTO BUTTON_data (timestamp,state) VALUES(datetime('now'), (?))",(state,))
	conn.commit()
	conn.close()



# main function
def main():
	prev_state_value = False
	past = datetime.datetime.now()

	while True:
		#accesses the state value of the GPIO pin
		state_value = GPIO.input(16)
		#defines now
		now = datetime.datetime.now()

		#Variable is a timedelta that measures duration between loops in which states have changed. 
		tdiff = now - past

		#Checks wether or not the state of the button has changed
		if state_value == prev_state_value:
			continue

		#Checks if door has been opened (state_value == True) and if state change is below defined delay
		elif state_value == True and tdiff > delay:
			print("The Door has been opened at {}".format(now))
			prev_state_value = state_value
			past = now
			state = 1
			logData(state)

		#Checks if door has been closed (state_value == True) and if state change is below defined delay
		elif state_value == False and tdiff > delay:
			print("The Door has been closed at %s" %(now))
			prev_state_value = state_value
			past = now
			state = 0
			logData(state)
		else:
			continue

#is called when script is executed
main()

# Nettes Feature. 
#https://realpython.com/python-send-email/ 
# Sende eine Mail, wenn Kühlschrank länger als 5 Minuten offen ist.
