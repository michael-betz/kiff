# Kiff
Kiff, the Kicad diff

# Requires
`pdftoppm` to convert the Kicad plots to bitmaps. (`apt install poppler-utils`)

Make sure `kiff.py` is in your path.

# Usage
Compare the current version against the one from 3 commits ago:

```bash
$ cd <kicad_project>
$ ./kiff.py my_pcb.kicad_pcb -c HEAD~3
```

Will plot each layer of each version as `.pdf` into 2 temporary directories.
Then uses `pdftoppm` to crop the pdfs and convert them to bitmap.
Bitmap data is read by `PIL` over stdin.
The resulting diff file is created as `.png` in python for each layer.
