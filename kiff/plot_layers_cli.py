#!/usr/bin/env python
import sys
from pathlib import Path
from subprocess import check_output

# global, because we only want to search once for the right cmd
cmd = None
version = None


def find_cmd():
    global cmd, version
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

    version = version_str.strip().decode()
    print("found kicad-cli version:", version)
    print("WARNING: automatic zone-refills are not supported (yet)")


def plot_layers(f_name, plot_dir, layers=["F.Cu", "B.Cu"], zone_refill=True):
    """
    use kicad-cli to create the .pdf plots.
    Supports native mode and flatpak mode.
    Not so sure what happens on Windows.
    Returns list of .pdf file-names written
    """
    if cmd is None:
        find_cmd()

    f_name = Path(f_name)
    plot_dir = Path(plot_dir)
    plot_dir.mkdir(exist_ok=True)

    # out_names = []

    if int(version.split(".")[0]) >= 9:
        # We can plot all the layers in one go with --mode-separate
        kicad_cli_args = [
            "pcb",
            "export",
            "pdf",
            "-l",
            ",".join(layers),
            "--black-and-white",
            "--mode-separate",
            "-o",
            str(plot_dir),
            str(f_name),
        ]

        cmd_full = cmd + kicad_cli_args
        print("$ " + " ".join(cmd_full))
        check_output(cmd_full)
    else:
        # We have to send a plot command for each layer separately
        for layer in layers:
            out_name = f_name.stem + "-" + layer.replace(".", "_") + ".pdf"

            kicad_cli_args = [
                "pcb",
                "export",
                "pdf",
                "-l",
                layer,
                "--black-and-white",
                "-o",
                str(plot_dir / out_name),
                str(f_name),
            ]

            cmd_full = cmd + kicad_cli_args
            print("$ " + " ".join(cmd_full))
            check_output(cmd_full)


if __name__ == "__main__":
    boardName = sys.argv[1]
    plot_dir = sys.argv[2]
    plot_layers(boardName, plot_dir)
