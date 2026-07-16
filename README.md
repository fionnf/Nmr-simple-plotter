# NMR Simple Plotter

Config-driven NMR plotting tool for Spinsolve (Magritek) benchtop NMR data. Edit a YAML file, run one command, get a publication-ready figure.

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

Reload your shell after editing:

```bash
source ~/.zshrc
```

---

## Workflow

### 1. Activate the environment

```bash
nmr-activate
```

### 2. Create a new plot config

Navigate to your experiment session folder (the one containing acquisition subfolders) and run:

```bash
cd /path/to/session/folder
nmr-new
```

You will be prompted for:
1. **Description** — required; saved as a comment at the top of the YAML
2. **Which experiments to include** — numbered list; accepts `1`, `1,3`, `1-3`, or `all`
3. **Plot name** — becomes a new subdirectory; e.g. `tripf_dmso` creates `tripf_dmso/plot.yaml`

The result is a clean folder structure:

```
FF049/
  260715-161733 TRIPF (FF049_008)/   ← raw Spinsolve data
  tripf_dmso/
    plot.yaml                         ← edit this
    tripf_dmso.pdf                    ← created on first plot run
  tripf_cdcl3/
    plot.yaml
    tripf_cdcl3.pdf
```

### 3. Edit the config

Open `plot.yaml` and adjust labels, colours, `xlim`, phase settings, etc. The full spectrum is shown by default — uncomment `xlim` once you know your peak region.

### 4. Plot

```bash
nmr-plot -c tripf_dmso/plot.yaml
```

The figure is saved inside the same folder as `plot.yaml`.

### 5. Fix the phase (if needed)

```bash
nmr-phase -p "../260715-161733 TRIPF (FF049_008)" --xlim -60 -220
```

Optional flags: `--lb 5.0` (line broadening in Hz), `--zf 8` (zero-fill factor).

**Interactive controls:**

| Control | Action |
|---------|--------|
| Click on spectrum | Place green anchor line on a peak (used by Autophase) |
| **Autophase** button | Optimise p0/p1 via minimum entropy, seeded from the selected peak angle |
| p0 slider | Zero-order phase shift (degrees) |
| p1 slider | First-order phase shift (degrees) |
| pivot slider | ppm position held fixed when sweeping p1 (red dashed line) — set to your main peak before adjusting p1 |
| **Zoom / Full spectrum** | Toggle between `--xlim` window and full spectrum |
| **Print values** | Print corrected p0/p1 to terminal |

Copy the printed values into your `plot.yaml`:

```yaml
    phase: "manual"
    p0: 63.82
    p1: -360.00
```

### 6. Deactivate when done

```bash
nmr-deactivate
```

---

## Scripts

| Script | Purpose |
|--------|---------|
| `new_plot.py` | Run in a session folder — prompts for description, experiments, and plot name; creates a subdirectory with `plot.yaml` |
| `plot.py` | Main plotter — reads a YAML config and saves figures |
| `phase_check.py` | Interactive phase correction with live sliders and autophase |

---

## YAML Config Reference

```yaml
# Description of this plot
# Run: nmr-plot -c plot.yaml

spectra:
  - path: "../260715-161733 TRIPF (FF049_008)"  # relative to this yaml file
    label: "TRIPF in DMSO"
    color: "tab:blue"
    linewidth: 1.0
    alpha: 1.0
    lb: 5.0                     # line broadening in Hz
    zf: 8                       # zero-fill factor
    offset: 0                   # vertical shift for stacking (intensity units)
    phase: "proc"               # "proc" | "auto" | "manual"
    # p0: 0.0                   # used only when phase: "manual"
    # p1: 0.0

  # Add more spectra to overlay or stack:
  # - path: "../260715-161204 Fluorine1D (FF049_007)"
  #   label: "FF049"
  #   color: "tab:orange"
  #   offset: 35                # stack above first spectrum

figure:
  size: [6.0, 4.5]             # [width, height] inches
  x_unit: "ppm"               # "ppm" → "Chemical Shift (ppm)"
                              # "hz"  → "Frequency Offset from Carrier (Hz)"
  # xlabel: "override"        # uncomment to override the auto label
  # xlim: [-60, -220]         # uncomment to set display window (high ppm, low ppm)

  box: false                  # true = full box, false = bottom spine only
  y_axis: false               # true = show y-axis and label
  ylabel: "Intensity (a.u.)"  # only shown when y_axis: true

  legend:
    show: true
    position: "upper right"   # string or [x, y] for manual placement
    fontsize: 9
    frameon: false

# Text annotations:
# labels:
#   - text: "peak A"
#     x: -130.5               # ppm (or Hz if x_unit: "hz")
#     y: 27.0                 # intensity units
#     color: "black"
#     fontsize: 9
#     ha: "center"            # "left" | "center" | "right"
#     va: "bottom"

output: "tripf_dmso"          # filename stem, saved next to this yaml
formats: ["pdf"]              # "png", "pdf", "svg"
```

### Phase options

| Value | Behaviour |
|-------|-----------|
| `"proc"` | Uses `p0Phase` / `p1Phase` stored in `proc.par` by the Spinsolve software |
| `"auto"` | nmrglue ACME autophase algorithm |
| `"manual"` | Uses the `p0` and `p1` values you provide (degrees) |

---

## Data Format

Point `path` at the Spinsolve experiment directory (the folder containing `acqu.par` and `data.1d`). Paths are always resolved relative to the yaml file's location, so `../subfolder` points one level up into the session folder.

```
260715-161733 TRIPF (FF049_008)/
├── acqu.par
├── data.1d
├── proc.par
└── ...
```

---

## Authors

Fionn Ferreira — fionn.ferreira@phys.chem.ethz.ch
