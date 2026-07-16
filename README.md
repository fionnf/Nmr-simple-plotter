# NMR Simple Plotter

Config-driven NMR plotting tool for Spinsolve (Magritek) data using nmrglue. Edit a YAML file, run one command, get a publication-ready figure.

## Setup

```bash
cd /path/to/nmr-simple-plotter
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Shell aliases (optional but recommended)

Add these to your `~/.zshrc` so the tools work from any terminal:

```bash
alias nmr-activate="source /path/to/nmr-simple-plotter/.venv/bin/activate"
alias nmr-deactivate="deactivate"
alias nmr-new="python /path/to/nmr-simple-plotter/new_plot.py"
alias nmr-plot="python /path/to/nmr-simple-plotter/plot.py"
alias nmr-phase="python /path/to/nmr-simple-plotter/phase_check.py"
```

Then reload your shell:

```bash
source ~/.zshrc
```

After that, the full workflow from any terminal is:

```bash
nmr-activate                  # activate the environment
cd /path/to/session/folder
nmr-new                       # create plot.yaml interactively
nmr-plot -c plot.yaml         # plot it
nmr-deactivate                # done
```

## Scripts

| Script | Purpose |
|--------|---------|
| `new_plot.py` | Run in a session folder — prompts for a description, lists experiments, writes `plot.yaml` |
| `plot.py` | Main plotter — reads a YAML config and saves figures |
| `phase_check.py` | Interactive phase correction with live sliders |

## Workflow

### 1. Activate the environment

```bash
nmr-activate
```

### 2. Initialise a plot config in your session folder

Navigate to a folder containing Spinsolve acquisition subfolders and run:

```bash
cd /path/to/session/folder
nmr-new
```

It will:
1. Ask for a description (required — saved as a comment at the top of the YAML)
2. List every Spinsolve subfolder it finds (`acqu.par` + `data.1d`)
3. Let you pick which to include (`1`, `1,3`, `1-3`, or `all`)
4. Write `plot.yaml` in the current folder, ready to edit and run

### 3. Edit and plot

Open `plot.yaml`, adjust labels, colours, `xlim`, phase settings, etc., then:

```bash
nmr-plot -c plot.yaml
```

Figures are saved next to `plot.yaml` (or wherever `output:` points).

### 4. Fix the phase (if needed)

If the phase from `proc.par` doesn't look right, use the interactive tool:

```bash
nmr-phase -p "260714-160018 Fluorine1D (FF048_013)" --xlim -60 -220
```

Optional flags: `--lb 5.0` (line broadening in Hz), `--zf 8` (zero-fill factor).

Three sliders let you dial in the correction:
- **p0** — zero-order (constant) phase shift
- **p1** — first-order (frequency-dependent) phase shift
- **pivot** — ppm position held fixed when sweeping p1 (red dashed line); place it on your main peak before adjusting p1

Click **Print values** to print the corrected values, then paste them into `plot.yaml`:

```yaml
    phase: "manual"
    p0: 63.82
    p1: -360.00
```

### 5. Deactivate when done

```bash
nmr-deactivate
```

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
