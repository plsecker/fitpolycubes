# EE4 R-pentacube oddity (5 copies)

## Final status

**A — MATCH. George Sicherman's construction in `5-17p.png` is the exact verified EE4 fixture construction.**

This is stronger than geometric equivalence: the reconstructed 25-cell target is exactly the fixture target, and the five piece cell-sets are exactly the five fixture placements. The only freedom is swapping the two visually identical gold copies.

The source image is the R-5 panel of Sicherman's chiral/disallowing-reflection figure. The standalone grey R at upper left is the reference R pentacube, not a sixth piece. The four colours used in the construction are red, gold, green, and aqua; gold is used for two copies.

## 1. Geometry and symmetry convention

The repository's R pentacube is

```text
{(0,0,0), (1,0,0), (1,1,0), (1,1,1), (2,1,0)}
```

Only the 24 proper cube rotations (`common.rotmatrix.RM`) are allowed. Reflections of R are forbidden.

EE4 is dual orthogonal mirror symmetry: two perpendicular coordinate mirror planes, with their product the corresponding 180-degree rotation. In the repository this is the order-4 Klein-four class.

## 2. Verified computational result

The corrected EE4 search established:

- 2,072,331 connected 25-cell EE4 targets were considered.
- 16 R-tilings were found.
- These comprise 4 canonical targets.
- The `tests/fixtures/ee4_R_5.json` witness is canonical target #1.
- The resulting target is the single EE4 "wall" shape in the canonical representation.

A coordinate-frame bug in the earlier search was corrected by translating the placement domain to include the negative-coordinate EE4 targets; `tests/test_ee4_coordinate_frame.py` protects that regression.

Those search results establish the mathematical existence result independently of the image comparison below.

## 3. George image reconstruction

Image used:

```text
5-17p.png
size: 169 x 142
sha256: 5f6731b2ae7af325d5b3f7d483fb9b6ec1a3a354b78c335286976ea0e70400e3
```

A key point in decoding the figure is that the small diagrams along the bottom are **the four z cross-sections of the construction**, not merely a colour palette.

The two middle diagrams are 3 x 5 cross-sections. Rows are x = -1, 0, 1; columns are y = -2, -1, 0, 1, 2. The two end diagrams show the two occupied cells in the outer layers.

Using `R` = red, `G` = gold, `N` = green, and `A` = aqua, the four layers decode to:

```text
z = +1:  ..R.G.   (occupied cells at x=0, y=-1,+1)

z =  0:
    .RRA.
    GR.GG
    .NNG.

z = -1:
    .RAA.
    GGNAG
    .GNN.

z = -2:  ..G.A.   (occupied cells at x=0, y=-1,+1)
```

The resulting target has exactly 25 cells.

## 4. Exact target comparison

The reconstructed target is:

```text
z=+1:
  (0,-1), (0,1)

z=0:
  (-1,-1), (-1,0), (-1,1),
  (0,-2), (0,-1), (0,1), (0,2),
  (1,-1), (1,0), (1,1)

z=-1:
  (-1,-1), (-1,0), (-1,1),
  (0,-2), (0,-1), (0,0), (0,1), (0,2),
  (1,-1), (1,0), (1,1)

z=-2:
  (0,-1), (0,1)
```

This is **identical cell-for-cell** to the target stored in `tests/fixtures/ee4_R_5.json`.

## 5. Exact five-piece reconstruction

The image's coloured cell sets reconstruct as follows.

### Green -> fixture P1

```text
(0,0,-1),
(1,-1,0),
(1,0,-1),
(1,0,0),
(1,1,-1)
```

This is exactly fixture `P1 = RM[5] + (1,-1,0)`.

### Gold -> fixture P2 + P3

The ten gold cells admit exactly two ordered 5+5 assignments, which differ only by swapping the two gold copies. The unordered partition is exactly:

```text
P2 = RM[11] + (0,2,-1):
  (0,1,0), (0,1,1), (0,2,-1), (0,2,0), (1,1,0)

P3 = RM[3] + (0,-2,0):
  (0,-2,-1), (0,-2,0), (0,-1,-2), (0,-1,-1), (1,-1,-1)
```

### Aqua -> fixture P4

```text
(-1,0,-1),
(-1,1,-1),
(-1,1,0),
(0,1,-2),
(0,1,-1)
```

This is exactly fixture `P4 = RM[17] + (0,1,-2)`.

### Red -> fixture P5

```text
(-1,-1,-1),
(-1,-1,0),
(-1,0,0),
(0,-1,0),
(0,-1,1)
```

This is exactly fixture `P5 = RM[23] + (0,-1,1)`.

Every reconstructed piece is a proper-rotation image of R; no reflected R piece is required.

## 6. Verdict

### A — exact match

The following independent checks all pass:

```text
target_exact              = True
green_exact_P1            = True
aqua_exact_P4             = True
red_exact_P5              = True
gold_exact_P2_P3          = True
all_five_piece_sets_exact = True
```

Therefore George's pictured construction is not merely another EE4 tiling of the same shape. It is the **same target and the same five placements** as the verified repository fixture, up to interchange of the two indistinguishable gold pieces.

**George's construction independently reproduced.**

## 7. Reproducibility

From the repository root, run:

```bash
python3 tools/frontier/analyze_george_figure.py \
  .opencode/openwork/inbox/chat-attachments/ses_f53cacb6fffe6REnaT6WcXctid/1fb056bd-5da6-442c-b2c5-6abbfae0bfee-5-17p.png \
  --json data/ee4_george_comparison.json
```

Expected final lines include:

```text
target_exact= True
green=P1: True
aqua=P4 : True
red=P5  : True
gold=P2+P3: True
gold_partitions= 2
VERDICT= A
George's construction independently reproduced: exact target and exact five-piece placement sets, with the two gold copies interchangeable.
```

No exhaustive search is performed by this comparison script.

## 8. Scope boundary

This closes the EE4/R-5 image-reconstruction question. No CK6/V45 data or code is involved in the reconstruction, and no new impossibility claim is made here.

---
*Finalised 2026-09-18.*
