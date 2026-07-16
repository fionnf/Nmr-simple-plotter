"""Baseline correction for NMR spectra."""

import numpy as np
from scipy.interpolate import UnivariateSpline
from ..config import BaselineConfig


def correct_baseline_polynomial(spectrum: np.ndarray, poly_order: int) -> np.ndarray:
    """Correct baseline using polynomial fit.

    Args:
        spectrum: Input spectrum
        poly_order: Order of polynomial (1-5)

    Returns:
        Baseline-corrected spectrum
    """
    x = np.arange(len(spectrum))
    # Fit polynomial to lowest 10% of points (background)
    threshold = np.percentile(spectrum, 10)
    mask = spectrum < threshold

    if mask.sum() > poly_order:
        coeffs = np.polyfit(x[mask], spectrum[mask], poly_order)
        baseline = np.polyval(coeffs, x)
    else:
        # Fallback: fit all points
        coeffs = np.polyfit(x, spectrum, poly_order)
        baseline = np.polyval(coeffs, x)

    return spectrum - baseline


def correct_baseline_airpls(spectrum: np.ndarray, lam: float = 1e4, niter: int = 10) -> np.ndarray:
    """Correct baseline using AIRPLS (Adaptive Iteratively Reweighted Penalized Least Squares).

    Args:
        spectrum: Input spectrum
        lam: Lambda parameter for smoothness
        niter: Number of iterations

    Returns:
        Baseline-corrected spectrum
    """
    x = np.arange(len(spectrum))

    # Initialize with polynomial fit
    coeffs = np.polyfit(x, spectrum, 3)
    baseline = np.polyval(coeffs, x)

    # Iterative refinement
    for _ in range(niter):
        weights = np.where(spectrum < baseline, 1.0, 0.1)
        coeffs = np.polyfit(x, spectrum, 3, w=weights)
        baseline = np.polyval(coeffs, x)

    return spectrum - baseline


def correct_baseline_spline(spectrum: np.ndarray, s: float = None) -> np.ndarray:
    """Correct baseline using spline fitting.

    Args:
        spectrum: Input spectrum
        s: Spline smoothing factor

    Returns:
        Baseline-corrected spectrum
    """
    x = np.arange(len(spectrum))

    # Use lowest 10% as anchor points for baseline
    threshold = np.percentile(spectrum, 10)
    mask = spectrum < threshold

    if mask.sum() > 4:
        # Fit spline to low points
        spline = UnivariateSpline(x[mask], spectrum[mask], s=s, k=min(3, mask.sum()-1))
        baseline = spline(x)
    else:
        # Fallback: polynomial
        coeffs = np.polyfit(x, spectrum, 2)
        baseline = np.polyval(coeffs, x)

    return spectrum - baseline


def apply_baseline_correction(spectrum: np.ndarray, config: BaselineConfig) -> np.ndarray:
    """Apply baseline correction based on configuration.

    Args:
        spectrum: Input spectrum
        config: BaselineConfig object

    Returns:
        Baseline-corrected spectrum
    """
    if config.method == "none":
        return spectrum
    elif config.method == "polynomial":
        return correct_baseline_polynomial(spectrum, config.poly_order)
    elif config.method == "airpls":
        return correct_baseline_airpls(spectrum)
    elif config.method == "spline":
        return correct_baseline_spline(spectrum)
    else:
        raise ValueError(f"Unknown baseline method: {config.method}")
