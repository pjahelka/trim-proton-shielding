"""Load configuration for the program and compute the grids"""
import configparser
from pathlib import Path

settings = {}

def read_config(config_file):
    """read a config file into a global dictionary"""
    global settings
    config = configparser.ConfigParser()
    config.read(config_file)
    settings['SRIM_PATH'] = Path( config['File Paths']['SRIM_PATH'] )
    settings['PROTON_SPECTRUM_FILE'] = Path(config['File Paths']['PROTON_SPECTRUM_FILE'])
    settings['SCATTERING_FILE_PATH'] = Path(config['File Paths']['SCATTERING_FILE_PATH'])
    settings['PROTON_RDC_FILE'] = Path(config['File Paths']['PROTON_RDC_FILE'])
    settings['THICKNESS'] = config['Shielding'].getfloat('THICKNESS')
    settings['PROTONS_SIMULATE'] = config['TRIM Config'].getint('PROTONS_SIMULATE')
    settings['PROTONS_TEST_TRANSMIT'] = config['TRIM Config'].getint('PROTONS_TEST_TRANSMIT')
    settings['PROTONS_TEST_BLOCK'] = config['TRIM Config'].getint('PROTONS_TEST_BLOCK')
    settings['SAFETY_IDX'] = config['TRIM Config'].getint('SAFETY_IDX')
    settings['FULL_TRANSMIT_KE'] = config['TRIM Config'].getfloat('FULL_TRANSMIT_KE')
    settings['THETA_MIN'] = config['TRIM Config'].getfloat('THETA_MIN')
    settings['THETA_MAX'] = config['TRIM Config'].getfloat('THETA_MAX')
    settings['THETA_NUM'] = config['TRIM Config'].getint('THETA_NUM')
    settings['SPECTRUM_ENERGIES_PER_DECADE'] = config['TRIM Config'].getint('SPECTRUM_ENERGIES_PER_DECADE')
    settings['DAMAGE_ENERGIES_PER_DECADE'] = config['Numerics'].getint('DAMAGE_ENERGIES_PER_DECADE')
    settings['ENERGIES_PER_DECADE_IMPORT'] = config['Numerics'].getint('ENERGIES_PER_DECADE_IMPORT')
    settings['BISECT_IDX_TOL'] = config['Numerics'].getint('BISECT_IDX_TOL')
    settings['POWER_LAW_FIT_POINTS'] = config['Numerics'].getint('POWER_LAW_FIT_POINTS')
    settings['CURVE_FIT_SIGMA'] = config['RDC'].getfloat('CURVE_FIT_SIGMA')
    settings['SOLAR_LAST_HEADER'] = config['Spectra Import']['SOLAR_LAST_HEADER']
    settings['TRAPPED_LAST_HEADER'] = config['Spectra Import']['TRAPPED_LAST_HEADER']
    settings['FIRST_FOOTER'] = config['Spectra Import']['FIRST_FOOTER']
    settings['TRAPPED_DURATION_LINE'] = config['Spectra Import'].getint('TRAPPED_DURATION_LINE')
    spectra_path_strs = config['Spectra Import']['SPECTRA_FILES']
    spectra_paths = [Path(path) for path in spectra_path_strs.split(',')]
    settings['SPECTRA_FILES'] = spectra_paths
    return 0


# TRIM_AUTO = os.path.join(SCRIPT_DIR, r'SRIM\TRIMAUTO')
# TRIM_IN = os.path.join(SCRIPT_DIR, r'SRIM\TRIM.IN')
# TRIM_TRANSMIT = os.path.join(SCRIPT_DIR, r'SRIM\SRIM Outputs\TRANSMIT.txt')
# #this link launches TRIM minimized which speeds it up a lot
# TRIM_EXEC = os.path.join(SCRIPT_DIR, r'SRIM\TRIM_min.exe.lnk')
#
#
#
# ANGLES = np.linspace(THETA_MIN, THETA_MAX, THETA_NUM, endpoint = True)
# ANGLES = [round(angle, 1) for angle in ANGLES]

if __name__ == '__main__':
    root = Path.cwd().parent
    example_config = root / 'example_config.ini'
    foo = read_config(example_config)
    print(settings)
