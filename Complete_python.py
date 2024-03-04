import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
import math
import pyvisa #para comunicar com os geradores de pulsos/corrente       
import usb.core # comunicação usb
import time #operações relacionadas com tempo
import urllib.request #para abrir URLs 
import functools as ft #operações complexas
import multiprocessing #para aumentar velocidade de cálculo
import threading # "" "" ""
import queue # "" "" ""
from scipy import optimize

rm = pyvisa.ResourceManager() 
instrument = rm.open_resource('USB0::0x0699::0x0358::C018403::INSTR') #source generator used

def function(a): ##This function removes the unwanted strings from the Yokogawa Values converting them into floats
    assert type(a) == str
    b = list(a.strip())
    return float(ft.reduce(lambda x, y: x + y, list(filter(lambda x: x.isdigit() or x == '.' or x == '-', b))))

def values(website, positions, result_queue): ###This function helps us get the values from the Yokogawa by putting its site in what positions are the the values taken from it and then put it in a queue for multithreading
    web_url = urllib.request.urlopen(website)
    content = str(web_url.read())
    values_list = [function(content[i[0]:i[1]]) for i in positions]
    result_queue.put(values_list)

def AFG_signals(p,limit,initial_values,result_queue): 
    b=time.time()
    c=b
    while time.time()-b<limit: ## continua a mandar sinais de tensao at]e 1MHz para a source Range
        initial_values=coefficients_solver(initial_values,time.time()-c,p)
        c=time.time()
        time.sleep(0.001)
    if initial_values[0]<10**6:
            instrument.write('SOUR1:FREQ '+str(initial_values[0])+'Hz')
            instrument.write('SOUR2:FREQ '+str(initial_values[0])+'Hz')
            instrument.write('SOUR1:PULS:WIDTH 50ns')
            instrument.write('SOUR2:PULS:WIDTH 50ns')
    ### Eduardo tu depois vais ter de por o comando para o gerador de sinais
    result_queue.put(initial_values)

def Promecium(y_Nd,Sigma_f,L_p,counts,P0,t): ## Funcao que da densidade do Promecium
    return ((y_Nd*Sigma_f*counts)/(L_p))*(1-math.exp(-L_p*t))+P0*math.exp(-L_p*t)    

def Samarium(S0,o_a,y_Nd,Sigma_f,counts,P0,L_p,t): # Funcao que da densidade do Samarium 
    return S0*math.exp(-o_a*t)+(y_Nd*Sigma_f/o_a)*(1-math.exp(-o_a*counts*t))-((y_Nd*Sigma_f*counts-L_p*P0)/(L_p-o_a*counts))*(math.exp(-o_a*counts*t)-math.exp(L_p*t))

def Iodine(I0,L_I,y_Te,Sigma_f,counts,t): ###Funcao que dá a densidade do Iodine
    return ((y_Te*Sigma_f*counts)/(L_I))*(1-math.exp(-L_I*t))+I0*math.exp(-L_I*t)

def Xenon(I0,X0,L_I,L_X,y_Te,y_Xe,Sigma_f,o_a,counts,t): ### Função que dá a densidade do Xénon
    return (((y_Te+y_Xe)*Sigma_f*counts)/(L_X+o_a*counts))*(1-math.exp(-L_X*t-o_a**counts*t))+((y_Te*Sigma_f*counts-L_I*I0)/(L_X-L_I+o_a*counts))*(math.exp(-L_X*t-o_a*counts*t)-math.exp(-L_I*t))+X0*math.exp(-(L_X+o_a*counts))

def threadings(): ### Thread Inicial quando está no Subcritico Só lê o valor do Yokogawa grande e do Yokogawa com a posição das barras
    if __name__ == "__main__":
        positions1 = [[2321, 2331], [3129, 3139], [3937, 3947], [4745, 4755], [5553, 5563], [6361, 6371]]
        positions2 = [[2339, 2346], [3145, 3152], [3951, 3959], [4758, 4766]]

        result_queue = queue.Queue()

        t1 = threading.Thread(target=values, args=('http://10.10.15.20/cgi-bin/moni/allch.cgi', positions1, result_queue))
        t2 = threading.Thread(target=values, args=('http://10.10.15.23/cgi-bin/ope/allch.cgi', positions2, result_queue))
    
        t1.start()
        t2.start()
        

        t1.join()
        t2.join()
        

        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
    if len(results[1])>len(results[0]):
        results=[results[1],results[0]]
    return results

