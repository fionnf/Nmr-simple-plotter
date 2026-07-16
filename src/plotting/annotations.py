"""Annotations for NMR figures (Phase 2 - placeholder)."""

from matplotlib.axes import Axes


def add_text_annotation(ax: Axes, text: str, xy: tuple, xytext: tuple = None, **kwargs) -> None:
    """Add text annotation to figure."""
    pass


def add_peak_markers(ax: Axes, peaks: list) -> None:
    """Add peak markers to figure."""
    pass


def add_inset(ax: Axes, inset_config: dict) -> None:
    """Add inset subplot."""
    pass
