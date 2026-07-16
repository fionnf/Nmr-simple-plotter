#!/usr/bin/env python
"""Simple NMR plotting script - edit config YAML and run this."""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.data_loader import DataLoader
from src.plotter import cli


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="NMR Simple Plotter")
    parser.add_argument("-c", "--config", required=True, help="Path to YAML config file")
    parser.add_argument("-o", "--output-dir", help="Override output directory")
    args = parser.parse_args()

    try:
        # Load configuration
        cfg = Config.from_yaml(args.config)
        if args.output_dir:
            cfg.output_dir = args.output_dir

        print(f"✓ Loaded config: {args.config}")
        print(f"  Experiment: {cfg.experiment_id}")
        print(f"  Data file: {cfg.data_file}")
        print(f"  Output dir: {cfg.output_dir}")

        # Load data
        freq_axis, spectrum = DataLoader.load(cfg.data_file, cfg.data_format)
        print(f"✓ Loaded spectrum: {len(spectrum)} points")
        print(f"  Frequency range: {freq_axis.min():.1f} to {freq_axis.max():.1f} ppm")
        print(f"  Intensity range: {spectrum.min():.0f} to {spectrum.max():.0f}")

        print("\nNote: Full plotting pipeline coming in Phase 1-2")
        print("Config structure is ready - edit the YAML files in examples/ to adjust parameters")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
