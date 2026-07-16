"""Figure construction and layout for NMR plots."""

from typing import Tuple, Optional
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np
from pathlib import Path
from ..config import Config
from . import styles


class FigureBuilder:
    """Builder class for creating matplotlib figures from config."""

    def __init__(self, config: Config):
        """Initialize figure builder with configuration.

        Args:
            config: Config object
        """
        self.config = config
        self.fig = None
        self.ax = None
        self._create_figure()

    def _create_figure(self) -> None:
        """Create figure with styling from config."""
        # Apply style
        styles.apply_style(self.config.figure_style.template)

        # Calculate figure size in inches (for Nature: 180mm = 7.09 inches)
        fig_width = self.config.figure_style.font_size / 72.0 * 35  # Rough conversion
        fig_height = fig_width * 0.6  # Standard aspect ratio

        self.fig, self.ax = plt.subplots(
            figsize=(fig_width, fig_height),
            dpi=self.config.figure_style.dpi
        )

    def plot_spectrum(self, freq_axis: np.ndarray, spectrum: np.ndarray, label: str = "",
                     color: Optional[str] = None, linewidth: float = 1.5,
                     linestyle: str = "solid", alpha: float = 0.9) -> None:
        """Plot a spectrum on the axes.

        Args:
            freq_axis: Frequency axis
            spectrum: Spectrum data
            label: Label for legend
            color: Line color
            linewidth: Line width
            linestyle: Line style (solid, dashed, dotted)
            alpha: Transparency
        """
        plot_params = {
            "linewidth": linewidth,
            "linestyle": linestyle,
            "alpha": alpha,
        }
        if color:
            plot_params["color"] = color

        self.ax.plot(freq_axis, spectrum, label=label, **plot_params)

    def set_axis_labels(self) -> None:
        """Set axis labels and limits from config."""
        self.ax.set_xlabel(self.config.figure.xlabel)
        self.ax.set_ylabel(self.config.figure.ylabel)

        if self.config.figure.title:
            self.ax.set_title(self.config.figure.title)

        if self.config.figure.xlim:
            self.ax.set_xlim(self.config.figure.xlim)

        if self.config.figure.ylim:
            self.ax.set_ylim(self.config.figure.ylim)

    def configure_axes(self) -> None:
        """Configure axes appearance from config."""
        if self.config.figure.grid:
            self.ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)

        # Legend
        if self.ax.get_legend_handles_labels()[0]:
            self.ax.legend(
                loc=self.config.figure.legend_position,
                frameon=self.config.figure.legend_frameon,
                fontsize=self.config.figure.legend_fontsize
            )

        self.fig.tight_layout()

    def save(self, output_dir: str, name: str = "spectrum", formats: list = None) -> list:
        """Save figure to file(s).

        Args:
            output_dir: Output directory path
            name: Base filename without extension
            formats: List of formats (png, pdf, svg)

        Returns:
            List of saved file paths
        """
        if formats is None:
            formats = self.config.output_formats

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        saved_files = []

        for fmt in formats:
            filepath = Path(output_dir) / f"{name}.{fmt}"
            if fmt == "png":
                self.fig.savefig(str(filepath), dpi=300, bbox_inches="tight")
            else:
                self.fig.savefig(str(filepath), bbox_inches="tight")
            saved_files.append(str(filepath))

        return saved_files

    def close(self) -> None:
        """Close figure."""
        plt.close(self.fig)
