#!/usr/bin/env python
import sys
from subprocess import CalledProcessError, check_output

# global, because we only want to search once for the right cmd
cmd = ""


def find_cmd():
    global cmd
    cmd = ["kicad-cli"]
    version_str = ""
    for _ in range(2):
        try:
            version_str = check_output(cmd + ["-v"])
        except FileNotFoundError:
            cmd = ["flatpak", "run", "--command=kicad-cli", "org.kicad.KiCad"]

    if version_str == "":
        print("Failed to run kicad-cli :(")
        exit(-1)

    print("found kicad-cli version:", version_str.strip().decode())
    print("WARNING: automatic zone-refills are not supported (yet)")


def plot_layers(f_name, plot_dir, layers=["F.Cu", "B.Cu"], zone_refill=True):
    """
    use kicad-cli to create the .pdf plots.
    Supports native mode and flatpak mode.
    Not so sure what happens on Windows.
    """
    if cmd == "":
        find_cmd()

    kicad_cli_args = [
        "pcb",
        "export",
        "pdf",
        "-l",
        ",".join(layers),
        "--black-and-white",
        f_name,
        "--mode-separate",
        "-o",
        plot_dir,
    ]
    cmd_full = cmd + kicad_cli_args

    print("$ " + " ".join(cmd_full))
    check_output(cmd_full)


if __name__ == "__main__":
    boardName = sys.argv[1]
    plot_dir = sys.argv[2]
    plot_layers(boardName, plot_dir)
