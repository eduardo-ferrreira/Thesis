import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(r"C:\Users\eduar\Documents\Faculdade\Mestrado IST\2º ano\1. Dissertação\teste run in\values_1.csv")
df['Time'] = df['Time']-df['Time'].iloc[0]
t= np.array(df['Time'])
i = df['Current']

df2 = pd.read_excel(r"C:\Users\eduar\Documents\Faculdade\Mestrado IST\2º ano\1. Dissertação\teste run in\Runin_10kW_19082013.xlsx")
t2 = np.array(df2['t(s)'])
power2 = df2['P (W)']
#print(df2['t(s)'])

#plt.plot(t2,power2)
#plt.plot(t,i)
#plt.yscale('log')
#plt.show()
index=0
for j in range(len(i)):
    if abs(i[j]-1.05e-6)<1e-7:
        index=j

print(index, i[index], t[index])

t1=t[13500:]-1257
t2=t2+68
power1=i[13500:]*10**10

#print(t1, '\n', t2)

plt.figure(figsize=(10,6))
plt.plot(t1, power1, label='FISSIONIST')
plt.plot(t2,power2,label='RPI')
plt.yscale('log')
plt.legend()
plt.xlabel('$t$')
plt.ylabel('$P$')
plt.savefig('run_in.pdf', dpi=600, bbox_inches='tight')
plt.show()