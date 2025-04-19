"""configuration for the program"""
import numpy as np
import os

#SiO2 thickness in um
SHIELD_THICKNESS = 20

#figure out file locations
SCRIPT_DIR = os.path.dirname(__file__)
TRIM_AUTO = os.path.join(SCRIPT_DIR, r'SRIM\TRIMAUTO')
TRIM_IN = os.path.join(SCRIPT_DIR, r'SRIM\TRIM.IN')
TRIM_TRANSMIT = os.path.join(SCRIPT_DIR, r'SRIM\SRIM Outputs\TRANSMIT.txt')
#this link launches TRIM minimized which speeds it up a lot
TRIM_EXEC = os.path.join(SCRIPT_DIR, r'SRIM\TRIM_min.exe.lnk')

#file for the input proton spectrum. Run import_spectra to generate
PROTON_SPECTRUM_FILE = r'spectra//combined_spectra.csv'
#file for saving the scattering matrix
SCATTERING_MATRIX_FILE = 'scattering_matrix.npy'

#file for the proton RDC
PROTON_RDC_FILE = r'RDCs\gaas_proton_efficiency.csv'

PROTONS_SIMULATE = 1E3 #number of protons to fire in real experiment
PROTONS_TEST_TRANSMIT = 1E2 #number of particles for testing for full transmission
PROTONS_TEST_BLOCK = 1E2 #number of particles for testing for full blocking
SAFETY_IDX = 0 #how many energy indices to extend the interesting range. Just in case.
FULL_TRANSMIT_KE = 0.95 #how much kinetic energies the protons need to keep on average to count for perfect transmission

#angles of incidence
THETA_MIN = 0
THETA_MAX = 90
THETA_NUM = 4
ANGLES = np.linspace(THETA_MIN, THETA_MAX, THETA_NUM, endpoint = True)
ANGLES = [round(angle, 1) for angle in ANGLES]

SPECTRUM_ENERGIES_PER_DECADE = 5 #energies per decade for the incident protons. Affects number of TRIM simulations
DAMAGE_ENERGIES_PER_DECADE = 20  #energies per decade for discretizing damage. Computationally cheap.
#error tolerance for bisection search in units of array index
BISECT_IDX_TOL = 1

#how many data points to use for fitting the IR and UV power laws in extrapolating RDCs
POWER_LAW_FIT_POINTS = 4
#sigma for fitting IR and UV data
CURVE_FIT_SIGMA = 0.01