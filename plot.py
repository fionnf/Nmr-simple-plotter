#!/usr/bin/env python
"""Simple NMR plotter. Edit a YAML config and run:
    python plot.py -c examples/config_spinsolve.yaml
"""
import argparse
import yaml
import numpy as np
import nmrglue as ng
import matplotlib.pyplot as plt
from pathlib import Path


def process_spinsolve(path, lb=1.0, zf=1, phase="proc", p0=0.0, p1=0.0):
    """Load and process a Spinsolve FID. Returns (ppm_axis, hz_axis, real_spectrum)."""
    dic, data = ng.spinsolve.read(path)
    acqu = dic["acqu"]
    proc = dic["proc"]

    obs        = float(acqu["b1Freq"])            # MHz
    sw_hz      = float(acqu["bandwidth"]) * 1e3   # kHz → Hz
    ppm_offset = float(proc.get("ppmOffset", 0))
    p0_proc    = float(proc.get("p0Phase", 0))
    p1_proc    = float(proc.get("p1Phase", 0))

    # em expects lb in units of points: lb_pts = lb_hz / sw_hz
    if lb > 0:
        data = ng.proc_base.em(data, lb=lb / sw_hz)

    if zf > 1:
        data = ng.proc_base.zf_size(data, len(data) * zf)

    data = ng.proc_base.fft(data)

    if phase == "auto":
        data = ng.proc_autophase.autops(data, "acme")
    elif phase == "manual":
        data = ng.proc_base.ps(data, p0=p0, p1=p1)
    else:  # "proc" — use values from proc.par
        data = ng.proc_base.ps(data, p0=p0_proc, p1=p1_proc)

    npts   = len(data)
    sw_ppm = sw_hz / obs
    # ppm axis: high ppm on index 0 so inverted x-axis gives correct NMR display
    ppm = np.linspace(ppm_offset + sw_ppm / 2,
                      ppm_offset - sw_ppm / 2, npts)
    hz  = ppm * obs

    return ppm, hz, data.real


def main():
    parser = argparse.ArgumentParser(description="NMR Simple Plotter")
    parser.add_argument("-c", "--config", required=True)
    args = parser.parse_args()

    with open(args.config) as f:
        cfg = yaml.safe_load(f)

    # Resolve all paths relative to the YAML file's directory so the config
    # and figures can live inside the experiment folder.
    cfg_dir = Path(args.config).resolve().parent
    for spec in cfg["spectra"]:
        spec["path"] = str((cfg_dir / spec["path"]).resolve())
    cfg["output"] = str(cfg_dir / cfg.get("output", "spectrum"))

    fig_cfg  = cfg.get("figure", {})
    figsize  = fig_cfg.get("size", [4.5, 6.0])
    x_unit   = fig_cfg.get("x_unit", "ppm").lower()  # "ppm" or "hz"
    show_box = fig_cfg.get("box", False)
    show_y   = fig_cfg.get("y_axis", False)

    fig, ax = plt.subplots(figsize=figsize)

    for spec in cfg["spectra"]:
        ppm, hz, intensity = process_spinsolve(
            path  = spec["path"],
            lb    = spec.get("lb", 1.0),
            zf    = spec.get("zf", 1),
            phase = spec.get("phase", "proc"),
            p0    = spec.get("p0", 0.0),
            p1    = spec.get("p1", 0.0),
        )
        offset = spec.get("offset", 0.0)
        x_data = hz if x_unit == "hz" else ppm
        ax.plot(x_data, intensity + offset,
                label     = spec.get("label", ""),
                color     = spec.get("color"),
                linewidth = spec.get("linewidth", 1.0),
                alpha     = spec.get("alpha", 1.0))

    # X axis — auto-label based on x_unit unless overridden
    default_xlabel = {
        "ppm": "Chemical Shift (ppm)",
        "hz":  "Frequency Offset from Carrier (Hz)",
    }.get(x_unit, f"Chemical Shift ({x_unit})")
    xlabel = fig_cfg.get("xlabel", default_xlabel)
    ax.set_xlabel(xlabel)
    ax.invert_xaxis()

    xlim = fig_cfg.get("xlim")
    if xlim:
        ax.set_xlim(max(xlim), min(xlim))

    # Y axis visibility
    if not show_y:
        ax.yaxis.set_visible(False)
    else:
        ax.set_ylabel(fig_cfg.get("ylabel", "Intensity (a.u.)"))

    # Box / spines
    if show_box:
        for spine in ax.spines.values():
            spine.set_visible(True)
    else:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)

    # Legend
    legend_cfg = fig_cfg.get("legend", {})
    if legend_cfg.get("show", True) and any(s.get("label") for s in cfg["spectra"]):
        loc = legend_cfg.get("position", "upper right")
        # support [x, y] list for manual bbox_to_anchor placement
        if isinstance(loc, list):
            ax.legend(bbox_to_anchor=loc, loc="lower left",
                      fontsize=legend_cfg.get("fontsize", 9),
                      frameon=legend_cfg.get("frameon", False))
        else:
            ax.legend(loc=loc,
                      fontsize=legend_cfg.get("fontsize", 9),
                      frameon=legend_cfg.get("frameon", False))

    # Text annotations / labels
    for lbl in cfg.get("labels", []):
        if not lbl.get("show", True):
            continue
        ax.text(lbl["x"], lbl["y"],
                lbl["text"],
                color    = lbl.get("color", "black"),
                fontsize = lbl.get("fontsize", 9),
                ha       = lbl.get("ha", "center"),
                va       = lbl.get("va", "bottom"))

    ax.grid(False)
    fig.tight_layout()

    output = cfg.get("output", "figures/spectrum")
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    for fmt in cfg.get("formats", ["png", "pdf"]):
        filepath = f"{output}.{fmt}"
        fig.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"Saved: {filepath}")

    plt.close(fig)


if __name__ == "__main__":
    main()
