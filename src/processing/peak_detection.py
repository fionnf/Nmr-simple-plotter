"""Peak detection and annotation for NMR spectra."""

import numpy as np
from typing import List, Tuple, Dict
from scipy.signal import find_peaks
from .metrics import calculate_fwhm
from ..config import PeakPickingConfig


def detect_peaks(spectrum: np.ndarray, threshold: float, min_distance: float) -> np.ndarray:
    """Detect peaks in spectrum.

    Args:
        spectrum: Input spectrum
        threshold: Peak height threshold (fraction of max)
        min_distance: Minimum distance between peaks (points)

    Returns:
        Array of peak indices
    """
    max_height = np.max(spectrum)
    height_threshold = threshold * max_height

    peaks, _ = find_peaks(spectrum, height=height_threshold, distance=min_distance)
    return peaks


def annotate_peaks(spectrum: np.ndarray, freq_axis: np.ndarray, peak_indices: np.ndarray) -> List[Dict]:
    """Annotate detected peaks with position, height, width.

    Args:
        spectrum: Input spectrum
        freq_axis: Frequency axis
        peak_indices: Indices of detected peaks

    Returns:
        List of peak annotations
    """
    annotations = []

    for peak_idx in peak_indices:
        fwhm = calculate_fwhm(spectrum, freq_axis, peak_idx)
        annotation = {
            "index": int(peak_idx),
            "position_ppm": float(freq_axis[peak_idx]),
            "height": float(spectrum[peak_idx]),
            "fwhm": float(fwhm),
        }
        annotations.append(annotation)

    return annotations


def apply_peak_picking(spectrum: np.ndarray, freq_axis: np.ndarray, config: PeakPickingConfig) -> Tuple[np.ndarray, List[dict]]:
    """Apply peak picking based on configuration.

    Args:
        spectrum: Input spectrum
        freq_axis: Frequency axis
        config: PeakPickingConfig object

    Returns:
        Tuple of (peak_indices, peak_annotations)
    """
    if not config.enabled:
        return np.array([]), []

    # Convert min_distance from ppm to points
    if len(freq_axis) > 1:
        ppm_per_point = (freq_axis[-1] - freq_axis[0]) / (len(freq_axis) - 1)
        min_dist_points = max(1, int(config.min_distance / abs(ppm_per_point)))
    else:
        min_dist_points = 1

    peaks = detect_peaks(spectrum, config.threshold, min_dist_points)
    annotations = []
    if config.annotate:
        annotations = annotate_peaks(spectrum, freq_axis, peaks)

    return peaks, annotations
