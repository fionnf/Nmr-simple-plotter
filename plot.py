#!/usr/bin/env python
"""Simple NMR plotter for Spinsolve (Magritek) and TopSpin (Bruker) data.
Edit a YAML config and run:
    python plot.py -c examples/config_spinsolve.yaml
"""
import argparse
import datetime
import yaml
from pathlib import Path

import matplotlib.pyplot as plt

from nmr_io import process_spectrum


def format_nucleus(raw: str) -> str:
    """'19F' → '$^{19}$F',  '1H' → '$^{1}$H', etc."""
    import re
    m = re.match(r'^(\d+)([A-Za-z]+)$', raw.strip())
    if m:
        return f"$^{{{m.group(1)}}}${m.group(2)}"
    return raw


def _fmt_num(value) -> str:
    """Round floats to 3 decimals for display; pass through non-numeric values as-is."""
    return f"{value:.3f}" if isinstance(value, float) else str(value)


def write_log(output: str, cfg: dict, spectra_meta: list):
    """Write a plain-text log alongside the figure."""
    lines = [
        "=" * 60,
        "NMR PLOT LOG",
        f"Generated : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Config    : {cfg.get('_config_path', '')}",
        "=" * 60,
    ]

    for i, (spec_cfg, acqu, proc) in enumerate(spectra_meta):
        nucleus = acqu.get("nucleus", "")
        pulse_length = acqu.get(f"pulseLength{nucleus}", acqu.get("pulseLength", "N/A"))
        lines += [
            "",
            f"── Spectrum {i + 1}: {spec_cfg.get('label', spec_cfg['path'])}",
            f"   Path            : {spec_cfg['path']}",
            "",
            "   Acquisition parameters",
            f"     Experiment      : {acqu.get('experiment', 'N/A')}",
            f"     Nucleus         : {acqu.get('nucleus', 'N/A')}",
            f"     Frequency       : {float(acqu.get('b1Freq', 0)):.6f} MHz",
            f"     Bandwidth       : {_fmt_num(acqu.get('bandwidth', 'N/A'))} kHz",
            f"     Acq. time       : {_fmt_num(acqu.get('acqTime', 'N/A'))} ms",
            f"     Dwell time      : {_fmt_num(acqu.get('dwellTime', 'N/A'))} µs",
            f"     Nr. points      : {acqu.get('nrPnts', 'N/A')}",
            f"     Nr. scans       : {acqu.get('nrScans', 'N/A')}",
            f"     Rep. time       : {_fmt_num(acqu.get('repTime', 'N/A'))} ms",
            f"     Pulse length    : {pulse_length} µs",
            f"     RX gain         : {acqu.get('rxGain', 'N/A')}",
            f"     Software        : {acqu.get('softwareVersion', 'N/A')}",
            "",
            "   Processing parameters",
            f"     Phase mode      : {spec_cfg.get('phase', 'proc')}",
        ]
        phase_mode = spec_cfg.get("phase", "proc")
        if phase_mode == "manual":
            lines.append(f"     p0              : {spec_cfg.get('p0', 0.0):.2f}°")
            lines.append(f"     p1              : {spec_cfg.get('p1', 0.0):.2f}°")
        else:
            src = {"proc": "instrument-processed", "saved": "saved"}.get(phase_mode, phase_mode)
            lines.append(f"     p0 ({src})".ljust(20) + f": {float(proc.get('p0Phase', 0)):.3f}°")
            lines.append(f"     p1 ({src})".ljust(20) + f": {float(proc.get('p1Phase', 0)):.3f}°")
        lines += [
            f"     Line broadening : {spec_cfg.get('lb', 1.0)} Hz",
            f"     Zero-fill       : {spec_cfg.get('zf', 1)}×",
            f"     Vertical offset : {spec_cfg.get('offset', 0)}",
        ]

    fig_cfg = cfg.get("figure", {})
    lines += [
        "",
        "── Figure settings",
        f"   Size    : {fig_cfg.get('size', 'default')}",
        f"   x unit  : {fig_cfg.get('x_unit', 'ppm')}",
        f"   xlim    : {fig_cfg.get('xlim', 'full spectrum')}",
        f"   Formats : {cfg.get('formats', ['pdf'])}",
        "",
        "=" * 60,
    ]

    log_path = output + ".log"
    Path(log_path).write_text("\n".join(lines))
    print(f"Log:   {log_path}")


def main():
    parser = argparse.ArgumentParser(description="NMR Simple Plotter")
    parser.add_argument("-c", "--config", required=True)
    args = parser.parse_args()

    with open(args.config) as f:
        cfg = yaml.safe_load(f)

    cfg_dir = Path(args.config).resolve().parent
    cfg["_config_path"] = str(Path(args.config).resolve())
    for spec in cfg["spectra"]:
        spec["path"] = str((cfg_dir / spec["path"]).resolve())
    cfg["output"] = str(cfg_dir / cfg.get("output", "spectrum"))

    fig_cfg  = cfg.get("figure", {})
    figsize  = fig_cfg.get("size", [4.5, 6.0])
    x_unit   = fig_cfg.get("x_unit", "ppm").lower()  # "ppm" or "hz"
    show_box = fig_cfg.get("box", False)
    show_y   = fig_cfg.get("y_axis", False)

    fig, ax = plt.subplots(figsize=figsize)

    spectra_meta = []
    for spec in cfg["spectra"]:
        ppm, hz, intensity, acqu, proc = process_spectrum(
            path  = spec["path"],
            lb    = spec.get("lb", 1.0),
            zf    = spec.get("zf", 1),
            phase = spec.get("phase", "proc"),
            p0    = spec.get("p0", 0.0),
            p1    = spec.get("p1", 0.0),
        )
        spectra_meta.append((spec, acqu, proc))
        offset = spec.get("offset", 0.0)
        x_data = hz if x_unit == "hz" else ppm
        ax.plot(x_data, intensity + offset,
                label     = spec.get("label", ""),
                color     = spec.get("color"),
                linewidth = spec.get("linewidth", 1.0),
                alpha     = spec.get("alpha", 1.0))

    # X axis — auto-label from nucleus and x_unit unless overridden
    raw_nucleus = spectra_meta[0][1].get("nucleus", "") if spectra_meta else ""
    nucleus_str = format_nucleus(raw_nucleus) + " " if raw_nucleus else ""
    default_xlabel = {
        "ppm": f"{nucleus_str}Chemical Shift (ppm)",
        "hz":  f"{nucleus_str}Frequency Offset from Carrier (Hz)",
    }.get(x_unit, f"{nucleus_str}Chemical Shift ({x_unit})")
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
    write_log(output, cfg, spectra_meta)


if __name__ == "__main__":
    main()
