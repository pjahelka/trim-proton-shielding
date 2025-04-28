"""
Find the proton angles and energies that are worth simulating in detail
"""
import config
import trim
import numpy as np
import numerics
def find_energy_bounds():
    """find upper and lower interesting energies for every incident angle"""
    energies = config.SIMULATED_SPECTRUM[:,0]
    #bounds of the interesting energies
    lower_energies_idx = []
    upper_energies_idx = []
    for angle in config.ANGLES[0:-1]: #don't actually run 90deg
        lower_energy = find_bound(angle, type = 'lower')
        lower_energies_idx.append(lower_energy)
        upper_energy = find_bound(angle, type = 'upper')
        upper_energies_idx.append(upper_energy)
        print(f'Interesting energies for angle {angle:.1f} are {energies[lower_energy]:.2e} and {energies[upper_energy]:.2e}')
    return np.transpose([np.array(lower_energies_idx), np.array(upper_energies_idx)])

def find_bound(angle, type):
    """find the upper or lower bound on the interesting energies for a given angle of incidence. Returns the index of the energy"""
    energies = config.SIMULATED_SPECTRUM[:,0]
    def f(energy):
        return test_interesting(angle, energy, type)
    left_bound = numerics.bisect_search(energies, f, config.SETTINGS['BISECT_IDX_TOL'])
    left_idx = left_bound[0]
    if type == 'lower':
        left_idx = max(0, left_idx - config.SETTINGS['SAFETY_IDX'])#update idx for safety and include wrap-around protection
    elif type == 'upper':
        left_idx = min(len(energies) - 1, left_idx + config.SETTINGS['SAFETY_IDX'] + 1) #extra plus 1 is because the binary search returns index to the left of the zero
    return left_idx


def test_interesting(angle, energy, bound_type):
    """for testing if an energy could be useful as a lower or upper bound for full blocking/transmission"""
    proton_number = 0
    if bound_type == 'lower':
        proton_number = config.SETTINGS['PROTONS_TEST_BLOCK']
    if bound_type == 'upper':
        proton_number = config.SETTINGS['PROTONS_TEST_TRANSMIT']
    #set up the TRIM simulation
    trim.config_trim(energy, config.SETTINGS['SHIELD_THICKNESS'], angle, proton_number)
    trim.run_trim()
    data = trim.read_transmission()
    #return logic
    if bound_type == 'lower':
        if len(data) ==0: #all protons were blocked
            return -1
        else:
            return 1
    if bound_type == 'upper':
        average_KE = np.mean(data['Energy, MeV'])
        if average_KE < config.SETTINGS['FULL_TRANSMIT_KE'] * energy: return -1 #didn't retain enough energy
        if len(data) == proton_number: return 1 #all protons transmitted
        else: return -1
    return 0 #shouldn't get here

if __name__ == '__main__':
    from pathlib import Path
    root = Path.cwd().parent
    example_config = root / 'example_config.ini'
    config.read_config(example_config)
    config.init_grids()
    foo = find_energy_bounds()
    print(foo)