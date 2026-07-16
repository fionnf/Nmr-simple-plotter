# NMR Simple Plotter

Config-driven NMR plotting tool for Spinsolve (Magritek) data using nmrglue. Edit a YAML file, run one command, get a publication-ready figure.

## Quick Start

```bash
pip install -r requirements.txt
python plot.py -c examples/config_spinsolve.yaml
```

## Scripts

| Script | Purpose |
|--------|---------|
| `plot.py` | Main plotter — reads a YAML config and saves figures |
| `phase_check.py` | Interactive phase correction with live sliders |

## Plotting

```bash
python plot.py -c examples/config_spinsolve.yaml
```

Figures are saved to the path set in `output:` (default `figures/`).

## Phase Correction

If the phase from `proc.par` doesn't look right, use the interactive tool to find good values:

```bash
python phase_check.py -p "examples/spinsolve_example/260714-160018 Fluorine1D (FF048_013)"

# optional flags
#   --lb 5.0          line broadening in Hz
#   --zf 8            zero-fill factor
#   --xlim -60 -220   ppm display range
```

Three sliders are shown:
- **p0** — zero-order (constant) phase shift
- **p1** — first-order (frequency-dependent) phase shift
- **pivot** — the ppm position that stays fixed when sweeping p1 (shown as a red dashed line); set this to your main peak before adjusting p1

Click **Print values** to copy the corrected p0/p1 into your YAML.

## YAML Config Reference

```yaml
# One or more spectra — overlay them by listing multiple entries
spectra:
  - path: "path/to/spinsolve/experiment/directory"
    label: "Sample A"           # legend label
    color: "tab:blue"
    linewidth: 1.0
    alpha: 1.0
    lb: 5.0                     # line broadening in Hz
    zf: 8                       # zero-fill factor
    offset: 0                   # vertical shift for stacking (intensity units)
    phase: "proc"               # "proc" | "auto" | "manual"
    # p0: 0.0                   # used only when phase: "manual"
    # p1: 0.0

  # - path: "path/to/second/experiment"
  #   label: "Sample B"
  #   color: "tab:orange"
  #   offset: 35                # stack above first spectrum

figure:
  size: [7.0, 2.5]             # [width, height] inches
  x_unit: "ppm"               # "ppm" → auto "Chemical Shift (ppm)"
                              # "hz"  → auto "Frequency Offset from Carrier (Hz)"
  # xlabel: "override"        # uncomment to override the auto label
  xlim: [-60, -220]           # display window

  box: false                  # true = full box, false = bottom spine only
  y_axis: false               # true = show y-axis and label
  ylabel: "Intensity (a.u.)"  # only shown when y_axis: true

  legend:
    show: true
    position: "upper right"   # string or [x, y] for manual placement
    fontsize: 9
    frameon: false

# Text annotations on the spectrum
# labels:
#   - text: "peak A"
#     x: -130.5               # in ppm (or Hz if x_unit: "hz")
#     y: 27.0                 # in intensity units
#     color: "black"
#     fontsize: 9
#     ha: "center"            # "left" | "center" | "right"
#     va: "bottom"            # "top" | "center" | "bottom"

output: "figures/spectrum"
formats: ["png", "pdf"]       # any combination of "png", "pdf", "svg"
```

### Phase options

| Value | Behaviour |
|-------|-----------|
| `"proc"` | Uses `p0Phase` / `p1Phase` stored in `proc.par` by the Spinsolve software |
| `"auto"` | nmrglue ACME autophase algorithm |
| `"manual"` | Uses the `p0` and `p1` values you provide (degrees) |

## Data Format

Point `path` at the Spinsolve experiment directory (the folder containing `acqu.par` and `data.1d`):

```
260714-160018 Fluorine1D (FF048_013)/
├── acqu.par
├── data.1d
├── proc.par
└── ...
```

## Authors

Fionn Ferreira — fionn.ferreira@phys.chem.ethz.ch
