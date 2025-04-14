from THM_main import Version5_THM_prototype
from iapws import IAPWS97
import numpy as np
from THM_main import plotting
import pandas as pd
import matplotlib.pyplot as plt
import os
import re

case_name = "MPHYS AT10"
#User choice:
solveConduction = True
plot_at_z1 = []

########## Thermal hydraulics parameters ##########
## Geometric parameters
#User choice:
solveConduction = True
zPlotting = []

If = 8
I1 = 3
# Sensitivity to the meshing parameters
Iz1 = 25 # number of control volumes in the axial direction, added 70 for comparison with GeN-Foam
# Iz1 = 10, 20, 40, 50, 70, 80 and 160 are supported for the DONJON solution


########## Choice of Thermalhydraulics correlation ##########
voidFractionCorrel = 'EPRIvoidCorrel' # 'modBestion', 'HEM1', 'GEramp', 'EPRIvoidModel'
frfaccorel = "Churchill" # 'base', 'blasius', 'Churchill', 'Churchill_notOK' ?
P2Pcorel = "lockhartMartinelli" # 'base', 'HEM1', 'HEM2', 'MNmodel', "lockhartMartinelli"
numericalMethod = "FVM" # "FVM": Solves the system using matrix inversion with preconditioning.
                        # "GaussSiedel" : Applies the Gauss-Seidel iterative solver.
                        # "BiCG" : Uses the BiConjugate Gradient method for solving non-symmetric or indefinite matrices.
                        # "BiCGStab" : Applies the BiCGStab (BiConjugate Gradient Stabilized) method to ensure faster and more stable convergence.

########## Thermal hydraulics parameters ##########
## Geometric parameters
canalType = "square" # "square", "cylindrical"
pitch =1.6256e-2 #1.295e-2 # m : ATRIUM10 pincell pitch   0.0126 #
fuelRadius = (1.0414e-2)/2 # m : fuel rod radius
#gapRadius = fuelRadius + 0.000001 # m : expansion gap radius : "void" between fuel and clad - equivalent to inner clad radius
cladRadius = (1.23e-2)/2 # m : clad external radius
gapRadius = cladRadius - 8.128e-5 # m : expansion gap radius : "void" between fuel and clad - equivalent to inner clad radius
height = 3.81 # m : height : 3.8 m : active core height in BWRX-300 SMR, 1.555 m : for GeNFoam comparison.


## Fluid parameters
# T_inlet, T_outlet = 270, 287 Celcius
#tInlet = 270 + 273.15 # K, for BWRX-300 SMR core, try lowering the inlet temperature to set boiling point back and reduce the void fraction increase in the first few cm
tInlet = 554.28 #281.13 + 273.15 #278.813 + 273.15 # K, for BWRX-300 SMR core
#Nominal operating pressure = 7.2 MPa (abs)
pOutlet =  7.1e6 # Pa 
# Nominal coolant flow rate = 1530 kg/s
massFlowRate = 0.24 #8.407 * 10**(-2) #1530  / (200*91)  # kg/s

## Material parameters
kFuel = 4.18 # W/m.K, TECHNICAL REPORTS SERIES No. 59 : Thermal Conductivity of Uranium Dioxide, IAEA, VIENNA, 1966
Hgap = 10000 
#Hgap = 9000
kClad = 21.5 # W/m.K, Thermal Conductivity of Zircaloy-2 (as used in BWRX-300) according to https://www.matweb.com/search/datasheet.aspx?MatGUID=eb1dad5ce1ad4a1f9e92f86d5b44740d
# k_Zircaloy-4 = 21.6 W/m.K too so check for ATRIUM-10 clad material but should have the same thermal conductivity

qFiss = 2.25442*10**8#1.61607*10**8 # W/m3 : Volumetric heat source in the fuel
qFiss_init_0 = []
for i in range(Iz1):
    qFiss_init_0.append(qFiss)
    
case2 = Version5_THM_prototype("Initialization of BWR Pincell equivalent canal", canalType, pitch, fuelRadius, gapRadius, cladRadius, 
                            height, tInlet, pOutlet, massFlowRate, qFiss_init_0, kFuel, Hgap, kClad, Iz1, If, I1, zPlotting, 
                            solveConduction, dt = 0, t_tot = 0, frfaccorel = frfaccorel, P2Pcorel = P2Pcorel, voidFractionCorrel = 'EPRIvoidModel',
                            numericalMethod = numericalMethod)

print(f'P_rgh = {case2.convection_sol.P[-1][-1] - case2.convection_sol.rho[-1][-1]*height*9.81} Pa')
print(f'P = {case2.convection_sol.P[-1]} Pa')
print(f'rgh = {case2.convection_sol.rho[-1][-1] * 9.81 * height} Pa')

z_p, x_p =np.loadtxt('BWR\THM_prototype\Python-Graphs-twoporflow\SingleRod_Pressure_axial.txt', delimiter='*', unpack=True)
z_T, x_T =np.loadtxt('BWR\THM_prototype\Python-Graphs-twoporflow\SingleRod_Tliq_axial.txt', delimiter='*', unpack=True)
z_VF, x_VF =np.loadtxt('BWR\THM_prototype\Python-Graphs-twoporflow\SingleRod_VoidFraction_axial.txt', delimiter='*', unpack=True)
x_T = [x_T[i] + 273.15 for i in range(len(x_T))]

