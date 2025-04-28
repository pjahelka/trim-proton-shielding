"""
Example computation of dose through a simple shield
"""
#add the modules to the path. There has to be a better way that works with autocomplete.
import sys
sys.path.append('./trim_proton_shielding')
import config
import calc_transmitted_spectrum
import calc_equiv_fluence


#read config and intialize the energy grids and spectra
config.read_config('example_config.ini')
config.init_grids()
#compute the scattering matrix and plot it
#calc_transmitted_spectrum.calc_scattering_matrix()
calc_transmitted_spectrum.visualize_scattering_matrix()
#compute the dose
# rdc = calc_equiv_fluence.load_proton_rdc(config.SETTINGS['PROTON_RDC_FILE'])
# spectrum = calc_transmitted_spectrum.calc_transmitted_spectrum()
# dose = calc_equiv_fluence.calc_fluence(spectrum, rdc, config.SETTINGS['PROTONS_TO_ELECTRONS'])
# print(f'{dose:.2e}')
# #edit some settings and recompute
# config.SETTINGS['SHIELD_THICKNESS'] = 100
# calc_transmitted_spectrum.calc_scattering_matrix()
# spectrum = calc_transmitted_spectrum.calc_transmitted_spectrum()
# dose = calc_equiv_fluence.calc_fluence(spectrum, rdc, config.SETTINGS['PROTONS_TO_ELECTRONS'])
# print(f'{dose:.2e}')
# #edit some settings and recompute
# config.SETTINGS['SPECTRUM_ENERGIES_PER_DECADE'] = 25
# config.init_grids() #need to recompute after editing energies per decade
# calc_transmitted_spectrum.calc_scattering_matrix()
# spectrum = calc_transmitted_spectrum.calc_transmitted_spectrum()
# dose = calc_equiv_fluence.calc_fluence(spectrum, rdc, config.SETTINGS['PROTONS_TO_ELECTRONS'])
# print(f'{dose:.2e}')

