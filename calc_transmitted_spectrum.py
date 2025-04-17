"""
Calculated the proton spectrum transmitted through a shield
"""
import trim_config
import numpy as np
import pandas as pd
import find_non_trivial_sims
import trim_helper


#calculate the matrix that describes how protons are slowed. It has three axes: angle of incidence, incident energy,
#and transmitted energy
def calc_scattering_matrix():
    possible_run_energies = trim_helper.simulated_spectrum[0]
    #calculate the interesting energies for each angle
    energy_bounds = find_non_trivial_sims.find_energy_bounds()
    scattering_data = []
    for angle_idx, angle in enumerate(trim_config.angles[:-1]):
        single_angle_scattering = []
        interesting_energy_idxs = energy_bounds[angle_idx]
        run_energies = possible_run_energies[interesting_energy_idxs[0]:interesting_energy_idxs[1] + 1]
        for run_energy in run_energies:
            trim_helper.config_trim(run_energy, trim_config.shield_thickness, angle, trim_config.particle_number)
            trim_helper.run_trim()
            transmission_data = trim_helper.read_transmission()
            scattering_matrix = trim_helper.calc_transmission_ratios(transmission_data, trim_config.particle_number)
            single_angle_scattering.append(scattering_matrix)
        scattering_data.append(single_angle_scattering)
    return scattering_data


if __name__ == "__main__":
    #foo = discretize_spectrum()
    foo = calc_slowing_matrix()
    print(foo)