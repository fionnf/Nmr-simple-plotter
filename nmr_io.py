"""Shared NMR data loading for Spinsolve (Magritek) and TopSpin (Bruker) formats.

Format is auto-detected from the experiment directory contents:
    Spinsolve : acqu.par + data.1d
    TopSpin   : acqus + fid
"""
from pathlib import Path

import numpy as np
import nmrglue as ng
import yaml


def resolve_config_path(config_arg: str | None) -> str:
    """Resolve the --config argument, defaulting to ./plot.yaml when omitted
    so commands just work when run from inside a plt_* folder."""
    if config_arg:
        return config_arg
    default = "plot.yaml"
    if not Path(default).exists():
        raise SystemExit(
            f"No {default!r} found in the current directory.\n"
            "Pass -c/--config explicitly, or cd into the plt_* folder created by nmr-new."
        )
    return default


def resolve_experiment_path(path_arg: str | None) -> str:
    """Resolve the --path argument, defaulting to the current directory when
    omitted so commands just work when run from inside an experiment folder."""
    if path_arg:
        return path_arg
    if is_experiment_dir(Path(".")):
        return "."
    raise SystemExit(
        "No Spinsolve or TopSpin experiment found in the current directory.\n"
        "Pass -p/--path explicitly, or cd into the experiment folder "
        "(containing acqu.par + data.1d, or acqus + fid)."
    )


def load_plot_config(config_path: str) -> dict:
    """Load a plot.yaml, resolving spectra paths and output relative to the yaml's directory."""
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    cfg_dir = Path(config_path).resolve().parent
    cfg["_config_path"] = str(Path(config_path).resolve())
    for spec in cfg["spectra"]:
        spec["path"] = str((cfg_dir / spec["path"]).resolve())
    cfg["output"] = str(cfg_dir / cfg.get("output", "spectrum"))
    return cfg


def detect_format(path: str) -> str:
    p = Path(path)
    if (p / "acqu.par").exists() and (p / "data.1d").exists():
        return "spinsolve"
    if (p / "acqus").exists() and (p / "fid").exists():
        return "topspin"
    raise ValueError(
        f"Unrecognized NMR data format in: {path}\n"
        "Expected a Spinsolve experiment folder (containing acqu.par + data.1d) "
        "or a TopSpin expno folder (containing acqus + fid). "
        "For TopSpin, point at the numbered expno subfolder (e.g. 'myrun/9'), "
        "not the dataset root ('myrun/')."
    )


def _require(d: dict, key: str, path: str) -> str:
    if key not in d:
        raise ValueError(f"Missing required TopSpin parameter {key!r} in {path}")
    return d[key]


def is_experiment_dir(path: Path) -> bool:
    """True if `path` is a Spinsolve or TopSpin experiment directory."""
    return ((path / "acqu.par").exists() and (path / "data.1d").exists()) or \
           ((path / "acqus").exists() and (path / "fid").exists())


def load_saved_phases(path: str) -> tuple[float, float]:
    """Read phases.txt from the experiment directory. Falls back to (0, 0) with a warning."""
    phase_file = Path(path) / "phases.txt"
    if not phase_file.exists():
        print(f"Warning: no phases.txt found in {path}, using p0=0 p1=0")
        return 0.0, 0.0
    p0, p1 = 0.0, 0.0
    for line in phase_file.read_text().splitlines():
        if "=" in line:
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip()
            if key == "p0":
                p0 = float(val)
            elif key == "p1":
                p1 = float(val)
    return p0, p1


