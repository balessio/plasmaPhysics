# plasmaPhysics
Collection of programs written for experimental plasma physics data analysis, June 2019-January 2020.
Sample of programs written during my internship and independent research on experimental plasma physics, June 2019-January 2020. Some dependencies were written by other lab members and are not included. 

compute_DP.py:
Extracts measurements from .mca files, which are outputted by the software interfacing the x-ray detector, and extracts calculated values from a spectral inversion script. Calculates additional derived parameters and organizes data into spreadsheets.

plot_DP.py:
Companion script to compute_DP.py for versatile plotting of derived parameters. Using the SETUP files, makes plot as specified.

plot_spectra_NOISE_SUBTRACT.py:
Plots measured x-ray spectra from .mca file and subtracts noise measurements.

check_empty_mca.py:
Simple script for eliminating empty data files from the collection after a day of experiments. Must be run before other scripts to prevent problems in data handling. 

MC_w_a.py:
Monte Carlo simulation for an electron beam emitting x-rays and being detected by our detector. Takes system parameters as input, gives an x-ray spectrum as output.

window_eff.py:
Calculates the efficiency of the window in front of the x-ray detector using transmission function and published structure data.

sim_window.py:
Takes x-ray spectra from Monte Carlo sim and incorporates the effect of the window. 

pi_sky.py:
Encryption scheme made for fun. Replaces every letter in the alphabet with three-number sequences from pi. Skips over repeat sequences, so that any irrational number can be used without degenerative alphabets. Takes a string as input, and outputs the encrypted version of the string.
