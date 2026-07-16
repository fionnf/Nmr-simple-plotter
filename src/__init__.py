"""NMR Simple Plotter - Config-driven NMR data processing and visualization."""

__version__ = "0.1.0"

from .config import Config
from .data_loader import DataLoader

__all__ = ["Config", "DataLoader"]
