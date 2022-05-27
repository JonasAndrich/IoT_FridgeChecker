#! /home/ubuntu/fridgechecker/bin/python
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

PATH = "/home/ubuntu/fridgechecker/Database.db"

# delay of state changes. State changes taking less than this are not recorded
delay = datetime.timedelta(seconds=0.3)


# log sensor data to sqlite3 database
def logdata(state):
    conn = sqlite3.connect(PATH)
    curs = conn.cursor()
    curs.execute("CREATE TABLE IF NOT EXISTS BUTTON_data"
                 "(timestamp TEXT, state INT )")

    curs.execute("INSERT INTO BUTTON_data VALUES(datetime('now'), (?))", (state,))
    conn.commit()
    conn.close()


# main function
def main():
    prev_state = False

    while True:
        # accesses the state value of the GPIO pin
        state = GPIO.input(16)
        time.sleep(delay.total_seconds())
        #print(state)

        now = datetime.datetime.now()

        # Checks wether or not the state of the button has changed
        if state == prev_state:
            continue

        # Checks if door has been opened (state == 1) and if state change is below defined delay
        elif state:
            print(state)
            print("The Door has been opened at {}".format(now))
            prev_state = state
            logdata(state)

        # Checks if door has been closed (state == 0)
        elif not state:
            print(state)
            print("The Door has been closed at %s" % now)
            prev_state = state
            logdata(state)


# is called when script is executed
main()
