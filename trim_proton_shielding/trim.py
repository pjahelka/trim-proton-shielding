"""Handles talking to TRIM. Configs, runs, and analyzes simulation results."""

import os
import numpy as np
import pandas as pd
import config
import collections
import subprocess
import numerics

def config_trim(energy, thickness, angle, particle_number):
    """setup TRIM.IN and TRIMAUTO for a trim simulation energy in MeV, thickness in um"""
    with open(config.SETTINGS['TRIM_PATHS']['TRIM_AUTO'], 'r') as file:
        #make sure TRIM is in auto made
        lines = file.readlines()
        lines[0] = '1\n'
    with open(config.SETTINGS['TRIM_PATHS']['TRIM_AUTO'], 'w') as file:
        file.writelines(lines)
    #edit TRIM.in
    with open(config.SETTINGS['TRIM_PATHS']['TRIM_IN'], 'r') as file:
        lines = file.readlines()
        lines[2] = f'     1   1.008      {energy * 1E3}       {angle}    {particle_number}        1     1E6\n' #multiply by 1000 for MeV -> keV
        lines[6] = '0 0 1 0 0 0\n'  #save new transmission file
        lines[10] = f'5 0 {thickness*10*1000}\n' #thickness is in angstroms
        lines[16] = f'1 "Polyethylene" {thickness*10*1000} .93 .666667 .333333\n' #set thickness of glass
    with open(config.SETTINGS['TRIM_PATHS']['TRIM_IN'], 'w') as file:
        file.writelines(lines)

def run_trim():
    """Run the prepared TRIM simulation"""
    #delete previous transmitted protons to avoid bugs with incomplete runs
    try:
        os.remove(config.SETTINGS['TRIM_PATHS']['TRIM_TRANSMIT'])
    except FileNotFoundError:
        pass
    #run trim
    subprocess.call(str(config.SETTINGS['TRIM_PATHS']['TRIM_EXEC']), shell = True)
    return 0


def calc_simulated_spectrum():
    """Make spectrum for TRIM Simulations

    take the proton integrated flux spectrum and convert it to number of protons with a given energy.
    """
    #load the spectrum
    proton_spectrum = pd.read_csv(config.SETTINGS['PROTON_SPECTRUM_FILE'])
    integral_flux = proton_spectrum['IFlux, cm-2'].to_numpy()
    energies = proton_spectrum['Energy, MeV'].to_numpy()
    # calculate the new energy grid
    num_decades = np.log10(max(energies) / min(energies))
    new_energies = np.logspace(np.log10(min(energies)), np.log10(max(energies)),
                               round(num_decades * config.SETTINGS['SPECTRUM_ENERGIES_PER_DECADE']), endpoint=True)
    new_iflux = np.interp(new_energies, energies, integral_flux)
    #calculate the proton counts. All UV protons go into the highest bin. Differences are used for the rest.
    protons = new_iflux - np.roll(new_iflux, -1)
    protons[-1] = new_iflux[-1]

    ret = np.transpose([np.array(new_energies), np.array(protons)])
    return ret

def read_transmission():
    """parses a TRIM transmission file to get the transmitted energies"""
    data = pd.read_csv(config.SETTINGS['TRIM_PATHS']['TRIM_TRANSMIT'], delimiter =r"\s+", header = 11, usecols=[3], names = ['Energy, eV'])
    #add a column for MeV energy, which will be the default in the rest of the program
    data['Energy, MeV'] = data['Energy, eV'].apply(lambda x: x/1E6)
    return data

def calc_transmission_ratios(transmission_data, num_protons):
    """turn a transmission file into a scattering matrix."""
    idxs = numerics.nearest_idx(config.DAMAGE_ENERGIES)(transmission_data['Energy, MeV'])
    counter = collections.Counter(idxs)
    scattering = np.zeros(len(config.DAMAGE_ENERGIES))
    scattering[list(counter.keys())] = list(counter.values())
    scattering = scattering / num_protons
    return scattering

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from pathlib import Path
    root = Path.cwd().parent
    example_config = root / 'example_config.ini'
    config.read_config(example_config)
    config.init_grids()
    config_trim(1, 10, 0, 1E4)
    run_trim()

