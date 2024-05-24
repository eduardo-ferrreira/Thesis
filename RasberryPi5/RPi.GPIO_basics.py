import RPi.GPIO as GPIO           # import RPi.GPIO module  
GPIO.setmode(GPIO.BCM)            # choose BCM or BOARD  
GPIO.setup(port_or_pin, GPIO.OUT) # set a port/pin as an output   
GPIO.output(port_or_pin, 1)       # set port/pin value to 1/GPIO.HIGH/True  
GPIO.output(port_or_pin, 0)       # set port/pin value to 0/GPIO.LOW/False  


import RPi.GPIO as GPIO            # import RPi.GPIO module  
from time import sleep             # lets us have a delay  
GPIO.setmode(GPIO.BCM)             # choose BCM or BOARD  
GPIO.setup(24, GPIO.OUT)           # set GPIO24 as an output   
  
try:  
    while True:  
        GPIO.output(24, 1)         # set GPIO24 to 1/GPIO.HIGH/True  
        sleep(0.5)                 # wait half a second  
        GPIO.output(24, 0)         # set GPIO24 to 0/GPIO.LOW/False  
        sleep(0.5)                 # wait half a second  
  
except KeyboardInterrupt:          # trap a CTRL+C keyboard interrupt  
    GPIO.cleanup()                 # resets all GPIO ports used by this program 

import RPi.GPIO as GPIO            # import RPi.GPIO module  
from time import sleep             # lets us have a delay  
GPIO.setmode(GPIO.BCM)             # choose BCM or BOARD  
GPIO.setup(24, GPIO.OUT)           # set GPIO24 as an output   
  
try:  
    while True:  
        GPIO.output(24, 1)         # set GPIO24 to 1/GPIO.HIGH/True  
        sleep(0.5)                 # wait half a second  
        if GPIO.input(24):  
            print "LED just about to switch off"  
        GPIO.output(24, 0)         # set GPIO24 to 0/GPIO.LOW/False  
        sleep(0.5)                 # wait half a second  
        if not GPIO.input(24):  
            print "LED just about to switch on"  
except KeyboardInterrupt:          # trap a CTRL+C keyboard interrupt  
    GPIO.cleanup()                 # resets all GPIO ports used by this program  


