# EE4 5-R tiling catalogue

Complete classification of all tilings of 25-cell EE4-invariant targets by five copies of the chiral pentacube **R** inside the 5×5×5 box. Reflections are forbidden (R is chiral); only proper rotations and translations of R are used.

## Result

We independently exhaustively classified all 5-R EE4 tilings:

- **16 raw tilings** of **8 literal targets** (4 canonical targets, one shape).
- **8 equivalence classes under target symmetry** (orbits of the proper subgroup {I, RZ} of the target's EE4 group).
- **1 equivalence class under full cubic symmetry O_h** (also 1 under proper rotations alone).
- **8 orientation-multiset families** of 2 tilings each (pure translates of each other).

## Verified counts

| quantity | value |
|---|---|
| connected EE4-invariant 25-cell targets | 2,072,331 |
| orbit-subsets explored | 5,630,888 |
| search nodes | 119,023 |
| raw tilings | 16 |
| literal targets | 8 |
| canonical targets | 4 |
| target classes under proper rotations | 1 |
| target classes under O_h | 1 |
| tiling classes under target symmetry | 8 |
| tiling classes under proper rotations | 1 |
| tiling classes under O_h | 1 |
| orientation-multiset classes | 8 |

## Structure

### Targets

- The 4 canonical targets are all **proper-rotation-equivalent**: one shape in 4 placements (related by c4, c2_ortho, c2_diag).
- Each canonical class contains **2 literal targets**, pure translates by (0, 0, ±1) along z.
- Every target has EE4 symmetry of order 4: {I, RZ, MX, MY}; the proper part is {I, RZ} (c2 about z).

### Tilings

- Each literal target has exactly **2 tilings**, related by RZ (the proper c2 about z).
- Every tiling has **trivial stabilizer** within the target's full EE4 group: each decomposition breaks all three nontrivial target symmetries (RZ, MX, MY).
- The two tilings of one literal target have **different RM multisets** (conjugate under RZ).
- The translate partner on the other literal target has the **same RM multiset**.
- All 16 tilings are equivalent under proper rotations + translations: **1 class under O_h** (and under proper rotations).

## The 8 classes under target symmetry

Each class is an RZ-orbit {T, RZ·T} on one literal target. Renders: `data/ee4_R_5/catalogue/`.

| class | tilings | canon | literal | RM multiset (T, RZ·T) | translate partner | render |
|---|---|---|---|---|---|---|
| 0, 9 | T0, T9 | 3 | A/A | {1, 3, 17, 19, 20}, {9, 11, 18, 21, 23} | T2 | `class_M1_3_17_19_20.png` |
| 1, 8 | T1, T8 | 4 | A/A | {1, 3, 17, 19, 22}, {9, 11, 16, 21, 23} | T3 | `class_M1_3_17_19_22.png` |
| 2, 11 | T2, T11 | 3 | B/B | {1, 3, 17, 19, 20}, {9, 11, 18, 21, 23} | T0 | `class_M1_3_17_19_20.png` |
| 3, 10 | T3, T10 | 4 | B/B | {1, 3, 17, 19, 22}, {9, 11, 16, 21, 23} | T1 | `class_M1_3_17_19_22.png` |
| 4, 7 | T4, T7 | 1 | B/B | {3, 5, 11, 17, 23}, {1, 9, 15, 19, 21} | T12 | `class_M3_5_11_17_23.png` |
| 5, 6 | T5, T6 | 2 | B/B | {3, 11, 13, 17, 23}, {1, 7, 9, 19, 21} | T13 | `class_M3_11_13_17_23.png` |
| 12, 15 | T12, T15 | 1 | A/A | {3, 5, 11, 17, 23}, {1, 9, 15, 19, 21} | T4 | `class_M3_5_11_17_23.png` |
| 13, 14 | T13, T14 | 2 | A/A | {3, 11, 13, 17, 23}, {1, 7, 9, 19, 21} | T5 | `class_M3_11_13_17_23.png` |

## Orientation-multiset families (8)

Each family pairs the two tilings with the same RM multiset; they are **pure translates** of each other (same decomposition, shifted by (0, 0, ±1) onto the other literal target of the same canonical class). They are *not* related by any target symmetry.

| multiset | tilings | translation | canonical target |
|---|---|---|---|
| {1, 3, 17, 19, 20} | T0, T2 | (0, 0, -1) | 3 |
| {1, 3, 17, 19, 22} | T1, T3 | (0, 0, -1) | 4 |
| {3, 5, 11, 17, 23} | T4, T12 | (0, 0, 1) | 1 |
| {3, 11, 13, 17, 23} | T5, T13 | (0, 0, 1) | 2 |
| {1, 7, 9, 19, 21} | T6, T14 | (0, 0, 1) | 2 |
| {1, 9, 15, 19, 21} | T7, T15 | (0, 0, 1) | 1 |
| {9, 11, 16, 21, 23} | T8, T10 | (0, 0, -1) | 4 |
| {9, 11, 18, 21, 23} | T9, T11 | (0, 0, -1) | 3 |

## Full tiling table

| id | canon | literal | RM multiset | piece translations | adjacency | contacts | boundary | fixed-plane cells | axis cells | stabilizer |
|---|---|---|---|---|---|---|---|---|---|---|
| T0 | 3 | A | {1, 3, 17, 19, 20} | (1,0,-1) / (-1,0,2) / (-2,0,1) / (2,0,0) / (-1,-1,1) | [1,3,4] / [0,2,4] / [1,4] / [0,4] / [0,1,2,3] | [0,3,0,3,3] / [3,0,3,0,1] / [0,3,0,0,3] / [3,0,0,0,2] / [3,1,3,2,0] | x-:[2] x+:[3] y-:[] y+:[] z-:[] z+:[1, 3] | [1,2,3] / [1,2,1] / [0,4,3] / [0,4,1] / [3,1,3] | – / – / – / – / [[0, 0, 0]] | identity |
| T1 | 4 | A | {1, 3, 17, 19, 22} | (1,0,-1) / (-1,0,2) / (-2,0,1) / (2,0,0) / (1,-1,0) | [1,3,4] / [0,2,4] / [1,4] / [0,4] / [0,1,2,3] | [0,3,0,3,1] / [3,0,3,0,3] / [0,3,0,0,2] / [3,0,0,0,3] / [1,3,2,3,0] | x-:[2] x+:[3] y-:[] y+:[] z-:[] z+:[1, 3] | [1,2,3] / [1,2,1] / [0,4,3] / [0,4,1] / [3,1,2] | – / – / – / – / [[0, 0, 1]] | identity |
| T2 | 3 | B | {1, 3, 17, 19, 20} | (1,0,-2) / (-1,0,1) / (-1,-1,0) / (2,0,-1) / (-2,0,0) | [1,2,3] / [0,2,4] / [0,1,3,4] / [0,2] / [1,2] | [0,3,3,3,0] / [3,0,1,0,3] / [3,1,0,2,3] / [3,0,2,0,0] / [0,3,3,0,0] | x-:[4] x+:[3] y-:[] y+:[] z-:[0, 4] z+:[] | [1,2,1] / [1,2,3] / [3,1,2] / [0,4,3] / [0,4,1] | – / – / [[0, 0, -1]] / – / – | identity |
| T3 | 4 | B | {1, 3, 17, 19, 22} | (1,0,-2) / (-1,0,1) / (1,-1,-1) / (2,0,-1) / (-2,0,0) | [1,2,3] / [0,2,4] / [0,1,3,4] / [0,2] / [1,2] | [0,3,1,3,0] / [3,0,3,0,3] / [1,3,0,3,2] / [3,0,3,0,0] / [0,3,2,0,0] | x-:[4] x+:[3] y-:[] y+:[] z-:[0, 4] z+:[] | [1,2,1] / [1,2,3] / [3,1,3] / [0,4,3] / [0,4,1] | – / – / [[0, 0, 0]] / – / – | identity |
| T4 | 1 | B | {3, 5, 11, 17, 23} | (1,-1,0) / (0,2,-1) / (0,-2,0) / (0,1,-2) / (0,-1,1) | [1,2,3,4] / [0,3] / [0,4] / [0,1,4] / [0,2,3] | [0,2,3,3,1] / [2,0,0,3,0] / [3,0,0,0,3] / [3,3,0,0,3] / [1,0,3,3,0] | x-:[] x+:[] y-:[2] y+:[1] z-:[2, 3] z+:[] | [1,3,2] / [4,0,3] / [4,0,1] / [2,1,1] / [2,1,3] | [[0, 0, -1]] / – / – / – / – | identity |
| T5 | 2 | B | {3, 11, 13, 17, 23} | (1,1,-1) / (0,2,-1) / (0,-2,0) / (0,1,-2) / (0,-1,1) | [1,2,3,4] / [0,3] / [0,4] / [0,1,4] / [0,2,3] | [0,3,2,1,3] / [3,0,0,3,0] / [2,0,0,0,3] / [1,3,0,0,3] / [3,0,3,3,0] | x-:[] x+:[] y-:[2] y+:[1] z-:[2, 3] z+:[] | [1,3,3] / [4,0,3] / [4,0,1] / [2,1,1] / [2,1,3] | [[0, 0, 0]] / – / – / – / – | identity |
| T6 | 2 | B | {1, 7, 9, 19, 21} | (0,-1,-2) / (0,1,1) / (0,-2,-1) / (-1,-1,-1) / (0,2,0) | [1,2,3] / [0,3,4] / [0,3] / [0,1,2,4] / [1,3] | [0,3,3,1,0] / [3,0,0,3,3] / [3,0,0,3,0] / [1,3,3,0,2] / [0,3,0,2,0] | x-:[] x+:[] y-:[2] y+:[4] z-:[0, 4] z+:[] | [2,1,1] / [2,1,3] / [4,0,3] / [1,3,3] / [4,0,1] | – / – / – / [[0, 0, 0]] / – | identity |
| T7 | 1 | B | {1, 9, 15, 19, 21} | (0,-1,-2) / (0,1,1) / (0,-2,-1) / (-1,1,0) / (0,2,0) | [1,2,3] / [0,3,4] / [0,3] / [0,1,2,4] / [1,3] | [0,3,3,3,0] / [3,0,0,1,3] / [3,0,0,2,0] / [3,1,2,0,3] / [0,3,0,3,0] | x-:[] x+:[] y-:[2] y+:[4] z-:[0, 4] z+:[] | [2,1,1] / [2,1,3] / [4,0,3] / [1,3,2] / [4,0,1] | – / – / – / [[0, 0, -1]] / – | identity |
| T8 | 4 | A | {9, 11, 16, 21, 23} | (2,0,1) / (-1,1,0) / (-1,0,-1) / (1,0,2) / (-2,0,0) | [1,3] / [0,2,3,4] / [1,3,4] / [0,1,2] / [1,2] | [0,2,0,3,0] / [2,0,1,3,3] / [0,1,0,3,3] / [3,3,3,0,0] / [0,3,3,0,0] | x-:[4] x+:[0] y-:[] y+:[] z-:[] z+:[3, 4] | [0,4,3] / [3,1,2] / [1,2,3] / [1,2,1] / [0,4,1] | – / [[0, 0, 1]] / – / – / – | identity |
| T9 | 3 | A | {9, 11, 18, 21, 23} | (2,0,1) / (1,1,1) / (-1,0,-1) / (1,0,2) / (-2,0,0) | [1,3] / [0,2,3,4] / [1,3,4] / [0,1,2] / [1,2] | [0,3,0,3,0] / [3,0,3,1,2] / [0,3,0,3,3] / [3,1,3,0,0] / [0,2,3,0,0] | x-:[4] x+:[0] y-:[] y+:[] z-:[] z+:[3, 4] | [0,4,3] / [3,1,3] / [1,2,3] / [1,2,1] / [0,4,1] | – / [[0, 0, 0]] / – / – / – | identity |
| T10 | 4 | B | {9, 11, 16, 21, 23} | (2,0,0) / (-1,1,-1) / (-2,0,-1) / (-1,0,-2) / (1,0,1) | [1,4] / [0,2,3,4] / [1,3] / [1,2,4] / [0,1,3] | [0,2,0,0,3] / [2,0,3,1,3] / [0,3,0,3,0] / [0,1,3,0,3] / [3,3,0,3,0] | x-:[2] x+:[0] y-:[] y+:[] z-:[0, 3] z+:[] | [0,4,1] / [3,1,3] / [0,4,3] / [1,2,1] / [1,2,3] | – / [[0, 0, 0]] / – / – / – | identity |
| T11 | 3 | B | {9, 11, 18, 21, 23} | (2,0,0) / (1,1,0) / (-2,0,-1) / (-1,0,-2) / (1,0,1) | [1,4] / [0,2,3,4] / [1,3] / [1,2,4] / [0,1,3] | [0,3,0,0,3] / [3,0,2,3,1] / [0,2,0,3,0] / [0,3,3,0,3] / [3,1,0,3,0] | x-:[2] x+:[0] y-:[] y+:[] z-:[0, 3] z+:[] | [0,4,1] / [3,1,2] / [0,4,3] / [1,2,1] / [1,2,3] | – / [[0, 0, -1]] / – / – / – | identity |
| T12 | 1 | A | {3, 5, 11, 17, 23} | (1,-1,1) / (0,1,-1) / (0,-1,2) / (0,-2,1) / (0,2,0) | [1,2,3,4] / [0,2,4] / [0,1,3] / [0,2] / [0,1] | [0,3,1,3,2] / [3,0,3,0,3] / [1,3,0,3,0] / [3,0,3,0,0] / [2,3,0,0,0] | x-:[] x+:[] y-:[3] y+:[4] z-:[] z+:[2, 4] | [1,3,3] / [2,1,3] / [2,1,1] / [4,0,3] / [4,0,1] | [[0, 0, 0]] / – / – / – / – | identity |
| T13 | 2 | A | {3, 11, 13, 17, 23} | (1,1,0) / (0,1,-1) / (0,-1,2) / (0,-2,1) / (0,2,0) | [1,2,3,4] / [0,2,4] / [0,1,3] / [0,2] / [0,1] | [0,1,3,2,3] / [1,0,3,0,3] / [3,3,0,3,0] / [2,0,3,0,0] / [3,3,0,0,0] | x-:[] x+:[] y-:[3] y+:[4] z-:[] z+:[2, 4] | [1,3,2] / [2,1,3] / [2,1,1] / [4,0,3] / [4,0,1] | [[0, 0, 1]] / – / – / – / – | identity |
| T14 | 2 | A | {1, 7, 9, 19, 21} | (0,1,2) / (0,2,1) / (-1,-1,0) / (0,-2,0) / (0,-1,-1) | [1,2,4] / [0,2] / [0,1,3,4] / [2,4] / [0,2,3] | [0,3,3,0,3] / [3,0,2,0,0] / [3,2,0,3,1] / [0,0,3,0,3] / [3,0,1,3,0] | x-:[] x+:[] y-:[3] y+:[1] z-:[] z+:[0, 3] | [2,1,1] / [4,0,3] / [1,3,2] / [4,0,1] / [2,1,3] | – / – / [[0, 0, 1]] / – / – | identity |
| T15 | 1 | A | {1, 9, 15, 19, 21} | (0,1,2) / (0,2,1) / (-1,1,1) / (0,-2,0) / (0,-1,-1) | [1,2,4] / [0,2] / [0,1,3,4] / [2,4] / [0,2,3] | [0,3,1,0,3] / [3,0,3,0,0] / [1,3,0,2,3] / [0,0,2,0,3] / [3,0,3,3,0] | x-:[] x+:[] y-:[3] y+:[1] z-:[] z+:[0, 3] | [2,1,1] / [4,0,3] / [1,3,3] / [4,0,1] / [2,1,3] | – / – / [[0, 0, 0]] / – / – | identity |

## Relationship to George's 5-17p construction

George's construction uses RM indices {3, 5, 11, 17, 23} — exactly the multiset of the family {3, 5, 11, 17, 23} (tilings T4, T12). The 5-R EE4 construction is independently verified; the correspondence with George's particular 5-17p construction remains **unconfirmed** (his target and translations are not available to us).
