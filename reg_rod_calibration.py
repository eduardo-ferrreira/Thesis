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

df1 = pd.read_csv(r'10-2024/21-10-2024/values_8.csv')
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
    if abs(t[i]-740)<5e-2:
        p0 = p[i]
        #print(p0)
        for j in range(len(p)):
            if abs(p[j]-2*p0)/(2*p0)<5e-4:
                T_d.append(round(t[j]-t[i],1))
                #print(p0, p[j], p[j]/p0)

print(T_d)

for i in range(len(t)):
    if abs(t[i]-1060)<5e-2:
        p0 = p[i]
        #print(p0)
        for j in range(len(p)):
            if abs(p[j]-2*p0)/(2*p0)<5e-4:
                T_d.append(round(t[j]-t[i],1))
                #print(p0, p[j], p[j]/p0)
"""for i in range(len(t)):
    if abs(t[i]-1425)<1e-3:
        p0 = p[i]
        for j in range(len(p)):
            if abs(p[j]-1.5*p0)/p0<1.5e-3:
                T_d.append(t[j]-t[i])
                #print(p0, p[j], p[j]/p0)"""
print(T_d)

for i in range(len(t)):
    if abs(t[i]-1370)<7.5e-2:
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

print(T_d)

for i in range(len(t)):
    if abs(t[i]-1670)<7.5e-2:
        p0 = p[i]
        #print(p0)
        for j in range(len(p)):
            if abs(p[j]-2*p0)/(2*p0)<10e-4:
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

print(T_d)

for i in range(len(t)):
    if abs(t[i]-2005)<5e-2:
        p0 = p[i]
        #print(p0)
        for j in range(len(p)):
            if abs(p[j]-2*p0)/(2*p0)<10e-4 and j<30000:
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

print(T_d)

for i in range(len(t)):
    if abs(t[i]-2510)<5e-2:
        p0 = p[i]
        print(p0)
        for j in range(len(p)):
            if abs(p[j]-2*p0)/(2*p0)<5e-5:
                T_d.append(round(t[j]-t[i],1))
                #print(t[j],t[i])
                #print(p0, p[j], p[j]/p0)

print(T_d)

period_list = []
i=0
p_value = 0
if len(T_d)==6:
    while i<6:
        #if i == 5:
        #    period_list.append(round(T_d[i]/np.log(1.5),1))
        #else:
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

    reg_rod = [0, 19.9, 29.7, 45.4, 59.8, 75.1, 100]
    #integral_reactivity2 = [0,85,149,241,307,334,346]

    cs_1 = CubicSpline(reg_rod_rpi, reactivity_rpi)
    cs_2 = CubicSpline(reg_rod, integral_reactivity)
    #cs_3 = CubicSpline(reg_rod, integral_reactivity2)
    #print(integral_reactivity, cs_2(0))

    x=np.linspace(0,100,100)
    cs_1_list = []
    cs_2_list = []
    #cs_3_list = []

    for i in range(len(x)):
        cs_1_list.append(cs_1(x[i]))
        cs_2_list.append(cs_2(x[i]))
    #    cs_3_list.append(cs_3(x[i]))

    plt.figure(figsize=(10,6))
    plt.plot(x, cs_2_list, label='fissionist')
    plt.plot(x, cs_1_list, label='rpi')
    #plt.plot(x, cs_3_list, label='rpi')
    plt.scatter(reg_rod[1:], integral_reactivity[1:])
    plt.scatter(reg_rod_rpi[1:], reactivity_rpi[1:])
    plt.xlim(0,100)
    plt.ylim(0,440)
    plt.legend()
    plt.xlabel('Rod position (%)')
    plt.ylabel(r'$\rho$ (pcm)')
    #plt.savefig('rod_calibration.pdf', dpi=600, bbox_inches='tight')
    plt.show()

    fig, ax1 = plt.subplots(figsize=(10,6))
    color = 'tab:red'
    ax1.set_xlabel('$t$ (s)')
    ax1.set_ylabel('Power (W)', color='k')
    ax1.set_yscale('log')
    line1, = ax1.plot(t, p, color=color, label='Power')
    ax1.tick_params(axis='y', labelcolor='k')
    ax2 = ax1.twinx()  # instantiate a second Axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('$k_{eff}$', color='k')  # we already handled the x-label with ax1
    line2, = ax2.plot(t, k, color='b', label='$k_{eff}$')
    ax2.set_ylim(0.99950, 1.004)
    line3 = ax2.axhline(y=1, xmin=0, xmax=max(t), color='tab:gray', linestyle='--', label='$k_{eff}=1$')
    ax2.tick_params(axis='y', labelcolor='k')
    # Combine legends
    lines = [line1, line2, line3]
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc='upper left')
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    #plt.savefig('power_rod_calib.pdf', dpi=600, bbox_inches='tight')
    #plt.show()