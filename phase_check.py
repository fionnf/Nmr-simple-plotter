#!/usr/bin/env python
"""Interactive phase correction tool.

Usage:
    python phase_check.py -p "examples/spinsolve_example/260714-160018 Fluorine1D (FF048_013)"
    python phase_check.py -p "..." --xlim -60 -220

Controls:
    Click on spectrum  — set peak anchor for autophase (green dashed line)
    p0 slider          — zero-order phase (degrees)
    p1 slider          — first-order phase (degrees)
    pivot slider       — ppm position fixed when sweeping p1 (red dashed line)
    Autophase          — optimise p0/p1, seeded from selected peak angle
    Zoom/Full          — toggle between --xlim window and full spectrum
    Print values       — print p0/p1 to terminal for copying into your YAML
"""
import argparse
import numpy as np
from scipy.optimize import minimize
import nmrglue as ng
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button


def load_fid(path, lb=5.0, zf=8):
    dic, data = ng.spinsolve.read(path)
    acqu = dic["acqu"]
    proc = dic["proc"]

    obs        = float(acqu["b1Freq"])
    sw_hz      = float(acqu["bandwidth"]) * 1e3
    ppm_offset = float(proc.get("ppmOffset", 0))
    p0_proc    = float(proc.get("p0Phase", 0))
    p1_proc    = float(proc.get("p1Phase", 0))

    if lb > 0:
        data = ng.proc_base.em(data, lb=lb / sw_hz)
    if zf > 1:
        data = ng.proc_base.zf_size(data, len(data) * zf)
    data = ng.proc_base.fft(data)

    npts   = len(data)
    sw_ppm = sw_hz / obs
    ppm    = np.linspace(ppm_offset + sw_ppm / 2,
                         ppm_offset - sw_ppm / 2, npts)
    return ppm, data, p0_proc, p1_proc


def apply_phase(fft_data, p0, p1, pivot_idx):
    """phase(i) = p0 + p1*(i - pivot_idx)/N  (slider convention)."""
    npts = len(fft_data)
    phase_rad = np.deg2rad(p0 + p1 * (np.arange(npts) - pivot_idx) / npts)
    return (fft_data * np.exp(1j * phase_rad)).real


def _entropy_cost(params, fft_data):
    """Minimum entropy cost, ng convention (pivot at index 0)."""
    p0, p1 = params
    npts = len(fft_data)
    phase_rad = np.deg2rad(p0 + p1 * np.arange(npts) / npts)
    real = (fft_data * np.exp(1j * phase_rad)).real
    shifted = real - real.min() + 1e-6
    p = shifted / shifted.sum()
    return float(np.sum(p * np.log(p)))


def _autophase(fft_data, peak_idx=None):
    """Minimise entropy to find (p0, p1) in ng convention.
    Seeds p0 from the phase angle at peak_idx if given."""
    p0_seed = -np.rad2deg(np.angle(fft_data[peak_idx])) if peak_idx is not None else 0.0
    res = minimize(
        _entropy_cost, [p0_seed, 0.0], args=(fft_data,),
        method="Nelder-Mead",
        options={"xatol": 0.05, "fatol": 1e-8, "maxiter": 2000},
    )
    return float(res.x[0]), float(res.x[1])


