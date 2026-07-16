"""Spectral smoothing for NMR data."""

import numpy as np
from scipy.signal import savgol_filter
from scipy.ndimage import gaussian_filter1d
from ..config import SmoothingConfig


def smooth_savgol(spectrum: np.ndarray, window_length: int, poly_order: int) -> np.ndarray:
    """Apply Savitzky-Golay smoothing.

    Args:
        spectrum: Input spectrum
        window_length: Window length for smoothing (must be odd)
        poly_order: Polynomial order

    Returns:
        Smoothed spectrum
    """
    if window_length % 2 == 0:
        window_length += 1
    window_length = min(window_length, len(spectrum) - 1)
    poly_order = min(poly_order, window_length - 1)
    return savgol_filter(spectrum, window_length, poly_order)


def smooth_moving_average(spectrum: np.ndarray, window_length: int) -> np.ndarray:
    """Apply moving average smoothing.

    Args:
        spectrum: Input spectrum
        window_length: Window length for smoothing

    Returns:
        Smoothed spectrum
    """
    kernel = np.ones(window_length) / window_length
    smoothed = np.convolve(spectrum, kernel, mode='same')
    return smoothed


def smooth_gaussian(spectrum: np.ndarray, sigma: float) -> np.ndarray:
    """Apply Gaussian smoothing.

    Args:
        spectrum: Input spectrum
        sigma: Standard deviation for Gaussian

    Returns:
        Smoothed spectrum
    """
    return gaussian_filter1d(spectrum, sigma=sigma)


def apply_smoothing(spectrum: np.ndarray, config: SmoothingConfig) -> np.ndarray:
    """Apply smoothing based on configuration.

    Args:
        spectrum: Input spectrum
        config: SmoothingConfig object

    Returns:
        Smoothed spectrum
    """
    if config.method == "none":
        return spectrum
    elif config.method == "savgol":
        return smooth_savgol(spectrum, config.window_length, config.poly_order)
    elif config.method == "moving_average":
        return smooth_moving_average(spectrum, config.window_length)
    elif config.method == "gaussian":
        return smooth_gaussian(spectrum, config.window_length / 3.0)
    else:
        raise ValueError(f"Unknown smoothing method: {config.method}")
