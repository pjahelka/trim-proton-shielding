"""Load configuration for the program and compute the grids"""
import configparser
from pathlib import Path
import numpy as np
import import_spectra
import pandas as pd
import numerics
#set up useful globals
SETTINGS = {}
ANGLES = []
SIMULATED_SPECTRUM = []
DAMAGE_ENERGIES = []

def read_config(config_file):
    """read a config file into the settings dictionary"""
    global SETTINGS
    config = configparser.ConfigParser()
    config.read(config_file)
    SETTINGS['SRIM_PATH'] = Path(config['File Paths']['SRIM_PATH'])
    SETTINGS['PROTON_SPECTRUM_FILE'] = Path(config['File Paths']['PROTON_SPECTRUM_FILE'])
    SETTINGS['SCATTERING_FILE_PATH'] = Path(config['File Paths']['SCATTERING_FILE_PATH'])
    SETTINGS['PROTON_RDC_FILE'] = Path(config['File Paths']['PROTON_RDC_FILE'])
    SETTINGS['SHIELD_THICKNESS'] = config['Shielding'].getfloat('SHIELD_THICKNESS')
    SETTINGS['PROTONS_SIMULATE'] = config['TRIM Config'].getint('PROTONS_SIMULATE')
    SETTINGS['PROTONS_TEST_TRANSMIT'] = config['TRIM Config'].getint('PROTONS_TEST_TRANSMIT')
    SETTINGS['PROTONS_TEST_BLOCK'] = config['TRIM Config'].getint('PROTONS_TEST_BLOCK')
    SETTINGS['SAFETY_IDX'] = config['TRIM Config'].getint('SAFETY_IDX')
    SETTINGS['FULL_TRANSMIT_KE'] = config['TRIM Config'].getfloat('FULL_TRANSMIT_KE')
    SETTINGS['THETA_MIN'] = config['TRIM Config'].getfloat('THETA_MIN')
    SETTINGS['THETA_MAX'] = config['TRIM Config'].getfloat('THETA_MAX')
    SETTINGS['THETA_NUM'] = config['TRIM Config'].getint('THETA_NUM')
    SETTINGS['SPECTRUM_ENERGIES_PER_DECADE'] = config['TRIM Config'].getint('SPECTRUM_ENERGIES_PER_DECADE')
    SETTINGS['DAMAGE_ENERGIES_PER_DECADE'] = config['Numerics'].getint('DAMAGE_ENERGIES_PER_DECADE')
    SETTINGS['ENERGIES_PER_DECADE_IMPORT'] = config['Numerics'].getint('ENERGIES_PER_DECADE_IMPORT')
    SETTINGS['BISECT_IDX_TOL'] = config['Numerics'].getint('BISECT_IDX_TOL')
    SETTINGS['POWER_LAW_FIT_POINTS'] = config['Numerics'].getint('POWER_LAW_FIT_POINTS')
    SETTINGS['CURVE_FIT_SIGMA'] = config['RDC'].getfloat('CURVE_FIT_SIGMA')
    SETTINGS['PROTONS_TO_ELECTRONS'] = config['RDC'].getfloat('PROTONS_TO_ELECTRONS')
    SETTINGS['SOLAR_LAST_HEADER'] = config['Spectra Import']['SOLAR_LAST_HEADER']
    SETTINGS['TRAPPED_LAST_HEADER'] = config['Spectra Import']['TRAPPED_LAST_HEADER']
    SETTINGS['FIRST_FOOTER'] = config['Spectra Import']['FIRST_FOOTER']
    SETTINGS['TRAPPED_DURATION_LINE'] = config['Spectra Import'].getint('TRAPPED_DURATION_LINE')
    spectra_path_strs = config['Spectra Import']['SPECTRA_FILES']
    spectra_paths = [Path(path.strip()) for path in spectra_path_strs.split(',')]
    SETTINGS['SPECTRA_FILES'] = spectra_paths
    #set up the TRIM file paths
    SETTINGS['TRIM_PATHS'] = {}
    SETTINGS['TRIM_PATHS']['TRIM_AUTO'] = SETTINGS['SRIM_PATH'] / 'TRIMAUTO'
    SETTINGS['TRIM_PATHS']['TRIM_IN'] = SETTINGS['SRIM_PATH'] / 'TRIM.IN'
    SETTINGS['TRIM_PATHS']['TRIM_TRANSMIT'] = SETTINGS['SRIM_PATH'] / 'SRIM Outputs/TRANSMIT.txt'
    #this link launches TRIM minimized which speeds it up a lot
    SETTINGS['TRIM_PATHS']['TRIM_EXEC'] = SETTINGS['SRIM_PATH'] / 'TRIM_min.exe.lnk'

    return 0

def init_grids():
    """Initialize the angles, damage energies, and incident spectrum"""
    #angles
    global ANGLES
    ANGLES = np.linspace(SETTINGS['THETA_MIN'], SETTINGS['THETA_MAX'], SETTINGS['THETA_NUM'], endpoint = True)
    #incident spectrum
    global SIMULATED_SPECTRUM
    SIMULATED_SPECTRUM = load_spectrum()
    #energy grid for damage
    global DAMAGE_ENERGIES
    damage_min_energy = 0.001
    damage_max_energy = max(SIMULATED_SPECTRUM[:, 0])
    damage_decades = np.log10(damage_max_energy / damage_min_energy)
    damage_num_samp = round(damage_decades * SETTINGS['DAMAGE_ENERGIES_PER_DECADE'])
    DAMAGE_ENERGIES = np.logspace(np.log10(damage_min_energy), np.log10(damage_max_energy), damage_num_samp)
    return 0


def load_spectrum():
    """Load the incident proton spectrum and resample it onto the TRIM grid. It's an omnidirectional IFlux over 4pi"""
    spectrum = pd.read_csv(SETTINGS['PROTON_SPECTRUM_FILE']).to_numpy()[:,[1,2]]
    min_energy = min(spectrum[:,0])
    max_energy = max(spectrum[:,0])
    num_decades = np.log10(max_energy/min_energy)
    num_samples = round(num_decades * SETTINGS['SPECTRUM_ENERGIES_PER_DECADE'])
    new_energies = np.logspace(np.log10(min_energy), np.log10(max_energy), num_samples)
    resampled_spectrum = numerics.log_interp(new_energies, spectrum[:, 0], spectrum[:, 1])
    return np.transpose([new_energies,resampled_spectrum])


if __name__ == '__main__':
    import pprint
    root = Path.cwd().parent
    example_config = root / 'example_config.ini'
    read_config(example_config)
    init_grids()
    pprint.pp(SETTINGS)
