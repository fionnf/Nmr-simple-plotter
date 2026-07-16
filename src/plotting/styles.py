"""Publication-quality style templates for NMR figures."""

import matplotlib.pyplot as plt
from typing import Dict, Any


# Journal-specific style templates
STYLES = {
    "nature": {
        "font.family": "sans-serif",
        "font.size": 8,
        "axes.labelsize": 8,
        "axes.titlesize": 10,
        "legend.fontsize": 7,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "lines.linewidth": 1.0,
        "axes.linewidth": 0.8,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
    },
    "jacs": {
        "font.family": "sans-serif",
        "font.size": 9,
        "axes.labelsize": 9,
        "axes.titlesize": 11,
        "legend.fontsize": 8,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "lines.linewidth": 1.5,
        "axes.linewidth": 1.0,
        "xtick.major.width": 1.0,
        "ytick.major.width": 1.0,
    },
    "custom": {
        "font.family": "sans-serif",
        "font.size": 10,
        "figure.dpi": 300,
        "savefig.dpi": 300,
    },
}


def get_style(template: str = "nature") -> Dict[str, Any]:
    """Get matplotlib style dictionary for a template.

    Args:
        template: Style template name (nature, jacs, custom)

    Returns:
        Dictionary of matplotlib rcParams
    """
    if template not in STYLES:
        raise ValueError(f"Unknown style template: {template}")
    return STYLES[template].copy()


def apply_style(template: str = "nature") -> None:
    """Apply matplotlib style template globally.

    Args:
        template: Style template name
    """
    style = get_style(template)
    plt.rcParams.update(style)
