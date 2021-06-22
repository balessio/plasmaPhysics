import numpy as np 
import os
import csv
import matplotlib.pyplot as plt
import time

# gives a parallel lists: [nergy_i in eV, ...] and [attenutaion coefficient_i in cm^2/g,...]
def atten_coeffs(element = 'Al'):
	with open((os.path.join(os.path.dirname(__file__),
		'atten_coeffs/mus-NIST-FFAST-'+element+'.txt')), 'r') as file:
		readlines = file.read().splitlines()
		enrg = [0]*len(readlines)
		coeff = [0]*len(readlines)
		for i in range(len(readlines)):
			split = readlines[i].split('  ') # two-space separation
			enrg[i] = to_float(split[0])*1000
			coeff[i] = to_float(split[1])
	return enrg, coeff

# converts strings of the form '#E#' to float for arbitrary numbers '#'
def to_float(string_in = '1E-1'):
	num_pow = string_in.split('E')
	return float(num_pow[0])*(10**float(num_pow[1]))

# calculates efficiency of a layer
def efficiency(coeffs = [], dens = 1, thick = 1, mass_portion = 1):
	return np.exp(-1*np.array(coeffs)*dens*thick*mass_portion)

with open((os.path.join(os.path.dirname(__file__),
	'atten_coeffs/C1C2Eff_pub.txt')), 'r') as file_p:
	readlines_p = file_p.read().splitlines()
	enrg_p = [0]*len(readlines_p)
	coeff_p = [0]*len(readlines_p)
	for i in range(len(readlines_p)):
		split_p = readlines_p[i].split('\t') # four-space separation
		enrg_p[i] = to_float(split_p[0])*1000
		coeff_p[i] = to_float(split_p[1])

def plot_eff(enrgs = np.zeros(2), eff = np.zeros(2), xLabel = 'Energy (eV)',
	yLabel = 'Efficiency (%)', plotTitle = 'Efficiency of Amptek C1 window'):
	plt.rc('font', family='serif',serif = "cmr10", size=20)
	plt.rcParams['mathtext.fontset']='cm'
	plt.figure(figsize=(10,6))
	plt.errorbar(enrgs, eff*100, linewidth=3, color='r', label='calculated')
	#plt.errorbar(enrg_p, np.array(coeff_p)*100, linewidth=3, color='b', label='published')
	#plt.legend(loc='best')
	plt.ylabel(yLabel)
	plt.xlabel(xLabel)
	plt.title(plotTitle)
	plt.ylim(top = 100, bottom = 0)
	plt.xlim(left = 0, right = 5000)
	plt.tight_layout(pad=0)
	plt.grid(linestyle='--')
	plt.show()

def CSV_eff(eff = np.zeros(2), saveTitle = 'save'+str(time.time())):
	if not os.path.exists(os.path.join(os.path.dirname(__file__), 'window_effs/')):
		os.makedirs(os.path.join(os.path.dirname(__file__), 'window_effs/'))
	with open((os.path.join(os.path.dirname(__file__), 
		'window_effs/'+saveTitle+'.csv')), 'w', newline='') as csvFile:
		writer = csv.writer(csvFile)
		writer.writerow(['Energy level (eV)','C1 number transmission efficiency'])
		for i in range(0,E_levels.size):
			writer.writerow([E_levels[i],effs[i]])

# Aluminum data for Al coating
enrg_Al, coeff_Al = atten_coeffs('Al')
dens_Al = 2.7 # g/cc
thick_Al = 0.000025 # cm
mass_portion_Al = 1

# Silicon data for Silicon Nitride (Si3N4) layer
enrg_Si, coeff_Si = atten_coeffs('Si')
dens_Si = 3.44 # g/cc
thick_Si = 0.000015 # cm
mass_portion_Si = 0.6006
# Silicon grid
dens_grid = 2.33 # g/cc
thick_grid = 0.0015 # cm
mass_portion_grid = 1

# Nitrogen data for Silicon Nitride (Si3N4) layer
enrg_N, coeff_N = atten_coeffs('N')
dens_N = 3.44 # g/cc
thick_N = 0.000015 # cm

mass_portion_N = 0.3994

####################################################

E_levels = np.full(500-3,-15.086) + 8.5025*np.array(range(3,500))
coeff_interp_Al = np.interp(E_levels, enrg_Al, coeff_Al)
coeff_interp_Si = np.interp(E_levels, enrg_Si, coeff_Si)
coeff_interp_N = np.interp(E_levels, enrg_N, coeff_N)

eff_Al = efficiency(coeffs = coeff_interp_Al, dens = dens_Al,
	thick = thick_Al, mass_portion = mass_portion_Al)
eff_Si = efficiency(coeffs = coeff_interp_Si, dens = dens_Si,
	thick = thick_Si, mass_portion = mass_portion_Si)
eff_N = efficiency(coeffs = coeff_interp_N, dens = dens_N,
	thick = thick_N, mass_portion = mass_portion_N)
eff_grid = efficiency(coeffs = coeff_interp_Si, dens = dens_grid,
	thick = thick_grid, mass_portion = mass_portion_grid)

effs = eff_Al * eff_Si * eff_N * (0.78 + (0.22*eff_grid))

plot_eff(enrgs = E_levels, eff = effs)
#CSV_eff(eff = effs, saveTitle = 'effs_Amptek_C1_calcVpub')
