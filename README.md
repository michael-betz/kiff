# Kiff, the Kicad diff
Graphically compare layout changes between two git versions of a PCB.

If `-c` is not given, compares the local working copy against the latest
version on git. This is useful to verify board changes before
committing them.

If a git commit-id is given in `-c`, will compare the local version
against this commit. This is useful to compare changes between 2 commits.

A useful shortcut for the commit-id is `HEAD~1`, which means the previous one.

Elements which have been added in the local version are colored green,
removed ones red.
Note that this may look inverted for features on copper fills.

# Installation (Debian Bullseye and newer)
At least python version 3.11 (to be verified) is required.

```bash
# Install dependencies
# poppler-utils is used to convert the Kicad .pdf plots to bitmaps
sudo apt install poppler-utils pipx

# Install kiff
pipx install git+https://github.com/michael-betz/kiff.git

# Give kiff a test-run
wget https://github.com/michael-betz/kiff/raw/refs/heads/main/test.zip
unzip test.zip
cd test/
kiff test5.kicad_pcb -c HEAD~1
```

# Supported Kicad versions
There are currently CI tests in place for versions 5.1.9, 6.0.11, 7.0.10, and 8.0.5. If the below badge is green, they've all succeeded.

[![CI status](https://github.com/michael-betz/kiff/actions/workflows/kicad.yml/badge.svg)](https://github.com/michael-betz/kiff/actions/workflows/kicad.yml)

By default, the legacy python API is used to generate the .pdfs. The API needs to be installed in your python path (`import pcbnew` must work). This API will be no more available in Kicad 9.

If the legacy API fails, kiff falls back on the `kicad-cli` command-line tool, which can also plot the .pdfs. This tool has been introduced in version 7.

kiff will try to run `kicad-cli` natively (make sure it is in your path). If that fails, it will try to run it in the flatpak container (assuming kicad was installed through flatpak).

Note that `kicad-cli`-mode still has some caveats. It does not support refreshing the copper-zone fills before diffing. Also it does not crop the image to the PCB size.

# Usage example
Compare the current version against the one from 3 commits ago:

```bash
$ cd <kicad_project>
$ kiff my_pcb.kicad_pcb -c HEAD~3

WARNING: couldn't find pcbnew legacy python API, using kicad-cli for pdf-exports
layers: F.Cu B.Cu F.SilkS B.SilkS
> plot_24eb330
found kicad-cli version: 9.0.0
WARNING: automatic zone-refills are not supported (yet)
$ flatpak run --command=kicad-cli org.kicad.KiCad pcb export pdf -l F.Cu,B.Cu,F.SilkS,B.SilkS --black-and-white test5.kicad_pcb --mode-separate -o plot_24eb330
$ git checkout HEAD~1
> plot_c8fa4b6
$ flatpak run --command=kicad-cli org.kicad.KiCad pcb export pdf -l F.Cu,B.Cu,F.SilkS,B.SilkS --black-and-white test5.kicad_pcb --mode-separate -o plot_c8fa4b6
$ git checkout -
Previous HEAD position was c8fa4b6 initial version done in kicad 5.1.2
Switched to branch 'main'
> diffs/F.Cu.png     (+0.000390, -0.001082)
> diffs/B.Cu.png     (+0.001569, -0.000358)
> diffs/F.SilkS.png  (+0.000000, -0.000018)
> diffs/B.SilkS.png  (+0.000000, -0.000000)
Removing temporary directories
```

This will generate `diffs/<layer_name>.png` for each layer.

![diff example](example.png)

It works by using `plot_layers.py` to make Kicad plot each layer of each version as `.pdf` into 2 temporary directories.
Then `pdftoppm` is called to crop the pdfs and convert them to bitmap. Bitmap data is read by `PIL` over stdin and the diff image is created in python using numpy arrays.
