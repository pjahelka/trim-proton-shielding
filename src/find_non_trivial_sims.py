"""
Find the proton angles and energies that are worth simulating in detail
"""
import config
import trim_helper
import numpy as np

#
def find_energy_bounds():
    """find upper and lower interesting energies for every incident angle"""
    energies = trim_helper.SIMULATED_SPECTRUM[:,0]
    #bounds of the interesting energies
    lower_energies_idx = []
    upper_energies_idx = []
    for angle in trim_config.ANGLES[0:-1]: #don't actually run 90deg
        lower_energy = find_bound(angle, type = 'lower')
        lower_energies_idx.append(lower_energy)
        upper_energy = find_bound(angle, type = 'upper')
        upper_energies_idx.append(upper_energy)
        print(f'Interesting energies for angle {angle:.1f} are {energies[lower_energy]:.2e} and {energies[upper_energy]:.2e}')
    return np.transpose([np.array(lower_energies_idx), np.array(upper_energies_idx)])

def find_bound(angle, type):
    """find the upper or lower bound on the interesting energies for a given angle of incidence. Returns the index of the energy"""
    energies = trim_helper.SIMULATED_SPECTRUM[:,0]
    def f(energy):
        return test_interesting(angle, energy, type)
    left_bound = trim_helper.bisect_search(energies, f)
    left_idx = left_bound[0]
    if type == 'lower':
        left_idx = max(0, left_idx - trim_config.SAFETY_IDX)#update idx for safety and include wrap-around protection
    elif type == 'upper':
        left_idx = min(len(energies) - 1, left_idx + trim_config.SAFETY_IDX + 1) #extra plus 1 is because the binary search returns index to the left of the zero
    return left_idx


def test_interesting(angle, energy, bound_type):
    """for testing if an energy could be useful as a lower or upper bound for full blocking/transmission"""
    if bound_type == 'lower':
        proton_number = trim_config.PROTONS_TEST_BLOCK
    if bound_type == 'upper':
        proton_number = trim_config.PROTONS_TEST_TRANSMIT
    #setup the TRIM simulation
    trim_helper.config_trim(energy, trim_config.SHIELD_THICKNESS, angle, proton_number)
    trim_helper.run_trim()
    data = trim_helper.read_transmission()
    #return logic
    if bound_type == 'lower':
        if len(data) ==0: #all protons were blocked
            return -1
        else:
            return 1
    if bound_type == 'upper':
        average_KE = np.mean(data['Energy, MeV'])
        if average_KE < trim_config.FULL_TRANSMIT_KE * energy: return -1 #didn't retain enough energy
        if len(data) == proton_number: return 1 #all protons transmitted
        else: return -1

if __name__ == '__main__':
    #foo = test_interesting(20, 3, 'upper')
    #foo = find_bound(0, 'upper')
    foo = find_energy_bounds()
    print(foo)