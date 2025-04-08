import numpy as np
import matplotlib.pyplot as plt

# read files and assign x and y axis values
y, x =np.loadtxt('SingleRod_Tliq_axial.txt', delimiter='*', unpack=True)
# y2, x2 =np.loadtxt('Axial_Tcoolant.txt', delimiter='*', unpack=True)


# plotting
plt.plot(x,y, label='BWR_SingleRod',color='b', alpha=0.7, linewidth=3)
# plt.plot(x2,y2, label='PWR FA', color='r', linestyle='dashed', linewidth=3)
plt.xlabel('Axial coolant temperature (°C)')
plt.ylabel('Axial node number (-)')

plt.legend()
plt.grid()
plt.show()
