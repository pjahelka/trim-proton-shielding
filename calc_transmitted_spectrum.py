"""
Calculate the proton spectrum transmitted through a shield
"""
import trim_config
import numpy as np
import find_non_trivial_sims
import trim_helper

def calc_scattering_matrix():
    """Do the TRIM simulations necessary to construct the scattering matrix

    It has three axes: angle of incidence, incident energy,
    and transmitted energy"""
    run_energies = trim_helper.SIMULATED_SPECTRUM[:,0]
    #calculate the interesting energies for each angle
    energy_bounds = find_non_trivial_sims.find_energy_bounds()
    scattering_data = []
    for angle_idx, angle in enumerate(trim_config.ANGLES[:-1]):
        single_angle_scattering = []
        interesting_energy_idxs = energy_bounds[angle_idx]
        for run_energy_idx, run_energy in enumerate(run_energies):
            #check if interesting
            if run_energy_idx < interesting_energy_idxs[0]: #if energy too low
                scattering_matrix = construct_trivial_scattering_matrix('lower', run_energy_idx)
                single_angle_scattering.append(scattering_matrix)
                continue
            if run_energy_idx > interesting_energy_idxs[1]: #if energy too high
                scattering_matrix =  construct_trivial_scattering_matrix('upper', run_energy_idx)
                single_angle_scattering.append(scattering_matrix)
                continue
            trim_helper.config_trim(run_energy, trim_config.SHIELD_THICKNESS, angle, trim_config.PROTONS_SIMULATE)
            print(f'Running TRIM for angle {angle:.1f} and energy {run_energy:.2f}')
            trim_helper.run_trim()
            transmission_data = trim_helper.read_transmission()
            scattering_matrix = trim_helper.calc_transmission_ratios(transmission_data, trim_config.PROTONS_SIMULATE)
            single_angle_scattering.append(scattering_matrix)
        scattering_data.append(single_angle_scattering)
    scattering_data = np.array(scattering_data)
    np.save(trim_config.SCATTERING_MATRIX_FILE, scattering_data, allow_pickle=False)
    return scattering_data

def construct_trivial_scattering_matrix(bound_type, energy_idx):
    """Construct the scattering matrix if the energy is above or below the range of interest"""
    num_energies = len(trim_helper.DAMAGE_ENERGIES)
    matrix = np.zeros(num_energies)
    if bound_type == 'lower': #fully blocking
        return matrix
    else:
        incident_energy = trim_helper.SIMULATED_SPECTRUM[:,0][energy_idx]
        scatter_idx = trim_helper.nearest_idx(trim_helper.DAMAGE_ENERGIES)(incident_energy)
        matrix[scatter_idx] = 1 #fully transmitting
        return matrix

def calc_transmitted_spectrum():
    """Calculate the transmitted spectrum"""
    scattering_matrix = np.load(trim_config.SCATTERING_MATRIX_FILE)
    #scattering_matrix has shape (angles,incident_energies, damage_energies)
    incident_angle_weighted = np.expand_dims(trim_helper.ANGLE_WEIGHT,1) * np.tile(trim_helper.SIMULATED_SPECTRUM[:,1],(len(trim_helper.ANGLE_WEIGHT),1))
    #incident_angle_weighted has shape (angles, incident energies)
    #einstein summation for integrating over incident energies and angles
    transmitted = np.einsum('ijk,ij',scattering_matrix,incident_angle_weighted)
    return transmitted

if __name__ == "__main__":
    calc_scattering_matrix()
    foo = trim_helper.calc_IFlux(calc_transmitted_spectrum())
    import matplotlib.pyplot as plt
    plt.plot(trim_helper.DAMAGE_ENERGIES, foo)
    plt.plot(trim_helper.SIMULATED_SPECTRUM[:,0], trim_helper.calc_IFlux(0.25*trim_helper.SIMULATED_SPECTRUM[:,1]))#0.25 is from flux only being from above and being incident on plane instead of ball
    plt.xscale('log')
    plt.yscale('log')
    plt.show()
    print(f'{foo[0]:.2e}')