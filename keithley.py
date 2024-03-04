import pyvisa # allows to communicate with the instrument
import time

rm = pyvisa.ResourceManager() 
resources = rm.list_resources()
print(resources) #list of devices connected

keithley = rm.open_resource('TCPIP0::10.10.15.107::inst0::INSTR') #choosing device
identification = keithley.query("*IDN?")
print('\n Identification of the instrument:', identification) #checking identification of the device being used

keithley.write(':SOUR:FUNC CURR')  # Set the source function to current
keithley.write(':SOUR:CURR 100E-6 ')  # Set the source current to 100uA
keithley.write(':OUTP ON')  # Turn on the output

keithley.write(':SOUR:CURR?')  # Query the current source value
time.sleep(1)
source_current = keithley.read()  # Read the current source value
print('\n Current being sourced (A): {:.3e}'.format(float(source_current)))