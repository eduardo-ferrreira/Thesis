import matplotlib.pyplot as plt
import matplotlib.animation as animation
import scipy
import time
import datetime
import os
import csv
import numpy as np
from scipy.integrate import odeint

"""
# Function to generate some data (replace this with your actual data generation process)
def generate_data():
    # Generate some dummy data (replace this with your actual data source)
    return [1, 2, 3, 4, 5]

# Initialize an empty list to store the real-time data
data_list = []

# Function to update the plot with new data
def update_plot(frame):
    # Get new data
    new_data = generate_data()
    # Append new data to the list
    data_list.extend(new_data)
    # Plot the updated data
    plt.cla()  # Clear the previous plot
    plt.plot(data_list)
    

#Create a figure and axis for the plot
fig, ax = plt.subplots()

# Create an animation that updates the plot every 100 milliseconds
ani = animation.FuncAnimation(fig, update_plot, interval=100)

# Show the plot
plt.show()
"""

##############################################################################################################################################

"""
# Get the current date and time
current_datetime = datetime.datetime.now().strftime("%H %d-%m-%Y")


# Print the current date and time
#print("Current date and time:", current_datetime)

day = datetime.datetime.now().strftime("%d-%m-%Y") #gives date in format day-month-year

# Example data
data = [
    [1, 'a'],
    [2, 'b'],
    [3, 'c']
]


day = datetime.datetime.now().strftime("%d-%m-%Y") #gives date in format day-month-year
counter = 0
filepath = os.path.join(day, f'values_{counter}.csv') #create filepath: a folder named with the current date
if not os.path.exists(day):
    os.mkdir(day)  # Create the directory if it doesn't exist
while os.path.exists(filepath): #if the current file path doesn't exist, create the file
    counter += 1 
    filepath = os.path.join(day, f'values_{counter}.csv')
    
with open(filepath, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['x'])  # Write header
    writer.writerows(data)  # Write rows of lists
"""
##############################################################################################################################################

# Experimental data from RPI
Lambda = [0.0127, 0.0317, 0.116, 0.311, 1.4, 3.87]  # decay constant of the precursors list
beta = [0.00031, 0.00166, 0.00151, 0.00328, 0.00103, 0.00021]  # precursors fractions list
l = 0.000055  # prompt neutrons
epsilon = 1  # fast fission factor
ld = l * (1 - sum(beta)) + sum([beta[i] * (1 / Lambda[i]) for i in range(len(Lambda))])  # slow decay lifetime

t = np.linspace(0, 1000, 100000)

def p_function(t):
    if t < 50:
        return 0
    elif 50 < t < 200:
        return 0.000366 * t * 1e-5
    else: #elif t > 900:
        return -0.000366 * t * 1e-5

def dSdt(S, t):  # return state vector of point reactor kinetic equations ODE's
    n, C1, C2, C3, C4, C5, C6 = S
    p = p_function(t)
    return [
        (p - sum(beta)) / l * n + sum([Lambda[i] * S[i + 1] for i in range(len(Lambda))]),
        beta[0] / l * n - Lambda[0] * C1,
        beta[1] / l * n - Lambda[1] * C2,
        beta[2] / l * n - Lambda[2] * C3,
        beta[3] / l * n - Lambda[3] * C4,
        beta[4] / l * n - Lambda[4] * C5,
        beta[5] / l * n - Lambda[5] * C6
    ]

# Initial conditions
counts = 11 #counts associated to all bars at 0%
initial_values = [counts,
                    (beta[0]*counts)/(Lambda[0]*l),
                    (beta[1]*counts)/(Lambda[1]*l),
                    (beta[2]*counts)/(Lambda[2]*l),
                    (beta[3]*counts)/(Lambda[3]*l),
                    (beta[4]*counts)/(Lambda[4]*l),
                    (beta[5]*counts)/(Lambda[5]*l)]

#initial_values = [0, 0, 0, 0, 0, 0, 0]

# Solve the differential equation
sol = odeint(dSdt, initial_values, t)

# sol contains the solution at each time point

plt.plot(t, sol.T[0])
plt.xlabel('$Time$')
plt.ylabel('$n$')
#plt.title("Reactivity insertion of $\\rho=5pcm$ at $t=0$," + ' ' + "and $\\rho=-100pcm$ at $t=300$.")
#plt.savefig('reactivity evolution', dpi=300, bbox_inches='tight')
plt.show()

##############################################################################################################################################

"""
list_of_lists = [[1, 2, 3], [4, 5], [6, 7, 8, 9], [0]]

# Find the biggest list using the max() function with a custom key
biggest_list = max(list_of_lists, key=len)
# Find the first list that contains a 0 value
list_with_zero = next((lst for lst in list_of_lists if 0 in lst), None)

#print("The biggest list is:", biggest_list)
#print(list_with_zero)


print([[1, 2, 3], [4, 5], [6, 7, 8, 9], [0]].remove([6, 7, 8, 9]))
"""

##############################################################################################################################################

"""
list_of_lists = [[1.1, 2.2, 1.0], [3.4, 4.5, 3.4], [6.7, 8.9, 7.0], [10.1, 11.2, 9.9]]

# Using a loop
for lst in list_of_lists:
    if round(lst[0]) == round(lst[2]):
        print("List with first value equal to third value:", lst)
        break
else:
    print("No such list found")

# Using list comprehension
result = next((lst for lst in list_of_lists if round(lst[0]) == round(lst[2])), None)
if result:
    print("List with first value equal to third value:", result)
else:
    print("No such list found")
""" 
##############################################################################################################################################
    
"""
main_list = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

# Known lists to remove
known_lists = [[1, 2, 3], [7, 8, 9]]

# Remove the known lists
filtered_list = [lst for lst in main_list if lst not in known_lists]

print("Filtered list:", filtered_list[0])
"""
##############################################################################################################################################