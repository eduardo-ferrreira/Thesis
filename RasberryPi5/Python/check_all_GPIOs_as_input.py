import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)

#GPIO groups
IOA = [2,3,4,5,6,7,8,9]
IOB = [10,11,12,13,14,15,16,17]
IOC = [18,19,20,21,22,23,24,25]
IOD = [26,27]

#check outputs in one group at a time
try:
	while True:
		x = 0
		while x < 5:
			x += 1
			for i in IOA: #leds blink 0.2s in I0x group
				GPIO.setup(i, GPIO.OUT, initial=0) # sets i to output and 0V, off
				GPIO.output(i,1) #port on
				sleep(0.2)
				GPIO.output(i,0) #port off

except KeyboardInterrupt: #ctrl+c to exit
	GPIO.cleanup() #clean up ports before exit
		
