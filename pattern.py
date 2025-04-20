# pattern.py

import numpy as np
from scipy.signal import correlate, find_peaks

def autocorrelation_period(color_seq):
    """
    Compute autocorrelation and find peaks at candidate periods.
    """
    seq = np.array(color_seq) - np.mean(color_seq)
    acf = correlate(seq, seq, mode='full')[len(seq)-1:]
    peaks, _ = find_peaks(acf, distance=1)  # :contentReference[oaicite:9]{index=9}
    return peaks

def kmp_prefix(s):
    """
    Compute KMP prefix function π in O(N) to get minimal period.
    """
    n = len(s)
    pi = [0]*n
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
    Return minimal period if it divides sequence length.
    """
    pi = kmp_prefix(color_seq)
    p = len(color_seq) - pi[-1]
    if len(color_seq) % p == 0:
        return p
    return None
