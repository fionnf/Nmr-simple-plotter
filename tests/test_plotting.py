"""Tests for plotting module."""

import pytest
import tempfile
from pathlib import Path
import numpy as np
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.plotting.figure_builder import FigureBuilder
from src.plotting import styles


def test_style_templates():
    """Test style template loading."""
    nature_style = styles.get_style("nature")
    assert nature_style["font.family"] == "sans-serif"
    assert nature_style["font.size"] == 8

    jacs_style = styles.get_style("jacs")
    assert jacs_style["font.size"] == 9


def test_invalid_style():
    """Test invalid style raises error."""
    with pytest.raises(ValueError):
        styles.get_style("invalid_template")


def test_figure_builder_creation():
    """Test FigureBuilder initialization."""
    cfg = Config(data_file="test.csv")
    builder = FigureBuilder(cfg)

    assert builder.fig is not None
    assert builder.ax is not None
    builder.close()


def test_plot_spectrum():
    """Test plotting a spectrum."""
    cfg = Config(data_file="test.csv", experiment_id="test-exp")
    builder = FigureBuilder(cfg)

    # Create synthetic spectrum
    freq = np.linspace(-150, 50, 100)
    spectrum = 1000 * np.exp(-((freq + 90)**2 / (2 * 10**2)))

    builder.plot_spectrum(freq, spectrum, label="Test spectrum", color="blue")
    builder.set_axis_labels()
    builder.configure_axes()

    # Verify axes were configured
    assert builder.ax.get_xlabel() == "Chemical Shift (ppm)"
    assert builder.ax.get_ylabel() == "Intensity (a.u.)"

    builder.close()


def test_figure_save():
    """Test saving figure to file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = Config(data_file="test.csv", output_dir=tmpdir)
        builder = FigureBuilder(cfg)

        freq = np.linspace(-150, 50, 100)
        spectrum = 1000 * np.exp(-((freq + 90)**2 / (2 * 10**2)))

        builder.plot_spectrum(freq, spectrum)
        builder.set_axis_labels()
        builder.configure_axes()

        saved_files = builder.save(tmpdir, "test_plot", ["pdf", "png"])

        assert len(saved_files) == 2
        assert Path(saved_files[0]).exists()
        assert Path(saved_files[1]).exists()

        builder.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
