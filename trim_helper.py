"""helper functions for the program"""

import os
import numpy as np
import pandas as pd

import import_spectra
import trim_config
import collections

def config_trim(energy, thickness, angle, particle_number):
    """setup TRIM.IN and TRIMAUTO for a trim simulation
    energy in MeV, thickness in um
    """
    with open(trim_config.trim_auto, 'r') as file:
        #make sure TRIM is in auto made
        lines = file.readlines()
        lines[0] = '1\n'
    with open(trim_config.trim_auto, 'w') as file:
        file.writelines(lines)
    #edit TRIM.in
    with open(trim_config.trim_in, 'r') as file:
        lines = file.readlines()
        lines[2] = f'     1   1.008      {energy * 1E3}       {angle}    {particle_number}        1     1E6\n' #multiply by 1000 for MeV -> keV
        lines[6] = '0 0 1 0 0 0\n'  #save new transmission file
        lines[10] = f'5 0 {thickness*10*1000}\n' #thickness is in angstroms
        lines[16] = f'1 "SiO2 - quartz (ICRU-245)" {thickness*10*1000} 2.32 .666667 .333333\n' #set thickness of glass
    with open(trim_config.trim_in, 'w') as file:
        file.writelines(lines)
    #print(
    #    f'Setup TRIM for {energy:.3e}, MeV, {thickness:.1f}, um, {angle:.1f} deg, {particle_number:.0E} protons'
    #)
#argument is energy in eV, thickness in um, angle in deg
def run_trim():
    #delete previous transmitted protons to avoid bugs with incomplete runs
    try:
        os.remove(trim_config.trim_transmit)
    except FileNotFoundError:
        pass
    #run trim
    os.system(trim_config.trim_exec)
    return 0

#take the proton density spectrum and convert it to number of protons with a given energy. returned energy is the upper end
#of each interval
def calc_simulated_spectrum():
    #load the spectrum
    density_spectrum = pd.read_csv(trim_config.proton_spectrum_file)
    density_flux = density_spectrum['DFlux, cm-2 MeV-1'].to_numpy()
    energies = density_spectrum['Energy, MeV'].to_numpy()
    #calculate the integrands
    integrands = 0.5 * (density_flux + np.roll(density_flux, 1)) * (energies - np.roll(energies, 1))
    integrands = integrands[1:]
    energies = energies[1:]
    return energies, integrands
#calculate as global because it depends on static file
simulated_spectrum = calc_simulated_spectrum()
#Make energy grid for the protons doing the damage, in MeV. min is an arbitrary IR cutoff. Max come from the spectra
#and is therefore in trim_helper because it requires calculations

damage_max_energy = max(simulated_spectrum[0])
damage_decades = np.log10(damage_max_energy / trim_config.damage_min_energy)
damage_num_samp = round(damage_decades * trim_config.energies_per_decade)
damage_energies = np.logspace(np.log10(trim_config.damage_min_energy), np.log10(damage_max_energy), damage_num_samp)


def read_transmission(): #parses a TRIM transmission file to get the transmitted energies
    data = pd.read_csv(trim_config.trim_transmit, delimiter = r"\s+", header = 11, usecols=[3], names = ['Energy, eV'])
    #add a column for MeV energy, which will be the default in the rest of the program
    data['Energy, MeV'] = data['Energy, eV'].apply(lambda x: x/1E6)
    return data

#find the index of the nearest element of another list. Call as: nearest_idx(ruler)(thing to measure)
def nearest_idx(values):
    def f(x):
        idx = np.argmin(np.abs(values - x))
        return idx
    return np.frompyfunc(f, 1, 1)

#turn a transmission file into a scattering matrix.
def calc_transmission_ratios(transmission_data, num_protons):
    idxs = nearest_idx(damage_energies)(transmission_data['Energy, MeV'])
    counter = collections.Counter(idxs)
    scattering = np.zeros(len(damage_energies))
    scattering[list(counter.keys())] = list(counter.values())
    scattering = scattering / num_protons
    return scattering

# logarithmic interpolator
def log_interp(x, xp, fp):
    log_fp = np.log(fp)
    new_fp = np.interp(x, xp, log_fp, right=0)
    new_fp = np.exp(new_fp)
    return new_fp

#bisection search for finding zeros of f over x. Assumes x is ordered smallest to largest and f is monotonic.
def bisect_search(x, f):
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
    while error > trim_config.bisect_idx_tol:
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

#calculate what fraction of the protons should be shot in at each angle
def calc_angle_weights():
    angle_weights = []
    num_angle = len(trim_config.angles)
    for idx in range(num_angle - 1): #exclude 90deg
        weight = 0.25*(np.cos(trim_config.angles[idx] * np.pi / 180)**2 - np.cos(trim_config.angles[idx + 1] * np.pi / 180)**2)
        angle_weights.append(weight)
    return angle_weights
#calculate because constant that depends on config
angle_weight = calc_angle_weights()

if __name__ == '__main__':
    def f(x):
        return x**2 - 1
    x = np.linspace(1.1,2,100)
    foo = bisect_search(x ,f)
    print(foo)