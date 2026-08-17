# Z-Frontier: Relations Among the 17 Component Shapes

Source: the 17 distinct connected-component shapes of the 100
layer-1 frontiers (`docs/z_frontier_component_shapes.md`), and the
per-shape structure (`docs/z_frontier_shape_structure.md`).

Shape numbering below follows `docs/z_frontier_component_shapes.md`
(order of first appearance).

## 1. Equivalence classes under rotation and reflection

Two shapes are in the same class if one can be obtained from the
other by rotation and/or reflection (then re-translated).

| Class | Shapes | Size | Orientations present | Total count |
|---|---|---|---|---|
| 1 | 1 | 1 | 1 of 1 | 620 |
| 2 | 2, 3 | 2 | 2 of 2 | 70 |
| 4 | 4, 6 | 3 | 2 of 2 | 12 |
| 5 | 5, 11, 15, 17 | 4 | 4 of 8 | 7 |
| 7 | 7, 8, 9, 14 | 3 | 4 of 4 | 16 |
| 10 | 10 | 4 | 1 of 4 | 1 |
| 12 | 12 | 4 | 1 of 2 | 1 |
| 13 | 13, 16 | 4 | 2 of 4 | 2 |

Notes:

- The single cell (shape 1) is invariant under all rotations and
  reflections.
- The domino (shapes 2, 3) and the straight triomino (shapes 4, 6)
  each occur in both of their orientations (horizontal and vertical).
- The L triomino (shapes 7, 8, 9, 14) occurs in all four of its
  orientations.
- The L tetromino (shapes 5, 11, 15, 17) occurs in four of its eight
  orientations (all four rotations of one chirality; the mirror
  chirality never occurs).
- The T tetromino (shapes 13, 16) occurs in two of its four
  orientations.
- The straight tetromino (shape 12) occurs in only one of its two
  orientations (vertical; the horizontal `####` never occurs).
- The S/Z tetromino (shape 10) occurs in only one of its four
  orientations.

## 2. Shapes occurring in multiple orientations

Shapes whose rotation/reflection also occurs among the 17:

- Domino: shapes 2 and 3.
- Straight triomino: shapes 4 and 6.
- L triomino: shapes 7, 8, 9, 14.
- L tetromino: shapes 5, 11, 15, 17.
- T tetromino: shapes 13 and 16.

## 3. Shapes occurring only once

Shapes with frequency 1 across all 100 frontiers:

- Shape 10 (S/Z tetromino, `.#`/`##`/`#.`).
- Shape 11 (L tetromino, `..#`/`###`).
- Shape 12 (straight tetromino, `#`/`#`/`#`/`#`).
- Shape 13 (T tetromino, `.#.`/`###`).
- Shape 14 (L triomino, `##`/`#.`).
- Shape 16 (T tetromino, `###`/`.#.`).
- Shape 17 (L tetromino, `##`/`.#`/`.#`).

Note: occurring once is independent of orientation class. Shape 11,
for example, occurs once but is one of four orientations of the L
tetromino; shape 10 occurs once and is the only orientation of its
class that occurs at all.

## 4. Shapes that appear together in the same frontier

A pair (i, j) below means shapes i and j occur as components of the
same layer-1 frontier in at least one record. Count = number of
records in which the pair co-occurs.

### Co-occurring pairs

| Pair | Count |
|---|---|
| 1 + 1 | 1728 |
| 1 + 2 | 225 |
| 1 + 3 | 163 |
| 1 + 4 | 24 |
| 1 + 5 | 13 |
| 1 + 6 | 36 |
| 1 + 7 | 34 |
| 1 + 8 | 28 |
| 1 + 9 | 18 |
| 1 + 10 | 5 |
| 1 + 11 | 5 |
| 1 + 12 | 3 |
| 1 + 13 | 5 |
| 1 + 14 | 4 |
| 1 + 15 | 10 |
| 1 + 16 | 5 |
| 1 + 17 | 5 |
| 2 + 2 | 5 |
| 2 + 3 | 8 |
| 2 + 4 | 3 |
| 2 + 5 | 1 |
| 2 + 6 | 3 |
| 2 + 7 | 1 |
| 2 + 8 | 2 |
| 2 + 12 | 1 |
| 2 + 14 | 1 |
| 3 + 3 | 1 |
| 3 + 8 | 2 |

Note: the pair table also includes same-shape pairs (i + i), meaning
two components of the same shape occur in one frontier (e.g. 1 + 1 =
two isolated cells). The never-co-occur list below covers pairs of
distinct shapes only.

### Distinct per-frontier shape sets

The 100 frontiers realize the following distinct sets of component
shapes (shape indices sorted; count = number of records):