def threadings1(p,limit,initial_values): #Quando passa para o estado supercritico Posição das barras mede e depois lê no Yokogawa ao mesmo tempo que está a ler ele corre as equações para temos um tempo mais pequeno
    if __name__ == "__main__":
        positions1 = [[2321, 2331], [3129, 3139], [3937, 3947], [4745, 4755], [5553, 5563], [6361, 6371]]
        positions2 = [[2339, 2346], [3145, 3152], [3951, 3959], [4758, 4766]]

        result_queue = queue.Queue()
        result_queue1= queue.Queue()

        t1 = threading.Thread(target=values, args=('http://10.10.15.20/cgi-bin/moni/allch.cgi', positions1, result_queue))
        t2 = threading.Thread(target=values, args=('http://10.10.15.23/cgi-bin/ope/allch.cgi', positions2, result_queue)) # Por tudo em um Thread.
        t3 = threading.Thread(target=AFG_signals, args=(p,limit,initial_values,result_queue1))

        t1.start()
        t2.start()
        t3.start()
        
        t1.join()
        t2.join()
        t3.join()
        
        # Collect results from the queue
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
    if len(results[1])>len(results[0]):
        results=[results[1],results[0]]
    results.append(result_queue1.get())
    return results

#### Valores experimentais
Lambda = [0.0127, 0.0317, 0.115, 0.311, 1.4, 3.87]
beta = [0.000266, 0.001491, 0.001316, 0.002849, 0.000896, 0.000182]
l = 0.00002
epsilon=1
#######
#print(Beta,LAMBDA)

