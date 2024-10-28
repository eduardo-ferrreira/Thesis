import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simpson
import csv

Lambda = [0.0127, 0.0317, 0.116, 0.311, 1.4, 3.87] #decay constants of the percursors 
beta = [0.00031, 0.00166, 0.00151, 0.00328, 0.00103, 0.00021] #percursors fractions

df = pd.read_csv(r'10-2024/28-10-2024/values_1.csv')

t = np.array(df['Time'])
n = np.array(df['Counts'])

#plt.scatter(t, n,s=4)
#plt.show()

for i in range(len(n)):
    if abs(n[i]-161434877)<1:
        index_30kW=i
        #print(index_30kW)
        i+=1 

integral = simpson(y=n[index_30kW:], x=t[index_30kW:])

summ = 0
for i in range(len(Lambda)):
    summ += beta[i]/Lambda[i]

p_ng = n[index_30kW]/integral*summ

print(t[index_30kW:][-1]-t[index_30kW:][0], p_ng*10**5)