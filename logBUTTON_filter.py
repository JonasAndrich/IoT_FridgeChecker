#! /usr/bin/python3
# -*- coding: utf-8 -*-
#

import time
import sqlite3
import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
import datetime

# configure GPIO of raspberry pi
GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
# Set pin 16 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)

dbPath = "/home/ubuntu/fridgechecker/Database.db"

# delay of state changes. State changes taking less than this are not recorded
# Change as you think
delay = datetime.timedelta(seconds=0.3)


# log sensor data to sqlite3 database
def logdata(state):
    conn = sqlite3.connect(dbPath)
    curs = conn.cursor()
    curs.execute("INSERT INTO BUTTON_data VALUES(datetime('now'), (?))", (state,))
    # curs.execute("INSERT INTO BUTTON_data (timestamp,state) VALUES(datetime('now'), (?))",(state,))
    conn.commit()
    conn.close()

# main function
def main():
    prev_state = False

    while True:
        # accesses the state value of the GPIO pin
        state = GPIO.input(16)
        past = datetime.datetime.now()
        print(state)

        time.sleep(delay.total_seconds())

        # defines now
        now = datetime.datetime.now()

        # Variable is a timedelta that measures duration between loops in which states have changed.
        tdelta = now - past

        # Checks wether or not the state of the button has changed

        if state == prev_state:
            continue

        # Checks if door has been opened (state == True) and if state change is below defined delay
        elif state == 1: #and tdelta > delay:
            print("The Door has been opened at {}".format(now))
            prev_state = state
            # past = now
            # state = 1
            logdata(state)

        # Checks if door has been closed (state == True) and if state change is below defined delay
        elif state == 0:# and tdelta > delay:
            print("The Door has been closed at %s" % now)
            prev_state = state
            # past = now
            # state = 0
            logdata(state)


#        else:
#            continue


# is called when script is executed
main()
