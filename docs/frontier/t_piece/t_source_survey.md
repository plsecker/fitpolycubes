# T-Pentacube Source Survey

**Date**: 2026-08-26  
**Status**: COMPLETE  
**Purpose**: Establish ground truth for T-pentacube Macro methodology transfer

---

## 1. Piece Definition

**Canonical coordinates** (from `common/registry.py`):
```
T = [[0,0,0],[1,0,0],[2,0,0],[1,1,0],[1,2,0]]
```

The T-pentacube is a flat T-shape in the xy-plane: a 3-cell horizontal bar with a 3-cell vertical stem centered at the middle cell.

**Shirakawa piece number**: 7 (of 12 pentominoes)  
**Kurnell number**: 80  
**Shirakawa URL**: https://puzzlewillbeplayed.com/Shirakawa/T.html

---

## 2. Rotational Orientations

**Total unique orientations**: 12 (same count as S-pentacube)

### Orientation classification by z-span:

| z-span | Count | Layer occupancy patterns |
|--------|-------|--------------------------|
| 1 (flat) | 4 | [5,0,0] — all 5 cells in one layer |
| 3 | 8 | [1,3,1], [3,1,1], [1,1,3] |

### Detailed orientation table:

| ID | z-span | Layer occ | Cells (canonical, min-z=0) |
|----|--------|-----------|-----------------------------|
| O0 | 1 | [5,0,0] | [[0,0,0],[1,0,0],[1,1,0],[1,2,0],[2,0,0]] |
| O1 | 3 | [1,3,1] | [[0,0,0],[0,0,1],[0,0,2],[0,1,1],[0,2,1]] |
| O2 | 1 | [5,0,0] | [[0,1,0],[1,1,0],[2,0,0],[2,1,0],[2,2,0]] |
| O3 | 3 | [1,1,3] | [[0,0,2],[0,1,0],[0,1,1],[0,1,2],[0,2,2]] |
| O4 | 1 | [5,0,0] | [[0,0,0],[0,1,0],[0,2,0],[1,1,0],[2,1,0]] |
| O5 | 3 | [3,1,1] | [[0,0,0],[0,1,0],[0,1,1],[0,1,2],[0,2,0]] |
| O6 | 1 | [5,0,0] | [[0,2,0],[1,0,0],[1,1,0],[1,2,0],[2,2,0]] |
| O7 | 3 | [1,3,1] | [[0,0,1],[0,1,1],[0,2,0],[0,2,1],[0,2,2]] |
| O8 | 3 | [3,1,1] | [[0,0,0],[1,0,0],[1,0,1],[1,0,2],[2,0,0]] |
| O9 | 3 | [1,3,1] | [[0,0,1],[1,0,1],[2,0,0],[2,0,1],[2,0,2]] |
| O10 | 3 | [1,1,3] | [[0,0,2],[1,0,0],[1,0,1],[1,0,2],[2,0,2]] |
| O11 | 3 | [1,3,1] | [[0,0,0],[0,0,1],[0,0,2],[1,0,1],[2,0,1]] |

### Key structural differences from S-pentacube:

1. **Flat orientations exist**: 4 of 12 orientations have z-span=1 (all 5 cells in one layer). This means T can fill a complete layer with a single piece, unlike S where every orientation spans 2 layers.

2. **z-span=3 orientations**: 8 orientations span 3 layers, with patterns [1,3,1], [3,1,1], [1,1,3]. The "thick" part (3 cells) can be in any of the three layers.

3. **No z-span=2 orientations**: Unlike S where all 12 orientations have z-span=2, T has no z-span=2 orientations at all.

4. **Chirality**: T is achiral (superposable on its mirror image). All 12 orientations are proper rotations; no reflection is needed.

---

## 3. Published Catalogue (Shirakawa/Sillke)

### Source: https://puzzlewillbeplayed.com/Shirakawa/T.html

The T page is the largest in the Shirakawa collection, covering thousands of entries across 3D, 4D, and 5D.

### 3D Primes (from `catalogues/t_catalogue.py`):

**85 prime boxes** across the following families:

| Family | Primes | Notes |
|--------|--------|-------|
| 3×7×N | 20 | Minimal 3-width prime |
| 3×8×N | 15, 35, 40 | |
| 3×10×N | 10, 14, 26, 27, 31, 32, 33, 35, 39 | 3×10×10 is minimal overall prime (Göbel 1989) |
| 3×11×N | 30, 35, 40, 45, 50, 55 | |
| 3×12×N | 15, 20, 25 | |
| 3×13×N | 20, 25, 30, 35 | |
| 3×14×N | 15 | |
| 3×15×N | 17, 18, 19, 21, 23 | 3×15×17 is minimal odd prime |
| 3×16+ | 20, 25 (various widths) | |
| 4×11×N | 80, 85, 100, 105, 110, 120 | |
| 4×12×N | 40, 45, 50, 55, 60, 65, 70, 75 | |
| 4×14×N | 20, 25, 30, 35 | |
| 4×15×N | 26, 28 | |
| 4×16/18/20 | 20, 22, 24 | |
| 5×5×N | 12 | Minimal even prime (Beeler 1990) |
| 5×8×N | 100, 103, 114, 118, 121, 128, 130-136, 137-199 | Extensive family |
| 5×9×N | 48, 60 | |
| 5×12×N | 13 | |
| 5×15×N | 18 | |
| 6×10×N | 15 | |
| 8×8×N | 10 | |
| 8×10×N | 10 | |

