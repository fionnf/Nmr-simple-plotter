"""Phase correction for NMR spectra."""

import numpy as np
from typing import Tuple
from scipy.optimize import minimize
from ..config import PhaseConfig


def correct_phase_manual(spectrum: np.ndarray, freq_axis: np.ndarray, phase0: float, phase1: float) -> np.ndarray:
    """Apply manual phase correction.

    Args:
        spectrum: Real spectrum
        freq_axis: Frequency axis
        phase0: Zero-order phase in degrees
        phase1: First-order phase in degrees/Hz

    Returns:
        Phase-corrected spectrum
    """
    phase0_rad = np.radians(phase0)
    phase1_rad = np.radians(phase1)

    # Apply phase correction
    phase_factor = np.exp(1j * (phase0_rad + phase1_rad * freq_axis))
    corrected = spectrum * phase_factor
    return np.real(corrected)


def _spectral_entropy(spectrum: np.ndarray) -> float:
    """Calculate normalized spectral entropy."""
    s = np.abs(spectrum)
    s = s / np.sum(s)
    entropy = -np.sum(s * np.log(s + 1e-10))
    return entropy


def correct_phase_auto(spectrum: np.ndarray, freq_axis: np.ndarray, method: str = "hybrid") -> Tuple[np.ndarray, float, float]:
    """Apply automatic phase correction using entropy minimization.

    Args:
        spectrum: Real spectrum
        freq_axis: Frequency axis
        method: "entropy" or "hybrid"

    Returns:
        Tuple of (corrected_spectrum, phase0, phase1)
    """
    def objective(phases):
        p0, p1 = phases
        corrected = correct_phase_manual(spectrum, freq_axis, p0, p1)
        return _spectral_entropy(corrected)

    # Initial guess
    x0 = [0.0, 0.0]
    bounds = [(-180, 180), (-10, 10)]

    result = minimize(objective, x0, method="L-BFGS-B", bounds=bounds)
    p0_opt, p1_opt = result.x

    corrected = correct_phase_manual(spectrum, freq_axis, p0_opt, p1_opt)
    return corrected, p0_opt, p1_opt


def apply_phase_correction(spectrum: np.ndarray, freq_axis: np.ndarray, config: PhaseConfig) -> np.ndarray:
    """Apply phase correction based on configuration.

    Args:
        spectrum: Input spectrum
        freq_axis: Frequency axis
        config: PhaseConfig object

    Returns:
        Phase-corrected spectrum
    """
    if config.auto:
        corrected, _, _ = correct_phase_auto(spectrum, freq_axis, config.entropy_method)
        return corrected
    else:
        return correct_phase_manual(spectrum, freq_axis, config.phase0, config.phase1)
