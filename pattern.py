"""
pattern.py
----------
Detect repeating bead‐color patterns via signal processing and string algorithms.
"""

import numpy as np
from scipy.signal import correlate, find_peaks

def autocorrelation_period(color_seq):
    """
    Compute autocorrelation (via FFT) and return lag peaks.

    Peaks at lags indicate candidate pattern lengths :contentReference[oaicite:10]{index=10}.
    """
    seq = np.array(color_seq) - np.mean(color_seq)
    acf = correlate(seq, seq, mode='full')[len(seq)-1:]
    peaks, _ = find_peaks(acf, distance=1)
    return peaks

def kmp_prefix(s):
    """
    Build KMP prefix‐function π for sequence s in O(N) time.

    π[i] = length of longest proper prefix of s[:i+1] which is also a suffix. :contentReference[oaicite:11]{index=11}
    """
    n = len(s)
    pi = [0] * n
    for i in range(1, n):
        j = pi[i-1]
        while j > 0 and s[i] != s[j]:
            j = pi[j-1]
        if s[i] == s[j]:
            j += 1
        pi[i] = j
    return pi

def minimal_period(color_seq):
    """
    Derive minimal period p from π such that len(seq) % p == 0, else None.
    """
    pi = kmp_prefix(color_seq)
    p = len(color_seq) - pi[-1]
    return p if len(color_seq) % p == 0 else None
