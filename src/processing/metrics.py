"""Metric calculations for NMR spectra."""

import numpy as np
from scipy.interpolate import interp1d
from scipy.integrate import trapezoid


def calculate_fwhm(spectrum: np.ndarray, freq_axis: np.ndarray, peak_index: int) -> float:
    """Calculate full-width at half-maximum (FWHM) for a peak.

    Args:
        spectrum: Input spectrum
        freq_axis: Frequency axis
        peak_index: Index of peak

    Returns:
        FWHM value in ppm
    """
    peak_height = spectrum[peak_index]
    half_height = peak_height / 2.0

    # Find left and right edges at half height
    # Search left
    left_idx = peak_index
    while left_idx > 0 and spectrum[left_idx] > half_height:
        left_idx -= 1

    # Search right
    right_idx = peak_index
    while right_idx < len(spectrum) - 1 and spectrum[right_idx] > half_height:
        right_idx += 1

    # Interpolate for more accurate boundaries
    if left_idx > 0:
        x_left = np.interp(half_height, [spectrum[left_idx], spectrum[left_idx+1]],
                          [freq_axis[left_idx], freq_axis[left_idx+1]])
    else:
        x_left = freq_axis[left_idx]

    if right_idx < len(spectrum) - 1:
        x_right = np.interp(half_height, [spectrum[right_idx], spectrum[right_idx-1]],
                           [freq_axis[right_idx], freq_axis[right_idx-1]])
    else:
        x_right = freq_axis[right_idx]

    fwhm = abs(x_right - x_left)
    return fwhm


def calculate_snr(spectrum: np.ndarray, freq_axis: np.ndarray, signal_region: tuple, noise_region: tuple) -> float:
    """Calculate signal-to-noise ratio.

    Args:
        spectrum: Input spectrum
        freq_axis: Frequency axis
        signal_region: (min, max) for signal region
        noise_region: (min, max) for noise region

    Returns:
        SNR value (dimensionless)
    """
    # Extract signal region
    sig_mask = (freq_axis >= signal_region[0]) & (freq_axis <= signal_region[1])
    signal = spectrum[sig_mask]

    # Extract noise region
    noise_mask = (freq_axis >= noise_region[0]) & (freq_axis <= noise_region[1])
    noise = spectrum[noise_mask]

    if len(signal) == 0 or len(noise) == 0:
        return 0.0

    signal_peak = np.max(signal)
    noise_std = np.std(noise)

    if noise_std == 0:
        return 0.0

    snr = signal_peak / noise_std
    return snr


def calculate_integral(spectrum: np.ndarray, freq_axis: np.ndarray, region: tuple) -> float:
    """Calculate integral (area under curve) for a region.

    Args:
        spectrum: Input spectrum
        freq_axis: Frequency axis
        region: (min, max) for integration region

    Returns:
        Integral value
    """
    mask = (freq_axis >= region[0]) & (freq_axis <= region[1])
    region_spec = spectrum[mask]
    region_freq = freq_axis[mask]

    if len(region_spec) < 2:
        return 0.0

    # Trapezoid rule integration
    integral = trapezoid(region_spec, region_freq)
    return integral


def calculate_spectral_entropy(spectrum: np.ndarray) -> float:
    """Calculate normalized spectral entropy.

    Args:
        spectrum: Input spectrum

    Returns:
        Entropy value (0-1 normalized)
    """
    s = np.abs(spectrum)
    s = s / np.sum(s)
    entropy = -np.sum(s * np.log(s + 1e-10))
    max_entropy = np.log(len(s))
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
    return normalized_entropy
