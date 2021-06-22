from datetime import datetime as dt
import os
import v5.python.xrayinv as xrayinv

start_time = dt.utcnow()

for dataFile in os.listdir('spectra/'):
	# check for proper file format (.mca)
	if ('.mca' in dataFile) and not('tmp' in dataFile):
		# extract from the .mca files
		xrayspectrum=xrayinv.XraySpectrum(xrayinv.MCAFile(os.path.join(
			os.path.dirname(__file__), 'spectra/' + dataFile)))
		if xrayspectrum.slow_count == 0: print('no data in file #' + str(dataFile.split('-')[0]))

end_time = dt.utcnow()
run_time = round(float((end_time - start_time).total_seconds())*1000, 5)
print('\nruntime: '+str(run_time)+' ms\n')