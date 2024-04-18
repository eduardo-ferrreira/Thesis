import pyvisa #para comunicar com os geradores de pulsos/corrente       
import time
import matplotlib.pyplot as plt

rm = pyvisa.ResourceManager()
keithley = rm.open_resource('USB0::0x05E6::0x2450::04608397::INSTR')
keithley.write(':SYST:REM')
keithley.write(':SOUR:FUNC CURR')  # Set the source function to current
keithley.write('SOUR:CURR:DEL:AUTO OFF')
keithley.write(':ROUT:TERM REAR')  # Set the output terminals to the rear panels
keithley.write(':OUTP ON')  # Turn on the output

timings = []

for i in range(15, 3000, 1):
    t0 = time.time()
    current = i*10**-10
    keithley.write(f':SOUR:CURR {current}')  #set the source current to desired value
    keithley.write('DISPlay:SCReen SWIPE_USER') #activate display text in the instrument
    keithley.write(f'DISPlay:USER1:TEXT "CURR: {current:.5e} A"') #show the current being sourced in text format. this was done due to display problems
    #print(current, i, time.time()-t0)
    timings.append(time.time()-t0)
    if time.time()-t0 > 0.2:
        print('LENTO', time.time()-t0)
        b = time.time()
        keithley.clear()
        c = time.time()
        print('clear time', c-b)
    print(i, current, time.time()-t0)

'''keithley.write('TRAC:MAKE "testData", 100') #Create a buffer named testData to store 100 readings
keithley.write('SENS:COUN 5') #Set the instrument to make 5 readings for all measurement requests
keithley.write('TRAC:TRIG "testData"') #Make the readings and store them in the buffer
keithley.write('TRAC:DATA? 1, 5, "testData", READ, REL') #Return five readings (including the measurement and relative time) from the user-defined buffer named testData
'''

t = [0]*len(timings)
i=1
while i < len(timings):
    t[i] = sum(timings[0:i])
    i += 1

plt.plot(t, timings)
plt.show()