def Range_Kutta_nuclear(y,init_values,h,p): #### Deixei o Range-Kutta só para caso alguém quiser mudar com coeficients
    K1_0=h*y[0](init_values[0],init_values[1],init_values[2],init_values[3],init_values[4],init_values[5],init_values[6],p)
    K1_1=h*y[1](init_values[0],init_values[1],init_values[2],init_values[3],init_values[4],init_values[5],init_values[6])
    K1_2=h*y[2](init_values[0],init_values[1],init_values[2],init_values[3],init_values[4],init_values[5],init_values[6])
    K1_3=h*y[3](init_values[0],init_values[1],init_values[2],init_values[3],init_values[4],init_values[5],init_values[6])
    K1_4=h*y[4](init_values[0],init_values[1],init_values[2],init_values[3],init_values[4],init_values[5],init_values[6])
    K1_5=h*y[5](init_values[0],init_values[1],init_values[2],init_values[3],init_values[4],init_values[5],init_values[6])
    K1_6=h*y[6](init_values[0],init_values[1],init_values[2],init_values[3],init_values[4],init_values[5],init_values[6])
    K2_0=h*y[0](init_values[0]+K1_0/2,init_values[1]+K1_0/2,init_values[2]+K1_0/2,init_values[3]+K1_0/2,init_values[4]+K1_0/2,init_values[5]+K1_0/2,init_values[6]+K1_0/2,p)
    K2_1=h*y[1](init_values[0]+K1_1/2,init_values[1]+K1_1/2,init_values[2]+K1_1/2,init_values[3]+K1_1/2,init_values[4]+K1_1/2,init_values[5]+K1_1/2,init_values[6]+K1_1/2)
    K2_2=h*y[2](init_values[0]+K1_2/2,init_values[1]+K1_2/2,init_values[2]+K1_2/2,init_values[3]+K1_2/2,init_values[4]+K1_2/2,init_values[5]+K1_2/2,init_values[6]+K1_2/2)
    K2_3=h*y[3](init_values[0]+K1_3/2,init_values[1]+K1_3/2,init_values[2]+K1_3/2,init_values[3]+K1_3/2,init_values[4]+K1_3/2,init_values[5]+K1_3/2,init_values[6]+K1_3/2)
    K2_4=h*y[4](init_values[0]+K1_4/2,init_values[1]+K1_4/2,init_values[2]+K1_4/2,init_values[3]+K1_4/2,init_values[4]+K1_4/2,init_values[5]+K1_4/2,init_values[6]+K1_4/2)
    K2_5=h*y[5](init_values[0]+K1_5/2,init_values[1]+K1_5/2,init_values[2]+K1_5/2,init_values[3]+K1_5/2,init_values[4]+K1_5/2,init_values[5]+K1_5/2,init_values[6]+K1_5/2)
    K2_6=h*y[6](init_values[0]+K1_6/2,init_values[1]+K1_6/2,init_values[2]+K1_6/2,init_values[3]+K1_6/2,init_values[4]+K1_6/2,init_values[5]+K1_6/2,init_values[6]+K1_6/2)
    K3_0=h*y[0](init_values[0]+K2_0/2,init_values[1]+K2_0/2,init_values[2]+K2_0/2,init_values[3]+K2_0/2,init_values[4]+K2_0/2,init_values[5]+K2_0/2,init_values[6]+K2_0/2,p)
    K3_1=h*y[1](init_values[0]+K2_1/2,init_values[1]+K2_1/2,init_values[2]+K2_1/2,init_values[3]+K2_1/2,init_values[4]+K2_1/2,init_values[5]+K2_1/2,init_values[6]+K2_1/2)
    K3_2=h*y[2](init_values[0]+K2_2/2,init_values[1]+K2_2/2,init_values[2]+K2_2/2,init_values[3]+K2_2/2,init_values[4]+K2_2/2,init_values[5]+K2_2/2,init_values[6]+K2_2/2)
    K3_3=h*y[3](init_values[0]+K2_3/2,init_values[1]+K2_3/2,init_values[2]+K2_3/2,init_values[3]+K2_3/2,init_values[4]+K2_3/2,init_values[5]+K2_3/2,init_values[6]+K2_3/2)
    K3_4=h*y[4](init_values[0]+K2_4/2,init_values[1]+K2_4/2,init_values[2]+K2_4/2,init_values[3]+K2_4/2,init_values[4]+K2_4/2,init_values[5]+K2_4/2,init_values[6]+K2_4/2)
    K3_5=h*y[5](init_values[0]+K2_5/2,init_values[1]+K2_5/2,init_values[2]+K2_5/2,init_values[3]+K2_5/2,init_values[4]+K2_5/2,init_values[5]+K2_5/2,init_values[6]+K2_5/2)
    K3_6=h*y[6](init_values[0]+K2_6/2,init_values[1]+K2_6/2,init_values[2]+K2_6/2,init_values[3]+K2_6/2,init_values[4]+K2_6/2,init_values[5]+K2_6/2,init_values[6]+K2_6/2)
    K4_0=h*y[0](init_values[0]+K3_0,init_values[1]+K3_0,init_values[2]+K3_0,init_values[3]+K3_0,init_values[4]+K3_0,init_values[5]+K3_0,init_values[6]+K3_0,p)
    K4_1=h*y[1](init_values[0]+K3_1,init_values[1]+K3_1,init_values[2]+K3_1,init_values[3]+K3_1,init_values[4]+K3_1,init_values[5]+K3_1,init_values[6]+K3_1)
    K4_2=h*y[2](init_values[0]+K3_2,init_values[1]+K3_2,init_values[2]+K3_2,init_values[3]+K3_2,init_values[4]+K3_2,init_values[5]+K3_2,init_values[6]+K3_2)
    K4_3=h*y[3](init_values[0]+K3_3,init_values[1]+K3_3,init_values[2]+K3_3,init_values[3]+K3_3,init_values[4]+K3_3,init_values[5]+K3_3,init_values[6]+K3_3)
    K4_4=h*y[4](init_values[0]+K3_4,init_values[1]+K3_4,init_values[2]+K3_4,init_values[3]+K3_4,init_values[4]+K3_4,init_values[5]+K3_4,init_values[6]+K3_4)
    K4_5=h*y[5](init_values[0]+K3_5,init_values[1]+K3_5,init_values[2]+K3_5,init_values[3]+K3_5,init_values[4]+K3_5,init_values[5]+K3_5,init_values[6]+K3_5)
    K4_6=h*y[6](init_values[0]+K3_6,init_values[1]+K3_6,init_values[2]+K3_6,init_values[3]+K3_6,init_values[4]+K3_6,init_values[5]+K3_6,init_values[6]+K3_6)
    init_values[0]=init_values[0]+K1_0/6+K2_0/3+K3_0/3+K4_0/6
    init_values[1]=init_values[1]+K1_1/6+K2_1/3+K3_1/3+K4_1/6
    init_values[2]=init_values[2]+K1_2/6+K2_2/3+K3_2/3+K4_2/6
    init_values[3]=init_values[3]+K1_3/6+K2_3/3+K3_3/3+K4_3/6
    init_values[4]=init_values[4]+K1_4/6+K2_4/3+K3_4/3+K4_4/6
    init_values[5]=init_values[5]+K1_5/6+K2_5/3+K3_5/3+K4_5/6
    init_values[6]=init_values[6]+K1_6/6+K2_6/3+K3_6/3+K4_6/6
    return [init_values[0],init_values[1],init_values[2],init_values[3],init_values[4],init_values[5],init_values[6]]