def read_files_in_directory(directory_path):
    data_dict = {}
    print(f"Reading files in directory: {directory_path}")
    # Parcourt tous les fichiers du dossier
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        print(f"Reading file: {file_path}")
        # Vérifie que c'est bien un fichier
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                content = file.read()
                    
                # Trouve la première parenthèse ouvrante et fermante
                start = content.find('(')
                end = content.find(')', start)
                #end = start + 74
                if start != -1 and end != -1:
                    # Extrait les données entre les parenthèses
                    data_str = content[start+1:end].strip()
                    # Divise les lignes en liste de chaînes
                    data_lines = data_str.splitlines()
                    if len(data_lines) != 1:
                        float_list = [float(item) for item in data_lines]
                        data_dict[filename] = float_list

                if len(data_lines) == 1:
                    # Trouve la première parenthèse ouvrante et fermante
                    start = content.find('(')
                    end = content.find(';', start)
                    #end = start
                    if start != -1 and end != -1:
                        # Extrait les données entre les parenthèses
                        data_str = content[start+1:end].strip()
                        # Divise les lignes en liste de chaînes
                        data_lines = data_str.splitlines()
                        data_lines.pop()
                        x, y, z = np.zeros(len(data_lines)), np.zeros(len(data_lines)), np.zeros(len(data_lines))
                        for i in range(len(data_lines)):
                            a = values = data_lines[i].strip("()").split()
                            x[i] = float(a[0])
                            y[i] = float(a[1])
                            z[i] = float(a[2])
                        data_dict[fr'{filename}_x'] = x
                        data_dict[fr'{filename}_y'] = y
                        data_dict[fr'{filename}_z'] = z
        
    return data_dict

datadict = read_files_in_directory(rf'BWR\THM_prototype\Python-Graphs-twoporflow\fluidRegion')
structureFraction = 1- (datadict['alpha.liquid'][0] + datadict['alpha.vapour'][0])
datadict['alpha.vapour'] = [item/(1-structureFraction) for item in datadict['alpha.vapour']]
Twater = [(1-datadict['alpha.vapour'][i]) * datadict['T.liquid'][i] + datadict['alpha.vapour'][i] * datadict['T.vapour'][i] for i in range(len(datadict['alpha.vapour']))]

print(datadict['alpha.vapour'])
z_gf = np.linspace(0, 3.81, len(datadict['alpha.vapour']))

print("temperature profil for THM_p", case2.convection_sol.T_water)
print("temperature profil for TwoPorFlow", x_T)
print("temperature profile for genfoam", datadict['T.liquid'])

z_p = [z_p[i] * 0.1524 for i in range(len(x_p))]
z_T = [z_T[i] * 0.1524 for i in range(len(x_T))]
z_VF = [z_VF[i] * 0.1524 for i in range(len(x_VF))]

fig, ax1 = plt.subplots()
ax1.plot(case2.convection_sol.T_water, z_T, label='THM_p',color='r', alpha=0.7, linewidth=3)
ax1.plot(x_T,z_T, label='TwoPorFlow',color='b', alpha=0.7, linewidth=3)
ax1.plot(Twater, z_gf, label='GeN-Foam',color='g', alpha=0.7, linewidth=3)
ax1.set_ylabel("Axial position in m")
ax1.set_xlabel("Temperature in K")
ax1.set_title("Temperature profile along the axial direction")
ax1.grid()
ax1.legend(loc="best")

fig, ax2 = plt.subplots()
ax2.plot(case2.convection_sol.voidFraction[-1], z_VF, label='THM_p',color='r', alpha=0.7, linewidth=3)
ax2.plot(x_VF,z_VF, label='TwoPorFlow',color='b', alpha=0.7, linewidth=3)
ax2.plot(datadict['alpha.vapour'], z_gf, label='GeN-Foam',color='g', alpha=0.7, linewidth=3)
ax2.set_ylabel("Axial position in m")
ax2.set_xlabel("Void fraction")
ax2.set_title("Void fraction profile along the axial direction")
ax2.grid()
ax2.legend(loc="best")

fig, ax3 = plt.subplots()
ax3.plot(case2.convection_sol.U[-1], case2.convection_sol.z_mesh)
ax3.set_ylabel("Axial position in m")
ax3.set_xlabel("Velocity in m/s")
ax3.set_title("Velocity profile along the axial direction")
ax3.grid()
ax3.legend(loc="best")

fig, ax4 = plt.subplots()
ax4.plot(case2.convection_sol.P[-1], z_p, label='THM_p',color='r', alpha=0.7, linewidth=3)
ax4.plot(x_p,z_p, label='TwoPorFlow',color='b', alpha=0.7, linewidth=3)
ax4.plot(datadict['p'], z_gf, label='GeN-Foam',color='g', alpha=0.7, linewidth=3)
ax4.set_ylabel("Axial position in m")
ax4.set_xlabel("Pressure in Pa")
ax4.set_title("Pressure profile along the axial direction")
ax4.grid()
ax4.legend(loc="best")

plt.show()