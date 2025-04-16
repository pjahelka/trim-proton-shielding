"""configuration for the program"""
import numpy as np
import os

#SiO2 thickness in um
shield_thickness = 2

#figure out file locations
script_dir = os.path.dirname(__file__)
trim_auto = os.path.join(script_dir, r"SRIM\TRIMAUTO")
trim_in = os.path.join(script_dir, r"SRIM\TRIM.IN")
trim_transmit = os.path.join(script_dir, r"SRIM\SRIM Outputs\TRANSMIT.txt")
trim_exec = os.path.join(script_dir, r"SRIM\TRIM_min.exe.lnk")

#file for the input proton spectrum. Run import_spectra to generate
proton_spectrum_file = r'spectra//combined_spectra.csv'

particle_number = 1E4 #number of protons to fire in real experiment
number_test_transmit = 1E4 #number of particles for testing for full transmission
number_test_block = 1E4 #number of particles for testing for full blocking


#angles of incidence
theta_min = 0
theta_max = 90
theta_num = 20
angles = np.linspace(theta_min, theta_max, theta_num, endpoint = False)
angles = [round(angle,1) for angle in angles]

energies_per_decade = 10 #how many energies to run per decade of energy that is interesting

#error tolerance for bisection search in units of array index
bisect_idx_tol = 1


