"""
Module that calculates the equivalent fluences using RDCs
"""
import numpy as np
import pandas as pd
import trim_config
import scipy.optimize
import trim_helper


def load_proton_rdc(rdc_file):
    """load rdc file and interpolate it onto the damage energy grid

    Use power law extrapolation for the UV and IR"""
    #load rdc file
    rdc = pd.read_csv(rdc_file)
    rdc = rdc.to_numpy()
    #get the data for fitting
    IR_data = rdc[:trim_config.POWER_LAW_FIT_POINTS]
    UV_data = rdc[-trim_config.POWER_LAW_FIT_POINTS:]
    #do the fit
    IR_fit = scipy.optimize.curve_fit(power_law, IR_data[:, 0], IR_data[:, 1], sigma = trim_config.CURVE_FIT_SIGMA)
    UV_fit = scipy.optimize.curve_fit(power_law, UV_data[:, 0], UV_data[:, 1], sigma = trim_config.CURVE_FIT_SIGMA)



    #break the damage energies into IR, middle, and UV
    IR_mask = trim_helper.DAMAGE_ENERGIES < min(rdc[:, 0])
    Mid_mask = (trim_helper.DAMAGE_ENERGIES > min(rdc[:, 0])) & (trim_helper.DAMAGE_ENERGIES < max(rdc[:, 0]))
    UV_mask = trim_helper.DAMAGE_ENERGIES > max(rdc[:, 0])




    return rdc

def power_law(x, a, b):
    return a * x**b

if __name__ == "__main__":
    load_proton_rdc(trim_config.PROTON_RDC_FILE)

    print(0)