| Shape set | Count |
|---|---|
| (1, 1, 1, 1, 1, 1, 1, 2) | 15 |
| (1, 1, 1, 1, 1, 1, 1, 3) | 15 |
| (1, 1, 1, 1, 1, 1, 1, 1) | 11 |
| (1, 1, 1, 1, 1, 2, 3) | 8 |
| (1, 1, 1, 1, 1, 1, 1, 1, 1) | 7 |
| (1, 1, 1, 1, 1, 1, 7) | 5 |
| (1, 1, 1, 1, 1, 1, 6) | 4 |
| (1, 1, 1, 1, 1, 1, 4) | 3 |
| (1, 1, 1, 1, 1, 1, 9) | 3 |
| (1, 1, 1, 1, 1, 2, 2) | 3 |
| (1, 1, 1, 1, 2, 6) | 3 |
| (1, 1, 1, 1, 1, 1, 8) | 2 |
| (1, 1, 1, 1, 1, 5) | 2 |
| (1, 1, 1, 1, 1, 15) | 2 |
| (1, 1, 1, 1, 2, 8) | 2 |
| (1, 1, 1, 1, 3, 8) | 2 |
| (1, 1, 1, 1, 1, 3, 3) | 1 |
| (1, 1, 1, 1, 1, 10) | 1 |
| (1, 1, 1, 1, 1, 11) | 1 |
| (1, 1, 1, 1, 1, 13) | 1 |
| (1, 1, 1, 1, 1, 16) | 1 |
| (1, 1, 1, 1, 1, 17) | 1 |
| (1, 1, 1, 1, 2, 2) | 1 |
| (1, 1, 1, 1, 2, 4) | 1 |
| (1, 1, 1, 1, 2, 7) | 1 |
| (1, 1, 1, 1, 2, 14) | 1 |
| (1, 1, 1, 2, 5) | 1 |
| (1, 1, 1, 2, 12) | 1 |
| (1, 1, 2, 2, 4) | 1 |

### Shapes that never co-occur

Pairs that never appear together: 111 of 136 possible pairs.

| Pair |
|---|---|
| 2 + 9 |
| 2 + 10 |
| 2 + 11 |
| 2 + 13 |
| 2 + 15 |
| 2 + 16 |
| 2 + 17 |
| 3 + 4 |
| 3 + 5 |
| 3 + 6 |
| 3 + 7 |
| 3 + 9 |
| 3 + 10 |
| 3 + 11 |
| 3 + 12 |
| 3 + 13 |
| 3 + 14 |
| 3 + 15 |
| 3 + 16 |
| 3 + 17 |
| 4 + 5 |
| 4 + 6 |
| 4 + 7 |
| 4 + 8 |
| 4 + 9 |
| 4 + 10 |
| 4 + 11 |
| 4 + 12 |
| 4 + 13 |
| 4 + 14 |
| 4 + 15 |
| 4 + 16 |
| 4 + 17 |
| 5 + 6 |
| 5 + 7 |
| 5 + 8 |
| 5 + 9 |
| 5 + 10 |
| 5 + 11 |
| 5 + 12 |
| 5 + 13 |
| 5 + 14 |
| 5 + 15 |
| 5 + 16 |
| 5 + 17 |
| 6 + 7 |
| 6 + 8 |
| 6 + 9 |
| 6 + 10 |
| 6 + 11 |
| 6 + 12 |
| 6 + 13 |
| 6 + 14 |
| 6 + 15 |
| 6 + 16 |
| 6 + 17 |
| 7 + 8 |
| 7 + 9 |
| 7 + 10 |
| 7 + 11 |
| 7 + 12 |
| 7 + 13 |
| 7 + 14 |
| 7 + 15 |
| 7 + 16 |
| 7 + 17 |
| 8 + 9 |
| 8 + 10 |
| 8 + 11 |
| 8 + 12 |
| 8 + 13 |
| 8 + 14 |
| 8 + 15 |
| 8 + 16 |
| 8 + 17 |
| 9 + 10 |
| 9 + 11 |
| 9 + 12 |
| 9 + 13 |
| 9 + 14 |
| 9 + 15 |
| 9 + 16 |
| 9 + 17 |
| 10 + 11 |
| 10 + 12 |
| 10 + 13 |
| 10 + 14 |
| 10 + 15 |
| 10 + 16 |
| 10 + 17 |
| 11 + 12 |
| 11 + 13 |
| 11 + 14 |
| 11 + 15 |
| 11 + 16 |
| 11 + 17 |
| 12 + 13 |
| 12 + 14 |
| 12 + 15 |
| 12 + 16 |
| 12 + 17 |
| 13 + 14 |
| 13 + 15 |
| 13 + 16 |
| 13 + 17 |
| 14 + 15 |
| 14 + 16 |
| 14 + 17 |
| 15 + 16 |
| 15 + 17 |
| 16 + 17 |