#### As sete funções kinematicas do comportamento dos neutrões 
N=lambda  n,c1,c2,c3,c4,c5,c6,p: ((p-sum(beta))/l)*n+0.0127*c1+0.0317*c2+0.116*c3+0.311*c4+1.40*c5+3.87*c6
C1=lambda n,c1,c2,c3,c4,c5,c6: (beta[0]/l)*n-0.0127*c1-0.0*c2-0*c3-0*c4-0*c5-0*c6
C2=lambda n,c1,c2,c3,c4,c5,c6: (beta[1]/l)*n-0*c1-0.0317*c2-0*c3-0*c4-0*c5-0*c6
C3=lambda n,c1,c2,c3,c4,c5,c6: (beta[2]/l)*n-0*c1-0*c2-0.116*c3-0*c4-0*c5-0*c6
C4=lambda n,c1,c2,c3,c4,c5,c6: (beta[3]/l)*n-0.0*c1-0.0*c2-0*c3-0.311*c4-0*c5-0*c6
C5=lambda n,c1,c2,c3,c4,c5,c6: (beta[4]/l)*n-0.0*c1-0.0*c2-0.0*c3-0*c4-1.40*c5-0*c6
C6=lambda n,c1,c2,c3,c4,c5,c6: (beta[5]/l)*n-0.0*c1-0.0*c2-0.0*c3-0.0*c4-0*c5-3.87*c6
###### Nice

def root_mean_squared(x):
    assert type(x)==list
    return (sum(list(map(lambda y: y**2,x)))/len(x))**.5


def taylor_polinomial(initial_values,interval,rhon): ###another method to solve these differential equations they work nice
    dN=((rhon-sum(beta))/l)*initial_values[0]+Lambda[0]*initial_values[1]+Lambda[1]*initial_values[2]+Lambda[2]*initial_values[3]+Lambda[3]*initial_values[4]+Lambda[4]*initial_values[5]+Lambda[5]*initial_values[6]
    dC1=(beta[0]*initial_values[0])/(l)-Lambda[0]*initial_values[1]
    dC2=(beta[1]*initial_values[0])/(l)-Lambda[1]*initial_values[2]
    dC3=(beta[2]*initial_values[0])/(l)-Lambda[2]*initial_values[3]
    dC4=(beta[3]*initial_values[0])/(l)-Lambda[3]*initial_values[4]
    dC5=(beta[4]*initial_values[0])/(l)-Lambda[4]*initial_values[5]
    dC6=(beta[5]*initial_values[0])/(l)-Lambda[5]*initial_values[6]
    return [initial_values[0]+interval*dN,initial_values[1]+interval*dC1,initial_values[2]+interval*dC2,initial_values[3]+interval*dC3,initial_values[4]+interval*dC4,initial_values[5]+interval*dC5,initial_values[6]+interval*dC6]



### Cubic spline  with the values of the teachers documents
x=[0,10,20,30,40,50,60,70,80,90,100]
y=[0,436,1383,3184,5506,7856,9734,11186,12145,12697,12873]

cs_total=CubicSpline(x,y)
######

def k(z,criticality): #### determines the value of k com base das posições das barras
    p=(cs_total(z)-criticality)*10**-5
    return -1/(p-1)

def polinomial_solver(x,p): #### determines the value of the polinomial at that instance at time equals x
    assert type(p)==list
    return sum(list(p[i]*x**i for i in range(0,len(p))))


