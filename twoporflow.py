from THM_main import Version5_THM_prototype
from iapws import IAPWS97
import numpy as np
from THM_main import plotting
import pandas as pd
import matplotlib.pyplot as plt
import os
import re

case_name = "MPHYS AT10 TWOPORFLOW"
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


z_p, x_p =np.loadtxt('BWR\THM_prototype\Python-Graphs-twoporflow\SingleRod_Pressure_axial.txt', delimiter='*', unpack=True)
z_T, x_T =np.loadtxt('BWR\THM_prototype\Python-Graphs-twoporflow\SingleRod_Tliq_axial.txt', delimiter='*', unpack=True)
z_VF, x_VF =np.loadtxt('BWR\THM_prototype\Python-Graphs-twoporflow\SingleRod_VoidFraction_axial.txt', delimiter='*', unpack=True)
x_T = [x_T[i] + 273.15 for i in range(len(x_T))]

z_p = [z_p[i] * 0.1524 for i in range(len(x_p))]
z_T = [z_T[i] * 0.1524 for i in range(len(x_T))]
z_VF = [z_VF[i] * 0.1524 for i in range(len(x_VF))]

fig, ax1 = plt.subplots()
ax1.step(z_T,case2.convection_sol.T_water , label='THM_p',color='r')
ax1.step(z_T , x_T, label='TWOPORFLOW',color='b')
ax1.step(z_gf, Twater, label='GeN-Foam',color='g')
ax1.set_xlabel("Axial position in m")
ax1.set_ylabel("Temperature in K")
#ax1.set_title("Temperature profile along the axial direction")
ax1.grid()
ax1.legend(loc="best")

fig, ax2 = plt.subplots()
ax2.step(z_VF,case2.convection_sol.voidFraction[-1], label='THM_p',color='r')
ax2.step(z_VF, x_VF, label='TwoPorFlow',color='b')
ax2.step(z_gf, datadict['alpha.vapour'], label='GeN-Foam',color='g')
ax2.set_xlabel("Axial position in m")
ax2.set_ylabel("Void fraction")
#ax2.set_title("Void fraction profile along the axial direction")
ax2.grid()
ax2.legend(loc="best")

fig, ax3 = plt.subplots()
ax3.plot(case2.convection_sol.U[-1], case2.convection_sol.z_mesh)
ax3.set_ylabel("Axial position in m")
ax3.set_xlabel("Velocity in m/s")
#ax3.set_title("Velocity profile along the axial direction")
ax3.grid()
ax3.legend(loc="best")

fig, ax4 = plt.subplots()
ax4.step(z_p, case2.convection_sol.P[-1], label='THM_p', color='r')
ax4.step(z_p, x_p, label='TwoPorFlow', color='b')
ax4.step(z_gf, datadict['p'], label='GeN-Foam',color='g')
ax4.set_xlabel("Axial position in m")
ax4.set_ylabel("Pressure in Pa")
#ax4.set_title("Pressure profile along the axial direction")
ax4.grid()
ax4.legend(loc="best")

plt.show()

# Charger les données
file_path = rf'BWR\THM_prototype\graph_axial.txt'
data = pd.read_csv(file_path, skipinitialspace=True)

# Afficher les premières lignes pour vérification
print("Aperçu des données:")
print(data.head())

# Informations générales sur les données
print("\nInformations sur les données:")
print(data.info())

#transformer les données en un dictionnaire simple:
data_TPF = data.to_dict(orient='list')

Dh = case2.convection_sol.Dh
roughness = 1.0 * (10**(-6))

#liste des paramètres dans le dictionnaire data_TPF:
#zPosition, Void, BoronCon, Pressure, TempVap, TempLiq, TempFuelC, TempStru, VelzVap, VelzLiq, Time

