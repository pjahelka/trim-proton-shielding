"""configuration for the program"""
import numpy as np
import os


TRIM_AUTO = os.path.join(SCRIPT_DIR, r'SRIM\TRIMAUTO')
TRIM_IN = os.path.join(SCRIPT_DIR, r'SRIM\TRIM.IN')
TRIM_TRANSMIT = os.path.join(SCRIPT_DIR, r'SRIM\SRIM Outputs\TRANSMIT.txt')
#this link launches TRIM minimized which speeds it up a lot
TRIM_EXEC = os.path.join(SCRIPT_DIR, r'SRIM\TRIM_min.exe.lnk')



ANGLES = np.linspace(THETA_MIN, THETA_MAX, THETA_NUM, endpoint = True)
ANGLES = [round(angle, 1) for angle in ANGLES]