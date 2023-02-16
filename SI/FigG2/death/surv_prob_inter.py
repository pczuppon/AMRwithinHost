import numpy as np
import matplotlib.pyplot as plt
import os
from numpy import genfromtxt
from scipy.special import hyp2f1
from scipy.special import expi

################################
################################ data
################################

os.chdir(os.path.realpath(''))


################################
################################ Import Data
################################

################################ Short - bacteriostatic
my_data = genfromtxt('surv_death_vary_c_fac_10_sc_0.txt', delimiter=',')

data1 = []
c_data1 = []
for i in range(len(my_data)):
    data1.append(float(my_data[i][1]))
    c_data1.append(float(my_data[i][0]))

################################ Short - bactericidal
my_data = genfromtxt('surv_death_vary_c_fac_10_sc_1.txt', delimiter=',')

data2 = []
c_data2 = []
for i in range(len(my_data)):
    data2.append(float(my_data[i][1]))
    c_data2.append(float(my_data[i][0]))


################################
################################ Plot surv prob
################################
plt.semilogx(c_data1,data1,'^',color='C0',markersize=10)
plt.vlines(0.017,0,.75,linestyle='dashed',color='black')
plt.plot(c_data2,data2,'^',color='C1',markersize=10)
plt.tick_params(axis='both', which='major', labelsize=15, width=1, length=10)
plt.tick_params(axis='both', which='minor', labelsize=10, width=1, length=5)
plt.ylim((-0.025,0.8))
plt.show()



