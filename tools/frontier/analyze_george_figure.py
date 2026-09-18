<<<<<<< HEAD
from PIL import Image
from itertools import permutations, product
from pathlib import Path
import argparse, json, hashlib

# George's 5-17p figure has four cross-section diagrams along the bottom.
# The two 3x5 diagrams use an 8 px pitch; their rows are x=-1,0,1 and
# columns are y=-2,-1,0,1,2. The two end diagrams contain the z=+1 and
# z=-2 single-cell layers.
COLORS = {
    'R': (255, 48, 48),   # red
    'G': (255, 215, 0),   # gold
    'N': (34, 139, 34),   # green
    'A': (127, 255, 212), # aqua
}

# Verified fixture witness copied from tests/fixtures/ee4_R_5.json.
FIXTURE_PIECES = {
    'P1': {(0,0,-1),(1,-1,0),(1,0,-1),(1,0,0),(1,1,-1)},
    'P2': {(0,1,0),(0,1,1),(0,2,-1),(0,2,0),(1,1,0)},
    'P3': {(0,-2,-1),(0,-2,0),(0,-1,-2),(0,-1,-1),(1,-1,-1)},
    'P4': {(-1,0,-1),(-1,1,-1),(-1,1,0),(0,1,-2),(0,1,-1)},
    'P5': {(-1,-1,-1),(-1,-1,0),(-1,0,0),(0,-1,0),(0,-1,1)},
}
FIXTURE_TARGET = set().union(*FIXTURE_PIECES.values())

FIXTURE_ORIENTATION = {'P1': 5, 'P2': 11, 'P3': 3, 'P4': 17, 'P5': 23}
FIXTURE_COLOR_MAP = {'N':'P1', 'G':'gold', 'A':'P4', 'R':'P5'}

R_CANONICAL = {(0,0,0),(1,0,0),(1,1,0),(1,1,1),(2,1,0)}


def det3(m):
    return (
        m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])
        -m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])
        +m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0])
    )


def proper_signed_permutation_matrices():
    mats = []
    for p in permutations(range(3)):
        for signs in product((-1,1), repeat=3):
            m = [[0]*3 for _ in range(3)]
            for i, j in enumerate(p):
                m[i][j] = signs[i]
            if det3(m) == 1:
                mats.append(tuple(tuple(r) for r in m))
    assert len(mats) == 24
    return mats

RM = proper_signed_permutation_matrices()

def apply(m, c):
    return tuple(sum(m[i][j]*c[j] for j in range(3)) for i in range(3))


def normalize(cells):
    mins = tuple(min(c[i] for c in cells) for i in range(3))
    return tuple(sorted(tuple(c[i]-mins[i] for i in range(3)) for c in cells))

R_SHAPES = {normalize([apply(m, c) for c in R_CANONICAL]) for m in RM}


def is_proper_R(cells):
    return normalize(cells) in R_SHAPES


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1<<20), b''):
            h.update(chunk)
    return h.hexdigest()


def classify_rgb(rgb):
    # Exact source colors; anti-aliased pixels are intentionally ignored.
    for k, v in COLORS.items():
        if tuple(rgb) == v:
            return k
    return '.'


def sample_grid(im, origin_x, origin_y, rows=3, cols=5):
    # Interior point of each 8x8 cell, away from shared black borders.
    out = []
    for i in range(rows):
        row = []
        for j in range(cols):
            x = origin_x + 4 + 8*j
            y = origin_y + 4 + 8*i
            row.append(classify_rgb(im.getpixel((x, y))))
        out.append(''.join(row))
    return out


def sample_single(im, x, y):
    return classify_rgb(im.getpixel((x, y)))


def cells_from_layers(layers):
    cells = {k:set() for k in COLORS}
    coords = []
    for z, grid in layers:
        if isinstance(grid, dict):
            items = ((x, y, k) for (x,y), k in grid.items())
        else:
            items = ((i-1, j-2, k) for i, row in enumerate(grid) for j, k in enumerate(row))
        for x, y, k in items:
            if k != '.':
                coord = (x, y, z)
                cells[k].add(coord)
                coords.append(coord)
    return cells, set(coords)


def find_gold_partition(gold_cells):
    sols = []
    gold = sorted(gold_cells)
    for a in __import__('itertools').combinations(gold, 5):
        A = set(a)
        B = gold_cells - A
        if A > B:  # canonicalize unordered pair by tuple ordering
            continue
        if is_proper_R(A) and is_proper_R(B):
            sols.append((A,B))
    return sols


