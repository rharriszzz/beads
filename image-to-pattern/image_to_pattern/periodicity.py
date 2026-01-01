"""Periodicity detection and pattern extraction utilities."""

from __future__ import annotations

from typing import Iterable, List

import numpy as np


def normalized_autocorrelation(seq: Iterable[int], max_lag: int | None = None) -> np.ndarray:
    """Compute normalized autocorrelation for integer sequence."""
    arr = np.array(list(seq), dtype=float)
    n = len(arr)
    if n == 0:
        return np.array([])
    if max_lag is None or max_lag >= n:
        max_lag = n - 1
    arr = arr - arr.mean()
    var = np.var(arr)
    if var == 0:
        return np.ones(max_lag + 1)
    corrs = np.zeros(max_lag + 1)
    for lag in range(max_lag + 1):
        if lag == 0:
            corrs[lag] = 1.0
            continue
        a = arr[:-lag]
        b = arr[lag:]
        corrs[lag] = np.dot(a, b) / ((n - lag) * var)
    return corrs


def estimate_period(seq: Iterable[int], max_period: int | None = None, min_period: int = 1) -> int:
    """Estimate dominant period using autocorrelation peak."""
    arr = list(seq)
    if not arr:
        return 0
    if max_period is None:
        max_period = max(min(len(arr) // 2, 200), 1)
    corrs = normalized_autocorrelation(arr, max_lag=max_period)
    best_lag = 0
    best_val = -np.inf
    for lag in range(min_period, len(corrs)):
        if corrs[lag] > best_val:
            best_val = corrs[lag]
            best_lag = lag
    return best_lag


def extract_pattern(seq: Iterable[int], period: int) -> List[int]:
    """Extract one period from the sequence, assuming it repeats."""
    arr = list(seq)
    if period <= 0 or period > len(arr):
        return arr
    return arr[:period]
