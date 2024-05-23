import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)

IO_OUT = 3
IO_IN = [2,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,
	22,23,24,25,26,27]
IN1 = 2 #selected GPIO to test as input
for i in IO_IN:
	GPIO.setup(i, GPIO.IN, pull_up_down = GPIO.PUD_UP) #rest of the GPIOs are input with pull up

try:
	while True:
		if GPIO.input(IN1):
			print("GPIO{0}".format(IN1), "=", GPIO.input(IN1))
			GPIO.output(IO_OUT, 1)
		else:
			print("GPIO{0}".format(IN1), "=", GPIO.input(IN1))
			GPIO.output(IO_OUT, 1)
		sleep(0.3)
except KeyboardInterrupt: #ctrl+c to exit
	GPIO.cleanup() #clean up ports before exit
		
