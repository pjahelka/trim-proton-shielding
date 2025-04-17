"""configuration for the program"""
import numpy as np
import os

#SiO2 thickness in um
shield_thickness = 5

#figure out file locations
script_dir = os.path.dirname(__file__)
trim_auto = os.path.join(script_dir, r"SRIM\TRIMAUTO")
trim_in = os.path.join(script_dir, r"SRIM\TRIM.IN")
trim_transmit = os.path.join(script_dir, r"SRIM\SRIM Outputs\TRANSMIT.txt")
#this link launches TRIM minimized which speeds it up a lot
trim_exec = os.path.join(script_dir, r"SRIM\TRIM_min.exe.lnk")

#file for the input proton spectrum. Run import_spectra to generate
proton_spectrum_file = r'spectra//combined_spectra.csv'

damage_min_energy = 0.001#minimum energy for calculating proton damage. max is calculated in trim_helper

particle_number = 1E4 #number of protons to fire in real experiment
number_test_transmit = 1E1 #number of particles for testing for full transmission
number_test_block = 1E1 #number of particles for testing for full blocking
safety_idx = 2 #how many energy indices to extend the interesting range. Just in case.


#angles of incidence
theta_min = 0
theta_max = 90
theta_num = 4
angles = np.linspace(theta_min, theta_max, theta_num, endpoint = True)
angles = [round(angle,1) for angle in angles]

energies_per_decade = 2 #how many energies to run per decade of energy that is interesting

#error tolerance for bisection search in units of array index
bisect_idx_tol = 1


