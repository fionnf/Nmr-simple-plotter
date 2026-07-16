"""Tests for data loader module."""

import pytest
import tempfile
from pathlib import Path
import numpy as np
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import DataLoader


def test_load_csv():
    """Test CSV data loading."""
    # Create temporary CSV file
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_file = Path(tmpdir) / "test.csv"
        with open(csv_file, 'w') as f:
            f.write("chemical_shift,intensity\n")
            f.write("-100.0,500\n")
            f.write("-90.0,800\n")
            f.write("-80.0,600\n")

        freq, spectrum = DataLoader.load(str(csv_file), "csv")

        assert len(freq) == 3
        assert len(spectrum) == 3
        assert freq[0] == -100.0
        assert spectrum[0] == 500
        assert spectrum[1] == 800


def test_load_txt():
    """Test TXT data loading."""
    with tempfile.TemporaryDirectory() as tmpdir:
        txt_file = Path(tmpdir) / "test.txt"
        with open(txt_file, 'w') as f:
            f.write("-100.0 500\n")
            f.write("-90.0 800\n")
            f.write("-80.0 600\n")

        freq, spectrum = DataLoader.load(str(txt_file), "txt")

        assert len(freq) == 3
        assert len(spectrum) == 3
        assert freq[0] == -100.0
        assert spectrum[1] == 800


def test_invalid_format():
    """Test invalid format raises error."""
    with pytest.raises(ValueError):
        DataLoader.load("dummy.txt", "invalid_format")


def test_missing_file():
    """Test missing file raises error."""
    with pytest.raises(FileNotFoundError):
        DataLoader.load("nonexistent.csv", "csv")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