def coefficients_solver(initial_values,time,p): ### Using Sochaki-Parker using polinomials to get results
    a=[initial_values[0]]
    b=[initial_values[1]]
    c=[initial_values[2]]
    d=[initial_values[3]]
    e=[initial_values[4]]
    f=[initial_values[5]]
    g=[initial_values[6]]
    while (abs(polinomial_solver(time,a)-polinomial_solver(time,a[:-1]))/abs(polinomial_solver(time,a)))>3*10**-4:
        a=a+[(1/(len(a)+1))*(((p-sum(beta))/l)*a[-1]+Lambda[0]*b[-1]+Lambda[1]*c[-1]+Lambda[2]*d[-1]+Lambda[3]*e[-1]+Lambda[4]*f[-1]+Lambda[5]*g[-1])]
        b=b+[(1/(len(b)+1))*(((beta[0]/l)*a[-2])-Lambda[0]*b[-1])]
        c=c+[(1/(len(c)+1))*(((beta[1]/l)*a[-2])-Lambda[1]*c[-1])]
        d=d+[(1/(len(d)+1))*(((beta[2]/l)*a[-2])-Lambda[2]*d[-1])]
        e=e+[(1/(len(e)+1))*(((beta[3]/l)*a[-2])-Lambda[3]*e[-1])]
        f=f+[(1/(len(f)+1))*(((beta[4]/l)*a[-2])-Lambda[4]*f[-1])]
        g=g+[(1/(len(g)+1))*(((beta[5]/l)*a[-2])-Lambda[5]*g[-1])]
    return [polinomial_solver(time,a),polinomial_solver(time,b),polinomial_solver(time,c),polinomial_solver(time,d),polinomial_solver(time,e),polinomial_solver(time,f),polinomial_solver(time,g)]




