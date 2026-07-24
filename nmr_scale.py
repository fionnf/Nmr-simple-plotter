#!/usr/bin/env python
"""Interactive vertical-scale adjustment for stacked/overlaid plots.

Usage:
    python nmr_scale.py -c plt_overlay1/plot.yaml
    python nmr_scale.py -c plt_overlay1/plot.yaml --xlim -60 -220

Loads every spectrum listed in the yaml (using each one's configured lb/zf/
phase), plots them together with their configured offsets, and gives each
one a scale slider (vertical intensity multiplier). Click "Save scales" to
write the resulting values back into the same plot.yaml's `scale:` key for
each spectrum, then rerun `nmr-plot` to render the final figure.
"""
import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

from nmr_io import process_spectrum, load_plot_config, resolve_config_path


def _spec_blocks(lines: list[str]) -> list[tuple[int, int]]:
    """Return (start, end) line-index ranges for each `- path:` spectrum entry."""
    starts = [i for i, l in enumerate(lines) if re.match(r'^\s*-\s*path\s*:', l)]
    blocks = []
    for idx, s in enumerate(starts):
        e = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
        for j in range(s + 1, e):
            if lines[j].strip() and not lines[j][0].isspace():
                e = j
                break
        blocks.append((s, e))
    return blocks


def save_scales(config_path: str, scales: list[float]) -> None:
    """Patch each spectrum's `scale:` value directly in the yaml text,
    preserving comments and formatting everywhere else in the file."""
    path = Path(config_path)
    lines = path.read_text().splitlines(keepends=True)
    blocks = _spec_blocks(lines)
    if len(blocks) != len(scales):
        raise ValueError("Spectrum count in the yaml changed since it was loaded — aborting save.")

    # Edit from the bottom up so earlier block indices stay valid after inserts.
    for (s, e), scale in reversed(list(zip(blocks, scales))):
        block = lines[s:e]
        scale_idx = None
        indent = "    "
        for j, l in enumerate(block):
            if re.match(r'^\s*#?\s*scale\s*:', l):
                scale_idx = j
                indent = re.match(r'^(\s*)', l).group(1)
                break
            m = re.match(r'^(\s*)(label|color|offset)\s*:', l)
            if m:
                indent = m.group(1)
        new_line = f"{indent}scale: {scale:.4f}\n"
        if scale_idx is not None:
            block[scale_idx] = new_line
        else:
            insert_at = len(block)
            for j, l in enumerate(block):
                if re.match(r'^\s*offset\s*:', l):
                    insert_at = j + 1
                    break
            block.insert(insert_at, new_line)
        lines[s:e] = block

    path.write_text("".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Interactive vertical-scale adjustment")
    parser.add_argument("-c", "--config", default=None,
                        help="plot.yaml to load and save scales into (defaults to ./plot.yaml)")
    parser.add_argument("--xlim", nargs=2, type=float, default=None,
                        metavar=("HIGH", "LOW"), help="ppm zoom window e.g. --xlim -60 -220")
    args = parser.parse_args()

    config_path = resolve_config_path(args.config)
    cfg = load_plot_config(config_path)
    specs = cfg["spectra"]
    fig_cfg = cfg.get("figure", {})
    x_unit = fig_cfg.get("x_unit", "ppm").lower()

    curves = []  # (x_data, intensity, offset) per spectrum
    for spec in specs:
        ppm, hz, intensity, acqu, proc = process_spectrum(
            path  = spec["path"],
            lb    = spec.get("lb", 1.0),
            zf    = spec.get("zf", 1),
            phase = spec.get("phase", "proc"),
            p0    = spec.get("p0", 0.0),
            p1    = spec.get("p1", 0.0),
        )
        x_data = hz if x_unit == "hz" else ppm
        curves.append((x_data, intensity, spec.get("offset", 0.0)))

    n = len(specs)
    scales_init = [float(spec.get("scale", 1.0)) for spec in specs]

    slider_h, slider_gap, buttons_h = 0.035, 0.012, 0.05
    bottom_margin = 0.03 + buttons_h + n * (slider_h + slider_gap)

    fig = plt.figure(figsize=(9, 5.5 + 0.4 * n))
    fig.subplots_adjust(top=0.93, bottom=bottom_margin, left=0.08, right=0.97)
    ax = fig.add_subplot(111)

    lines = []
    for (x_data, intensity, offset), spec, scale0 in zip(curves, specs, scales_init):
        (line,) = ax.plot(x_data, intensity * scale0 + offset,
                          lw=1.0, color=spec.get("color"),
                          label=spec.get("label", ""))
        lines.append(line)

    ax.invert_xaxis()
    if args.xlim:
        ax.set_xlim(max(args.xlim), min(args.xlim))
    for sp in ["top", "right", "left"]:
        ax.spines[sp].set_visible(False)
    ax.yaxis.set_visible(False)
    if any(s.get("label") for s in specs):
        ax.legend(fontsize=9, frameon=False)
    ax.set_xlabel(f"Chemical Shift ({x_unit})")
    title = ax.set_title("Adjust scale sliders, then click Save scales", fontsize=9)

    sliders = []
    for i, spec in enumerate(specs):
        y = 0.03 + buttons_h + i * (slider_h + slider_gap)
        ax_s = fig.add_axes([0.16, y, 0.60, slider_h])
        label = (spec.get("label") or f"spec {i + 1}")[:16]
        sl = Slider(ax_s, label, 0.0, 5.0, valinit=scales_init[i], valstep=0.01)
        sliders.append(sl)

    def redraw(_=None):
        for line, (x_data, intensity, offset), sl in zip(lines, curves, sliders):
            line.set_ydata(intensity * sl.val + offset)
        ax.relim()
        ax.autoscale_view(scalex=False)
        fig.canvas.draw_idle()

    for sl in sliders:
        sl.on_changed(redraw)

    ax_btn_reset = fig.add_axes([0.16, 0.03, 0.18, buttons_h - 0.012])
    ax_btn_print = fig.add_axes([0.38, 0.03, 0.18, buttons_h - 0.012])
    ax_btn_save  = fig.add_axes([0.60, 0.03, 0.18, buttons_h - 0.012])
    btn_reset = Button(ax_btn_reset, "Reset")
    btn_print = Button(ax_btn_print, "Print values")
    btn_save  = Button(ax_btn_save,  "Save scales")

    def on_reset(_):
        for sl, s0 in zip(sliders, scales_init):
            sl.set_val(s0)

    def on_print(_):
        print("\n--- Copy into your plot.yaml (or click Save scales) ---")
        for spec, sl in zip(specs, sliders):
            print(f"  {spec.get('label', spec['path'])}: scale: {sl.val:.4f}")
        print("---------------------------------------------------------\n")

    def on_save(_):
        try:
            save_scales(config_path, [sl.val for sl in sliders])
        except ValueError as e:
            title.set_text(f"Save failed: {e}")
            fig.canvas.draw_idle()
            return
        print(f"Saved scales to: {config_path}")
        title.set_text(f"Saved scales to {Path(config_path).name}")
        fig.canvas.draw_idle()

    btn_reset.on_clicked(on_reset)
    btn_print.on_clicked(on_print)
    btn_save.on_clicked(on_save)

    plt.show()


if __name__ == "__main__":
    main()
