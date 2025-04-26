import config
import numpy as np
import calc_transmitted_spectrum
import calc_equiv_fluence
import matplotlib.pyplot as plt

def angles_convergence():
    """figure out how many angles of incidence we need"""
    num_angles = range(5, 20, 3)
    fluences = []
    tested_angle_nums = []
    rdc = calc_equiv_fluence.load_proton_rdc(config.SETTINGS['PROTON_RDC_FILE'])
    for num_angle in num_angles:
        config.SETTINGS['THETA_NUM'] = num_angle
        config.init_grids()
        calc_transmitted_spectrum.calc_scattering_matrix()
        spectrum = calc_transmitted_spectrum.calc_transmitted_spectrum()
        fluence = calc_equiv_fluence.calc_fluence(spectrum, rdc, config.SETTINGS['PROTONS_TO_ELECTRONS'])
        fluences.append(fluence)
        tested_angle_nums.append(num_angle)
        plt.plot(tested_angle_nums, fluences)
        plt.show()
        print(num_angle)
        print(f'{fluence:.2e}')
    return num_angles, fluences

def spectrum_energies_per_decade_convergence():
    """Test energies per decade of incident spectrum"""
    energies_per_decades = [25, 50, 75, 100, 125, 150, 175, 200]
    fluences = []
    tested_numbers = []
    rdc = calc_equiv_fluence.load_proton_rdc(config.SETTINGS['PROTON_RDC_FILE'])
    for energies_per_decade in energies_per_decades:
        #set the variable
        config.SETTINGS['SPECTRUM_ENERGIES_PER_DECADE'] = energies_per_decade
        #recalc spectrum
        config.init_grids()
        calc_transmitted_spectrum.calc_scattering_matrix()
        spectrum = calc_transmitted_spectrum.calc_transmitted_spectrum()
        fluence = calc_equiv_fluence.calc_fluence(spectrum, rdc,  config.SETTINGS['PROTONS_TO_ELECTRONS'])
        fluences.append(fluence)
        tested_numbers.append(energies_per_decade)
        plt.plot(tested_numbers, fluences)
        plt.show()
        print(energies_per_decade)
        print(f'{fluence:.2e}')
    return energies_per_decades, fluences



if __name__ == '__main__':
    from pathlib import Path
    root = Path.cwd().parent
    example_config = root / 'example_config.ini'
    config.read_config(example_config)
    config.init_grids()

    num_angles, angle_fluences = angles_convergence()
    num_per_dec, num_per_dec_fluences = spectrum_energies_per_decade_convergence()
    print(0)