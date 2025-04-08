import numpy as np
import matplotlib.pyplot as plt

# read files and assign x and y axis values
y, x =np.loadtxt('SingleRod_Tliq_axial.txt', delimiter='*', unpack=True)
y2, x2 =np.loadtxt('SingleRod_Tsat_axial.txt', delimiter='*', unpack=True)


# plotting
plt.plot(x,y, label='BWR SingleRod Tliq',color='b', alpha=0.7, linewidth=3)
plt.plot(x2,y2, label='BWR SingleRod Tsat', color='r', linestyle='dashed', linewidth=3)
plt.xlabel('Axial Temperature (°C)')
plt.ylabel('Axial levels (-)')

plt.legend()
plt.grid()
plt.show()# Schreibe hier Deinen Code :-)
