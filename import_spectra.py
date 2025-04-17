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
import trim_helper
import re
import pandas as pd


#figure out file locations
spectra_files = [
    r"spectra\\15yr_geo_solar.txt",
    r"spectra\\15yr_geo_trapped.txt"
]
spectra_paths = []
for spectra_file in spectra_files:
    spectra_paths.append(os.path.join(trim_config.script_dir, spectra_file))

#lines in each file that mean we've gotten to real data lines
solar_last_header = r"'Exposure','hrs', 1,'Proton Exposure Time'"
trapped_last_header = r"'DFlux','cm!u-2!n s!u-1!n MeV!u-1!n', 1,'Differential Flux'"
trapped_duration_line = 43 - 1 #line number of mission duration for trapped spectra. This may vary SPENVIS-run to SEPNVIS-run

#and the end of data line
first_footer = r"'End of Block'"

def extract_data(file):
    duration = 0 #length of segment, used for figuring out if trapped proton spectra
    data = []
    data_line = False
    trapped = False #for figuring out if we need to deal with duration
    with open(file) as f:
        lines = f.readlines()
        duration = re.findall(r"\d+\.\d+", lines[trapped_duration_line])  # extract duration in days
        if duration:
            duration = float(duration[0])
            duration = duration * 31.5E6  # convert to seconds
        for line in lines:
            if line.startswith(solar_last_header): #figure out if start of data block and if trapped or solar
                data_line = True
                continue
            if line.startswith(trapped_last_header):
                data_line = True
                trapped = True
                continue
            if line.startswith(first_footer): #figure out if end of data block
                break
            if data_line:
                data.append(np.fromstring(line, sep=','))
    data = np.array(data)
    data = data[:,[0,2]] #select energies and DFlux
    if trapped:
        data[:,1] = data[:,1] * duration #turn flux/s to flux for trapped spectra
    #get rid of rows with zero-fluxes
    mask = data[:,1] != 0
    return data[mask]

def combine_spectra(spectra_table): #argument is a list of proton spectra
    #find the extremal energies in the data
    min_energies = []
    max_energies = []
    for spectra in spectra_table:
        min_energies.append(np.min(spectra[:,0]))
        max_energies.append(np.max(spectra[:,0]))
    min_energy = min(min_energies)
    max_energy = max(max_energies)
    #calculate how many decades of data and the number of sample points
    decades = np.log10(max_energy/min_energy)
    num_samp = round(decades * trim_config.energies_per_decade)
    #generate the new energy grid to use
    new_energies = np.logspace(np.log10(min_energy), np.log10(max_energy), num_samp)
    resampled_spectra = []
    #resample the spectra using logarithmic interpolation
    for spectra in spectra_table:
        resampled_spectrum = trim_helper.log_interp(new_energies, spectra[:, 0], spectra[:, 1])
        resampled_spectra.append(resampled_spectrum)
    #sum and return
    resampled_spectrum = np.sum(resampled_spectra, axis = 0)
    return new_energies, resampled_spectrum

if __name__ == "__main__":
    spectra = []
    for spectra_path in spectra_paths:
        spectra.append(extract_data(spectra_path))
    new_energies, combined_spectra = combine_spectra(spectra)
    import matplotlib.pyplot as plt
    foo = extract_data(spectra_paths[0])
    plt.plot(foo[:, 0], foo[:, 1])
    foo = extract_data(spectra_paths[1])
    plt.plot(foo[:,0], foo[:,1])
    plt.plot(new_energies, combined_spectra)
    plt.yscale('log')
    plt.xscale('log')
    plt.show()
    df = pd.DataFrame(data=np.transpose([new_energies, combined_spectra]), columns=['Energy, MeV', 'DFlux, cm-2 MeV-1'])
    df.to_csv(trim_config.proton_spectrum_file)
