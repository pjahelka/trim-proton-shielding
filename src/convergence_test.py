import calc_equiv_fluence
import calc_transmitted_spectrum
import trim_config
import trim_helper
import numpy as np
import matplotlib.pyplot as plt
import import_spectra

rdc = calc_equiv_fluence.load_proton_rdc(trim_config.PROTON_RDC_FILE)

def angles_convergence():
    """figure out how many angles of incidence we need"""
    num_angles = range(10, 20)
    fluences = []
    tested_angle_nums = []
    for num_angle in num_angles:
        trim_config.ANGLES = np.linspace(0, 90, num_angle)
        trim_helper.ANGLE_WEIGHT = trim_helper.calc_angle_weights()
        calc_transmitted_spectrum.calc_scattering_matrix()
        spectrum = calc_transmitted_spectrum.calc_transmitted_spectrum()
        fluence = calc_equiv_fluence.calc_fluence(spectrum, rdc, trim_config.POWER_PROTONS_TO_ELECTRONS)
        fluences.append(fluence)
        tested_angle_nums.append(num_angle)
        plt.plot(tested_angle_nums, fluences)
        plt.show()
        print(num_angle)
        print(f'{fluence:.2e}')
    return num_angles, fluences

def spectrum_energies_per_decade_convergence():
    """Test energies per decade of incident spectrum"""
    energies_per_decades = [100, 200, 50]
    fluences = []
    tested_numbers = []
    for energies_per_decade in energies_per_decades:
        #set the variable
        trim_config.SPECTRUM_ENERGIES_PER_DECADE = energies_per_decade
        #recalc spectrum
        trim_helper.SIMULATED_SPECTRUM = trim_helper.calc_simulated_spectrum()
        calc_transmitted_spectrum.calc_scattering_matrix()
        spectrum = calc_transmitted_spectrum.calc_transmitted_spectrum()
        fluence = calc_equiv_fluence.calc_fluence(spectrum, rdc, trim_config.POWER_PROTONS_TO_ELECTRONS)
        fluences.append(fluence)
        tested_numbers.append(energies_per_decade)
        plt.plot(tested_numbers, fluences)
        plt.show()
        print(energies_per_decade)
        print(f'{fluence:.2e}')
    return energies_per_decades, fluences



if __name__ == '__main__':
    #num_angles, fluences = angles_convergence()
    foo = spectrum_energies_per_decade_convergence()
    print(foo)
