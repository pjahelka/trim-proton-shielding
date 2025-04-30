This program is for simulating proton transmission through thin solar cell proton shields. The code has two main steps. First is calculating a proton scattering matrix using TRIM that can be used to determine the proton-spectrum after the radiation shield. The second is then using the slowed spectrum and a relative damage coefficient (RDC) model to calculate equivalent fluxes that can then be used for predicting performance degradation.

It's important to set up the shield layers via the TRIM GUI and then edit the code in trim.py for your shield stack.

Use the import_spectra script to combine SPENVIS proton spectra into a single file for later usage. It has magic constants for line identification you may need to edit.

There are three different energy discretization grids. One for combining SPENVIS spectra, one for the TRIM simulation energies, and one for the shielded spectrum.
Fine SPENVIS and shielded spectra are computationally cheap, the TRIM simulations are computationally expensive.

The default energy unit is MeV, but TRIM uses both keV and eV, so there are unit conversions floating around in the code.

Use calc_transmitted_spectrum for calculating the transmitted proton spectrum. This can take a while. You can save the calculated scattering matrix and analysis functions will assume it's been saved as specified in the config file.

The code includes a SRIM application folder that includes a shortcut to TRIM that will run it minimized which will dramatically enhance simulation speed.

This work is supported by the Caltech Space Solar Power Project.