### Minimal primes:
- **Minimal odd**: 3×15×17 (van de Konijnenberg 2009)
- **Minimal even**: 8×8×10 (Shirakawa 2014)
- **Smallest overall**: 3×10×10 (Göbel 1989)

### Known impossible families:
- 3×[3-6]×N, 3×9×N: all impossible
- 3×7×N: only multiples of 20 work
- 3×10×N: many specific lengths impossible
- 4×[4-9]×N: all impossible
- 4×10×N: all impossible
- 4×11×N: many lengths impossible (s:0 notation = semigroup)
- 5×[6-7]×N: all impossible
- 5×8×[8-99]: all impossible (except primes)
- 5×9×[9-32]: all impossible
- 5×10×[10-11]: impossible
- 6×6×N: all impossible
- 6×7×N: many lengths impossible

---

## 4. Existing Repository Data

### Solution files:
| File | Box | Source | Format |
|------|-----|--------|--------|
| `data/solutions_hybrid_t_5x10x10.dat` | 5×10×10 | Hybrid MP+Numba solver | Binary (header only) |
| `data/solutions_hybrid_t_5x10x28.dat` | 5×10×28 | Hybrid MP+Numba solver | Binary (header only) |

Both files appear to contain only a header line; no actual placement data is readable.

### Existing code:
| File | Purpose |
|------|---------|
| `solvers/t_3x15_macro_feasibility.py` | Quick Macro feasibility test for 3×15×17 |
| `catalogues/t_catalogue.py` | Catalogue with 85 primes, impossible families |
| `docs/pieces/T.md` | Piece audit document |
| `docs/frontier/t_3x15x17_second_orbit.md` | Investigation report (UNDETERMINED) |

### No SVG witnesses exist in the repository.
No SVG files, no extracted `.dat` solutions with actual placement data, and no concrete tiling data for T.

---

## 5. Available SVG Witnesses (External)

The Shirakawa T page does NOT appear to contain inline SVG images for individual tilings (unlike the S page which had SVG solutions for 4×9, 5×7, 5×9, 5×10 cross-sections).

The Sicherman odd-box page (referenced in `t_3x15x17_second_orbit.md`) has an image of the 3×15×17 tiling, but this has not been extracted.

**No machine-readable T tiling data is available from published sources in this repository.**

---

## 6. Key Implications for Macro Transfer

1. **Flat orientations change the state model**: With z-span=1 orientations, a single piece can fill an entire layer. This means the "fill L0" phase of a macro edge can complete in 1 piece instead of requiring multiple pieces.

2. **3-layer state model still works**: The maximum z-span is 3 (same as S), so the 3-layer frontier window is sufficient.

3. **Gate state may differ**: With flat orientations, the gate state (FULL,0,0) may be reachable differently since a single flat piece can fill L0 completely.

4. **No SVG witnesses available**: Unlike S where SVG extraction was the primary cycle discovery method, T has no readily extractable SVG solutions. This means cycle discovery must rely on:
   - Direct solver searches (for small boxes like 3×10×10, 5×5×12)
   - External tiling data acquisition
   - Macro closure computation (if tractable)

5. **Computational challenge**: The minimal odd box 3×15×17 has 45 cells per layer and 153 pieces, making direct Macro closure infeasible (as confirmed by `t_3x15_macro_feasibility.py`).

6. **Best initial targets for cycle discovery**:
   - 3×10×10 (smallest prime, 60 pieces, 30 cells/layer)
   - 5×5×12 (smallest even prime, 60 pieces, 25 cells/layer)
   - 3×7×20 (30 cells/layer, 84 pieces)
   - 3×8×15 (24 cells/layer, 72 pieces)

---

## 7. Provenance

| Source | Date | Contents |
|--------|------|----------|
| `common/registry.py` | Repository | T piece coordinates |
| `common/rotmatrix.py` | Repository | 24 rotation matrices |
| `catalogues/t_catalogue.py` | Repository | 85 primes, impossibility rules |
| `shirakawa/T.md` | Repository | Page summary (lossy) |
| `docs/pieces/T.md` | 2026-08-10 | Piece audit |
| `docs/frontier/t_3x15x17_second_orbit.md` | 2026-08-21 | Feasibility investigation |
| `solvers/t_3x15_macro_feasibility.py` | Repository | Macro feasibility test |
| `https://puzzlewillbeplayed.com/Shirakawa/T.html` | Feb 18, 2015 | Primary source (fetched 2026-08-26) |