import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
import matplotlib.pylab as pylab

params = {'legend.fontsize': 'x-large',
          'figure.figsize': (15, 5),
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
pylab.rcParams.update(params)



Lambda = [0.0127, 0.0317, 0.116, 0.311, 1.4, 3.87] #decay constants of the percursors 
beta = [0.00031, 0.00166, 0.00151, 0.00328, 0.00103, 0.00021] #percursors fractions
l = 0.000055 # l is the prompt neutron lifetime (Matos et al.)

df1 = pd.read_csv(r'C:\Users\eduar\Documents\Faculdade\Mestrado IST\2º ano\1. Dissertação\teste calibracao br\values_1.csv')
df1['Time'] = df1['Time']-df1['Time'].iloc[0]

t = np.array(df1['Time'])
p = 1e10*np.array(df1['Current'])
k = np.array(df1['k'])

#plt.plot(t,p)
#plt.yscale('log')
#plt.show()

def inhour(T):
    p = l/T
    for i in range(len(Lambda)):
        p += beta[i]/(l+Lambda[i]*T)
    return p

T_d = []

for i in range(len(t)):
    if abs(t[i]-1044)<1e-3:
        p0 = p[i]
        #print(p0)
        for j in range(len(p)):
            if abs(p[j]-2*p0)/(2*p0)<9.5e-4:
                T_d.append(round(t[j]-t[i],1))
                #print(p0, p[j], p[j]/p0)

#print(T_d)

for i in range(len(t)):
    if abs(t[i]-1425)<1e-3:
        p0 = p[i]
        #print(p0)
        for j in range(len(p)):
            if abs(p[j]-2*p0)/(2*p0)<2.5e-4:
                T_d.append(round(t[j]-t[i],1))
                #print(p0, p[j], p[j]/p0)
"""for i in range(len(t)):
    if abs(t[i]-1425)<1e-3:
        p0 = p[i]
        for j in range(len(p)):
            if abs(p[j]-1.5*p0)/p0<1.5e-3:
                T_d.append(t[j]-t[i])
                #print(p0, p[j], p[j]/p0)"""
#print(T_d)

for i in range(len(t)):
    if abs(t[i]-1770)<7.44e-2:
        p0 = p[i]
        #print(p0)
        for j in range(len(p)):
            if abs(p[j]-2*p0)/(2*p0)<5e-4:
                T_d.append(round(t[j]-t[i],1))
                #print(t[j],t[i])
                #print(p0, p[j], p[j]/p0)
"""for i in range(len(t)):
    if abs(t[i]-1770)<7.44e-2:
        p0 = p[i]
        for j in range(len(p)):
            if abs(p[j]-1.5*p0)/p0<5.85e-4:
                T_d.append(t[j]-t[i])
                #print(t[j],t[i])
                #print(p0, p[j], p[j]/p0)"""

#print(T_d)

for i in range(len(t)):
    if abs(t[i]-2080)<5e-2:
        p0 = p[i]
        #print(p0)
        for j in range(len(p)):
            if abs(p[j]-2*p0)/(2*p0)<2.5e-4:
                T_d.append(round(t[j]-t[i],1))
                #print(t[j],t[i])
                #print(p0, p[j], p[j]/p0)
"""for i in range(len(t)):
    if abs(t[i]-2080)<7.44e-2:
        p0 = p[i]
        #print(p0)
        for j in range(len(p)):
            if abs(p[j]-1.5*p0)/p0<7e-4:
                T_d.append(t[j]-t[i])
                #print(t[j],t[i])
                #print(p0, p[j], p[j]/p0)"""

#print(T_d)

for i in range(len(t)):
    if abs(t[i]-2425)<5e-2:
        p0 = p[i]
        #print(p0)
        for j in range(len(p)):
            if abs(p[j]-2*p0)/(2*p0)<2.5e-4:
                T_d.append(round(t[j]-t[i],1))
                #print(t[j],t[i])
                #print(p0, p[j], p[j]/p0)
"""for i in range(len(t)):
    if abs(t[i]-2425)<7.44e-2:
        p0 = p[i]
        #print(p0)
        for j in range(len(p)):
            if abs(p[j]-1.5*p0)/p0<1e-3:
                T_d.append(t[j]-t[i])
                #print(t[j],t[i])
                #print(p0, p[j], p[j]/p0)"""

#print(T_d)

for i in range(len(t)):
    if abs(t[i]-3100)<7.44e-2:
        p0 = p[i]
        #print(p0)
        for j in range(len(p)):
            if abs(p[j]-1.5*p0)/p0<3e-4:
                T_d.append(round(t[j]-t[i],1))
                #print(t[j],t[i])
                #print(p0, p[j], p[j]/p0)

#print(T_d)

period_list = []
i=0
p_value = 0
if len(T_d)==6:
    while i<6:
        if i == 5:
            period_list.append(round(T_d[i]/np.log(1.5),1))
        else:
            period_list.append(round(T_d[i]/np.log(2),1))
        i+=1

    reactivity = [0]
    integral_reactivity = [0]
    for T in period_list:
        p_value = round(inhour(T)*10**5)
        integral_reactivity.append(sum(reactivity)+p_value)
        reactivity.append(p_value)
    print(T_d, '\n', period_list, '\n', reactivity, '\n', integral_reactivity)

reg_rod_rpi = [0,20.2,29.8,44.9,60.2,75.4,100]#
reactivity_rpi = [0,81,142,233,299,324,331]

reg_rod = [0,20,30,45,60,75,100]

cs_1 = CubicSpline(reg_rod_rpi, reactivity_rpi)
cs_2 = CubicSpline(reg_rod, integral_reactivity)

x=np.linspace(0,100,1000)
cs_1_list = []
cs_2_list = []

for i in range(len(x)):
    cs_1_list.append(cs_1(x[i]))
    cs_2_list .append(cs_2(x[i]))

plt.figure(figsize=(10,6))
plt.plot(x, cs_2_list, label='fissionist')
plt.plot(x, cs_1_list, label='rpi')
plt.scatter(reg_rod[1:], integral_reactivity[1:])
plt.scatter(reg_rod_rpi[1:], reactivity_rpi[1:])
plt.xlim(0,100)
plt.ylim(0,350)
plt.legend()
plt.savefig('rod_calibration.pdf', dpi=600, bbox_inches='tight')
plt.show()
