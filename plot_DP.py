####
## balessio
## last updated 22 July 2019
## paired with compute_DP.py
## (relies on the format of .csv files from that script)
####
import matplotlib.pyplot as plt 
import csv
from datetime import datetime as dt
import numpy as np
import os
import xrayinv

# read specifications from SETUP/
for SETUP in os.listdir('SETUP/plot_DP/'):
	if not('.txt' in SETUP): continue
	# read specifications from SETUP
	with open((os.path.join(os.path.dirname(__file__),
		'SETUP/plot_DP/'+SETUP)), 'r') as file:
		readlines = file.read().splitlines()
		spectraFiles = readlines[5].split(',')
		indepVar = readlines[7].split(',')
		lineGroupFiles = []
		lineGroupIndepVar = []
		lineGroupLabels = []
		if ('None' in readlines[9]):
			lineGroupFiles = [spectraFiles]
			lineGroupIndepVar = [indepVar]
			for i in range(0,len(lineGroupFiles)): lineGroupLabels.append('')
		else:
			holder = readlines[9].split('?')
			for a in holder:
				group = a.split(',')
				lineGroupLabels.append(group[0])
				lineGroupFiles.append(group[1:])
				x = []
				for fileNum in group[1:]:
					x.append(indepVar[spectraFiles.index(fileNum)])
				lineGroupIndepVar.append(x)
		fileNameSDD1 = readlines[11]
		fileNameSDD2 = readlines[13]
		yLabel = readlines[15]
		xLabel = readlines[17]
		plotTitle = readlines[19]
		shouldLog = False
		if ('Yes' in readlines[21]): shouldLog = True
		msrmntCol = readlines[23].split(',')
		for i in range(0,len(msrmntCol)): msrmntCol[i] = int(msrmntCol[i])
		errorCol = []
		for x in msrmntCol: errorCol.append(0)
		rescalings = readlines[25].split(',')
		for i in range(0,len(rescalings)):
			if not('None' in rescalings[i]): rescalings[i] = float(rescalings[i])
			else: rescalings[i] = 1.0
		fmt = ''
		if ('Yes' in readlines[27]): fmt = 'o'
		plotLimits = readlines[29].split(',')
		shouldSave = False
		if ('Save' in readlines[31]): shouldSave = True

	dpSDD1 = {}
	dpSDD2 = {}

	with open(os.path.join(os.path.dirname(__file__),
		'OUTPUT/derived_parameters/'+fileNameSDD1+'.csv')) as file:
		read = csv.reader(file, delimiter=',')
		titleRowOn = True
		for row in read:
			if not(titleRowOn): 
				num = str(row[0]).split('-')[0]
				for x,f in zip(indepVar,spectraFiles):
					if (num == f):
						dpSDD1[round(float(x),32)] = row
			else:
				titleRowOn = False
				titleRow = row
				for i in range(0,len(msrmntCol)):
					if (msrmntCol[i] < len(row)-1):
						if ('+/-' in row[msrmntCol[i]+1]):
							errorCol[i] = msrmntCol[i]+1

	with open(os.path.join(os.path.dirname(__file__),
		'OUTPUT/derived_parameters/'+fileNameSDD2+'.csv')) as file:
		read = csv.reader(file, delimiter=',')
		titleRowOn = True
		for row in read:
			if not(titleRowOn): 
				num = str(row[0]).split('-')[0]
				for x,f in zip(indepVar,spectraFiles):
					if (num == f):
						dpSDD2[round(float(x),32)] = row
			else:
				titleRowOn = False
				titleRow = row
				for i in range(0,len(msrmntCol)):
					if (msrmntCol[i] < len(row)-1):
						if ('+/-' in row[msrmntCol[i]+1]):
							errorCol[i] = msrmntCol[i]+1

	plt.rc('font', family='serif',serif = "cmr10", size=20)
	plt.rcParams['mathtext.fontset']='cm'
	plt.figure(figsize=(10,6))

	xVarSDD1 = sorted(dpSDD1)
	xVarSDD2 = sorted(dpSDD2)

	for fileNums, label in zip(lineGroupFiles, lineGroupLabels):
		for c,d in zip(msrmntCol,errorCol):
			yVar = []
			yErr = []
			xVar = []
			for x in xVarSDD1:
				row = dpSDD1[round(float(x),32)]
				if (row[0].split('-')[0] in fileNums):
					yVar.append(float(row[c]))
					xVar.append(float(x))
					if (d == 0): yErr.append(0)
					else: yErr.append(float(row[d]))
			yVar = np.array(yVar)
			xVar = np.array(xVar)
			yErr = np.array(yErr)
			for factor,msrmnt in zip(rescalings,msrmntCol):
				if (c == msrmnt):
					yVar = factor*np.array(yVar)
					yErr = factor*np.array(yErr)
					if not(factor == 1.0) and not(('times '+str(factor)) in titleRow[c]):
						titleRow[c]+=', times '+str(factor)
			if (yVar.any()):
				plt.errorbar(xVar, yVar, yerr=yErr, linewidth=2,
					fmt=fmt, label=label+' SDD1 '+titleRow[c])
			yVar = []
			yErr = []
			xVar = []
			for x in xVarSDD2:
				row = dpSDD2[round(float(x),32)]
				if (row[0].split('-')[0] in fileNums):
					yVar.append(float(row[c]))
					xVar.append(float(x))
					if (d == 0): yErr.append(0)
					else: yErr.append(float(row[d]))
			yVar = np.array(yVar)
			xVar = np.array(xVar)
			yErr = np.array(yErr)
			for factor,msrmnt in zip(rescalings,msrmntCol):
				if (c == msrmnt):
					yVar = factor*np.array(yVar)
					yErr = factor*np.array(yErr)
					if not(factor == 1.0) and not(('times '+str(factor)) in titleRow[c]):
						titleRow[c]+=', times '+str(factor)
			if (yVar.any()):
				plt.errorbar(xVar, yVar, yerr=yErr, linewidth=2,
					fmt=fmt, label=label+' SDD2 '+titleRow[c])

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
	plt.legend(loc='best', prop={'size': 12})
	if (shouldLog): plt.yscale('log')
	plt.tight_layout(pad=0)
	plt.grid(linestyle='--')
	if not os.path.exists(os.path.join(
		os.path.dirname(__file__), 'OUTPUT/plots/derived_parameter_plots/')):
		os.makedirs(os.path.join(os.path.dirname(__file__), 'OUTPUT/plots/derived_parameter_plots/'))
	if (shouldSave):
		plt.savefig(os.path.join(os.path.dirname(__file__),
			'OUTPUT/plots/derived_parameter_plots/'+SETUP[:-4]+'.pdf'))
		print('created: '+SETUP[:-4]+'.pdf')
	else: plt.show()
