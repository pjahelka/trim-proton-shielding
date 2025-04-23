This program is for simulating proton transmission through thin solar cell proton shields where MC-SCREAM and EQFLUX are inadequate because the NIEL method of MC-SCREAM overestimates low-energy proton damage and EQFLUX underestimates low-energy proton transmission. The code has two main steps. First is calculating a proton scattering matrix using TRIM that can be used to determine the proton-spectrum after the radiation shield. The second is then uisng the slowed spectrum and a relative damage coefficient (RDC) model to calculate equivalent fluences that can then be used for predicting performance degredation.

It's important to setup the shield layers via the TRIM GUI and then edit the code in trim_helper.config_trim for your shield stack.

Run the import_spectra script to combine SPENVIS proton spectra into a single file for later usage. It has magic constants for line identification you may need to edit.

There are three different energy discretization grids. One for combinding SPENVIS spectra, one for the TRIM simulation energies, and one for the shielded spectrum.
Fine SPENVIS and shielded spectra are computationally cheap, the TRIM simulations are computationally expensive.

The default energy unit is MeV, but TRIM uses both keV and eV, so there are unit conversions floating around in the code.

Use calc_transmitted_spectrum for calculating the trasmitted proton spectrum. This can take a while. You can save the calculated scattering matrix and analysis functions will assume it's been saved under trim_config.SCATTERING_MATRIX_FILE.

The code includes a SRIM application folder that includes a shortcut to TRIM that will run it minimized which will dramatically enhance simulation speed.

Based on convergence testing, some sane defaults for trim_config.py are:
THETA_NUM = 15
PROTONS_SIMULATE = 1E2
PROTONS_TEST_TRANSMIT = 1E1
PROTONS_TEST_BLOCK = 1E1
SPECTRUM_ENERGIES_PER_DECADE = 20

On an 8840HS CPU, a simulation takes about five minutes, limited by TRIM calling the Windows display server.

This work is supported by the Caltech Space Solar Power Project.