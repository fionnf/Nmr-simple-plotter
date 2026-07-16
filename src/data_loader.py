"""Data loader for NMR spectral data from various formats."""

import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import h5py
import csv


class DataLoader:
    """Abstract base class for loading NMR data."""

    @staticmethod
    def load(filepath: str, data_format: str = "csv") -> Tuple[np.ndarray, np.ndarray]:
        """Load NMR data from file.

        Args:
            filepath: Path to data file
            data_format: Format of data file (spinsolve_h5, bruker_fid, csv, txt)

        Returns:
            Tuple of (chemical_shift, intensity) arrays
        """
        if data_format == "spinsolve_h5":
            return DataLoader.load_spinsolve_h5(filepath)
        elif data_format == "bruker_fid":
            return DataLoader.load_bruker_fid(filepath)
        elif data_format == "csv":
            return DataLoader.load_csv(filepath)
        elif data_format == "txt":
            return DataLoader.load_txt(filepath)
        else:
            raise ValueError(f"Unsupported data format: {data_format}")

    @staticmethod
    def load_spinsolve_h5(filepath: str) -> Tuple[np.ndarray, np.ndarray]:
        """Load Spinsolve HDF5 format NMR data.

        Spinsolve exports FID data in HDF5 format with processing metadata.
        This loads the processed 1D spectrum and frequency axis.
        """
        with h5py.File(filepath, 'r') as f:
            # Typical Spinsolve HDF5 structure
            if 'Spectrum' in f:
                spectrum = f['Spectrum'][:]
            else:
                # Fallback: look for any 1D dataset
                spectrum = f[list(f.keys())[0]][:]

            if 'FrequencyAxis' in f:
                freq_axis = f['FrequencyAxis'][:]
            else:
                # Generate frequency axis if not provided
                freq_axis = np.arange(len(spectrum))

        return freq_axis, spectrum

    @staticmethod
    def load_bruker_fid(filepath: str) -> Tuple[np.ndarray, np.ndarray]:
        """Load Bruker TopSpin FID format.

        Bruker FID files are binary with associated parameter files.
        For now, this is a placeholder that assumes FID is stored as binary float32.
        """
        fid_path = Path(filepath)
        if not fid_path.exists():
            raise FileNotFoundError(f"FID file not found: {filepath}")

        # Read binary FID data (assuming 32-bit float)
        with open(filepath, 'rb') as f:
            fid_data = np.fromfile(f, dtype=np.float32)

        # FFT to get spectrum
        spectrum = np.abs(np.fft.fft(fid_data))
        freq_axis = np.fft.fftfreq(len(fid_data))

        return freq_axis, spectrum

    @staticmethod
    def load_csv(filepath: str) -> Tuple[np.ndarray, np.ndarray]:
        """Load NMR data from CSV file.

        Expected format: two columns (chemical_shift, intensity)
        """
        data = np.genfromtxt(filepath, delimiter=',', skip_header=1)
        if data.ndim == 1:
            raise ValueError("CSV file must have at least 2 columns")
        return data[:, 0], data[:, 1]

    @staticmethod
    def load_txt(filepath: str) -> Tuple[np.ndarray, np.ndarray]:
        """Load NMR data from text file (space or tab-separated).

        Expected format: two columns (chemical_shift, intensity)
        """
        data = np.genfromtxt(filepath)
        if data.ndim == 1:
            raise ValueError("Text file must have at least 2 columns")
        return data[:, 0], data[:, 1]


def load_spectrum(filepath: str, data_format: str = "csv") -> Tuple[np.ndarray, np.ndarray]:
    """Convenience function to load spectrum data."""
    return DataLoader.load(filepath, data_format)
