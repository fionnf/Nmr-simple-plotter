#!/usr/bin/env python
"""Simple NMR plotting script - edit config YAML and run this."""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.data_loader import DataLoader
from src.processing.pipeline import process_spectrum
from src.processing.metrics import calculate_snr
from src.plotting.figure_builder import FigureBuilder


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
        print(f"\n✓ Loaded spectrum: {len(spectrum)} points")
        print(f"  Frequency range: {freq_axis.min():.1f} to {freq_axis.max():.1f} ppm")
        print(f"  Intensity range: {spectrum.min():.0f} to {spectrum.max():.0f}")

        # Process spectrum
        print(f"\n✓ Processing spectrum...")
        result = process_spectrum(freq_axis, spectrum, cfg)
        processed_spectrum = result["spectrum"]
        peaks = result["peak_indices"]
        print(f"  Baseline corrected: {cfg.processing.baseline.method}")
        print(f"  Phase correction: {'auto' if cfg.processing.phase.auto else 'manual'}")
        print(f"  Smoothing: {cfg.processing.smoothing.method}")
        print(f"  Peaks detected: {len(peaks)}")

        # Calculate metrics
        print(f"\n✓ Calculating metrics...")
        if cfg.analysis.snr.enabled and cfg.analysis.snr.signal_region and cfg.analysis.snr.noise_region:
            snr = calculate_snr(processed_spectrum, freq_axis, cfg.analysis.snr.signal_region, cfg.analysis.snr.noise_region)
            print(f"  SNR: {snr:.1f}")

        if len(peaks) > 0:
            print(f"  Peak positions: {[f'{freq_axis[p]:.1f}' for p in peaks[:3]]} ppm")

        # Create figure and plot
        print(f"\n✓ Creating figure...")
        builder = FigureBuilder(cfg)

        # Plot main spectrum
        builder.plot_spectrum(freq_axis, processed_spectrum, label=cfg.data_file)

        # Plot additional spectra from config.plots if defined
        if cfg.plots:
            print(f"  Plotting {len(cfg.plots)} spectra from config...")
            for plot_config in cfg.plots:
                try:
                    freq, spec = DataLoader.load(plot_config.file, cfg.data_format)
                    # Process this spectrum too
                    proc_result = process_spectrum(freq, spec, cfg)
                    proc_spec = proc_result["spectrum"]

                    builder.plot_spectrum(
                        freq, proc_spec,
                        label=plot_config.label,
                        color=plot_config.color,
                        linewidth=plot_config.linewidth,
                        linestyle=plot_config.linestyle,
                        alpha=plot_config.alpha
                    )
                except Exception as e:
                    print(f"  Warning: Could not load {plot_config.file}: {e}")

        builder.set_axis_labels()
        builder.configure_axes()

        # Save figure
        print(f"✓ Saving figure...")
        experiment_name = cfg.experiment_id or "spectrum"
        saved_files = builder.save(cfg.output_dir, experiment_name, cfg.output_formats)

        for filepath in saved_files:
            print(f"  → {filepath}")

        builder.close()

        print(f"\n✓ Complete!")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
