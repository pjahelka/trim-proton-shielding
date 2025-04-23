"""helper functions for the program"""

import os
import numpy as np
import pandas as pd
import trim_config
import collections
import subprocess

def config_trim(energy, thickness, angle, particle_number):
    """setup TRIM.IN and TRIMAUTO for a trim simulation energy in MeV, thickness in um"""
    with open(trim_config.TRIM_AUTO, 'r') as file:
        #make sure TRIM is in auto made
        lines = file.readlines()
        lines[0] = '1\n'
    with open(trim_config.TRIM_AUTO, 'w') as file:
        file.writelines(lines)
    #edit TRIM.in
    with open(trim_config.TRIM_IN, 'r') as file:
        lines = file.readlines()
        lines[2] = f'     1   1.008      {energy * 1E3}       {angle}    {particle_number}        1     1E6\n' #multiply by 1000 for MeV -> keV
        lines[6] = '0 0 1 0 0 0\n'  #save new transmission file
        lines[10] = f'5 0 {thickness*10*1000}\n' #thickness is in angstroms
        lines[16] = f'1 "SiO2 - quartz (ICRU-245)" {thickness*10*1000} 2.32 .666667 .333333\n' #set thickness of glass
    with open(trim_config.TRIM_IN, 'w') as file:
        file.writelines(lines)



def run_trim():
    """Run the prepared TRIM simulation"""
    #delete previous transmitted protons to avoid bugs with incomplete runs
    try:
        os.remove(trim_config.TRIM_TRANSMIT)
    except FileNotFoundError:
        pass
    #run trim
    subprocess.call(trim_config.TRIM_EXEC, shell=True)
    return 0


def calc_simulated_spectrum():
    """Make spectrum for TRIM Simulations

    take the proton integrated flux spectrum and convert it to number of protons with a given energy.
    """
    #load the spectrum
    proton_spectrum = pd.read_csv(trim_config.PROTON_SPECTRUM_FILE)
    integral_flux = proton_spectrum['IFlux, cm-2'].to_numpy()
    energies = proton_spectrum['Energy, MeV'].to_numpy()
    # calculate the new energy grid
    num_decades = np.log10(max(energies) / min(energies))
    new_energies = np.logspace(np.log10(min(energies)), np.log10(max(energies)),
                               round(num_decades * trim_config.SPECTRUM_ENERGIES_PER_DECADE), endpoint=True)
    new_iflux = np.interp(new_energies, energies, integral_flux)
    #calculate the proton counts. All UV protons go into the highest bin. Differences are used for the rest.
    protons = new_iflux - np.roll(new_iflux, -1)
    protons[-1] = new_iflux[-1]

    ret = np.transpose([np.array(new_energies), np.array(protons)])
    return ret
#calculate as global because it depends on static file
SIMULATED_SPECTRUM = calc_simulated_spectrum()

#Make energy grid for the protons doing the damage, in MeV. min is an arbitrary IR cutoff. Max come from the proton spectra
#and is therefore in trim_helper because it requires calculations
DAMAGE_MIN_ENERGY = 0.001
DAMAGE_MAX_ENERGY = max(SIMULATED_SPECTRUM[:,0])
DAMAGE_DECADES = np.log10(DAMAGE_MAX_ENERGY / DAMAGE_MIN_ENERGY)
DAMAGE_NUM_SAMP = round(DAMAGE_DECADES * trim_config.DAMAGE_ENERGIES_PER_DECADE)
DAMAGE_ENERGIES = np.logspace(np.log10(DAMAGE_MIN_ENERGY), np.log10(DAMAGE_MAX_ENERGY), DAMAGE_NUM_SAMP)


def read_transmission():
    """parses a TRIM transmission file to get the transmitted energies"""
    data = pd.read_csv(trim_config.TRIM_TRANSMIT, delimiter =r"\s+", header = 11, usecols=[3], names = ['Energy, eV'])
    #add a column for MeV energy, which will be the default in the rest of the program
    data['Energy, MeV'] = data['Energy, eV'].apply(lambda x: x/1E6)
    return data

def nearest_idx(values):
    """find the index of the nearest element of another list. Call as: nearest_idx(ruler)(thing to measure)"""
    def f(x):
        idx = np.argmin(np.abs(values - x))
        return idx
    return np.frompyfunc(f, 1, 1)

def calc_transmission_ratios(transmission_data, num_protons):
    """turn a transmission file into a scattering matrix."""
    idxs = nearest_idx(DAMAGE_ENERGIES)(transmission_data['Energy, MeV'])
    counter = collections.Counter(idxs)
    scattering = np.zeros(len(DAMAGE_ENERGIES))
    scattering[list(counter.keys())] = list(counter.values())
    scattering = scattering / num_protons
    return scattering




def bisect_search(x, f):
    """bisection search for finding zeros of f over x. Assumes x is ordered smallest to largest and f is monotonic."""
    #initialize algorithm
    N = len(x)
    left_idx = 0
    left = x[0]
    right_idx = N - 1
    right = x[-1]
    mid_idx = round(N/2)
    mid = x[mid_idx]
    error = right_idx - left_idx
    f_left = f(left)
    f_right = f(right)
    f_mid = f(mid)
    # check it has a zero
    if np.sign(f_left) == np.sign(f_right): #return -1 if no zero
        return -1
    while error > trim_config.BISECT_IDX_TOL:
        #compare signs
        if np.sign(f_left) == np.sign(f_mid): #if true, zero is in the right interval
            left_idx = mid_idx
            left = x[mid_idx]
            f_left = f_mid
            mid_idx = round((left_idx + right_idx) / 2)
            mid = x[mid_idx]
            f_mid = f(mid)
            error = right_idx - left_idx
        else:
            right_idx = mid_idx
            right = x[mid_idx]
            f_right = f_mid
            mid_idx = round((left_idx + right_idx) / 2)
            mid = x[mid_idx]
            f_mid = f(mid)
            error = right_idx - left_idx
    #return the left-hand side of the suspected zero
    return left_idx, left, f_left


def calc_angle_weights():
    """calculate what fraction of the protons should be shot in at each angle"""
    angle_weights = []
    num_angle = len(trim_config.ANGLES)
    for idx in range(num_angle - 1): #exclude 90deg
        weight = 0.25*(np.cos(trim_config.ANGLES[idx] * np.pi / 180) ** 2 - np.cos(trim_config.ANGLES[idx + 1] * np.pi / 180) ** 2)
        angle_weights.append(weight)
    return np.array(angle_weights)
#calculate because constant that depends on config
ANGLE_WEIGHT = calc_angle_weights()

def calc_IFlux(fluxes):
    """Turn protons at specific energies into an IFlux for nice plotting"""
    reverse_flux = np.flip(fluxes) #because SPENVIS calcs IFlux from high to low energy
    cumsum = np.cumsum(reverse_flux)
    return np.flip(cumsum)

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    total_protons = []
    for j in range(4,20,5):
        trim_config.SPECTRUM_ENERGIES_PER_DECADE = j
        SIMULATED_SPECTRUM = calc_simulated_spectrum()
        total_protons.append(sum(SIMULATED_SPECTRUM[:,1]))
    #plt.xscale('log')
    #plt.yscale('log')
    plt.plot(total_protons)
    plt.legend()
    plt.show()

