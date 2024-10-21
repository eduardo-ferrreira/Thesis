#code by Luís and Eduardo
#CTN, October 18th 2024

#Packages used
import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
import math
import pyvisa
import time
import urllib.request
import functools as ft
import multiprocessing
import threading
import queue
import scipy
import random
import csv
import datetime
import os
import pandas as pd 
import paramiko
from scipy.integrate import odeint

#Devices used using SCPI code and pyvisa
rm = pyvisa.ResourceManager()
instrument = rm.open_resource('USB0::0x0699::0x0358::C018403::0::INSTR') #Arbitrary Function Generator
keithley_2450_A = rm.open_resource('USB0::0x05E6::0x2450::04608397::0::INSTR') #Current Source Channel 2
keithley_2450_B = rm.open_resource('USB0::0x05E6::0x2450::04636373::0::INSTR') #Current Source Channel 3
keithley_2450_C = rm.open_resource('USB0::0x05E6::0x2450::04639284::0::INSTR') #Current Source Channel 1
#keithley_220 = rm.open_resource('GPIB0::12::INSTR')
#keithley_236 = rm.open_resource('GPIB0::16::INSTR')

#Raspberry SSH connection data
remote_host = '10.10.15.61' #raspberry pi IP
remote_port = 22  #SSH port
username = 'fissionist'
password = 'fissionist'

#Experimental data from RPI
Lambda = [0.0127, 0.0317, 0.116, 0.311, 1.4, 3.87] #decay constants of the percursors 
beta = [0.00031, 0.00166, 0.00151, 0.00328, 0.00103, 0.00021] #percursors fractions
l = 0.000055 # l is the prompt neutron lifetime (Matos et al.)
ld = l * (1-sum(beta)) + beta[0]*(1/Lambda[0]) + beta[1]*(1/Lambda[1]) + beta[2]*(1/Lambda[2]) + beta[3]*(1/Lambda[3]) + beta[4]*(1/Lambda[4]) + beta[5]*(1/Lambda[5]) 
# ld is the mean generation time with delayed neutrons
m_rod = 15 # kg
g = 9.81 # m s ^ -2
p_water = 1000 # kg m ^ -3
a= 0.0602 #m
b=0.021 #m
#r_rod = 0.05 # m
l_rod = 0.629 # m
A_rod = 0.035*0.021+np.pi*0.0105**2 #0.035*0.004*2+np.pi*(10.5e-3-6.5e-3)**2 #np . pi * a * b # m ^2
V_rod = A_rod * l_rod # m ^3
c_d = 0.82 # coefficient drag of a long cylinder
y0_rod = l_rod+l_rod/2# max height position of the center of mass of the rods
vy0_rod = 0 # initial velocity of the rods before scram

#Cubic splines to know the p corresponding to the rods position (values from the professor's documents)
df = pd.read_csv('p_rods.csv')
x = np.array(df['x'])
y1=np.array(df['y1'])
y2=np.array(df['y2'])
y3=np.array(df['y3'])
y4=np.array(df['y4'])
yr=np.array(df['yr'])
cs_1 = CubicSpline(x,y1)
cs_2 = CubicSpline(x,y2)
cs_3 = CubicSpline(x,y3)
cs_4 = CubicSpline(x,y4)
cs_r = CubicSpline(x,yr)

#df = pd.read_csv('rod_calibration.csv')
#mininimo, maximo = df['min'], df['max'] #min and max values of voltage in carapau for rods at 0% and 100%
#Functions
def function(url_string): #Removes the unwanted strings from the Yokogawa Values converting them into floats
    assert type(url_string) == str
    url_string_list = list(url_string.strip())
    return float(ft.reduce(lambda x, y: x + y, list(filter(lambda x: x.isdigit() or x == '.' or x == '-', url_string_list))))

def values(website, positions, result_queue): #Get the values from the Yokogawa by putting its site in what positions are the the values taken from it and then put it in a queue for multithreading
    web_url = urllib.request.urlopen(website)
    content = str(web_url.read())
    values_list = [function(content[i[0]:i[1]]) for i in positions] #positions is the list of lists with the voltage readings
    result_queue.put(values_list) #multithreading

t0 = time.perf_counter()

