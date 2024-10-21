import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pylab as pylab


params = {'legend.fontsize': 'x-large',
          'figure.figsize': (15, 5),
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
pylab.rcParams.update(params)

v_in = [0,1,1.5,2,2.5,3,4,5,6,7,8,9,10,15,20,25,29]
v1k = [4.93,4.92,4.37,3.35,2.1,0.97,0.4,0.36,0.35,0.35,0.35,0.34,0.34,0.36,0.37,0.38,0.39]
v2k = [4.93,4.92,3.79,1.39,0.26,0.21,0.18,0.17,0.16,0.16,0.16,0.16,0.16,0.16,0.18,0.19,0.2]
v4k7 = [4.93,4.86,2.66,0.19,0.16,0.14,0.13,0.12,0.12,0.12,0.12,0.11,0.1,0.12,0.13,0.14,0.15]
v05k = [4.93, 4.92,4.64,4.13,3.47,2.7,1.22,0.72,0.56,0.46,0.41,0.39,0.37,0.32,0.31,0.31,0.31]

plt.figure(figsize=(10,6))
plt.scatter(v_in[:13], v05k[:13], s=20, label= '0.5k$\Omega$', marker='o')
plt.scatter(v_in[:13], v1k[:13], s=20, label= '1k$\Omega$', marker='^')
plt.scatter(v_in[:13], v2k[:13], s=20, label= '2k$\Omega$', marker='v')
plt.scatter(v_in[:13], v4k7[:13], s=20, label= '4.7k$\Omega$', marker='s')
#plt.show()
plt.plot(v_in[:13], v05k[:13])
plt.plot(v_in[:13], v1k[:13])
plt.plot(v_in[:13], v2k[:13])
plt.plot(v_in[:13], v4k7[:13])
#plt.xticks(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
plt.xticks([0,1,2,3,4,5,6,7,8,9,10])
plt.hlines(y=1.6, xmin=v_in[0], xmax=v_in[12], colors='r', linestyles='--')
plt.hlines(y=1.8, xmin=v_in[0], xmax=v_in[12], colors='r', linestyles='--')
plt.xlabel('$V_{in}$ [V]')
plt.ylabel('$V_{opto}$ [V]')
plt.ylim(0,5)
plt.xlim(0,10)
plt.legend()
x=np.array([0,1,2,3,4,5,6,7,8,9,10])
y1=np.array([1.6]*11)
y2=np.array([1.8]*11)
plt.fill_between(x, y1, y2, where=(y1<y2), color='C1', alpha=0.3)
plt.savefig('transfer_function.pdf', dpi=600, bbox_inches='tight')
plt.show()