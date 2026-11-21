#!/usr/bin/env python3
"""Entry program for the news-image-20261121 bounty (program/v1).

Writes the finished page to /output/entry.png. The image itself was drawn
at build time by render.py (Pillow, build-time only) and is committed in
this repository as entry.png; this program is pure stdlib and only copies
it, so the run is deterministic: same input bytes, same output bytes.
"""
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("wrote", dst, os.path.getsize(dst), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
