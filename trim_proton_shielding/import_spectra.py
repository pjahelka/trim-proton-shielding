"""
Script for reading and extracting information from SPENVIS proton fluxes and combining them into a single file

This code assumes a lot about the structure of the SPENVIS output file. In particular, it assumes that:
    One of the header lines below marks the start of data
    The data you want is in the first data block
    That the data columns are ordered energy, IFlux, DFlux

We also need to parse mission duration because the trapped proton spectra from SPENVIS is per-second.
The SPENVIS headers are difficult to parse because duration appears multiple times at different lines
with different values so the logic below is horrible
"""

import os
import numpy as np
import config
import re
import pandas as pd
import numerics

def extract_data(file):
    """Parse a SPENVIS proton spectrum file"""
    data = []
    data_line = False
    trapped = False #for figuring out if we need to deal with duration
    duration = 0
    with open(file) as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('\'Duration:'): #search for duration line
                if duration != 0: #if already defined, skip, because the first is the mission duration
                    continue
                duration_day = float(re.findall(r"\d+\.\d+", line)[0]) #duration in days
                duration = duration_day * 86400 #convert to seconds
            if line.startswith(config.SETTINGS['SOLAR_LAST_HEADER']): #figure out if start of data block and if trapped or solar
                data_line = True
                continue
            if line.startswith(config.SETTINGS['TRAPPED_LAST_HEADER']):
                data_line = True
                trapped = True
                continue
            if line.startswith(config.SETTINGS['FIRST_FOOTER']): #figure out if end of data block
                break
            if data_line:
                data.append(np.fromstring(line, sep=','))
    data = np.array(data)
    data = data[:,[0,1]] #select energies and IFlux
    if trapped:
        data[:,1] = data[:,1] * duration #turn flux/s to flux for trapped proton spectra
    #get rid of rows with zero-fluxes
    mask = data[:,1] != 0
    return data[mask]

def combine_spectra(spectra_table):
    """Combine proton spectra into a single file"""
    min_energies = []
    max_energies = []
    for spectra in spectra_table:
        min_energies.append(np.min(spectra[:,0]))
        max_energies.append(np.max(spectra[:,0]))
    min_energy = min(min_energies)
    max_energy = max(max_energies)
    #calculate how many decades of data and the number of sample points
    decades = np.log10(max_energy/min_energy)
    num_samp = round(decades * config.SETTINGS['ENERGIES_PER_DECADE_IMPORT'])
    #generate the new energy grid to use
    new_energies = np.logspace(np.log10(min_energy), np.log10(max_energy), num_samp)
    resampled_spectra = []
    #resample the proton spectra using logarithmic interpolation
    for spectra in spectra_table:
        resampled_spectrum = numerics.log_interp(new_energies, spectra[:, 0], spectra[:, 1])
        resampled_spectra.append(resampled_spectrum)
    #sum and return
    resampled_spectrum = np.sum(resampled_spectra, axis = 0)
    return new_energies, resampled_spectrum

def save_combined_spectrum():
    """Calculate and save the combined spectrum. It's an IFlux"""
    spectra = []
    for spectra_path in config.SETTINGS['SPECTRA_FILES']:
        spectra.append(extract_data(spectra_path))
    new_energies, combined_spectra = combine_spectra(spectra)
    df = pd.DataFrame(data=np.transpose([new_energies, combined_spectra]), columns=['Energy, MeV', 'IFlux, cm-2'])
    df.to_csv(config.SETTINGS['PROTON_SPECTRUM_FILE'])
    return df

if __name__ == "__main__":
    from pathlib import Path
    root = Path.cwd().parent
    example_config = root / 'example_config.ini'
    config.read_config(example_config)
    save_combined_spectrum()

