# NMR Simple Plotter

Config-driven NMR data processing and plotting tool for publication-quality figures. All configuration in YAML files - commit to git for reproducibility.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run plotter with config file
python plot.py -c examples/config_exp48_static.yaml
```

## How It Works

1. **Edit config YAML** - Adjust experiment ID, data file, processing parameters, styling
2. **Run script** - `python plot.py -c your_config.yaml`
3. **Get figures** - Publication-quality PNG + PDF in `figures/` directory

## Configuration

All settings in YAML files. Example:

```yaml
experiment_id: "exp-48"
data_file: "data/spectrum.csv"
data_format: "csv"

processing:
  phase:
    auto: true
    phase0: 0
  baseline:
    method: "polynomial"
    poly_order: 3

figure_style:
  template: "nature"  # or "jacs", "custom"
  dpi: 300

output_formats: ["pdf", "png"]
```

## Features (Roadmap)

### Phase 0: Infrastructure ✓
- Pydantic config validation
- Generic data loader (CSV, HDF5, Bruker)
- CLI structure

### Phase 1: Processing (In Progress)
- Phase correction (auto + manual)
- Baseline correction (polynomial, AIRPLS, spline)
- Smoothing (Savitzky-Golay, moving average, Gaussian)
- Peak detection and annotation
- Metrics (FWHM, SNR, integral)

### Phase 2: Publication Styling
- Journal templates (Nature, JACS)
- Multi-plot layouts
- Annotations (text, arrows, insets)
- 300 DPI export

### Phase 3: Analysis
- Linewidth tracking
- SNR calculation
- Angle sweep analysis
- Magic angle detection
- High-field comparison

### Phase 4: Batch & Automation
- Multi-config batch processing
- Parameter sweeps
- Directory watcher for real-time plotting
- Figure index generation

### Phase 5: Interactive Reports
- PDF report compilation
- Interactive HTML (Plotly)
- Markdown report indices

## Example Configs

- `examples/config_exp48_static.yaml` - Static spectrum with analysis
- `examples/config_exp49_sweep.yaml` - Magic angle sweep series

Edit these and run:
```bash
python plot.py -c examples/config_exp48_static.yaml
python plot.py -c examples/config_exp49_sweep.yaml
```

## Data Format

Supports:
- **CSV/TXT**: Two columns (chemical_shift, intensity)
- **Spinsolve HDF5**: Native format from Spinsolve console
- **Bruker FID**: TopSpin format (binary)

Example CSV:
```
chemical_shift,intensity
-100.0,500
-90.0,800
-80.0,600
...
```

## Vault Integration

Configs stored alongside experiment logs in `phd_dash_vault/experiments/`:

```
phd_dash_vault/experiments/
├── 2026-07-16-exp-48.md
├── 2026-07-16-exp-48-plotting-config.yaml
├── 2026-07-16-exp-49.md
└── 2026-07-16-exp-49-plotting-config.yaml
```

Recreate figures anytime:
```bash
python plot.py -c phd_dash_vault/experiments/2026-07-16-exp-48-plotting-config.yaml
```

## Testing

```bash
pytest tests/ -v
pytest tests/ --cov=src  # Coverage report
```

## Development

Phase-based implementation:
1. **Phase 0** - Infrastructure & config ✓
2. **Phase 1** - Processing pipeline
3. **Phase 2** - Figure styling
4. **Phase 3** - Analysis & metrics
5. **Phase 4** - Batch processing
6. **Phase 5** - Interactive features

See `/root/.claude/plans/concurrent-churning-stroustrup.md` for detailed plan.

## Authors

- Fionn Ferreira (fionn.ferreira@phys.chem.ethz.ch)

## License

MIT
