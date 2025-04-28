"""Helper functions for numerics"""
import numpy as np

def log_interp(x, xp, fp):
    """logarithmic interpolator"""
    log_fp = np.log(fp)
    new_fp = np.interp(x, xp, log_fp, right=0)
    new_fp = np.exp(new_fp)
    return new_fp

def nearest_idx(values):
    """find the index of the nearest element of another list. Call as: nearest_idx(ruler)(thing to measure)"""
    def f(x):
        idx = np.argmin(np.abs(values - x))
        return idx
    return np.frompyfunc(f, 1, 1)

def bisect_search(x, f, error_tolerance):
    """bisection search for finding zeros of f over x. Assumes x is ordered smallest to largest and f is monotonic."""
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
    while error > error_tolerance:
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

def calc_IFlux(DFlux):
    """Turn protons at specific energies into an IFlux for nice plotting"""
    reverse_flux = np.flip(DFlux) #because SPENVIS calcs IFlux from high to low energy
    cumsum = np.cumsum(reverse_flux)
    return np.flip(cumsum)

def calc_DFlux(IFlux):
    """Turn an IFlux into a DFlux using the implcit energy grid

    Not really a DFlux because not energy normalized. Think of protons at specific energies."""
    DFlux = IFlux - np.roll(IFlux, -1)
    DFlux[-1] = IFlux[-1]
    return DFlux

def power_law(x, a, b):
    return a * x**b

if __name__ == "__main__":
    print(calc_DFlux([6,4,3,1,-1]))