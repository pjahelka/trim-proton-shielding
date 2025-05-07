"""
Calculate the proton spectrum transmitted through a shield
"""
import config
import numpy as np
import find_non_trivial_sims
import trim
import numerics

def calc_scattering_matrix():
    """Do the TRIM simulations necessary to construct the scattering matrix

    It has three axes: angle of incidence, incident energy,
    and transmitted energy"""
    run_energies = config.SIMULATED_SPECTRUM[:,0]
    #calculate the interesting energies for each angle
    energy_bounds = find_non_trivial_sims.find_energy_bounds()
    scattering_data = []
    for angle_idx, angle in enumerate(config.ANGLES[:-1]): #don't do 90deg
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
            trim.config_trim(run_energy, config.SETTINGS['SHIELD_THICKNESS'], angle, config.SETTINGS['PROTONS_SIMULATE'])
            print(f'Running TRIM for angle {angle:.1f} and energy {run_energy:.2f}')
            trim.run_trim()
            transmission_data = trim.read_transmission()
            scattering_matrix = trim.calc_transmission_ratios(transmission_data, config.SETTINGS['PROTONS_SIMULATE'])
            single_angle_scattering.append(scattering_matrix)
        scattering_data.append(single_angle_scattering)
    scattering_data = np.array(scattering_data)
    #tack on the 90deg data as zeros to make integrals easier later
    scattering_data = np.pad(scattering_data, ((0, 1),(0,0),(0,0)), mode='constant', constant_values=0)
    np.save(config.SETTINGS['SCATTERING_FILE_PATH'], scattering_data, allow_pickle=False)
    return scattering_data

def construct_trivial_scattering_matrix(bound_type, energy_idx):
    """Construct the scattering matrix if the energy is above or below the range of interest"""
    num_energies = len(config.DAMAGE_ENERGIES)
    matrix = np.zeros(num_energies)
    if bound_type == 'lower': #fully blocking
        return matrix
    else:
        incident_energy = config.SIMULATED_SPECTRUM[:,0][energy_idx]
        scatter_idx = numerics.nearest_idx(config.DAMAGE_ENERGIES)(incident_energy)
        matrix[scatter_idx] = 1 #fully transmitting
        return matrix

def calc_transmitted_spectrum():
    """Calculate the transmitted omnidirectional spectrum"""
    #load scattering matrix
    scattering_matrix = np.load(config.SETTINGS['SCATTERING_FILE_PATH'])
    #transpose spectrum to get it in the right shape for broadcasting the angle factors
    scattering_matrix = scattering_matrix.transpose([1,2,0])
    # radian angles
    angles_rad = config.ANGLES * np.pi / 180
    #calculate angle factors
    angle_factors = np.sin(angles_rad)/2 #two from assuming infinite back-shield (2pi/4pi)
    #broadcast the angle factors and scattering matrix together
    scattering_matrix_angles = scattering_matrix * angle_factors
    #integrate over the angles of incidence
    scattering_matrix_angle_reduced = np.trapezoid(scattering_matrix_angles, angles_rad)
    #product sum with the incident spectrum to get the transmitted one
    simulated_DFlux = numerics.calc_DFlux(config.SIMULATED_SPECTRUM[:,1])
    transmitted = np.einsum('ij,i', scattering_matrix_angle_reduced, simulated_DFlux)
    return transmitted

def visualize_scattering_matrix():
    """Visualize the scattering matrix

    contour plot with incident energies and trasmitted energies as the axes
    which uses angle weights correctly.
    """
    # load matrix
    scattering_matrix = np.load(config.SETTINGS['SCATTERING_FILE_PATH'])
    # transpose spectrum to get it in the right shape for broadcasting the angle factors
    scattering_matrix = scattering_matrix.transpose([1, 2, 0])
    # calculate angle factors
    angle_factors = 0.5 * np.sin(config.ANGLES * np.pi / 180) * np.cos(config.ANGLES * np.pi / 180)
    # broadcast the angle factors and scattering matrix together
    scattering_matrix_angles = scattering_matrix * angle_factors
    # radian angles
    angles_rad = config.ANGLES * np.pi / 180
    # integrate over the angles of incidence
    scattering_matrix_angle_reduced = np.trapezoid(scattering_matrix_angles, angles_rad)
    #Normalize the max of each transmitted energy to 1 so we can see where the transmitted protons are coming from
    normalized_matrix = np.zeros_like(scattering_matrix_angle_reduced)
    for damage_energy_idx in range(len(config.DAMAGE_ENERGIES)):
        row_max = max(scattering_matrix_angle_reduced[:,damage_energy_idx])
        if np.isclose(row_max, 0):
            continue
        normalized = scattering_matrix_angle_reduced[:,damage_energy_idx]/row_max
        normalized_matrix[:,damage_energy_idx] = normalized


    import matplotlib.pyplot as plt
    #plt.contourf(config.DAMAGE_ENERGIES, config.SIMULATED_SPECTRUM[:,0], normalized_matrix, np.linspace(0,1,100))
    plt.pcolor(config.DAMAGE_ENERGIES, config.SIMULATED_SPECTRUM[:,0], normalized_matrix, shading = 'auto' )
    plt.xscale('log')
    plt.yscale('log')
    plt.xlim(1E-3, 10)
    plt.ylim(6E-1, 10)
    plt.xlabel('Trasmitted Energy, MeV')
    plt.ylabel('Incident Energy, MeV')
    plt.title('Transmission-Normalized Scattering Matrix')
    plt.colorbar(ticks = np.linspace(0,1,11))
    plt.savefig('pretty_scattering_matrix.png')
    plt.show()
    return 0


if __name__ == "__main__":
    from pathlib import Path
    root = Path.cwd().parent
    example_config = root / 'example_config.ini'
    config.read_config(example_config)
    config.init_grids()
    calc_scattering_matrix()
    calc_transmitted_spectrum()
    visualize_scattering_matrix()
    foo = numerics.calc_IFlux(calc_transmitted_spectrum())
    import matplotlib.pyplot as plt
    plt.plot(config.DAMAGE_ENERGIES, foo)
    plt.plot(config.SIMULATED_SPECTRUM[:,0], numerics.calc_IFlux(0.25*config.SIMULATED_SPECTRUM[:,1]))#0.25 is from flux only being from above and being incident on plane instead of ball
    plt.xscale('log')
    plt.yscale('log')
    plt.show()
    print(f'{foo[0]:.2e}')
    print(0)