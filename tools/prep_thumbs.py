#!/usr/bin/env python3
"""One-time prep: build repo thumbs/*.jpg from the verified Commons photos.

Sources (Wikimedia Commons, freely licensed; staged at ../thumbs-source/):
- antalya-coast.jpg -- Antalya_falezler.jpg (Antalya cliff coast, bay, city)
- kingdom-centre-riyadh.jpg -- Kingdom Centre Riyadh 2024.jpeg, CC BY-SA 4.0,
  Hamza A. Durrani (Kingdom Centre tower at night)
- lake-junin.jpg -- Lago_de_Junin-Juni_Peru.jpg (Lake Junin, Junin Province)

Each source is resized with PIL Lanczos to 314 px wide and cropped to a
314x88 band: top-weighted for the portrait Kingdom Centre shot (frac 0.0),
so the inverted-arch top stays in frame; near-centre bands for the two
landscapes. Output JPEG quality 82. This script is build-time provenance
only; it is NOT needed at grade time (the graded program, main.py, only
copies the finished entry.png).
"""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SRC = os.path.join(os.path.dirname(REPO), "thumbs-source")
OUT = os.path.join(REPO, "thumbs")
W, H = 314, 88

# (source file, output file, crop-band fraction: 0.0 = top, 0.5 = centre)
JOBS = [
    ("antalya-coast.jpg", "antalya.jpg", 0.42),
    ("kingdom-centre-riyadh.jpg", "riyadh.jpg", 0.0),
    ("lake-junin.jpg", "junin.jpg", 0.45),
]


def band(im, frac):
    """Resize to W wide, then take an H-tall band at the given fraction."""
    w, h = im.size
    im = im.resize((W, round(h * W / w)), Image.LANCZOS)
    max_y = im.size[1] - H
    y0 = round(max_y * frac)
    return im.crop((0, y0, W, y0 + H))


def main():
    os.makedirs(OUT, exist_ok=True)
    for src, dst, frac in JOBS:
        im = Image.open(os.path.join(SRC, src)).convert("RGB")
        out = os.path.join(OUT, dst)
        band(im, frac).save(out, "JPEG", quality=82)
        print("wrote", dst, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
