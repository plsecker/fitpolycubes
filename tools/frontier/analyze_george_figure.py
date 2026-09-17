#!/usr/bin/env python3
"""
EXPLORATORY / EXPERIMENTAL — do not treat as proof.

Pixel-archaeology tool used during the EE4 5-R investigation to probe
George Sicherman's 5-17p.png raster.  It was never able to pin the
figure's perspective projection or to decode the palette diagrams into
five unambiguous R orientations, and its bottom-region dumps conflicted
between runs.  The final EE4 result does NOT depend on this script or on
any of its output: the mathematical result is the exhaustive search in
tools/order4_R_class_comparison.py plus the verified witness
tests/fixtures/ee4_R_5.json (see docs/frontier/ee4_R_oddity.md).

Kept only as historical evidence of the image-analysis detour.

Final pixel classifier (fixed twice):
  - white  : r>252 and g>252 and b>252 (near-pure background)
  - black  : r<40 and g<40 and b<40
  - aqua   : g>r+40 and b>r+40 and r<160   (127,255,212)
  - gold   : r>g and g>b and b<60          (255,215,0 bright; 89,73,0 dark)
  - green  : g>r and g>b and r<100         (34,139,34 bright; 15,86,15 dark)
  - red    : r>g and r>b and g<70          (255,48,48 bright; 199,33,33 dark)
  - gray   : |r-g|<=40 and |g-b|<=40 and r>40  (shades incl. top faces)

Usage: python3 tools/frontier/analyze_george_figure.py [region]
  regions: palette | top | bottom | all
"""

import sys
from PIL import Image

IMG = ("/home/philip/Work/fitpolycubes/.opencode/openwork/inbox/chat-attachments/"
       "ses_f53cacb6fffe6REnaT6WcXctid/1fb056bd-5da6-442c-b2c5-6abbfae0bfee-5-17p.png")


def classify(r, g, b):
    if r > 252 and g > 252 and b > 252:
        return "."
    if r < 40 and g < 40 and b < 40:
        return "K"
    if g > r + 40 and b > r + 40 and r < 160:
        return "A"
    if r > g and g > b and b < 60:
        return "G"
    if g > r and g > b and r < 100:
        return "g"
    if r > g and r > b and g < 70:
        return "R"
    if abs(r - g) <= 40 and abs(g - b) <= 40 and r > 40:
        return "S"
    return "?"


def grid(im, r0, r1, c0, c1, step=1):
    px = im.load()
    out = []
    for y in range(r0, r1, step):
        row = []
        for x in range(c0, c1, step):
            r, g, b = px[x, y][:3]
            row.append(classify(r, g, b))
        out.append("".join(row))
    return out


def main():
    region = sys.argv[1] if len(sys.argv) > 1 else "all"
    im = Image.open(IMG).convert("RGB")
    w, h = im.size
    print(f"image {w}x{h}")

    if region in ("all", "palette"):
        print("\n=== PALETTE STRIP rows 108-142 ===")
        for i, row in enumerate(grid(im, 108, 142, 0, w)):
            print(f"{108+i:3d} {row}")

    if region in ("all", "top"):
        print("\n=== MAIN FIGURE TOP rows 0-42, cols 47-169 ===")
        for i, row in enumerate(grid(im, 0, 42, 47, 169)):
            print(f"{i:3d} {row}")

    if region in ("all", "bottom"):
        print("\n=== MAIN FIGURE BOTTOM rows 42-100, cols 47-169 ===")
        for i, row in enumerate(grid(im, 42, 100, 47, 169)):
            print(f"{42+i:3d} {row}")


if __name__ == "__main__":
    main()