def _process_spinsolve(path, lb, zf, phase, p0, p1):
    dic, data = ng.spinsolve.read(path)
    acqu = dic["acqu"]
    proc = dic["proc"]

    obs        = float(acqu["b1Freq"])            # MHz
    sw_hz      = float(acqu["bandwidth"]) * 1e3   # kHz → Hz
    ppm_offset = float(proc.get("ppmOffset", 0))
    p0_proc    = float(proc.get("p0Phase", 0))
    p1_proc    = float(proc.get("p1Phase", 0))

    if lb > 0:
        data = ng.proc_base.em(data, lb=lb / sw_hz)

    if zf > 1:
        data = ng.proc_base.zf_size(data, len(data) * zf)

    data = ng.proc_base.fft(data)

    if phase == "auto":
        data = ng.proc_autophase.autops(data, "acme")
    elif phase == "manual":
        data = ng.proc_base.ps(data, p0=p0, p1=p1)
    elif phase == "saved":
        p0, p1 = load_saved_phases(path)
        proc["p0Phase"], proc["p1Phase"] = p0, p1
        data = ng.proc_base.ps(data, p0=p0, p1=p1)
    else:  # "proc"
        data = ng.proc_base.ps(data, p0=p0_proc, p1=p1_proc)

    npts   = len(data)
    sw_ppm = sw_hz / obs
    ppm = np.linspace(ppm_offset + sw_ppm / 2,
                      ppm_offset - sw_ppm / 2, npts)
    hz  = ppm * obs

    return ppm, hz, data.real, acqu, proc


def _topspin_acqu(acqus: dict) -> dict:
    """Map TopSpin acqus fields onto the same key names process_spectrum's
    callers expect (mirrors the Spinsolve acqu.par field names)."""
    d = acqus.get("D", [])
    p = acqus.get("P", [])
    td    = acqus.get("TD")
    sw_hz = acqus.get("SW_h")
    # AQ/DW aren't always stored in acqus — derive from TD and SW_h instead.
    aq_ms = float(td) / (2 * float(sw_hz)) * 1e3 if td and sw_hz else "N/A"
    dw_us = 1.0 / (2 * float(sw_hz)) * 1e6 if sw_hz else "N/A"
    return {
        "experiment":      acqus.get("PULPROG", "N/A"),
        "nucleus":         acqus.get("NUC1", "N/A"),
        "b1Freq":          acqus.get("SFO1", 0),
        "bandwidth":       float(acqus.get("SW_h", 0)) / 1e3,   # Hz → kHz
        "acqTime":         aq_ms,
        "dwellTime":       dw_us,
        "nrPnts":          acqus.get("TD", "N/A"),
        "nrScans":         acqus.get("NS", "N/A"),
        "repTime":         float(d[1]) * 1e3 if len(d) > 1 else "N/A",
        "pulseLength":     p[1] if len(p) > 1 else "N/A",
        "rxGain":          acqus.get("RG", "N/A"),
        "softwareVersion": "TopSpin",
    }


def _topspin_proc(procs: dict) -> dict:
    return {
        "p0Phase":   procs.get("PHC0", 0),
        "p1Phase":   procs.get("PHC1", 0),
        "ppmOffset": procs.get("OFFSET", 0),
    }


