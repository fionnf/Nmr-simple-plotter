"""Tests for data processing modules."""

import pytest
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processing.phase import apply_phase_correction, correct_phase_manual
from src.processing.baseline import apply_baseline_correction
from src.processing.smoothing import apply_smoothing
from src.processing.metrics import calculate_fwhm, calculate_snr, calculate_integral
from src.processing.peak_detection import detect_peaks
from src.config import Config, PhaseConfig, BaselineConfig, SmoothingConfig


@pytest.fixture
def synthetic_spectrum():
    """Create a simple synthetic spectrum for testing."""
    freq = np.linspace(-150, 50, 200)
    # Gaussian peak centered at -90 ppm
    spectrum = 1000 * np.exp(-((freq + 90)**2 / (2 * 10**2)))
    return freq, spectrum


def test_phase_correction_manual(synthetic_spectrum):
    """Test manual phase correction."""
    freq, spectrum = synthetic_spectrum
    corrected = correct_phase_manual(spectrum, freq, phase0=10.0, phase1=0.0)

    # Should preserve spectrum shape
    assert len(corrected) == len(spectrum)
    assert np.all(np.isfinite(corrected))


def test_baseline_correction_polynomial(synthetic_spectrum):
    """Test polynomial baseline correction."""
    freq, spectrum = synthetic_spectrum
    config = BaselineConfig(method="polynomial", poly_order=3)
    corrected = apply_baseline_correction(spectrum, config)

    # Should reduce baseline
    assert len(corrected) == len(spectrum)
    assert np.all(np.isfinite(corrected))


def test_baseline_none(synthetic_spectrum):
    """Test that no baseline correction returns same spectrum."""
    freq, spectrum = synthetic_spectrum
    config = BaselineConfig(method="none")
    corrected = apply_baseline_correction(spectrum, config)

    np.testing.assert_array_almost_equal(corrected, spectrum)


def test_smoothing_savgol(synthetic_spectrum):
    """Test Savitzky-Golay smoothing."""
    freq, spectrum = synthetic_spectrum
    config = SmoothingConfig(method="savgol", window_length=11, poly_order=3)
    smoothed = apply_smoothing(spectrum, config)

    assert len(smoothed) == len(spectrum)
    assert np.all(np.isfinite(smoothed))


def test_smoothing_none(synthetic_spectrum):
    """Test that no smoothing returns same spectrum."""
    freq, spectrum = synthetic_spectrum
    config = SmoothingConfig(method="none")
    smoothed = apply_smoothing(spectrum, config)

    np.testing.assert_array_almost_equal(smoothed, spectrum)


def test_calculate_fwhm(synthetic_spectrum):
    """Test FWHM calculation."""
    freq, spectrum = synthetic_spectrum
    # Find peak index
    peak_idx = np.argmax(spectrum)

    fwhm = calculate_fwhm(spectrum, freq, peak_idx)

    # For Gaussian with sigma=10, FWHM ~= 2.355 * sigma = 23.55
    assert fwhm > 0
    assert fwhm < 30  # Should be roughly 23.55


def test_calculate_snr(synthetic_spectrum):
    """Test SNR calculation."""
    freq, spectrum = synthetic_spectrum
    signal_region = (-100, -80)
    noise_region = (30, 50)

    snr = calculate_snr(spectrum, freq, signal_region, noise_region)

    assert snr > 0
    # For synthetic Gaussian peak, SNR can be very high
    assert snr > 100  # Should have good SNR


def test_calculate_integral(synthetic_spectrum):
    """Test integral calculation."""
    freq, spectrum = synthetic_spectrum
    region = (-100, -80)

    integral = calculate_integral(spectrum, freq, region)

    assert integral > 0


def test_detect_peaks(synthetic_spectrum):
    """Test peak detection."""
    freq, spectrum = synthetic_spectrum
    peaks = detect_peaks(spectrum, threshold=0.1, min_distance=5)

    # Should find at least one peak
    assert len(peaks) > 0
    # Peak should be near -90 ppm
    peak_freq = freq[peaks[0]]
    assert -95 < peak_freq < -85


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
