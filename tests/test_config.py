"""Tests for configuration module."""

import pytest
import tempfile
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config, PhaseConfig, BaselineConfig, FigureConfig


def test_config_default():
    """Test default configuration creation."""
    cfg = Config(data_file="test.csv")
    assert cfg.data_file == "test.csv"
    assert cfg.data_format == "csv"
    assert cfg.output_formats == ["pdf", "png"]


def test_phase_config():
    """Test phase correction configuration."""
    phase_cfg = PhaseConfig(auto=True, phase0=10.0, phase1=5.0)
    assert phase_cfg.auto is True
    assert phase_cfg.phase0 == 10.0
    assert phase_cfg.phase1 == 5.0


def test_baseline_config():
    """Test baseline correction configuration."""
    baseline_cfg = BaselineConfig(method="polynomial", poly_order=3)
    assert baseline_cfg.method == "polynomial"
    assert baseline_cfg.poly_order == 3


def test_config_from_dict():
    """Test loading config from dictionary."""
    config_dict = {
        "data_file": "spectrum.csv",
        "data_format": "csv",
        "experiment_id": "exp-001",
    }
    cfg = Config.from_dict(config_dict)
    assert cfg.data_file == "spectrum.csv"
    assert cfg.experiment_id == "exp-001"


def test_config_yaml_roundtrip():
    """Test saving and loading YAML configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = Config(
            experiment_id="exp-001",
            data_file="spectrum.csv",
            data_format="csv",
        )

        yaml_path = Path(tmpdir) / "config.yaml"
        cfg.to_yaml(str(yaml_path))

        loaded_cfg = Config.from_yaml(str(yaml_path))
        assert loaded_cfg.experiment_id == cfg.experiment_id
        assert loaded_cfg.data_file == cfg.data_file
        assert loaded_cfg.data_format == cfg.data_format


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
