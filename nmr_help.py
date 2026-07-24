#!/usr/bin/env python
"""List available nmr-simple-plotter commands.

Usage:
    python nmr_help.py
"""

COMMANDS = [
    ("nmr-activate",   "Activate the tool's virtualenv"),
    ("nmr-deactivate", "Deactivate the virtualenv"),
    ("nmr-new",        "Run in a session folder to create a plt_<name>/plot.yaml from its experiment subfolders"),
    ("nmr-plot",       "-c <plot.yaml>              Render the figure(s) + a .log file"),
    ("nmr-phase",      "-p <experiment dir>          Interactive phase correction (sliders, saves phases.txt)"),
    ("nmr-scale",      "-c <plot.yaml>               Interactive vertical-scale sliders for stacked/overlaid plots (saves into plot.yaml)"),
    ("nmr-help",       "Show this list"),
]


def main():
    print("nmr-simple-plotter — available commands\n")
    width = max(len(name) for name, _ in COMMANDS)
    for name, desc in COMMANDS:
        print(f"  {name.ljust(width)}  {desc}")
    print("\nTypical workflow: nmr-activate -> cd session folder -> nmr-new -> nmr-plot -> nmr-phase / nmr-scale as needed.")
    print("Docs: https://github.com/fionnf/Nmr-simple-plotter#readme")


if __name__ == "__main__":
    main()
