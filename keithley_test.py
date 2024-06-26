import pyvisa #para comunicar com os geradores de pulsos/corrente       
import time
import matplotlib.pyplot as plt
import numpy as np

rm = pyvisa.ResourceManager()
#print(rm.list_resources())

#keithley_220 = rm.open_resource('GPIB0::12::INSTR')
keithley_236 = rm.open_resource('GPIB0::16::INSTR')



#KEITHLEY 2450

'''
keithley.write(':SYST:REM')
keithley.write(':SOUR:FUNC CURR')  # Set the source function to current
keithley.write('SOUR:CURR:DEL:AUTO OFF')
keithley.write(':ROUT:TERM REAR')  # Set the output terminals to the rear panels
keithley.write(':OUTP ON')  # Turn on the output'''


#KEITHLEY 220

'''
keithley_220.write('D0X') #Display current source
#time.sleep(5)
keithley_220.write('F1X') #Operate (set to programmed value)
time.sleep(0.1)
keithley_220.write('R0X')
time.sleep(0.1)
keithley_220.write('V10X')
keithley_220.write('P1X')
time.sleep(0.1)
keithley_220.write('I100e-6X')
'''


time.sleep(10)

#KEITHLEY 236

"""while True:
    keithley_236.write('LLO')
    keithley_236.write('N1X')
    time.sleep(1) 
    keithley_236.write('F1,1X')
    time.sleep(1)
    keithley_236.write('L10,0X')
    keithley_236.write('B1000E-10,0,0X')
"""

'''while True:
    keithley_236.write('TRANSMIT=3X')
    keithley_236.write('CMD$="LISTEN 16 SDC"X')
    keithley_236.write('CALL TRANSMIT(CMD$,STATUS%)X')
    keithley_236.write('LLOX')
    keithley_236.write('RENX')
'''

#"""
while True:
    keithley_236.write('REN')
    keithley_236.write('F1,1X')
    time.sleep(1) 
    keithley_236.write('O1X')
    time.sleep(1)
    keithley_236.write('N1X')
    time.sleep(1)
    keithley_236.write('L10,0X')
    keithley_236.write('B1E-8,0,0X')
#"""
    
""""
keithley_236.write('F1,1X')
time.sleep(1) 
keithley_236.write('O1X')
time.sleep(1)
keithley_236.write('N1X')
time.sleep(1)
keithley_236.write('L10,0X')

values = [[],[]]

for i in range(350, 1500, 50):
    current = i*10**-10    
    keithley_236.write(f'B{current},0,0X')
    time.sleep(i)
    
    #values[0].append(i)
    #values[1].append(i_value)

print(values)"""

'''
timings = []

for i in range(5, 100, 5):
    j=i
    t0 = time.time()
    current = i *10**-6
    keithley_236.write(f'{current},0,0X')
    #keithley_220.write('W1X')
    time.sleep(1)
    timings.append(time.time()-t0)
    print(f"{i}, {current:.1e}, {time.time() - t0:.2f}")

t = np.linspace(5, 100, 19)

plt.plot(t, timings)
plt.show()

'''