def taylor_polinomial(initial_values, interval, rhon):#, source): # method to solve these differential equations they work nice
    k = 1/(1-rhon)
    L = l/k
    dN=((rhon-sum(beta))/L)*initial_values[0]+Lambda[0]*initial_values[1]+Lambda[1]*initial_values[2]+Lambda[2]*initial_values[3]+Lambda[3]*initial_values[4]+Lambda[4]*initial_values[5]+Lambda[5]*initial_values[6] #+ source/l
    dC1=(beta[0]*initial_values[0])/(L)-Lambda[0]*initial_values[1]
    dC2=(beta[1]*initial_values[0])/(L)-Lambda[1]*initial_values[2]
    dC3=(beta[2]*initial_values[0])/(L)-Lambda[2]*initial_values[3]
    dC4=(beta[3]*initial_values[0])/(L)-Lambda[3]*initial_values[4]
    dC5=(beta[4]*initial_values[0])/(L)-Lambda[4]*initial_values[5]
    dC6=(beta[5]*initial_values[0])/(L)-Lambda[5]*initial_values[6]
    return [initial_values[0]+interval*dN,initial_values[1]+interval*dC1,initial_values[2]+interval*dC2,initial_values[3]+interval*dC3,initial_values[4]+interval*dC4,initial_values[5]+interval*dC5,initial_values[6]+interval*dC6]

def rod_drop(state_vector, scram_list, h):  #taylor method to simulate the rod drop
    y_values = state_vector[::2]  #y0_1, y0_2, y0_3, y0_4
    vy_values = state_vector[1::2]  #vy0_1, vy0_2, vy0_3, vy0_4
    updated_state = []
    for i in range(4):
        if scram_list[i]==True: 
            dydt = vy_values[i]
            dvydt = 1/m_rod*(0.5*c_d*p_water*A_rod*vy_values[i]**2-(m_rod-p_water*V_rod)*g) #rod falling in water differential equation
            new_y = y_values[i]+ h*dydt
            new_vy = vy_values[i] + h*dvydt
            if new_y <= 0:
                new_y = 0
            updated_state.append(new_y)
            updated_state.append(new_vy)
        else:
            updated_state.append(y_values[i])
            updated_state.append(vy_values[i])
    return updated_state  #state vector with positions and velocities

def ld_function(t, k): #ld is not constant, it varies with the concentration of the 6 precursors
    ld = l * (1-sum(beta))
    sum_delayed = 0
    for i in range(len(Lambda)):
        sum_delayed += beta[i]/Lambda[i]*(1-np.exp(-Lambda[i]*t))
    ld += sum_delayed
    #ld = l+k*sum_delayed
    #print('ld: ', ld)
    return ld

def k(v_values, criticality, rasp_output, scram, state_vector, h): 
    assert type(v_values) == list and len(v_values) == 5 # determines the value of k based on the rods positions
    p, scram, state_vector = safety_actions(rasp_output, criticality, v_values, scram, state_vector, h)
    k = round(-1/(p-1), 5) #returning k
    return k, scram, state_vector

def place(counts, k, source): 
    return math.log(1-counts*(1-k)/(source), k)#) / math.log(k) #operação inversa da soma geométrica para descobrir o N no expoente correspondente ao numero de contagens
                                                         #dois logs apenas para mudar de base

def continuation(counts, k, source, time, ld):#, result_queue):
    if round(counts, 8) >= round(source/(1-k), 8):
        counts = round(source/(1-k),8)
    else:
        n = place(counts,k,source)
        counts = source*(1-k**(n+time/ld))/(1-k) #next iteration of the geometric sum
    return counts


def tau(counts, dt, k): #reactor period
    if len(counts)>11:
        N0 = sum(counts[0:5])/5 #averaging the first 5 values of counts list
        N = sum(counts[-6:-1])/5 #averaging the last 5 values of counts list
        if N == N0 and k!=1:
            return 10**8 #in case the list of values has N0 equal to the last N, infinite period
        else:
            return sum(dt) / math.log(N/N0)
    else:
        return 10**8

def Inhour(T, k):
    L = l/k
    a = 0
    for i in range(len(beta)):
        a += (beta[i]/(1+Lambda[i]*T))
    return L/T + a

def root_mean_squared(x): #gives RMS of a list
    assert type(x) == list
    return (sum(list(map(lambda y: y**2, x)))/len(x))**.5

