#!/usr/bin/env python
"""Run this inside an experiment session folder to create a plot.yaml.

    python /path/to/new_plot.py

It will:
  1. Ask for a description (required — goes as a comment at the top of the yaml)
  2. List the Spinsolve experiment subfolders it finds
  3. Let you choose which ones to include
  4. Write a ready-to-edit plot.yaml in the current folder
"""
import re
import sys
from pathlib import Path

COLORS = ["tab:blue", "tab:orange", "tab:green", "tab:red",
          "tab:purple", "tab:brown", "tab:pink", "tab:gray"]


def is_spinsolve_dir(path: Path) -> bool:
    return (path / "acqu.par").exists() and (path / "data.1d").exists()


def parse_selection(text: str, n: int) -> list[int]:
    """Parse '1,3', '1-3', 'all', or '2' into zero-based indices."""
    text = text.strip().lower()
    if text == "all":
        return list(range(n))
    indices = set()
    for part in text.split(","):
        part = part.strip()
        if "-" in part:
            a, _, b = part.partition("-")
            try:
                lo, hi = int(a), int(b)
                indices.update(range(lo - 1, hi))
            except ValueError:
                return []
        else:
            try:
                indices.add(int(part) - 1)
            except ValueError:
                return []
    valid = [i for i in sorted(indices) if 0 <= i < n]
    return valid if valid else []


def build_yaml(comment: str, selected: list[Path], plot_name: str) -> str:
    lines = [
        f"# {comment}",
        f"# Run: nmr-plot -c {plot_name}/plot.yaml",
        f"# Docs: https://github.com/fionnf/Nmr-simple-plotter#readme",
        "",
        "spectra:",
    ]
    for i, folder in enumerate(selected):
        color = COLORS[i % len(COLORS)]
        lines += [
            f'  - path: "../{folder.name}"',
            f'    label: "{folder.name}"',
            f'    color: "{color}"',
            f'    linewidth: 1.0',
            f'    lb: 5.0',
            f'    zf: 8',
            f'    phase: "proc"   # proc | auto | manual',
            f'    # p0: 0.0',
            f'    # p1: 0.0',
            f'    offset: 0',
            '',
        ]
    lines += [
        "figure:",
        "  size: [6.0, 4.5]",
        '  x_unit: "ppm"     # "ppm" or "hz"',
        "  # xlim: [-60, -220] # uncomment to set display window",
        "",
        "  box: false",
        "  y_axis: false",
        "",
        "  legend:",
        "    show: true",
        '    position: "upper right"',
        "    fontsize: 9",
        "    frameon: false",
        "",
        f'output: "{plot_name}"',
        'formats: ["pdf"]',
    ]
    return "\n".join(lines) + "\n"


def main():
    cwd = Path.cwd()

    subfolders = sorted([d for d in cwd.iterdir()
                         if d.is_dir() and is_spinsolve_dir(d)])

    if not subfolders:
        print("No Spinsolve experiment folders found in the current directory.")
        print("(Looking for folders containing acqu.par and data.1d)")
        sys.exit(1)

    # ── Description (required) ────────────────────────────────────────────
    print("\nDescription for this plot (required, becomes a comment in the yaml):")
    while True:
        comment = input("  > ").strip()
        if comment:
            break
        print("  Cannot be empty — enter a short description.")

    # ── Folder selection ──────────────────────────────────────────────────
    print(f"\nFound {len(subfolders)} experiment folder(s):")
    for i, folder in enumerate(subfolders, 1):
        print(f"  [{i}] {folder.name}")

    print("\nWhich to include? (e.g. 1  or  1,3  or  1-3  or  all)")
    while True:
        raw = input("  > ").strip()
        indices = parse_selection(raw, len(subfolders))
        if indices:
            break
        print("  Invalid — try again.")

    selected = [subfolders[i] for i in indices]
    print(f"\nSelected: {', '.join(f.name for f in selected)}")

    # ── Plot name / directory ─────────────────────────────────────────────
    # Extract expno from parentheses in folder names e.g. "260715-161733 TRIPF (FF049_008)" → "FF049_008"
    expnos = []
    for f in selected:
        m = re.search(r'\(([^)]+)\)', f.name)
        if m:
            expnos.append(m.group(1))
    expno_prefix = "_".join(expnos) + "_" if expnos else ""

    print("\nPlot name (e.g. tripf_dmso — folder will be created as plt_<expno>_<name>):")
    while True:
        raw_name = input("  > ").strip()
        if raw_name:
            break
        print("  Cannot be empty.")

    plot_name = f"plt_{expno_prefix}{raw_name}"
    plot_dir = cwd / plot_name
    if plot_dir.exists():
        print(f"\n{plot_name}/ already exists. Overwrite plot.yaml inside? [y/N]")
        if input("  > ").strip().lower() != "y":
            print("Aborted.")
            sys.exit(0)
    else:
        plot_dir.mkdir()

    # ── Write yaml ────────────────────────────────────────────────────────
    out_path = plot_dir / "plot.yaml"
    out_path.write_text(build_yaml(comment, selected, plot_name))

    print(f"\nCreated: {plot_dir}/")
    print(f"         └── plot.yaml  (output → {plot_name}.pdf)")
    print(f"\nEdit it, then run:")
    print(f"  nmr-plot -c {out_path}")


if __name__ == "__main__":
    main()
