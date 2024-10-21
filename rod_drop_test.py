import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

m_rod = 15 # kg
g = 9.81 # m s ^ -2
p_water = 1000 # kg m ^ -3
a= 0.0602 #m
b=0.021 #m
r_rod = 0.05 # m
l_rod = 0.629 # m
A_rod = 0.035*0.004*2+np.pi*(10.5e-3-6.5e-3)**2#0.035*0.021+np.pi*0.0105**2 #np . pi * a * b # m ^2
V_rod = A_rod * l_rod # m ^3
c_d = 0.82 # coefficient drag of a long cylinder
y0_rod = l_rod+l_rod/2# max height position of the center of mass of the rods
vy0_rod = 0 # initial velocity of the rods before scram

def dSdt(t,S):
    y, vy = S
    dSdt = vy, 1/ m_rod *(1/2* c_d * p_water * A_rod * vy**2 -( m_rod - p_water * V_rod )*g ) # rod falling in water differential equation
    return dSdt

t=np.linspace(0,0.5,1000)
S0=(y0_rod, vy0_rod)
sol=odeint(dSdt, y0=S0, t=t, tfirst=True)

x_taylor=[0, 0.01, 0.06, 0.14, 0.24, 0.3, 0.35, 0.41, 0.43]
y_taylor=[y0_rod, y0_rod*0.9999, y0_rod*0.98, y0_rod*0.9, y0_rod*0.7, y0_rod*0.55, y0_rod*0.35, y0_rod*0.1, y0_rod*0]

plt.figure(figsize=(10,6))
plt.plot(t, sol.T[0], label='Runge-Kutta 4$^{th}$ order', color='b')
plt.scatter(x_taylor,y_taylor, label='Taylor 1$^{st}$ order (hipotético)', color='tab:orange')
plt.plot(x_taylor,y_taylor,color='tab:orange')#, label='Taylor 1$^{st}$ order')
#plt.vlines(x=0.430,ymin=0, ymax=max(sol.T[0]), linestyle='--')
#plt.vlines(x=0.470,ymin=0, ymax=max(sol.T[0]), linestyle='--')
#plt.hlines(y=0,xmin=0, xmax=max(t), linestyle='--')
plt.ylim(0,1)
plt.xlim(0,max(t))
plt.ylabel('Rod height (m)')
plt.xlabel('$t$ (s)')
y1=np.array(0.427)
y2=np.array(0.467)
plt.fill_between(x=[0.430,0.470], y1=0, y2=1, where=[0.430,0.470], color='C1', alpha=0.3, label='RPI data')
plt.legend()
plt.savefig('rod_drop.pdf', dpi=600, bbox_inches='tight')
plt.show()
