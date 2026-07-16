"""Processing pipeline that coordinates all processing steps."""

import numpy as np
from typing import Tuple, Dict, Any

from ..config import Config
from .phase import apply_phase_correction
from .baseline import apply_baseline_correction
from .smoothing import apply_smoothing
from .peak_detection import apply_peak_picking


def process_spectrum(freq_axis: np.ndarray, spectrum: np.ndarray, config: Config) -> Dict[str, Any]:
    """Apply full processing pipeline to spectrum.

    Args:
        freq_axis: Frequency axis
        spectrum: Raw spectrum
        config: Config object with processing settings

    Returns:
        Dictionary with processed spectrum and metadata
    """
    processed = spectrum.copy()

    # Phase correction
    if config.processing.phase.auto or config.processing.phase.phase0 != 0 or config.processing.phase.phase1 != 0:
        processed = apply_phase_correction(processed, freq_axis, config.processing.phase)

    # Baseline correction
    if config.processing.baseline.method != "none":
        processed = apply_baseline_correction(processed, config.processing.baseline)

    # Smoothing
    if config.processing.smoothing.method != "none":
        processed = apply_smoothing(processed, config.processing.smoothing)

    # Peak detection
    peak_indices, peak_annotations = apply_peak_picking(processed, freq_axis, config.processing.peak_picking)

    return {
        "freq_axis": freq_axis,
        "spectrum": processed,
        "peak_indices": peak_indices,
        "peak_annotations": peak_annotations,
        "config": config,
    }