data_TPF['TSat'] = [IAPWS97(P = data_TPF['Pressure'][i]/1e6, x = 0).T for i in range(len(data_TPF['Pressure']))]
data_TPF['rhoLiq'] = [IAPWS97(T = data_TPF['TSat'][i], x = 0).rho for i in range(len(data_TPF['Pressure']))]
data_TPF['rhoVap'] = [IAPWS97(T = data_TPF['TSat'][i], x = 1).rho for i in range(len(data_TPF['Pressure']))]
data_TPF['muLiq'] = [IAPWS97(T = data_TPF['TSat'][i], x = 0).mu for i in range(len(data_TPF['Pressure']))]
data_TPF['muVap'] = [IAPWS97(T = data_TPF['TSat'][i], x = 1).mu for i in range(len(data_TPF['Pressure']))]
data_TPF['ReLiq'] = [data_TPF['rhoLiq'][i] * data_TPF['VelzLiq'][i] * Dh / data_TPF['muLiq'][i] for i in range(len(data_TPF['Pressure']))]
data_TPF['ReVap'] = [data_TPF['rhoVap'][i] * data_TPF['VelzVap'][i] * Dh / data_TPF['muVap'][i] for i in range(len(data_TPF['Pressure']))]
data_TPF['w'] = [(((data_TPF['ReLiq'][i] +  data_TPF['ReVap'][i]) * 0.5) - 1300)/2000 for i in range(len(data_TPF['Pressure']))]
data_TPF['C_LM'] = [20*data_TPF['w'][i] + 5*(1-data_TPF['w'][i]) for i in range(len(data_TPF['Pressure']))]
data_TPF['fLiq'] = [8*((8/data_TPF['ReLiq'][i])**12 + 1/((2.457*np.log(1/((7/data_TPF['ReLiq'][i])**0.9 + 0.27*(roughness / Dh))))**16+(37530/data_TPF['ReLiq'][i])**16)**(3/2))**(1/12) for i in range(len(data_TPF['Pressure']))]
data_TPF['fVap'] = [8*((8/data_TPF['ReVap'][i])**12 + 1/((2.457*np.log(1/((7/data_TPF['ReVap'][i])**0.9 + 0.27*(roughness / Dh))))**16+(37530/data_TPF['ReVap'][i])**16)**(3/2))**(1/12) for i in range(len(data_TPF['Pressure']))]
data_TPF['FLiq'] = [data_TPF['fLiq'][i] * data_TPF['rhoLiq'][i] * data_TPF['VelzLiq'][i]*(1-data_TPF['Void'][i])**2 / (2*Dh) for i in range(len(data_TPF['Pressure']))]
data_TPF['FVap'] = [data_TPF['fVap'][i] * data_TPF['rhoVap'][i] * data_TPF['VelzVap'][i]*(1-data_TPF['Void'][i])**2 / (2*Dh) for i in range(len(data_TPF['Pressure']))]
data_TPF['FLV'] = [data_TPF['FLiq'][i]*data_TPF['VelzLiq'][i] + data_TPF['FVap'][i]*data_TPF['VelzVap'][i] + data_TPF['C_LM'][i]*(1-data_TPF['Void'][i])*data_TPF['Void'][i]*np.sqrt(data_TPF['fVap'][i] * data_TPF['fLiq'][i] * data_TPF['rhoLiq'][i] * data_TPF['rhoVap'][i])*data_TPF['VelzVap'][i]/(2*Dh) for i in range(len(data_TPF['Pressure']))]


""" for i in range(len(case2.convection_sol.U[-1])):
    print(f'index {i} :')
    print(case2.convection_sol.areaMatrix_1[-1][i])
    print(case2.convection_sol.areaMatrix_1[-1][i]/case2.convection_sol.areaMatrix)
    print(case2.convection_sol.Dz)
    print(case2.convection_sol.U[-1][i])
    print(case2.convection_sol.rho[-1][i])
    print(case2.convection_sol.U[-1][i]**2 * case2.convection_sol.rho[-1][i])
    print((case2.convection_sol.areaMatrix_1[-1][i]/case2.convection_sol.areaMatrix - 1)/case2.convection_sol.Dz)
    print((case2.convection_sol.areaMatrix_1[-1][i]/case2.convection_sol.areaMatrix - 1)/case2.convection_sol.Dz * (case2.convection_sol.U[-1][i]**2 * case2.convection_sol.rho[-1][i]))
 """

pressureDrop_THM = [(case2.convection_sol.areaMatrix_1[-1][i]/case2.convection_sol.flowArea - 1)/case2.convection_sol.Dz * (case2.convection_sol.U[-1][i]**2 * case2.convection_sol.rho[-1][i]) for i in range(len(case2.convection_sol.U[-1]))]
print(pressureDrop_THM)
print(f'Terme de chute de pression:')
for i in range(len(data_TPF['Pressure'])):
    print(f'TPF: {data_TPF["FLV"][i]} Pa, THM: {pressureDrop_THM[i]} Pa')
