"""
Script for reading and extracting information from SPENVIS proton fluxes and combining them into a single file

This code assumes a lot about the structure of the SPENVIS output file. In particular, it assumes that:
    One of the header lines below marks the start of data
    The data you want is in the first data block
    That the data columns are ordered energy, IFlux, DFlux

We also need to parse mission duration because the trapped spectra from SPENVIS is per-second.
The SPENVIS headers are difficult to parse because duration appears multiple times at different lines
with different values so the logic below is horrible
"""

import os
import numpy as np
import trim_config
import re
import pandas as pd

def extract_data(file):
    """Parse a SPENVIS proton spectrum file"""
    data = []
    data_line = False
    trapped = False #for figuring out if we need to deal with duration
    with open(file) as f:
        lines = f.readlines()
        duration = re.findall(r"\d+\.\d+", lines[trim_config.TRAPPED_DURATION_LINE])  # extract duration in days
        if duration:
            duration = float(duration[0])
            duration = duration * 31.5E6  # convert to seconds
        for line in lines:
            if line.startswith(trim_config.SOLAR_LAST_HEADER): #figure out if start of data block and if trapped or solar
                data_line = True
                continue
            if line.startswith(trim_config.TRAPPED_LAST_HEADER):
                data_line = True
                trapped = True
                continue
            if line.startswith(trim_config.FIRST_FOOTER): #figure out if end of data block
                break
            if data_line:
                data.append(np.fromstring(line, sep=','))
    data = np.array(data)
    data = data[:,[0,1]] #select energies and IFlux
    if trapped:
        data[:,1] = data[:,1] * duration #turn flux/s to flux for trapped spectra
    #get rid of rows with zero-fluxes
    mask = data[:,1] != 0
    return data[mask]

def combine_spectra(spectra_table):
    """Combine spectra into a single file"""
    min_energies = []
    max_energies = []
    for spectra in spectra_table:
        min_energies.append(np.min(spectra[:,0]))
        max_energies.append(np.max(spectra[:,0]))
    min_energy = min(min_energies)
    max_energy = max(max_energies)
    #calculate how many decades of data and the number of sample points
    decades = np.log10(max_energy/min_energy)
    num_samp = round(decades * trim_config.ENERGIES_PER_DECADE_IMPORT)
    #generate the new energy grid to use
    new_energies = np.logspace(np.log10(min_energy), np.log10(max_energy), num_samp)
    resampled_spectra = []
    #resample the spectra using logarithmic interpolation
    for spectra in spectra_table:
        resampled_spectrum = log_interp(new_energies, spectra[:, 0], spectra[:, 1])
        resampled_spectra.append(resampled_spectrum)
    #sum and return
    resampled_spectrum = np.sum(resampled_spectra, axis = 0)
    return new_energies, resampled_spectrum

def log_interp(x, xp, fp):
    """logarithmic interpolator"""
    log_fp = np.log(fp)
    new_fp = np.interp(x, xp, log_fp, right=0)
    new_fp = np.exp(new_fp)
    return new_fp

def save_combined_spectrum():
    """quickly recaculate the incident spectrum file.

    Only really used this during convergence testing"""
    # figure out file locations

    spectra_paths = []
    for spectra_file in trim_config.SPECTRA_FILES:
        spectra_paths.append(os.path.join(trim_config.SCRIPT_DIR, spectra_file))

    spectra = []
    for spectra_path in spectra_paths:
        spectra.append(extract_data(spectra_path))
    new_energies, combined_spectra = combine_spectra(spectra)
    df = pd.DataFrame(data=np.transpose([new_energies, combined_spectra]), columns=['Energy, MeV', 'IFlux, cm-2'])
    df.to_csv(trim_config.PROTON_SPECTRUM_FILE)
    return df

if __name__ == "__main__":
    save_combined_spectrum()

