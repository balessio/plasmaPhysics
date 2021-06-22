#### author: balessio 
#### last updated 5 July 2019 by balessio
## this program extracts derived parameters from .mca files and 
## the forward fits (see cswanson matlab code),
## makes calculations, and organizes into .csv files
####
####

# for putting the data into a csv file
import csv
# for timing the program and working with file times
from datetime import datetime as dt
# for computations and convenient arrays
import numpy as np
# for convenient directory access
import os
# tools written by eevans for extracting metadata from mca files
import xrayinv

# time the program
start_time = dt.utcnow()

for SETUP in os.listdir('SETUP/compute_DP/'):
	E_cutoff_SDD1 = 0
	E_cutoff_SDD2 = 0
	if not('.txt' in SETUP): continue
	# read specifications from SETUP
	with open((os.path.join(os.path.dirname(__file__),
		'SETUP/compute_DP/'+SETUP)), 'r') as file:
		readlines = file.read().splitlines()
		cutoffChannel = int(readlines[3].split(':')[1])

	# arrays recording the metadata from each detector
	# includes file number, time of creation,  count rate,
	# count rate above the given channel,  Maxwellian-Fit electron temperature,
	# Maxwellian-Fit electron density
	form = [('file name',object),
		('time of creation',dt),
		('count rate',np.float32),
		('count rate error',np.float32),
		('count rate above threshold',np.float32),
		('count rate above threshold error',np.float32),
		('avg energy above threshold',np.float32),
		('avg energy above threshold error',np.float32),
		('Maxwellian-Fit electron temperature',np.float32),
		('Maxwellian-Fit electron density',np.float32)]
	SDD1 = []
	SDD2 = []

	# iterate through the folder with the data
	for dataFile in os.listdir('spectra/'):
		# check for proper file format (.mca)
		if (len(dataFile) < 4): continue
		if not('.mca' in dataFile[-4:]) or not('SDD' in dataFile): continue
		# extract from the .mca files
		xrayspectrum=xrayinv.XraySpectrum(xrayinv.MCAFile(os.path.join(
			os.path.dirname(__file__), 'spectra/' + dataFile)))
		energy_cal=np.array(xrayinv.CalData.energy_cal(xrayspectrum.serial,
			xrayspectrum.peaking,xrayspectrum.flattop)
			)*xrayinv.CalData.gain(xrayspectrum.serial)/xrayspectrum.gain

		# check for no accumulation
		if (xrayspectrum.accum == 0): continue
		# the count rate is given by the total count divided by the accumulated time
		countRate = xrayspectrum.slow_count / xrayspectrum.accum
		countRateError = np.sqrt(xrayspectrum.slow_count) / xrayspectrum.accum

		# time of creation
		fileTime = xrayspectrum.datetime

		# records the counts along each channel from the .mca file
		channelCounts = []
		# records the count beyond the specified cutoff channel
		channelCount = 0
		with open((os.path.join(os.path.dirname(__file__), 
			'spectra/' + dataFile)), 'rb') as read:
			readlines = read.readlines()
			# finds counts for all channels, in between lines '<<DATA>>'
			# and '<<END>>' in the .mca file
			collect = False
			for line in readlines:
				line = line.decode('utf-8',errors='ignore')
				if '<<END>>' in line: break
				if collect:
					channelCounts.append(int(line))
				if '<<DATA>>' in line:
					collect = True
		# sums the counts at or above the specified channel until the last channel
		lastChannel = len(channelCounts)
		# also calculate the average energy above this threshold 
		# minus the energy of the threshold channel
		energySum = 0
		if (lastChannel > cutoffChannel):
			channel = cutoffChannel
			while channel <= lastChannel:
				channelCount += channelCounts[channel-1]
				energyOfChannel = channel*energy_cal[1]+energy_cal[0]
				energySum += energyOfChannel * channelCounts[channel-1]
				channel += 1
		# count rate above the given channel
		channeledCountRate = channelCount / xrayspectrum.accum
		channeledCountRateError = np.sqrt(channelCount) / xrayspectrum.accum
		if (channelCount > 0):
			avgEaboveThreshold = (energySum / channelCount) - (
				cutoffChannel*energy_cal[1]+energy_cal[0])
			avgEaboveThresholdError = avgEaboveThreshold / np.sqrt(channelCount)
		else:
			avgEaboveThreshold = 0
			avgEaboveThresholdError = 0
			channeledCountRate = 0.0
			channeledCountRateError = 1.0 / xrayspectrum.accum

		# temperature and density from the forward-fit text files
		temperature, density = 0, 0
		for fFitFile in os.listdir('spectra/forward_fit/'):
			# match file numbers and find the text file
			if (('.txt' in fFitFile) and 
				(float(dataFile.split('-')[0]) == float(fFitFile.split('-')[0]))):
				with open(os.path.join(os.path.dirname(__file__), 
					'spectra/forward_fit/' + fFitFile), 'r') as read:
					readlines = read.readlines()
					# relies on the most current format of these text files
					temperature = float(readlines[1][2:])
					density = float(readlines[0][2:])/1000000000.0
					break

		# put data acquired into an inputtable row
		row = (dataFile,fileTime,countRate,countRateError,
			channeledCountRate,channeledCountRateError,avgEaboveThreshold,
			avgEaboveThresholdError,temperature,density)
		# check which detector before inputting the metadata
		if ('SDD1' in dataFile):
			SDD1.append(row)
			E_cutoff_SDD1 = cutoffChannel*energy_cal[1]+energy_cal[0]
		elif ('SDD2' in dataFile):
			SDD2.append(row)
			E_cutoff_SDD2 = cutoffChannel*energy_cal[1]+energy_cal[0]
			
	# convert to numpy arrays to put the data in order of time of creation
	npSDD1 = np.asarray(SDD1, dtype=form)
	npSDD2 = np.asarray(SDD2, dtype=form)
	npSDD1 = np.sort(npSDD1, order='time of creation')
	npSDD2 = np.sort(npSDD2, order='time of creation')

	# titles for columns of the .csv files
	titles_SDD1 = ['file name','time of creation','count rate (/s)','+/-',
		'count rate above threshold ' + str(round(E_cutoff_SDD1,1)) + ' eV (/s)','+/-',
		'avg energy above threshold ' + str(round(E_cutoff_SDD1,1)) + ' eV','+/-',
		'Maxwellian-Fit electron temperature (eV)',
		'Maxwellian-Fit electron density (10^9/cm^3)']
	titles_SDD2 = ['file name','time of creation','count rate (/s)','+/-',
		'count rate above threshold ' + str(round(E_cutoff_SDD2,1)) + ' eV (/s)','+/-',
		'avg energy above threshold ' + str(round(E_cutoff_SDD2,1)) + ' eV','+/-',
		'Maxwellian-Fit electron temperature (eV)',
		'Maxwellian-Fit electron density (10^9/cm^3)']

	# write the csv file for SDD1
	if not os.path.exists(os.path.join(os.path.dirname(__file__), 'OUTPUT/derived_parameters/')):
		os.makedirs(os.path.join(os.path.dirname(__file__), 'OUTPUT/derived_parameters/'))
	with open((os.path.join(os.path.dirname(__file__), 
		'OUTPUT/derived_parameters/' +SETUP[:-4]+'_SDD1.csv')), 'w', newline='') as csvFile:
		writer = csv.writer(csvFile)
		writer.writerow(titles_SDD1)
		for row in npSDD1:
	    	# format the time and add each element to the input
			writer.writerow([row[0],row[1].strftime('%H:%M'),
				row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9]])

	# write the csv file for SDD2
	with open((os.path.join(os.path.dirname(__file__), 
		'OUTPUT/derived_parameters/'+SETUP[:-4]+'_SDD2.csv')), 'w', newline='') as csvFile:
		writer = csv.writer(csvFile)
		writer.writerow(titles_SDD2)
		for row in npSDD2:
			# format the time and add each element to the input
			writer.writerow([row[0],row[1].strftime('%H:%M'),
				row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9]])
	print('\nData synchronized to:\n'+SETUP[:-4]+'_SDD1.csv\n'+SETUP[:-4]+'_SDD2.csv\n')
	# show the run_time in ms
end_time = dt.utcnow()
run_time = round(float((end_time - start_time).total_seconds())*1000, 5)
print('runtime = ' + str(run_time) + ' ms\n')
####
####