def main():
    parser = argparse.ArgumentParser(description="Interactive NMR phase correction")
    parser.add_argument("-p", "--path", required=True, help="Spinsolve experiment directory")
    parser.add_argument("--lb",   type=float, default=5.0, help="Line broadening in Hz")
    parser.add_argument("--zf",   type=int,   default=8,   help="Zero-fill factor")
    parser.add_argument("--xlim", nargs=2, type=float, default=None,
                        metavar=("HIGH", "LOW"), help="ppm zoom window e.g. --xlim -60 -220")
    args = parser.parse_args()

    ppm, fft_data, p0_init, p1_init = load_fid(args.path, lb=args.lb, zf=args.zf)
    N = len(fft_data)

    ppm_full_hi = ppm.max()
    ppm_full_lo = ppm.min()

    if args.xlim:
        ppm_zoom_hi, ppm_zoom_lo = max(args.xlim), min(args.xlim)
    else:
        ppm_zoom_hi, ppm_zoom_lo = ppm_full_hi, ppm_full_lo

    pivot_ppm_init = (ppm_zoom_hi + ppm_zoom_lo) / 2.0
    pivot_idx_init = int(np.argmin(np.abs(ppm - pivot_ppm_init)))

    zoomed           = [args.xlim is not None]
    selected_peak    = [None]   # ppm of clicked peak anchor

    # ── Layout ───────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(9, 5.5))
    fig.subplots_adjust(top=0.93, bottom=0.30, left=0.08, right=0.97)
    ax = fig.add_subplot(111)

    spec = apply_phase(fft_data, p0_init, p1_init, pivot_idx_init)
    (line,)     = ax.plot(ppm, spec, lw=0.8, color="tab:blue")
    pivot_vline = ax.axvline(pivot_ppm_init, color="red",   lw=0.8, ls="--", alpha=0.6)
    peak_vline  = ax.axvline(0,              color="green", lw=0.8, ls=":",  alpha=0.8)
    peak_vline.set_visible(False)

    ax.invert_xaxis()
    if zoomed[0]:
        ax.set_xlim(ppm_zoom_hi, ppm_zoom_lo)
    ax.set_xlabel("Chemical Shift (ppm)")
    for sp in ["top", "right", "left"]:
        ax.spines[sp].set_visible(False)
    ax.yaxis.set_visible(False)

    title = ax.set_title(
        f"p0 = {p0_init:.2f}°   p1 = {p1_init:.2f}°   pivot = {pivot_ppm_init:.2f} ppm"
        "   |   click spectrum to set peak anchor",
        fontsize=9,
    )

    # ── Sliders ──────────────────────────────────────────────────────────────
    ax_p0    = fig.add_axes([0.12, 0.20, 0.76, 0.04])
    ax_p1    = fig.add_axes([0.12, 0.13, 0.76, 0.04])
    ax_pivot = fig.add_axes([0.12, 0.06, 0.76, 0.04])

    sl_p0    = Slider(ax_p0,    "p0 (°)",      -180, 180,
                      valinit=p0_init, valstep=0.5)
    sl_p1    = Slider(ax_p1,    "p1 (°)",      -360, 360,
                      valinit=p1_init, valstep=1.0)
    sl_pivot = Slider(ax_pivot, "pivot (ppm)", ppm_full_lo, ppm_full_hi,
                      valinit=pivot_ppm_init, valstep=0.5)

    # ── Buttons ──────────────────────────────────────────────────────────────
    ax_btn_auto  = fig.add_axes([0.12, 0.01, 0.20, 0.04])
    ax_btn_zoom  = fig.add_axes([0.38, 0.01, 0.20, 0.04])
    ax_btn_print = fig.add_axes([0.64, 0.01, 0.20, 0.04])

    btn_auto  = Button(ax_btn_auto,  "Autophase")
    btn_zoom  = Button(ax_btn_zoom,  "Full spectrum" if zoomed[0] else "Zoom")
    btn_print = Button(ax_btn_print, "Print values")

    # ── Callbacks ────────────────────────────────────────────────────────────
    def redraw(p0, p1, pivot_ppm):
        pivot_idx = int(np.argmin(np.abs(ppm - pivot_ppm)))
        line.set_ydata(apply_phase(fft_data, p0, p1, pivot_idx))
        pivot_vline.set_xdata([pivot_ppm, pivot_ppm])
        ax.relim()
        ax.autoscale_view(scalex=False)
        anchor = f"   |   anchor = {selected_peak[0]:.2f} ppm" if selected_peak[0] is not None else \
                 "   |   click spectrum to set peak anchor"
        title.set_text(
            f"p0 = {p0:.2f}°   p1 = {p1:.2f}°   pivot = {pivot_ppm:.2f} ppm{anchor}"
        )
        fig.canvas.draw_idle()

    def on_slider(_):
        redraw(sl_p0.val, sl_p1.val, sl_pivot.val)

    def on_click(event):
        # Only respond to left-clicks in the spectrum axes (not sliders/buttons)
        if event.inaxes is not ax or event.button != 1:
            return
        selected_peak[0] = event.xdata
        peak_vline.set_xdata([event.xdata, event.xdata])
        peak_vline.set_visible(True)
        redraw(sl_p0.val, sl_p1.val, sl_pivot.val)

    def on_autophase(_):
        peak_idx = (int(np.argmin(np.abs(ppm - selected_peak[0])))
                    if selected_peak[0] is not None else None)

        title.set_text("Optimising…")
        fig.canvas.draw_idle()
        fig.canvas.flush_events()

        p0_ng, p1_ng = _autophase(fft_data, peak_idx)

        # Convert ng convention (pivot at index 0) → slider convention (current pivot)
        pivot_idx = int(np.argmin(np.abs(ppm - sl_pivot.val)))
        p0_slider = (p0_ng + p1_ng * pivot_idx / N + 180) % 360 - 180

        sl_p0.set_val(float(np.clip(p0_slider, -180, 180)))
        sl_p1.set_val(float(np.clip(p1_ng,     -360, 360)))

    def on_zoom(_):
        if zoomed[0]:
            ax.set_xlim(ppm_full_hi, ppm_full_lo)
            btn_zoom.label.set_text("Zoom")
            zoomed[0] = False
        else:
            ax.set_xlim(ppm_zoom_hi, ppm_zoom_lo)
            btn_zoom.label.set_text("Full spectrum")
            zoomed[0] = True
        fig.canvas.draw_idle()

    def on_print(_):
        p0, p1    = sl_p0.val, sl_p1.val
        pivot_ppm = sl_pivot.val
        pivot_idx = int(np.argmin(np.abs(ppm - pivot_ppm)))
        p0_yaml   = p0 - p1 * pivot_idx / N
        print("\n--- Copy into your YAML ---")
        print('    phase: "manual"')
        print(f"    p0: {p0_yaml:.2f}")
        print(f"    p1: {p1:.2f}")
        print("---------------------------\n")

    sl_p0.on_changed(on_slider)
    sl_p1.on_changed(on_slider)
    sl_pivot.on_changed(on_slider)
    fig.canvas.mpl_connect("button_press_event", on_click)
    btn_auto.on_clicked(on_autophase)
    btn_zoom.on_clicked(on_zoom)
    btn_print.on_clicked(on_print)

    plt.show()


if __name__ == "__main__":
    main()
