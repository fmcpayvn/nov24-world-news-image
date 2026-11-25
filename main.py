#!/usr/bin/env python3
"""Copy the pre-built front page to the grader's output directory.

Standard library only: the grader runs this with no network on a
read-only copy of the repository, so nothing is installed and nothing
is written back into the repo. The image is already rendered
(entry.png, 1024x1024); this just places it at $MAKEFUN_OUTPUT_DIR/entry.png.
Deterministic: both graded runs write the same bytes. The copy is
verified by size afterwards, so a truncated write fails loudly
instead of submitting a partial image.
"""
import os
import shutil

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out, exist_ok=True)
    src = os.path.join(here, "entry.png")
    dst = os.path.join(out, "entry.png")
    shutil.copyfile(src, dst)
    if os.path.getsize(dst) != os.path.getsize(src):
        raise SystemExit("entry.png copy incomplete")
