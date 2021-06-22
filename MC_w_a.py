# balessio
# last updated 20200103

import numpy as np
import matplotlib.pyplot as plt
import time
import os
import csv

start_time = time.time()

pulse = 5000 # number of SDD window durations to simulate over
I_fac = 1 # factor by which to multiply 1 nA
save_title = 'pulse5000tau_I1nA'

# NOTE: SDD2, PT = 1us FT = 12ns: offset = -15.0860 eV, multiplier = 8.5025
# E_levels spans from channel 2 (10.4215 eV ~ 10 eV) to channel 120 (1005.214 eV ~ 1 keV)
# needed constants
c = 2.99792*(10**8) # m/s
epsilon_0 = 8.85418781*(10**(-12)) # F/m
h = 6.626*(10**(-34)) # Js
e_charge = 1.602*(10**(-19)) # C
m_e = 9.109383632*(10**(-31))  # kg
r_e = 2.81794033*(10**(-15)) # m
n_graphite = 1.136*(10**(29)) # /m^3
fsc = 0.00729735257 # fine structure constant
Z = 6 # atomic number of Carbon

# needed parameters
PT = 10**(-6) # s
FW = 12*(10**(-9)) # s
tau = (2*PT + FW)
accum = pulse*tau
I = I_fac*(10**(-9)) # A
detector_area = 17 # mm^2
x = 20 # distance from target to SDD, in cm

E_levels = np.full(121-3,-15.086) + 8.5025*np.array(range(3,121))
E_interval = E_levels[E_levels.size-1]-E_levels[E_levels.size-2]
#print(np.searchsorted(E_levels, 300))
E_levels_complete = np.full(500-3,-15.086) + 8.5025*np.array(range(3,500))
# classical Gaunt factor, must input energy bins for transmission between
def Gaunt(bin_1 = 1, bin_2 = 2):
	# calculations
	E_1 = E_levels[bin_1]
	E_2 = E_levels[bin_2]
	if (E_2 >= E_1):
		return 0.0
	nu_1 = (8*c*epsilon_0*(h**3)*E_1/((Z**2)*m_e*(e_charge**4)))**(-2)
	nu_2 = (8*c*epsilon_0*(h**3)*E_2/((Z**2)*m_e*(e_charge**4)))**(-2)
	G = ((3**(0.5))/np.pi)*(nu_2/nu_1)*((1-np.exp(-2*np.pi*nu_1))/(1-np.exp(
		-2*np.pi*nu_2)))*np.log((nu_2+nu_1)/(nu_2-nu_1))
	return G

#P = np.zeros((E_levels.size, E_levels.size))
P = [[0]*E_levels.size]*E_levels.size
for i in range(1, E_levels.size):
	gaunt_factors = np.zeros(E_levels.size)
	for j in range(0, E_levels.size):
		gaunt_factors[j] = Gaunt(i, j)
	sum_gaunt = np.sum(gaunt_factors)
	probabilities = gaunt_factors/sum_gaunt
	P[i] = list(probabilities)
# P[0] is full of zeros, P[i] is a parallel array to E_levels
# P[i][j] is the probability of going from bin i to j
# which is zero if j > i

# assign each transmission to a range on the number line
# and use a uniform random variable to pick the transmission
# until the electron is out of energy
# when considering pulse pileup, record each x-ray if
# another random variable hits a value with probability of the solid angle
# if multiple do from the same electron, add their energies to make one x-ray
# also consider window transmission and valence-electron slowing-down

# gives the probabilistically picked (int-valued) bin transmitted to,
# given the ordered array of probabilities P[j] for the current bin j
# input array must sum to 1
def Transmission(ind = 1):
	if (ind < 2): return 0
	spread = 0
	r = np.random.random_sample()
	for i in range(0, ind):
		spread += P[ind][i]
		if (r < spread): return i

def plot_XEDF(XEDF = np.zeros(E_levels_complete.size), xLabel = 'Energy (eV)', yLabel = '# of photons',
	plotTitle = 'XEDF', shouldLog = True):
	plt.rc('font', family='serif',serif = "cmr10", size=20)
	plt.rcParams['mathtext.fontset']='cm'
	plt.figure(figsize=(10,6))
	plt.errorbar(E_levels_complete, XEDF, linewidth=3)
	plt.ylabel(yLabel)
	plt.xlabel(xLabel)
	plt.title(plotTitle)
	if (shouldLog): plt.yscale('log')
	plt.tight_layout(pad=0)
	plt.grid(linestyle='--')
	plt.show()