position_list=[]
def safety_actions(rasp_out, criticality, v_values, scram, state_vector, h):
    scram_list = [False] * 4  #default no scram
    rod_indices = {'20':[0, 1, 2, 3], '19':[1, 2, 3], '18':[0, 2, 3], '17':[0, 1, 3],  #dictionary with outputs of importances from raspberry associated
                   '16':[0, 1, 2], '15':[2, 3], '14':[1, 3], '13':[0, 3], '12':[1, 2], #to the index of the rod that drops
                   '11':[0, 2], '10':[0, 1], '9':[3], '8':[2], '7':[1], '6':[0]}

    if not scram:
        state_vector = [v_values[i//2]/5*y0_rod if i%2 == 0 else 0 for i in range(8)] #creates a vector with positions y and velocity vy of each rod based on carapau readings

    if rasp_out in rod_indices:
        for i in rod_indices[rasp_out]:
            scram_list[i] = True #sets scram state of the rods that the raspberry signalized
        state_vector = rod_drop(state_vector, scram_list, h) #creates new vector with new y and vy of the falling rods
        scram = True #scram state is now true so the rods positions based on carapau readings will be ignored
    if scram==True:
        position_list.append(state_vector[0])
    print(state_vector[0])
    pct = [state_vector[i*2]/y0_rod*100 if scram_list[i] else v_values[i]*20 for i in range(4)] #new withdrawn percentages if scram as occurred
    for i in range(len(pct)):
        if pct[i]<=0:
            pct[i]=0 #make sure the percentages dont fall below 0%
    p = (cs_1(pct[0]) + cs_2(pct[1]) + cs_3(pct[2]) + cs_4(pct[3]) + cs_r(v_values[4] * 20) - criticality) * 10**-5 #calculates new reactivity using new withdrawn percentages

    p = max(p, -9093*10**-5) #limits reactivity to its minimum -9093pcm
    return p, scram, state_vector

##########################################################################################################################################
# INSTRUMENTS COMMANDS

def activate_instruments(): #using SCPI commands 
    instrument.write('SOUR1:FUNC PULS') #pulse mode
    instrument.write('SOUR1:BURS:STATe OFF') #burst off mode
    instrument.write('SOUR1:FREQ 2Hz') 
    instrument.write('SOUR1:PULS:WIDTH 1000ns')
    instrument.write('OUTP1:POL NORM') #positive pulse only
    instrument.write('SOUR1:VOLT:LEV:IMM:AMPL 5VPP') #max 5V
    instrument.write('SOUR1:VOLT:LEV:IMM:OFFS 2.5V') #offset 2.5V
    instrument.write('OUTP1 ON') #activate output
    instrument.write('SOUR2:FUNC PULS') #same for CH2  
    instrument.write('SOUR2:BURS:STATe OFF')
    instrument.write('SOUR2:FREQ 2Hz')
    instrument.write('SOUR2:PULS:WIDTH 1000ns')
    instrument.write('OUTP2:POL NORM')
    instrument.write('SOUR2:VOLT:LEV:IMM:AMPL 5VPP')
    instrument.write('SOUR2:VOLT:LEV:IMM:OFFS 2.5V')
    instrument.write('OUTP2 ON')

    #keithley_2450_A.write('*RST')
    #keithley_2450_B.write('*RST')
    #keithley_2450_C.write('*RST')
    time.sleep(2)
    keithley_2450_A.write(':SOUR:FUNC CURR')  # Set the source function to current
    keithley_2450_B.write(':SOUR:FUNC CURR')  # Set the source function to current
    keithley_2450_C.write(':SOUR:FUNC CURR')  # Set the source function to current
    time.sleep(2)
    keithley_2450_A.write('SOUR:CURR:DEL:AUTO OFF')
    keithley_2450_B.write('SOUR:CURR:DEL:AUTO OFF')
    keithley_2450_C.write('SOUR:CURR:DEL:AUTO OFF')
    keithley_2450_A.write('SOURce:CURRent:READ:BACK ON')
    keithley_2450_B.write('SOURce:CURRent:READ:BACK ON')
    keithley_2450_C.write('SOURce:CURRent:READ:BACK ON')
    time.sleep(2)
    #keithley_2450_A.write('SOURce:CURRent:VLIM 21')
    #keithley_2450_B.write('SOURce:CURRent:VLIM 21')
    #keithley_2450_C.write('SOURce:CURRent:VLIM 21')
    time.sleep(2)
    keithley_2450_A.write(':ROUT:TERM REAR')  # Set the output terminals to the rear panels
    keithley_2450_B.write(':ROUT:TERM REAR')  # Set the output terminals to the rear panels
    keithley_2450_C.write(':ROUT:TERM REAR')  # Set the output terminals to the rear panels
    time.sleep(5)
    keithley_2450_A.write(':OUTP ON')  # Turn on the output
    keithley_2450_B.write(':OUTP ON')  # Turn on the output
    keithley_2450_C.write(':OUTP ON')  # Turn on the output
    time.sleep(5)
    ###############################################################################
    # for keithley 220

    #keithley_220.write('D0X') #Display current source
    #keithley_220.write('F1X') #Operate (set to programmed value)
    #keithley_220.write('R0X') #range auto
    #keithley_220.write('P1X') # Continuous pulse

    # for keithley 236

    #keithley_236.write('N1X') #Operate (set to programmed value)
    #keithley_236.write('F1,1X') #source current measure voltage
    #keithley_236.write('L10,0X') #voltage range 10V
    ###############################################################################
    time.sleep(5)
    instrument.write('SOUR1:FREQ 20Hz')
    instrument.write('SOUR2:FREQ 20Hz')
    time.sleep(10)

def afg_command(counts): #for CH1 and CH2
    counts = float('{:.2e}'.format(counts))
    if counts > 50000:
        instrument.write('SOUR1:FREQ 50000 Hz') #writes in the afg the value of the counts
        instrument.write('SOUR2:FREQ 50000 Hz')
        #instrument.write('SOUR1:FREQ '+str(30000)+'Hz') #writes in the afg the value of the counts given by the coefficients_solver
        #instrument.write('SOUR2:FREQ '+str(30000)+'Hz')
    else:
        instrument.write('SOUR1:FREQ '+str(counts)+'Hz') #writes in the afg the value of the counts
        instrument.write('SOUR2:FREQ '+str(counts)+'Hz')
        instrument.write('SOUR1:PULS:WIDTH 200ns')
        instrument.write('SOUR2:PULS:WIDTH 200ns')
        instrument.write('SOUR1:PULS:WIDTH 200ns') #para simular fission chamber
        instrument.write('SOUR2:PULS:WIDTH 200ns')

keithleys_cycle_times = []

last_update_time = 0

def keithley_command(current):
    global last_update_time
    current = float('{:.2e}'.format(current)) #exponential format with two decimal places
    if time.time() - last_update_time > 0.35:
        if current <=5e-12:
            #
            keithley_2450_A.write(f':SOUR:CURR 5e-12')  #set the source current to desired value
            keithley_2450_B.write(f':SOUR:CURR 5e-12')  #set the source current to desired value
            keithley_2450_C.write(f':SOUR:CURR 5e-12')  #set the source current to desired value 
                #last_update_time = time.time()
        elif 5e-12 <= current <= 200e-6:
            #if time.time() - last_update_time > 0.4: #only send signals every 0.35s to keithley in this range. this is due to keithley limitations.
            keithley_2450_A.write(f':SOUR:CURR {current}')  #set the source current to desired value
            keithley_2450_B.write(f':SOUR:CURR {current}')  #set the source current to desired value
            keithley_2450_C.write(f':SOUR:CURR {current}')  #set the source current to desired value 
                #last_update_time = time.time()
        else:
            keithley_2450_A.write(':SOUR:CURR 200-6')  #set the source current to 135uA so that it doesnt surpass log lin specs
            keithley_2450_B.write(':SOUR:CURR 200-6')  
            keithley_2450_C.write(':SOUR:CURR 200-6')  
        last_update_time = time.time()
    else:
        pass

    #keithley_220.write(f'I{current:.3E}X') # for keithley 220
    #keithley_236.write(f'B{current:.3E},0,0X') # for keithley 236


def AFG_signals(p, limit, initial_values, result_queue):#, source): #used in supercritical state only
    t1 = time.time()
    h = 0.0005
    i = 0
    while i*h < limit:
        initial_values = taylor_polinomial(initial_values, h, p) #taylor's method to solve ODE system
        i += 1
    current = 100*10**-12/(5*10**3)*initial_values[0]  #current-counts proportionality, 5kcps<->100pA
    afg_command(initial_values[0]) #sets in the afg the value of the counts
    keithley_command(current) #sets in the keithley the value of the current
    
    while abs(time.time() - t1) < limit: #this condition ensures that this function takes "limit" seconds
        continue
    result_queue.put(initial_values) #multithreading

##########################################################################################################################################
# MULTITHREADING


def off(initial_values): #shuts outputs when the counts are out of range of operation
    #instrument.write('OUTP1 OFF')
    #instrument.write('OUTP2 OFF')
    #keithley_2450_A.write(':OUTP OFF')
    #keithley_2450_B.write(':OUTP OFF')
    #keithley_2450_C.write(':OUTP OFF')
    #keithley_220.write('????')
    #keithley_236.write('????')
    counts=initial_values[0]
    current = 100*10**-12 / (5*10**3) * counts
    print('WARNING: Counts/Power/time limit reached.')
    i=0
    while i<10:
        counts /= 2
        current /= 2
        keithley_command(current)
        afg_command(counts)
        i+=1
        time.sleep(1)

def threadings(): # initial thread only used when in subcritical state; reads values of SALMAO and CARAPAU
    if __name__ == "__main__":
        positions1 = [[2321, 2331], [3129, 3139], [3937, 3947], [4745, 4755], [5553, 5563], [6361, 6371]] #positions in the url string where the values of the readings may be
        positions2 = [[2339, 2346], [3145, 3152], [3951, 3959], [4758, 4766]]

        result_queue = queue.Queue()

        th1 = threading.Thread(target = values, args=('http://10.10.15.20/cgi-bin/moni/allch.cgi', positions1, result_queue)) #carapau
        th2 = threading.Thread(target = values, args=('http://10.10.15.23/cgi-bin/ope/allch.cgi', positions2, result_queue)) #salmao
        th3 = threading.Thread(target = values, args=('http://10.10.15.22/cgi-bin/ope/allch.cgi', positions2, result_queue)) #truta 
    
        th1.start() #start the threading
        th2.start()
        th3.start()

        th1.join() #joins the threading, output is given when both readings are complete
        th2.join()
        th3.join()

        # Collect results from the queue
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
    for lst in results:
        if len(lst) == 4 and round(lst[3], 2) == 0: # truta has length 4 and its CH4 has no readings
            truta = lst
        elif len(lst) == 6:
            carapau = lst
    salmao = [lst for lst in results if lst not in [carapau, truta]][0] #exclusion of parts
    results = [carapau, salmao, truta] #ensure that the order of the readings is [carapau, salmao, truta]
    return results
    #return results #readings from carapau, salmao and truta """

def get_raspberry_output_thread(remote_host, remote_port, username, password, result_queue): # Function to run get_raspberry_output in a separate thread
    while True:  # Keep fetching the output in a loop if needed
        output = get_raspberry_output(remote_host, remote_port, username, password)
        result_queue.put(output)  # Put the output in the queue
        #time.sleep(0.1)  # Adjust sleep time for how often you want to fetch the output

def threadings1(p, limit, initial_values):# source, command): #when in supercritical state, reads rods position at the same time as the ODE's are solved so that compiling time is shorter;
    if __name__ == "__main__":           #same as threadings(), but it receives ODE's since geometric sum is no longer valid; uses AFG function to control the instruments
        positions1 = [[2321, 2331], [3129, 3139], [3937, 3947], [4745, 4755], [5553, 5563], [6361, 6371]]
        positions2 = [[2339, 2346], [3145, 3152], [3951, 3959], [4758, 4766]]

        result_queue = queue.Queue()
        result_queue1= queue.Queue()

        th1 = threading.Thread(target = values, args=('http://10.10.15.20/cgi-bin/moni/allch.cgi', positions1, result_queue))
        th2 = threading.Thread(target = values, args=('http://10.10.15.23/cgi-bin/ope/allch.cgi', positions2, result_queue))
        th3 = threading.Thread(target = AFG_signals, args=(p, limit, initial_values, result_queue1))#, source))
        th4 = threading.Thread(target = values, args=('http://10.10.15.22/cgi-bin/ope/allch.cgi', positions2, result_queue))

        th1.start()
        th2.start()
        th3.start()
        th4.start()
        #th5.start()
        #th6.start()

        th1.join()
        th2.join()
        th3.join()
        th4.join()

        # Collect results from the queue

        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
    for lst in results:
        if len(lst) == 4 and round(lst[3], 2) == 0: # truta has length 4 and its CH4 has no readings
            truta = lst
        elif len(lst) == 6:
            carapau = lst
    salmao = [lst for lst in results if lst not in [carapau, truta]][0] #exclusion of parts
    results = [carapau, salmao, truta] #ensure that the order of the readings is [carapau, salmao, truta]
    #results.append(result_queue2.get()) #get output from raspberry
    results.append(result_queue1.get()) #last value of the results list is the list calculated by coefficients_solver 
    return results

##################################################################################################################################
# SSH AND RASPBERRY

def execute_remote_file(remote_host, remote_port, username, password, command):
    ssh = paramiko.SSHClient() #create an SSH client
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(remote_host, port=remote_port, username=username, password=password) #connect to the remote server
        stdin, stdout, stderr = ssh.exec_command(command) #execute command
        #print("stdout" + stdout)
        for line in stdout:
            bit_value = line.strip()
            return bit_value #get the output bit value

        errors = []
        for line in stderr:
            errors.append(line.strip())
        
        if errors:
            print("Errors:")
            for error in errors:
                print(error)

    except Exception as e:
        print(f"Failed to execute command: {e}")
    
    finally:
        ssh.close() #close the SSH connection

def send_k_value(remote_host, remote_port, username, password, k_value):
    formatted_string = f"k={k_value}"
    command = f'echo "{formatted_string}" > /home/fissionist/RaspberryPi/variable.txt'
    #execute_remote_file(remote_host, remote_port, username, password, command)
    # Run the SSH command in a new thread
    threading.Thread(target=execute_remote_file, args=(remote_host, remote_port, username, password, command)).start()


def get_raspberry_output(remote_host, remote_port, username, password):#, result_queue):
    command = '/home/fissionist/RaspberryPi/all_bits_5 --skip-lcd-init' # command to run the raspberry program
    output = execute_remote_file(remote_host, remote_port, username, password, command)
    return output
    #result_queue.put(output) #multithreading

###########################################################################################################################################
#SAVING DATA 

def data(time, counts, current, k, period, salmao, truta, t_ciclo): #save data to CSV file to then open with a notebook
    
    month_year = datetime.datetime.now().strftime("%m-%Y")  #current month and year in format MM-YYYY
    month_path = os.path.join(os.getcwd(), month_year)
    if not os.path.exists(month_path):
        os.makedirs(month_path)
    day = datetime.datetime.now().strftime("%d-%m-%Y")  #current day in format DD-MM-YYYY
    day_path = os.path.join(month_path, day)
    if not os.path.exists(day_path):
        os.makedirs(day_path)
    counter = 0
    filepath = os.path.join(day_path, f'values_{counter}.csv')
    while os.path.exists(filepath):
        counter += 1
        filepath = os.path.join(day_path, f'values_{counter}.csv')

    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time', 'Counts', 'Current', 'k', 'Period',
                        'CH1_SALMAO', 'CH2_SALMAO', 'CH1_TRUTA', 'CH2_TRUTA', 'CH3_TRUTA', 't cycle'])  # Write header
        writer.writerows(zip(time, counts, current, k, period, salmao[0], salmao[1], truta[0], truta[1], truta[2], t_ciclo)) # Write rows of lists

