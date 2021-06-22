import matplotlib.pyplot as plt
from datetime import datetime as dt
import numpy as np
import os
import xrayinv

for SETUP in os.listdir('SETUP/plot_spectra/'):
	if not('.txt' in SETUP): continue
	# read specifications from SETUP
	with open((os.path.join(os.path.dirname(__file__), 'SETUP/plot_spectra/'+SETUP)), 'r') as file:
		readlines = file.read().splitlines()
		spectraFiles = readlines[5].split(',')
		labels = readlines[7].split(',')
		rescalings = []
		for x in readlines[9].split(','):
			if ('None' in x): rescalings.append(1.0)
			else: rescalings.append(float(x))
		shouldLog = True
		if not('Yes' in readlines[11]): shouldLog = False
		plotLimits = readlines[13].split(',')
		yLabel = readlines[15]
		xLabel = readlines[17]
		plotTitle = readlines[19]
		shouldSave = False
		if ('Save' in readlines[21]): shouldSave = True

	spectra = {}
	for file in os.listdir('spectra/'):
		num = 0
		if ('.mca' in file) and not('tmp' in file):
			num = file.split('-')[0]
			if ('noise' in file):
				noise_file = num
			spec = np.array([0])
			enrg = np.array([0])
			xrayspectrum=xrayinv.XraySpectrum(xrayinv.MCAFile(os.path.join(
				os.path.dirname(__file__), 'spectra/' + file)))
			spec = np.append(spec, xrayspectrum.channels)
			enrg = np.append(enrg, xrayspectrum.energies)
			spectra[num] = (enrg, spec)


	plt.rc('font', family='serif',serif = "cmr10", size=20)
	plt.rcParams['mathtext.fontset']='cm'
	plt.figure(figsize=(10,6))

	for (file,rescale,label) in zip(spectraFiles,rescalings,labels):
		if not (noise_file in file):
			noise_array = np.array(spectra[noise_file][1])
			data_array = np.array(spectra[file][1])
			noise_array = np.append(noise_array,np.zeros(data_array.size-noise_array.size))
			y_variable = data_array - noise_array
			plt.errorbar(np.array(spectra[file][0]), rescale*y_variable, linewidth=1, label=label, color='orange')

	if not('None' in plotLimits[0]): 
		plt.xlim(left=float(plotLimits[0]))
	if not('None' in plotLimits[1]): 
		plt.xlim(right=float(plotLimits[1]))
	if not('None' in plotLimits[2]): 
		plt.ylim(bottom=float(plotLimits[2]))
	if not('None' in plotLimits[3]): 
		plt.ylim(top=float(plotLimits[3]))
	plt.ylabel(yLabel)
	plt.xlabel(xLabel)
	plt.title(plotTitle)
	plt.legend(loc='best')
	if (shouldLog): plt.yscale('log')
	plt.tight_layout(pad=0)
	plt.grid(linestyle='--')
	if not os.path.exists(os.path.join(os.path.dirname(__file__), 'OUTPUT/plots/spectra_plots/')):
		os.makedirs(os.path.join(os.path.dirname(__file__), 'OUTPUT/plots/spectra_plots/'))
	if (shouldSave):
		plt.savefig(os.path.join(os.path.dirname(__file__),
			'OUTPUT/plots/spectra_plots/'+SETUP[:-4]+'.pdf'))
		print('created: '+SETUP[:-4]+'.pdf')
	else: plt.show()
