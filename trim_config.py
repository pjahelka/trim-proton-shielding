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

PROTONS_SIMULATE = 1E2 #number of protons to fire in real experiment
PROTONS_TEST_TRANSMIT = 1E1 #number of particles for testing for full transmission
PROTONS_TEST_BLOCK = 1E1 #number of particles for testing for full blocking
SAFETY_IDX = 1 #how many energy indices to extend the interesting range. Just in case.
FULL_TRANSMIT_KE = 0.95 #how much kinetic energies the protons need to keep on average to count for perfect transmission

#angles of incidence
THETA_MIN = 0
THETA_MAX = 90
THETA_NUM = 10
ANGLES = np.linspace(THETA_MIN, THETA_MAX, THETA_NUM, endpoint = True)
ANGLES = [round(angle, 1) for angle in ANGLES]

SPECTRUM_ENERGIES_PER_DECADE = 20 #energies per decade for the incident protons. Affects number of TRIM simulations
DAMAGE_ENERGIES_PER_DECADE = 50  #energies per decade for discretizing damage. Computationally cheap.
#error tolerance for bisection search in units of array index
BISECT_IDX_TOL = 1

#how many data points to use for fitting the IR and UV power laws in extrapolating RDCs
POWER_LAW_FIT_POINTS = 4
#sigma for fitting IR and UV data
CURVE_FIT_SIGMA = 0.001

#conversion ratio for 10MeV protons to 1MeV electrons
POWER_PROTONS_TO_ELECTRONS = 1000

#config for importing a new spectrum
SPECTRA_FILES = [
        r"spectra\\15yr_geo_solar.txt",
        r"spectra\\15yr_geo_trapped.txt"
    ]
# lines in each file that mean we've gotten to real data lines
SOLAR_LAST_HEADER = r"'Exposure','hrs', 1,'Proton Exposure Time'"
TRAPPED_LAST_HEADER = r"'DFlux','cm!u-2!n s!u-1!n MeV!u-1!n', 1,'Differential Flux'"
TRAPPED_DURATION_LINE = 43 - 1  # line number of mission duration for trapped spectra. This may vary SPENVIS-run to SEPNVIS-run
# and the end of data line
FIRST_FOOTER = r"'End of Block'"
ENERGIES_PER_DECADE_IMPORT = 100