def plot_XEDF_multiple(XEDF = [np.zeros(E_levels_complete.size)], xLabel = 'Energy (eV)', 
	yLabel = '# of photons', plotTitle = 'XEDF', shouldLog = True, labels = ['1 nA'],
	saveTitle = 'save'+str(time.time())):
	plt.rc('font', family='serif',serif = "cmr10", size=20)
	plt.rcParams['mathtext.fontset']='cm'
	plt.figure(figsize=(10,6))
	for xx, lab in zip(XEDF, labels):
		plt.errorbar(E_levels_complete, xx, linewidth=3, label = lab)
	plt.xlim(right=3500.0)
	plt.ylabel(yLabel)
	plt.xlabel(xLabel)
	plt.title(plotTitle)
	plt.legend(loc='best')
	if (shouldLog): plt.yscale('log')
	plt.tight_layout(pad=0)
	plt.grid(linestyle='--')
	if not (saveTitle == 'None'):
		if not os.path.exists(os.path.join(os.path.dirname(__file__), 'simulated_spectra/')):
			os.makedirs(os.path.join(os.path.dirname(__file__), 'simulated_spectra/'))
		plt.savefig(os.path.join(os.path.dirname(__file__), 'simulated_spectra/'+saveTitle+'.pdf'))
	else: plt.show()

def CSV_spec(XEDF = [np.zeros(E_levels_complete.size)], saveTitle = 'save_spec'+str(time.time())):
	if not os.path.exists(os.path.join(os.path.dirname(__file__), 'simulated_spectra/')):
		os.makedirs(os.path.join(os.path.dirname(__file__), 'simulated_spectra/'))
	with open((os.path.join(os.path.dirname(__file__), 
		'simulated_spectra/'+saveTitle+'.csv')), 'w', newline='') as csvFile:
		writer = csv.writer(csvFile)
		writer.writerow(['Energy level (eV)','XEDF with pileups','XEDF no pileups'])
		for i in range(0,XEDF[0].size):
			writer.writerow([E_levels_complete[i],XEDF[0][i],XEDF[1][i]])

def CSV_record(rec = np.zeros((2,2)), saveTitle = 'save_rec'+str(time.time())):
	if not os.path.exists(os.path.join(os.path.dirname(__file__), 'simulated_spectra/')):
		os.makedirs(os.path.join(os.path.dirname(__file__), 'simulated_spectra/'))
	with open((os.path.join(os.path.dirname(__file__), 
		'simulated_spectra/'+saveTitle+'.csv')), 'w', newline='') as csvFile:
		writer = csv.writer(csvFile)
		writer.writerow(np.append(['Energy level (eV)'], E_levels_complete))
		for i in range(0, pulse):
			writer.writerow(np.append(['pulse #'+str(i+1)], rec[i]))

# EEDF
eedf = [0]*E_levels.size
# for monoenergetic electron beam 1 keV
#eedf[E_levels.size-1] = int(I*accum/e_charge)
eedf[E_levels.size-1] = int(I*accum/e_charge)
print('total # of electrons in beam: '+str(sum(eedf)))
# XEDF
xedf = [0]*E_levels_complete.size

# probability that any x-ray hits the detector
prob_det = detector_area/(4*np.pi*100*(x**2))

e_in_pulse = int(I*tau/e_charge)
print('# electrons per pulse: '+str(e_in_pulse))

# MC
# i - Transmission(M[j]) gives the energy bin of the emitted X-ray
record = np.zeros((pulse, E_levels_complete.size))
which_pulse = 1
for i in range(E_levels.size-1, 0, -1):
	electrons = int(eedf[i])
	if (electrons == 0):
		continue
	grouped = 1
	pileups = 0
	for electron in range(0, electrons):
		cur_bin = i
		while (cur_bin > 0):
			new_bin = Transmission(cur_bin)
			if (np.random.random_sample() <= prob_det):
				pileups += cur_bin - new_bin
				record[which_pulse-1][cur_bin-new_bin] += 1
			cur_bin = new_bin
		if ((pileups > 0) and (grouped >= e_in_pulse) and (pileups < E_levels_complete.size)):
			xedf[pileups] += 1
		if (grouped > e_in_pulse):
			which_pulse += 1
			grouped = 0
			pileups = 0
		grouped += 1
	eedf[i]=0

########## hastily added
# EEDF
eedf = [0]*E_levels.size
# for monoenergetic electron beam 1 keV
#eedf[E_levels.size-1] = int(I*accum/e_charge)
eedf[E_levels.size-1] = int(I*accum/e_charge)
# XEDF
xedf_b = [0]*E_levels_complete.size

# MC
# i - Transmission(M[j]) gives the energy bin of the emitted X-ray
for i in range(E_levels.size-1, 0, -1):
	electrons = int(eedf[i])
	if (electrons == 0):
		continue
	for electron in range(0, electrons):
		cur_bin = i
		while (cur_bin > 0):
			new_bin = Transmission(cur_bin)
			xedf_b[cur_bin - new_bin] += 1
			cur_bin = new_bin
	eedf[i]=0

#############

print('time: '+str(time.time()-start_time)+'s')

plot_XEDF_multiple([xedf, prob_det*np.array(xedf_b)], 
	plotTitle = 'Simulated Bremsstrahlung Spectrum', labels = ['pileup', 'no pileup'],
	saveTitle = save_title)

CSV_spec(XEDF = [np.array(xedf), prob_det*np.array(xedf_b)], saveTitle = save_title+'_spec')
CSV_record(rec = record, saveTitle = save_title+'_rec')
