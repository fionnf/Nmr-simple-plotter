# NMR Simple Plotter

A config-driven NMR plotting tool for **Spinsolve (Magritek)** benchtop data and **TopSpin (Bruker)** data. Edit a YAML file, run one command, get a publication-ready figure — plus a full acquisition/processing log alongside it.

- **Format auto-detection** — point a spectrum's `path` at either a Spinsolve or TopSpin experiment folder; nothing to configure, it's read directly from the folder's contents.
- **Interactive phase correction** (`nmr-phase`) — sliders + peak-anchored autophase, saved for reuse.
- **Interactive scale adjustment** (`nmr-scale`) — sliders for stacking/overlaying multiple spectra, saved directly into your config.
- **Full processing log** — every figure ships with a `.log` recording exactly how it was produced.

## Contents

- [Setup](#setup)
- [Quickstart workflow](#quickstart-workflow)
- [Command reference](#command-reference)
- [YAML config reference](#yaml-config-reference)
- [Data format detection](#data-format-detection)
- [Troubleshooting](#troubleshooting)

---

## Setup

```bash
cd /path/to/nmr-simple-plotter
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Shell aliases (recommended)

Add these to your `~/.zshrc` so every command works from any terminal, in any folder:

```bash
alias nmr-activate="source /path/to/nmr-simple-plotter/.venv/bin/activate"
alias nmr-deactivate="deactivate"
alias nmr-new="python /path/to/nmr-simple-plotter/new_plot.py"
alias nmr-plot="python /path/to/nmr-simple-plotter/plot.py"
alias nmr-phase="python /path/to/nmr-simple-plotter/phase_check.py"
alias nmr-scale="python /path/to/nmr-simple-plotter/nmr_scale.py"
alias nmr-help="python /path/to/nmr-simple-plotter/nmr_help.py"
```

Reload your shell after editing, or open a new terminal tab:

```bash
source ~/.zshrc
```

Run `nmr-help` any time to see this list of commands without leaving your terminal.

---

## Quickstart workflow

### 1. Activate the environment

```bash
nmr-activate
```

### 2. Create a new plot config

Navigate to your experiment session folder — the one containing the numbered/dated experiment subfolders — and run:

```bash
cd /path/to/session/folder
nmr-new
```

You'll be prompted for:

1. **Description** — required; saved as a comment at the top of the YAML.
2. **Which experiments to include** — numbered list; accepts `1`, `1,3`, `1-3`, or `all`.
3. **Plot name** — e.g. `tripf_dmso`; the folder is created as `plt_<name>` so all plot folders sort together.

This produces a clean, self-contained folder structure per plot:

```
FF049/
  260715-161733 TRIPF (FF049_008)/    ← raw experiment data (Spinsolve or TopSpin)
  plt_tripf_dmso/
    plot.yaml                          ← edit this
    plt_tripf_dmso.png / .pdf          ← created on first plot
    plt_tripf_dmso.log                 ← acquisition + processing record
  plt_tripf_cdcl3/
    plot.yaml
    plt_tripf_cdcl3.png / .pdf
    plt_tripf_cdcl3.log
```

### 3. Edit the config

Open `plot.yaml` and adjust labels, colours, `xlim`, phase settings, etc. The full spectrum is shown by default — uncomment `xlim` once you know your peak region. See the [YAML config reference](#yaml-config-reference) for every option.

### 4. Plot

```bash
nmr-plot -c plt_tripf_dmso/plot.yaml
```

Or, if you're already inside the `plt_tripf_dmso/` folder, just:

```bash
nmr-plot
```

`-c`/`--config` defaults to `./plot.yaml`, so every command in this tool works with no arguments as long as you're standing inside the plot's own folder. The figure(s) and a `.log` file are saved alongside `plot.yaml`. The log records the full acquisition parameters (nucleus, frequency, number of scans, dwell time, pulse length, RX gain, software version), all processing parameters (phase mode, p0/p1, lb, zf, scale, offset), and figure settings — a complete record of exactly how the figure was produced.

### 5. Fix the phase (if needed)

```bash
nmr-phase -p "../260715-161733 TRIPF (FF049_008)" --xlim -60 -220
```

Optional flags: `--lb 5.0` (line broadening in Hz), `--zf 8` (zero-fill factor).

**Interactive controls:**

| Control                  | Action                                                                                   |
| ------------------------ | ---------------------------------------------------------------------------------------- |
| Click on spectrum        | Place a green anchor line on a peak (used by Autophase)                                  |
| **Autophase** button     | Optimise p0/p1 via minimum entropy, seeded from the selected peak angle                  |
| p0 slider                | Zero-order phase shift (degrees)                                                         |
| p1 slider                | First-order phase shift (degrees)                                                        |
| pivot slider             | ppm position held fixed when sweeping p1 (red dashed line) — set to your main peak first |
| **Zoom / Full spectrum** | Toggle between the `--xlim` window and the full spectrum                                 |
| **Print values**         | Print corrected p0/p1 to the terminal, for copying by hand                               |
| **Save phases**          | Write p0/p1 to `phases.txt` in the experiment directory, for use with `phase: "saved"`   |

Either copy the printed values into `plot.yaml`:

```yaml
    phase: "manual"
    p0: 63.82
    p1: -360.00
```

or use `phase: "saved"` to automatically pick up whatever `nmr-phase` last saved for that experiment.

### 6. Adjust vertical scale for stacked/overlaid plots (if needed)

```bash
nmr-scale -c plt_tripf_dmso/plot.yaml
```

Loads every spectrum in the config (using each one's configured `lb`/`zf`/`phase`/`offset`) and gives each one a vertical-scale slider.

| Control                     | Action                                                                    |
| --------------------------- | ------------------------------------------------------------------------- |
| Scale slider (per spectrum) | Vertical intensity multiplier, live-previewed on the plot                 |
| **Reset**                   | Restore every slider to the value that was loaded from the file           |
| **Print values**            | Print the current scale values to the terminal, for copying by hand       |
| **Save scales**             | Write each spectrum's value into its `scale:` key directly in `plot.yaml` |

Saving patches only the `scale:` line for each spectrum — every comment and everything else in the file is left untouched. Rerun `nmr-plot` afterwards to render with the new scaling.

### 7. Deactivate when done

```bash
nmr-deactivate
```

---

## Command reference

| Command          | Usage                                        | Purpose                                                                                                               |
| ---------------- | -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `nmr-activate`   | `nmr-activate`                               | Activate the tool's virtualenv                                                                                        |
| `nmr-deactivate` | `nmr-deactivate`                             | Deactivate the virtualenv                                                                                             |
| `nmr-new`        | `nmr-new`                                    | Run in a session folder — prompts for description, experiments, and plot name; creates `plt_<name>/plot.yaml`         |
| `nmr-plot`       | `nmr-plot [-c plot.yaml]`                    | Render the figure(s) + a `.log` file. `-c` defaults to `./plot.yaml`                                                  |
| `nmr-phase`      | `nmr-phase -p <experiment dir> [--xlim H L]` | Interactive phase correction (sliders + autophase), saves `phases.txt`                                                |
| `nmr-scale`      | `nmr-scale [-c plot.yaml] [--xlim H L]`      | Interactive vertical-scale sliders for stacked/overlaid plots, saves into `plot.yaml`. `-c` defaults to `./plot.yaml` |
| `nmr-help`       | `nmr-help`                                   | List all available commands                                                                                           |

### Underlying scripts

| Script           | Purpose                                                                                     |
| ---------------- | ------------------------------------------------------------------------------------------- |
| `new_plot.py`    | Backs `nmr-new`                                                                             |
| `plot.py`        | Backs `nmr-plot`                                                                            |
| `phase_check.py` | Backs `nmr-phase`                                                                           |
| `nmr_scale.py`   | Backs `nmr-scale`                                                                           |
| `nmr_help.py`    | Backs `nmr-help`                                                                            |
| `nmr_io.py`      | Shared internals — format detection, spectrum processing, config loading. Not run directly. |

---

## YAML config reference

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
    # scale: 1.0                # vertical intensity multiplier — adjust with nmr-scale
    phase: "proc"               # "proc" | "auto" | "manual" | "saved"
    # p0: 0.0                   # used only when phase: "manual"
    # p1: 0.0

  # Add more spectra to overlay or stack:
  # - path: "../260715-161204 Fluorine1D (FF049_007)"
  #   label: "FF049"
  #   color: "tab:orange"
  #   offset: 35                # stack above first spectrum

figure:
  size: [6.0, 4.5]             # [width, height] inches
  x_unit: "ppm"                # "ppm" → "¹⁹F Chemical Shift (ppm)"  (nucleus auto-read)
                                # "hz"  → "¹⁹F Frequency Offset from Carrier (Hz)"
  # xlabel: "override"         # uncomment to override the auto label
  # xlim: [-60, -220]          # uncomment to set display window (high ppm, low ppm)

  box: false                   # true = full box, false = bottom spine only
  y_axis: false                # true = show y-axis and label
  ylabel: "Intensity (a.u.)"   # only shown when y_axis: true

  legend:
    show: true
    position: "upper right"    # string or [x, y] for manual placement
    fontsize: 9
    frameon: false

# Text annotations:
# labels:
#   - text: "peak A"
#     x: -130.5                # ppm (or Hz if x_unit: "hz")
#     y: 27.0                  # intensity units
#     color: "black"
#     fontsize: 9
#     ha: "center"             # "left" | "center" | "right"
#     va: "bottom"

output: "tripf_dmso"           # filename stem, saved next to this yaml
formats: ["png", "pdf"]        # any of "png", "pdf", "svg" — defaults to png+pdf if omitted
```

### Phase options

| Value      | Behaviour                                                                                                                                |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `"proc"`   | **Spinsolve:** uses `p0Phase`/`p1Phase` from `proc.par`. **TopSpin:** uses the instrument's own already-processed `pdata/1/1r` directly. |
| `"auto"`   | nmrglue's ACME autophase algorithm                                                                                                       |
| `"manual"` | Uses the `p0` and `p1` values you provide, in degrees                                                                                    |
| `"saved"`  | Uses the p0/p1 last saved by `nmr-phase`'s **Save phases** button (`phases.txt` in the experiment directory)                             |

---

## Data format detection

Point `path` at the experiment directory — the format (Spinsolve or TopSpin) is auto-detected from its contents, no config needed. Paths are always resolved relative to the yaml file's location, so `../subfolder` points one level up into the session folder.

**Spinsolve** — the folder containing `acqu.par` and `data.1d`:

```
260715-161733 TRIPF (FF049_008)/
├── acqu.par
├── data.1d
├── proc.par
└── ...
```

**TopSpin** — the expno folder containing `acqus` and `fid` (e.g. `myrun/9` — point at the numbered expno subfolder, not the dataset root `myrun/`):

```
myrun/9/
├── acqus
├── fid
├── pdata/1/
│   ├── procs
│   └── 1r
└── ...
```

For TopSpin, `phase: "proc"` reads the spectrum TopSpin itself already processed and phased (`pdata/1/1r`) rather than re-deriving phase values — TopSpin's stored phase convention doesn't map onto nmrglue's, so this is the reliable path. `"auto"`, `"manual"`, and `"saved"` reprocess the raw `fid` the same way as Spinsolve.

---

## Troubleshooting

| Symptom                                                    | Fix                                                                                                                                                                                   |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `error: the following arguments are required: -c/--config` | You ran `nmr-plot`/`nmr-scale` outside a `plt_*` folder with no `plot.yaml` in the current directory. Either `cd` into the plot's folder, or pass `-c path/to/plot.yaml` explicitly.  |
| `No 'plot.yaml' found in the current directory.`           | Same as above — run `nmr-new` first to generate one, or pass `-c` explicitly.                                                                                                         |
| `Unrecognized NMR data format in: ...`                     | The `path` doesn't contain `acqu.par`+`data.1d` (Spinsolve) or `acqus`+`fid` (TopSpin). For TopSpin, make sure you're pointing at the numbered expno subfolder, not the dataset root. |
| No experiment folders found by `nmr-new`                   | Run it from inside the session folder that directly contains the experiment subfolders (Spinsolve session folders, or a TopSpin dataset's expno folders like `1`, `2`, `9`).          |

---

## Authors

Fionn Ferreira — fionn.ferreira@phys.chem.ethz.ch