########################################################################################################################################
#MAIN FUNCTION

t_initial = time.time() 

t_ciclo = [0]
cycles = [0]
times = []
n = []
t_ciclo_sup = []
times_ld = []
salmao = [[],[]]
truta = [[],[],[]]
cont_list = []
times_raspberry = []
ld_list = []
k_value_list = []
times_k = []
period = []
global scram_time
scram_time = 0
t_fall = [0]

def simulation(source, criticality, stoptime, limit):
    global scram_time
    activate_instruments()
    time.sleep(10)
    cont = True
    counts = 11 #counts associated to all bars at 0%
    k_value = 1 - source/counts #k asssociated at 11 counts
    scram=False
    state_vector = [0,0,0,0,0,0,0,0]  # State vector for the rods
    initial_values = [counts,
                    (beta[0]*counts)/(Lambda[0]*l),
                    (beta[1]*counts)/(Lambda[1]*l),
                    (beta[2]*counts)/(Lambda[2]*l),
                    (beta[3]*counts)/(Lambda[3]*l),
                    (beta[4]*counts)/(Lambda[4]*l),
                    (beta[5]*counts)/(Lambda[5]*l)] #initial approximation of the 7 variables
    
    t4 = time.time()

    result_queue = queue.Queue()
    threading.Thread(target=get_raspberry_output_thread, args=(remote_host, remote_port, username, password, result_queue), daemon=True).start() # Start the thread that will fetch Raspberry Pi output asynchronously
    time.sleep(1) #important so that the queue already has a value when the loop begins
    scram = False
    scram_time_noted = False
    while 10 < initial_values[0] < 10**15 and time.time()-t4 < stoptime:
        k_list = [k_value]*5 #to store the values of consecutive k's, in order to do the average and reduce noise influence
        k_value = round(root_mean_squared(k_list), 5)
        b = time.time()
        c = time.time()
        d = time.time()
        e = time.time()

        while k_value < 1 and cont == True:

            t_init_cycle = time.time()
            if time.time()-t4>stoptime:
                break

            z = threadings() #yokogawa readings
            carapau = z[0] #CARAPAU readings
            del carapau[-1] #deleting last value from CARAPAU because it's not used 
            rasp_time = time.time()
            if not result_queue.empty(): 
                raspberry_output = result_queue.get() #checks raspberry 24 bits. has raspberry output every 3-4 cycles 
            times_raspberry.append(time.time()-rasp_time) 

            new_counts = continuation(initial_values[0], k_value, source, time.time()-b, ld)

            n.append(new_counts)
            times.append(time.time()-t4)
            times_ld.append(time.time()-t4)
            salmao[0].append(z[1][0]) #salmao ch1 readings
            salmao[1].append(z[1][1]) 
            truta[0].append(z[2][0]) #truta readings
            truta[1].append(z[2][1])
            truta[2].append(z[2][2])
            current = 100*10**-12 / (5*10**3) * new_counts #current-counts proportionality, 5kcps<->100pA
            afg_command(new_counts) #sending commands
            keithley_command(current)
             
            b = time.time() # give new value to b

            if time.time()-e > 0.3: #send k values to status monitor every 0.3s
                send_k_value(remote_host, remote_port, username, password, k_value)
                e=time.time()

            initial_values=[new_counts,
                            (beta[0]*new_counts)/(Lambda[0]*l),
                            (beta[1]*new_counts)/(Lambda[1]*l),
                            (beta[2]*new_counts)/(Lambda[2]*l),
                            (beta[3]*new_counts)/(Lambda[3]*l),
                            (beta[4]*new_counts)/(Lambda[4]*l),
                            (beta[5]*new_counts)/(Lambda[5]*l)]
            
            print(f'k: {k_value}, Counts: {initial_values[0]:.3e}, Cont: {cont}, Current: {current:.3e}, Raspberry output: {raspberry_output}, Time passed: {(time.time()-t4)/60}')
            max_index = min(101, len(n))
            period.append(tau(n[-max_index:-1], times[-max_index:-1], k_value)) #use last 100 values to calculate period
            if scram == True:
                t_fall.append(time.time()-c)
            new_k, scram, state_vector = k(v_values=carapau, criticality=criticality, rasp_output=raspberry_output, scram=scram, state_vector=state_vector, h=time.time()-c) #new k calculated
            c=time.time()
            if scram==True and scram_time_noted==False:
                scram_time=time.time()-t4
                scram_time_noted = True
            del k_list[0]
            k_list = k_list + [new_k] # now the list of k's includes the new k, will do this for new k's while the cycle iterates
            k_value = round(root_mean_squared(k_list), 5)
            t_ciclo.append(time.time()-t_init_cycle)
            cycles.append(cycles[-1]+1)
            k_value_list.append(k_value)
            
        counts = initial_values[0]
        p = [((k_value - 1) / k_value)] * 5 #list of reactivities to average (to decrease noise)
        initial_values = [counts,
                        (beta[0]*counts)/(Lambda[0]*l),
                        (beta[1]*counts)/(Lambda[1]*l),
                        (beta[2]*counts)/(Lambda[2]*l),
                        (beta[3]*counts)/(Lambda[3]*l),
                        (beta[4]*counts)/(Lambda[4]*l),
                        (beta[5]*counts)/(Lambda[5]*l)]
                
        previous_values = [counts]*100 #will be used to calculate the period
        cont = False
        scram=False
        c=time.time()
        e = time.time()

        while cont == False and initial_values[0] < 10**15: #Second cycle supercritical state.

            if time.time()-t4>stoptime:
                break

            rasp_time = time.time()
            if not result_queue.empty(): 
                raspberry_output = result_queue.get() #checks raspberry 24 bits. has raspberry output every 3-4 cycles 
            times_raspberry.append(rasp_time)

            t5 = time.time()
            z = threadings1(sum(p)/len(p), limit, initial_values) #[carapau, salmao, truta, ODE solution vector]
            carapau=z[0]
            del carapau[-1]
            del p[0]
            if scram == True:
                t_fall.append(time.time()-c)
            new_p, scram, state_vector = safety_actions(raspberry_output, criticality, carapau, scram, state_vector, h=time.time()-c)
            c=time.time()  
            p.append(new_p)          
            salmao[0].append(z[1][0]) #salmao ch1 readings
            salmao[1].append(z[1][1]) 
            truta[0].append(z[2][0]) #truta readings
            truta[1].append(z[2][1])
            truta[2].append(z[2][2])

            initial_values1 = z[-1] # [O.D.E solution vector]
            n.append(initial_values1[0])       
            times.append(time.time() - t4)
            del previous_values[0]
            previous_values = previous_values+[initial_values1[0]]
            current = float('{:.2e}'.format(100*10**-12/(5*10**3)*initial_values[0])) #current-counts proportionality, 5kcps<->100pA
            k_value = round(-1/(sum(p)/len(p)-1), 5)
            p_value = round(sum(p)/len(p) * 10**5) #reactivity given in pcm
            max_index = min(101, len(n))
            period.append(tau(n[-max_index:-1], times[-max_index:-1], k_value)) #use last 100 values to calculate period
            print(f'p: {p_value}, Counts: {initial_values[0]}, I:{current}, RaspPi Output: {raspberry_output}, Time passed: {(time.time()-t4)/60}')
            initial_values = initial_values1

            if time.time()-e > 0.3: #send k values to status monitor every 0.3s
                send_k_value(remote_host, remote_port, username, password, k_value)
                e=time.time()

            if k_value != 1:
                if source/(1-k_value) > initial_values[0] and k_value <= 0.99999:#source / (1-k_value) > initial_values[0] and k_value <= 0.99999: #making sure that counts do not go below theoretical level of 1/1-k when in subcritical state
                    cont = True  #sends back to startup channel
                    cont_list.append(cont)
                else:
                    cont = False
                    cont_list.append(cont) 
            #del times[0]
            
            h = 0.0001 #Taylor method being used here to compensate the time spent in threadings. predict how the initial_values list has evolved during the time spent at threadings.
            i = 0 
            while h*i < time.time()-t5-limit:
                initial_values = taylor_polinomial(initial_values, h, p[-1])
                i += 1

            t_ciclo.append(time.time()-t5)
            t_ciclo_sup.append(time.time()-t5)
            cycles.append(cycles[-1]+1)
            k_value_list.append(k_value)
            ld_list.append(0.1012)

    off(initial_values) #shuts off the instruments after the loop ends"""