b=time.time()
# Find the root of reactivity(x) - 400 = 0 using the Newton-Raphson method
#print(time.time()-b)
#print("roots "+str(root))
def simulation(): ### This is a simulation of the bars with the reactor
    instrument.write('SOUR1:FUNC PULS')
    instrument.write('SOUR1:BURS:STATe OFF')
    instrument.write('SOUR1:FREQ 2Hz')
    instrument.write('SOUR1:PULS:WIDTH 1000ns')
    instrument.write('OUTP1:POL NORM')
    instrument.write('SOUR1:VOLT:LEV:IMM:AMPL 5VPP')
    instrument.write('SOUR1:VOLT:LEV:IMM:OFFS 2.5V')
    instrument.write('OUTP1 ON')
    instrument.write('SOUR2:FUNC PULS')
    instrument.write('SOUR2:BURS:STATe OFF')
    instrument.write('SOUR2:FREQ 2Hz')
    instrument.write('SOUR2:PULS:WIDTH 1000ns')
    instrument.write('OUTP2:POL NORM')
    instrument.write('SOUR2:VOLT:LEV:IMM:AMPL 5VPP')
    instrument.write('SOUR2:VOLT:LEV:IMM:OFFS 2.5V')
    instrument.write('OUTP2 ON') ### initial output of the Function Generator
    time.sleep(10)
    instrument.write('SOUR1:FREQ 6Hz')
    instrument.write('SOUR2:FREQ 6Hz')
    time.sleep(10)
    k1=k(0,9097.35452975902)
    cont=True
    counts=11
    initial_values=[counts,(beta[0]*counts)/(Lambda[0]*l),(beta[1]*counts)/(Lambda[1]*l),(beta[2]*counts)/(Lambda[2]*l),(beta[3]*counts)/(Lambda[3]*l),(beta[4]*counts)/(Lambda[4]*l),(beta[5]*counts)/(Lambda[5]*l)]
    while initial_values[0]<10**12 and initial_values[0]>10:
        x1=[k1,k1,k1,k1,k1,k1,k1,k1,k1,k1,k1] ### averages necessary to reduce the noise saving values of time a k, maybe should remove them.
        while k1<1:
            if 1/(1-round(root_mean_squared(x1),5))<100 and cont==True:
                z=threadings()[0][0]
                instrument.write('SOUR1:FREQ '+str((1.7/(1-round(root_mean_squared(x1),5))**0.9)*math.exp(-0.00001/(1-round(root_mean_squared(x1),5))))+'Hz')
                instrument.write('SOUR1:PULS:DCYC 0.001')
                instrument.write('SOUR2:FREQ '+str((1.7/(1-round(root_mean_squared(x1),5))**0.9)*math.exp(-0.00001/(1-round(root_mean_squared(x1),5))))+'Hz')
                instrument.write('SOUR2:PULS:DCYC 0.001')
                k2=k1
                k1=k(z*20,9097.35452975902)
                del x1[0]
                x1=x1+[k1]
                print([x1[-1],z*20,cont])
            else:
                z=threadings()[0][0]
                instrument.write('SOUR1:FREQ '+str((1.7/(1-round(root_mean_squared(x1),5))**0.95)*math.exp(-0.00001/(1-round(root_mean_squared(x1),5))))+'Hz')
                instrument.write('SOUR1:PULS:WIDTH 100ns')
                instrument.write('SOUR2:FREQ '+str((1.7/(1-round(root_mean_squared(x1),5))**0.95)*math.exp(-0.00001/(1-round(root_mean_squared(x1),5))))+'Hz')
                instrument.write('SOUR2:PULS:WIDTH 100ns')
                k2=k1
                k1=k(z*20,9097.35452975902)
                del x1[0]
                x1=x1+[k1]
                print([x1[-1],z*20,cont]) 
        counts=1/(1-root_mean_squared(x1))
        p=[((k1-1)/k1),((k1-1)/k1),((k1-1)/k1),((k1-1)/k1),((k1-1)/k1),((k1-1)/k1),((k1-1)/k1),((k1-1)/k1),((k1-1)/k1),((k1-1)/k1)]
        initial_values=[counts,(beta[0]*counts)/(Lambda[0]*l),(beta[1]*counts)/(Lambda[1]*l),(beta[2]*counts)/(Lambda[2]*l),(beta[3]*counts)/(Lambda[3]*l),(beta[4]*counts)/(Lambda[4]*l),(beta[5]*counts)/(Lambda[5]*l)]
        #print(initial_values)
        previous_values=[counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts,counts]
        cont=False
        while cont==False: #Second cycle supercritical state.
            z=threadings1(sum(p)/len(p),0.06,initial_values)
            p1=(cs_total(z[0][0]*20)-9097.35452975902)*10**-5
            del p[0]
            p=p+[p1]
            #T=optimize.newton(lambda x: reactivity(x) - p, x0=0.0001, tol=1e-8)
            initial_values1=z[-1]
            del previous_values[0]
            previous_values=previous_values+[initial_values1[0]]
            #print(previous_values)
            if abs(previous_values[-1]-previous_values[0])<0.1:
                print([round(-1/((sum(p)/len(p))-1),5),round(z[0][0]*20,1),10**8,cont,initial_values1[0]])
            else:
                print([round(-1/((sum(p)/len(p))-1),5),round(z[0][0]*20,1),cont,initial_values1[0]])
            initial_values=initial_values1
            k1=round(-1/(p1-1),5)
            if (1.7/(1-round(k1,5))**0.9)*math.exp(-0.00001/(1-round(k1,5)))>initial_values1[0] and k1<1:
                cont=True 
            else:
                continue
            #initial_values=coefficients_solver(initial_values,time.time()-b,p)
            #initial_values=Range_Kutta_nuclear([N,C1,C2,C3,C4,C5,C6],initial_values,(time.time()-b)*.02,p)
            #instrument.write('SOUR1:FREQ '+str(initial_values[0])+'Hz')
            #instrument.write('SOUR2:FREQ '+str(initial_values[0])+'Hz')
            #b=time.time()
            #instrument.write('SOUR1:PULS:WIDTH 50ns')
            #instrument.write('SOUR2:PULS:WIDTH 50ns')
            #counts=counts*math.exp((time.time()-b)/T)
            #p1=p
            #if i==50:
            #   x=x+[time.time()-w]
            #  y=y+[initial_values[0]]
            # i=0
            #else:
            #   i=i+1
    #return [x,y]




r=simulation()
instrument.write('OUTP1 OFF')
instrument.write('OUTP2 OFF')
"""
plt.figure(figsize=(17,11))
plt.plot(r[0],r[1],label="values",marker=",",markersize=2)
plt.legend()
plt.yscale('log')
plt.show()
"""