#!/usr/bin/env python3
"""Deliver the submitted front-page image to the grader's output directory.

The entry is the pre-rendered 1024x1024 PNG in this repository
(`entry.png`). This script copies it, byte for byte, into the directory
named by the MAKEFUN_OUTPUT_DIR environment variable (default "out"),
creating that directory when it does not exist yet.

Only the standard library is used (os and shutil), and every path is
relative to this file, so the script runs unchanged in the grader's
read-only sandbox.
"""

import os
import shutil
import sys

SOURCE_NAME = "entry.png"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fail(message):
    """Print an error and stop with a non-zero exit status."""
    print(f"main.py: error: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_signature(path):
    """First 8 bytes of a file, for PNG signature checks."""
    with open(path, "rb") as handle:
        return handle.read(len(PNG_SIGNATURE))


def check_png(path, role):
    """Fail loudly unless the file at path starts with the PNG signature."""
    if read_signature(path) != PNG_SIGNATURE:
        fail(f"{role} {path} is not a PNG file")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)

    if not os.path.isfile(source):
        fail(f"missing {SOURCE_NAME} next to main.py")
    check_png(source, "source")

    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    if not output_dir:
        fail("MAKEFUN_OUTPUT_DIR is set but empty")
    os.makedirs(output_dir, exist_ok=True)

    destination = os.path.join(output_dir, SOURCE_NAME)
    shutil.copyfile(source, destination)
    check_png(destination, "copied")

    source_size = os.path.getsize(source)
    copied_size = os.path.getsize(destination)
    if copied_size != source_size:
        fail(
            f"copied {destination} is {copied_size} bytes, "
            f"expected {source_size} bytes from {source}"
        )

    print(f"main.py: wrote {destination} ({copied_size} bytes)")


if __name__ == "__main__":
    main()