simulation(source=2, criticality=9093, stoptime=900, limit=0.1)#, int_time=1, stop_time=10000) #why source=2?

current = 100*10**-12/5000*np.array(n)
data(times, n, current, k_value_list, period, salmao, truta, t_ciclo) #save data into csv files

from scipy.integrate import odeint

def dSdt(t, S):
    y, v_y = S
    dSdt = [v_y, 1/m_rod*(0.5*c_d*p_water*A_rod*v_y**2-(m_rod-p_water*V_rod)*g) ]
    return dSdt

y_0 = y0_rod #m
v_y0 = 0 #initial conditions for the first mode

t_list = np.arange(0, times[-1], 0.001) #sets the number of laps taken
S_0 = (y_0, v_y0)
sol = odeint(dSdt, y0=S_0, t=t_list, tfirst=True)

plt.plot(t_list, sol.T[0], label='range kutta')
if len(t_fall)==len(position_list)>0:
    plt.plot(t_fall, position_list, label='taylor, h=variavel')
    plt.ylim(0, 0.6)
    plt.legend()
plt.show()

filepath=r'C:/Users/eduardo.ferreira/Documents/rod_position.csv'
with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['position', 't fall'])  # Write header
        writer.writerows(zip(position_list, t_fall)) # Write rows of lists
