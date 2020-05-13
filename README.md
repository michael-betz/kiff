# Kiff, the Kicad diff
Graphically compares layout changes between the current version (B) and a
specific git commit-id, given as a parameter (A).

Elements which have been removed from A are shown
in red, elements which have been added to A are green.

Make sure you have no un-commited changes before using this script.

![diff example](example.png)

# Requires
  * `pdftoppm` to convert the Kicad plots to bitmaps (`apt install poppler-utils`)
  * `numpy` for image manipulations
  * `kiff.py` needs to be in your path

# Usage
Compare the current version against the one from 3 commits ago:

```bash
$ cd <kicad_project>
$ kiff.py my_pcb.kicad_pcb -c HEAD~3
```

Will plot each layer of each version as `.pdf` into 2 temporary directories.
Then uses `pdftoppm` to crop the pdfs and convert them to bitmap. Bitmap data is read by `PIL` over stdin and the diff image is created in python using numpy arrays.
