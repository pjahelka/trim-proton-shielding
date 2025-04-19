This program is for simulating proton transmission through thin radiation shields where MC-SCREAM and EQFLUX are inadequate because MC-SCREAM overestimates low-energy proton damage and EQFLUX underestimates low-energy proton transmission. The code includes a SRIM application folder that includes a shortcut to TRIM that will run it minimized which will dramatically enhance simulation speed.

It's important to setup the shield layers via the TRIM GUI and then edit the code in trim_helper.config_trim for your shield stack.

Run the import_spectra script to combine SPENVIS proton spectra into a single file for later usage. It has magic constants for line identification you may need to edit.

There are two different energy discretization grids. One for the incoming proton spectrum and one for the shielded spectrum.
This is because the proton RDC data extends to lower energies than the proton spectrum data.

The default energy unit is MeV, but TRIM uses both keV and eV, so there are unit conversions floating around

Use calc_transmitted_spectrum for calculating the trasmitted proton spectrum. This can take a while. You can save the
spectrum, and analysis functions will assume it's been saved under trim_config.SCATTERING_MATRIX_FILE