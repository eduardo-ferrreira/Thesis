import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import matplotlib.pylab as pylab

params = {'legend.fontsize': 'x-large',
          'figure.figsize': (15, 5),
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
pylab.rcParams.update(params)

df1=pd.read_csv(r'C:\Users\eduar\Documents\Faculdade\Mestrado IST\2º ano\1. Dissertação\Estudo_k\teste5.csv') #cabo curto
df2=pd.read_csv(r'C:\Users\eduar\Documents\Faculdade\Mestrado IST\2º ano\1. Dissertação\Estudo_k\teste8.csv') #cabo longo

#print(df1.head())

k_1 = np.array(df1['K'])
k_2 = np.array(df2['K'])

for i in range(len(k_1)):
    k_1[i] = round(k_1[i],5)

for i in range(len(k_2)):
    k_2[i] = round(k_2[i],5)

dk_1 = []
dk_2 = []

for i in range(1, len(k_1)-1):
    diff1 = abs(k_1[i+1]-k_1[i])
    #diff1 = abs(round(k_1[i+1]-k_1[i],5))
    if diff1 != 0:
        dk_1.append(diff1)

for i in range(1, len(k_2)-1):
    diff2 = abs(round(k_2[i+1]-k_2[i],5))
    if diff2 != 0:
        dk_2.append(diff2)

plt.figure(figsize=(10,6))
plt.hist(dk_1, bins=len((dk_1)), alpha=0.7, color='blue', edgecolor='black', density=False)
plt.xlabel('$|\delta k|$')
plt.ylabel('Frequency')
plt.savefig('diffk_curto_zeroless.pdf', dpi=600, bbox_inches='tight')
#plt.show()

plt.figure(figsize=(10,6))
plt.hist(dk_2, bins=len(dk_2), alpha=0.7, color='blue', edgecolor='black', density=False)
pylab.ticklabel_format(axis='x', style='sci', scilimits=(-5, -5), useOffset=False)
plt.xlabel('$|\delta k|$')
plt.ylabel('Frequency')
plt.savefig('diffk_longo_zeroless.pdf', dpi=600, bbox_inches='tight')
#plt.show()
#print(k_1)