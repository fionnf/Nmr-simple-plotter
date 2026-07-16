"""Main CLI entry point for NMR plotter."""

import click
from pathlib import Path
from .config import Config
from .data_loader import DataLoader
import sys


@click.group()
def cli():
    """NMR Simple Plotter - Config-driven NMR data processing and visualization."""
    pass


@cli.command()
@click.option('--config', '-c', required=True, type=click.Path(exists=True),
              help='Path to YAML configuration file')
@click.option('--output-dir', '-o', type=click.Path(), default=None,
              help='Override output directory from config')
def plot(config, output_dir):
    """Generate NMR plot from configuration file."""
    try:
        cfg = Config.from_yaml(config)

        if output_dir:
            cfg.output_dir = output_dir

        # Load data
        freq_axis, spectrum = DataLoader.load(cfg.data_file, cfg.data_format)

        click.echo(f"Loaded spectrum from: {cfg.data_file}")
        click.echo(f"Spectrum shape: {spectrum.shape}")
        click.echo(f"Output directory: {cfg.output_dir}")
        click.echo(f"Output formats: {', '.join(cfg.output_formats)}")

        # TODO: Apply processing, plotting, export in subsequent phases

        click.echo("✓ Plot generation would occur here (Phase 2+)")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--output', '-o', type=click.Path(), default='example_config.yaml',
              help='Output path for example configuration')
def init_config(output):
    """Generate an example configuration file."""
    example_config = Config(
        experiment_id="exp-001",
        data_file="data/spectrum.csv",
        data_format="csv",
        output_dir="figures",
    )
    example_config.to_yaml(output)
    click.echo(f"✓ Example configuration saved to: {output}")


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
def validate(config_file):
    """Validate a configuration file."""
    try:
        cfg = Config.from_yaml(config_file)
        click.echo("✓ Configuration is valid")
        click.echo(f"  Experiment: {cfg.experiment_id}")
        click.echo(f"  Data file: {cfg.data_file}")
        click.echo(f"  Output formats: {', '.join(cfg.output_formats)}")
    except Exception as e:
        click.echo(f"✗ Configuration error: {e}", err=True)
        sys.exit(1)


def main():
    """Entry point for console script."""
    cli()


if __name__ == '__main__':
    main()
