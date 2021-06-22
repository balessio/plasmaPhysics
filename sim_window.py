import csv
import numpy as np 
import matplotlib.pyplot as plt 
import os
import random


filename = 'pulse750000tau_I0_01nA_rec'
pulse = 750000


E_levels = np.full(500-3,-15.086) + 8.5025*np.array(range(3,500))
pulses = np.zeros((pulse,E_levels.size))

# converts strings of the form '#E#' to float for arbitrary numbers '#'
def to_float(string_in = '1E-1'):
	num_pow = string_in.split('E')
	return float(num_pow[0])*(10**float(num_pow[1]))

def plot_XEDF(XEDF = np.zeros(E_levels.size), xLabel = 'Energy (eV)', yLabel = '# of photons',
	plotTitle = 'XEDF', shouldLog = True):
	plt.rc('font', family='serif',serif = "cmr10", size=20)
	plt.rcParams['mathtext.fontset']='cm'
	plt.figure(figsize=(10,6))
	plt.errorbar(E_levels, XEDF, linewidth=3, color='r')
	plt.ylabel(yLabel)
	plt.xlabel(xLabel)
	plt.title(plotTitle)
	if (shouldLog): plt.yscale('log')
	plt.tight_layout(pad=0)
	plt.grid(linestyle='--')
	plt.show()

effs = [0]*E_levels.size

with open((os.path.join(os.path.dirname(__file__),
		'window_effs/effs_Amptek_C1_calcVpub.csv')), 'r') as file:
	rows = csv.reader(file)
	i=0
	a=0
	for row in rows:
		if a==0:
			a=1
			continue
		effs[i] = row[1]
		i+=1
#print(effs[0])


with open((os.path.join(os.path.dirname(__file__),
		'simulated_spectra/'+filename+'.csv')), 'r') as file:
	rows = csv.reader(file)
	i = 0
	a = 0
	for row in rows:
		if a==0:
			a = 1
			continue
		pulses[i] = row[1:]
		i+=1

XEDF = [0]*E_levels.size
for row in pulses:
	pile = 0
	for i in range(len(row)):
		if row[i]==0: continue
		eff = 0
		if 'E' in effs[i]:
			eff = to_float(effs[i])
		else: 
			eff = float(effs[i])
		if np.random.random_sample() < eff:
			pile+=int(i*row[i])
	if not pile == 0:
		XEDF[pile] += 1

plot_XEDF(XEDF)