def _process_topspin(path, lb, zf, phase, p0, p1):
    dic, data = ng.bruker.read(path)
    acqus = dic["acqus"]
    procs = dic["procs"]
    acqu  = _topspin_acqu(acqus)
    proc  = _topspin_proc(procs)

    obs        = float(_require(acqus, "SFO1", path))   # MHz, raw acquisition carrier freq
    sw_hz      = float(_require(acqus, "SW_h", path))   # Hz
    ppm_offset = float(procs.get("OFFSET", 0))
    sw_ppm     = sw_hz / obs

    if phase not in ("auto", "manual", "saved"):
        phase = "proc"

    if phase == "proc":
        # Use TopSpin's own processed spectrum directly (already phased and
        # apodized) rather than re-deriving p0/p1 — TopSpin's PHC0/PHC1
        # phase convention doesn't map cleanly onto nmrglue's, but the
        # processed 1r data is already correct.
        _, real = ng.bruker.read_pdata(str(Path(path) / "pdata" / "1"))
        si = int(procs.get("SI", len(real)))
        # SF is the referenced/calibrated spectrometer freq (may differ from
        # the raw SFO1 if the spectrum was chemical-shift referenced in
        # TopSpin) — both the ppm and hz axes must use it consistently.
        sf          = float(procs.get("SF", obs))
        sw_ppm_proc = float(procs.get("SW_p", sw_hz)) / sf
        ppm = np.linspace(ppm_offset, ppm_offset - sw_ppm_proc, si)
        hz  = ppm * sf
        return ppm, hz, real, acqu, proc

    fid = ng.bruker.remove_digital_filter(dic, data)

    if lb > 0:
        fid = ng.proc_base.em(fid, lb=lb / sw_hz)

    if zf > 1:
        fid = ng.proc_base.zf_size(fid, len(fid) * zf)

    spec = ng.proc_base.fft(fid)

    if phase == "auto":
        spec = ng.proc_autophase.autops(spec, "acme")
    elif phase == "manual":
        spec = ng.proc_base.ps(spec, p0=p0, p1=p1)
    else:  # "saved"
        p0, p1 = load_saved_phases(path)
        proc["p0Phase"], proc["p1Phase"] = p0, p1
        spec = ng.proc_base.ps(spec, p0=p0, p1=p1)

    npts = len(spec)
    ppm  = np.linspace(ppm_offset, ppm_offset - sw_ppm, npts)
    hz   = ppm * obs

    return ppm, hz, spec.real, acqu, proc


def process_spectrum(path, lb=1.0, zf=1, phase="proc", p0=0.0, p1=0.0):
    """Load and process an NMR FID, auto-detecting Spinsolve vs TopSpin format.

    Returns (ppm, hz, real_spectrum, acqu, proc).
    """
    fmt = detect_format(path)
    if fmt == "spinsolve":
        return _process_spinsolve(path, lb, zf, phase, p0, p1)
    return _process_topspin(path, lb, zf, phase, p0, p1)


def load_fid_for_phasing(path, lb=5.0, zf=8):
    """Load + FFT (unphased) for interactive phase correction.

    Returns (ppm, fft_data, p0_init, p1_init) in nmrglue's phase convention
    (pivot at index 0). For TopSpin data p0_init/p1_init are 0.0 — TopSpin's
    stored PHC0/PHC1 use a different phase convention that doesn't map
    directly onto slider values here.
    """
    fmt = detect_format(path)

    if fmt == "spinsolve":
        dic, data = ng.spinsolve.read(path)
        acqu, proc = dic["acqu"], dic["proc"]
        obs        = float(acqu["b1Freq"])
        sw_hz      = float(acqu["bandwidth"]) * 1e3
        ppm_offset = float(proc.get("ppmOffset", 0))
        p0_init    = float(proc.get("p0Phase", 0))
        p1_init    = float(proc.get("p1Phase", 0))
    else:
        dic, data = ng.bruker.read(path)
        data = ng.bruker.remove_digital_filter(dic, data)
        acqus, procs = dic["acqus"], dic["procs"]
        obs        = float(_require(acqus, "SFO1", path))
        sw_hz      = float(_require(acqus, "SW_h", path))
        ppm_offset = float(procs.get("OFFSET", 0))
        p0_init, p1_init = 0.0, 0.0

    if lb > 0:
        data = ng.proc_base.em(data, lb=lb / sw_hz)
    if zf > 1:
        data = ng.proc_base.zf_size(data, len(data) * zf)
    fft_data = ng.proc_base.fft(data)

    npts   = len(fft_data)
    sw_ppm = sw_hz / obs
    if fmt == "spinsolve":
        ppm = np.linspace(ppm_offset + sw_ppm / 2, ppm_offset - sw_ppm / 2, npts)
    else:
        ppm = np.linspace(ppm_offset, ppm_offset - sw_ppm, npts)

    return ppm, fft_data, p0_init, p1_init