def fmt(cells):
    return '[' + ', '.join(map(str, sorted(cells))) + ']'


def analyse(image_path):
    image_path = Path(image_path)
    im = Image.open(image_path).convert('RGB')
    if im.size != (169,142):
        raise AssertionError(f'expected 169x142, got {im.size}')

    # Bottom strip geometry. The middle two diagrams are 3x5 grids at
    # origins x=34 and x=81, y=115, with 8 px pitch. The end layers are
    # drawn as two isolated cells.
    z_plus = {(0,-1): classify_rgb(im.getpixel((7,126))),
              (0,1): classify_rgb(im.getpixel((23,126)))}
    z0 = sample_grid(im, 34, 115, 3, 5)
    zm1 = sample_grid(im, 81, 115, 3, 5)
    zminus2 = {(0,-1): classify_rgb(im.getpixel((137,126))),
               (0,1): classify_rgb(im.getpixel((153,126)))}

    # Convert the compact layer diagrams directly to cell-coordinate maps.
    layers = [
        (+1, z_plus),
        (0, z0),
        (-1, zm1),
        (-2, zminus2),
    ]
    color_sets, target = cells_from_layers(layers)

    # For easier presentation, reconstruct the grouped piece colors.
    non_gold = {k: v for k,v in color_sets.items() if k != 'G'}
    gold_solutions = find_gold_partition(color_sets['G'])

    # Compare exact target and exact five placement sets to fixture.
    exact_green = color_sets['N'] == FIXTURE_PIECES['P1']
    exact_aqua = color_sets['A'] == FIXTURE_PIECES['P4']
    exact_red = color_sets['R'] == FIXTURE_PIECES['P5']
    fixture_gold = {frozenset(FIXTURE_PIECES['P2']), frozenset(FIXTURE_PIECES['P3'])}
    exact_gold = any(
        {frozenset(a), frozenset(b)} == fixture_gold
        for a,b in gold_solutions
    )
    target_match = target == FIXTURE_TARGET
    all_piece_match = exact_green and exact_aqua and exact_red and exact_gold

    verdict = 'A' if target_match and all_piece_match else 'C'
    # B would only arise if the target matched but the exact decomposition did not.
    if target_match and not all_piece_match:
        verdict = 'B'

    result = {
        'image': str(image_path),
        'sha256': sha256(image_path),
        'size': list(im.size),
        'slices': {
            'z=+1': {f'{x},{y}': k for (x,y),k in z_plus.items()},
            'z=0': z0,
            'z=-1': zm1,
            'z=-2': {f'{x},{y}': k for (x,y),k in zminus2.items()},
        },
        'cells': {k: sorted(v) for k,v in color_sets.items()},
        'gold_partitions': [
            {'P2': sorted(a), 'P3': sorted(b)} for a,b in gold_solutions
        ],
        'matches': {
            'target_exact': target_match,
            'green_exact_P1': exact_green,
            'aqua_exact_P4': exact_aqua,
            'red_exact_P5': exact_red,
            'gold_exact_P2_P3': exact_gold,
            'all_five_piece_sets_exact': all_piece_match,
        },
        'fixture_orientation_indices': FIXTURE_ORIENTATION,
        'verdict': verdict,
    }
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('image', nargs='?', default='5-17p.png')
    ap.add_argument('--json', type=Path)
    args = ap.parse_args()
    r = analyse(args.image)
    print(f"image_size={r['size'][0]}x{r['size'][1]}")
    print('z=+1:', r['slices']['z=+1'])
    print('z=0 :'); [print('  ', x) for x in r['slices']['z=0']]
    print('z=-1:'); [print('  ', x) for x in r['slices']['z=-1']]
    print('z=-2:', r['slices']['z=-2'])
    print('target_exact=', r['matches']['target_exact'])
    print('green=P1:', r['matches']['green_exact_P1'])
    print('aqua=P4 :', r['matches']['aqua_exact_P4'])
    print('red=P5  :', r['matches']['red_exact_P5'])
    print('gold=P2+P3:', r['matches']['gold_exact_P2_P3'])
    print('gold_partitions=', len(r['gold_partitions']))
    print('VERDICT=', r['verdict'])
    if r['verdict'] == 'A':
        print("George's construction independently reproduced: exact target and exact five-piece placement sets, with the two gold copies interchangeable.")
    if args.json:
        args.json.write_text(json.dumps(r, indent=2) + '\n')


if __name__ == '__main__':
    main()
=======
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
>>>>>>> 77a425b3222e4a9a0fa2e560fe7fb9dab0f7566f
