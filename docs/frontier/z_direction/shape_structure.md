# Z-Frontier: Structure of the 100 Layer-1 Shapes

Source: the 100 layer-1 shapes of the layer-shift states in
`docs/z_frontier_shift_shapes.md` (states from
`docs/z_frontier_state_stats_1m.md`, lines 140-239).

## Method

- Grid: 4 columns (x = 0-3) by 8 rows (y = 0-7), bit = x + 4y.
- Connectivity: 4-neighbor (orthogonal adjacency).
- Component classification:
  - **P (path)**: every cell has at most 2 in-component neighbors
    (includes isolated single cells).
  - **C (cycle)**: every cell has exactly 2 in-component neighbors.
  - **N (neither)**: some cell has 3 or more in-component neighbors
    (branching).

## Per-shape table

| Rec | Cells | Comps | Component sizes | Kinds |
|---|---|---|---|---|
| 1 | 8 | 8 | 1+1+1+1+1+1+1+1 | PPPPPPPP |
| 2 | 8 | 6 | 2+2+1+1+1+1 | PPPPPP |
| 3 | 8 | 8 | 1+1+1+1+1+1+1+1 | PPPPPPPP |
| 4 | 8 | 8 | 1+1+1+1+1+1+1+1 | PPPPPPPP |
| 5 | 8 | 8 | 1+1+1+1+1+1+1+1 | PPPPPPPP |
| 6 | 8 | 8 | 1+1+1+1+1+1+1+1 | PPPPPPPP |
| 7 | 8 | 8 | 1+1+1+1+1+1+1+1 | PPPPPPPP |
| 8 | 8 | 8 | 1+1+1+1+1+1+1+1 | PPPPPPPP |
| 9 | 8 | 8 | 1+1+1+1+1+1+1+1 | PPPPPPPP |
| 10 | 8 | 8 | 1+1+1+1+1+1+1+1 | PPPPPPPP |
| 11 | 8 | 8 | 1+1+1+1+1+1+1+1 | PPPPPPPP |
| 12 | 8 | 8 | 1+1+1+1+1+1+1+1 | PPPPPPPP |
| 13 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 14 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 15 | 9 | 7 | 2+2+1+1+1+1+1 | PPPPPPP |
| 16 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 17 | 9 | 6 | 3+2+1+1+1+1 | PPPPPP |
| 18 | 9 | 7 | 2+2+1+1+1+1+1 | PPPPPPP |
| 19 | 9 | 6 | 4+1+1+1+1+1 | PPPPPP |
| 20 | 9 | 6 | 3+2+1+1+1+1 | PPPPPP |
| 21 | 9 | 7 | 3+1+1+1+1+1+1 | PPPPPPP |
| 22 | 9 | 7 | 3+1+1+1+1+1+1 | PPPPPPP |
| 23 | 9 | 6 | 4+1+1+1+1+1 | PPPPPP |
| 24 | 9 | 6 | 3+2+1+1+1+1 | PPPPPP |
| 25 | 9 | 7 | 2+2+1+1+1+1+1 | PPPPPPP |
| 26 | 9 | 7 | 2+2+1+1+1+1+1 | PPPPPPP |
| 27 | 9 | 7 | 2+2+1+1+1+1+1 | PPPPPPP |
| 28 | 9 | 6 | 3+2+1+1+1+1 | PPPPPP |
| 29 | 9 | 7 | 3+1+1+1+1+1+1 | PPPPPPP |
| 30 | 9 | 7 | 3+1+1+1+1+1+1 | PPPPPPP |
| 31 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 32 | 9 | 6 | 3+2+1+1+1+1 | PPPPPP |
| 33 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 34 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 35 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 36 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 37 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 38 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 39 | 9 | 6 | 4+1+1+1+1+1 | PPPPPP |
| 40 | 9 | 7 | 3+1+1+1+1+1+1 | PPPPPPP |
| 41 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 42 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 43 | 9 | 6 | 4+1+1+1+1+1 | PPPPPP |
| 44 | 9 | 5 | 4+2+1+1+1 | PPPPP |
| 45 | 9 | 5 | 4+2+1+1+1 | PPPPP |
| 46 | 9 | 5 | 3+2+2+1+1 | PPPPP |
| 47 | 9 | 7 | 2+2+1+1+1+1+1 | PPPPPPP |
| 48 | 9 | 7 | 3+1+1+1+1+1+1 | PPPPPPP |
| 49 | 9 | 6 | 3+2+1+1+1+1 | PPPPPP |
| 50 | 9 | 6 | 3+2+1+1+1+1 | PPPPPP |
| 51 | 9 | 7 | 2+2+1+1+1+1+1 | PPPPPPP |
| 52 | 9 | 7 | 3+1+1+1+1+1+1 | PPPPPPP |
| 53 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 54 | 9 | 7 | 2+2+1+1+1+1+1 | PPPPPPP |
| 55 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 56 | 9 | 9 | 1+1+1+1+1+1+1+1+1 | PPPPPPPPP |
| 57 | 9 | 6 | 4+1+1+1+1+1 | NPPPPP |
| 58 | 9 | 7 | 3+1+1+1+1+1+1 | PPPPPPP |
| 59 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 60 | 9 | 6 | 3+2+1+1+1+1 | PPPPPP |
| 61 | 9 | 7 | 3+1+1+1+1+1+1 | PPPPPPP |
| 62 | 9 | 6 | 4+1+1+1+1+1 | PPPPPP |
| 63 | 9 | 7 | 3+1+1+1+1+1+1 | PPPPPPP |
| 64 | 9 | 6 | 4+1+1+1+1+1 | PPNPPP |
| 65 | 9 | 7 | 3+1+1+1+1+1+1 | PPPPPPP |
| 66 | 9 | 7 | 2+2+1+1+1+1+1 | PPPPPPP |
| 67 | 9 | 6 | 4+1+1+1+1+1 | PPPPPP |
| 68 | 9 | 6 | 3+2+1+1+1+1 | PPPPPP |
| 69 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 70 | 9 | 6 | 4+1+1+1+1+1 | PPPPPP |
| 71 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 72 | 9 | 7 | 3+1+1+1+1+1+1 | PPPPPPP |
| 73 | 9 | 7 | 3+1+1+1+1+1+1 | PPPPPPP |
| 74 | 9 | 9 | 1+1+1+1+1+1+1+1+1 | PPPPPPPPP |
| 75 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 76 | 9 | 7 | 3+1+1+1+1+1+1 | PPPPPPP |
| 77 | 9 | 9 | 1+1+1+1+1+1+1+1+1 | PPPPPPPPP |
| 78 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 79 | 9 | 7 | 2+2+1+1+1+1+1 | PPPPPPP |
| 80 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 81 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 82 | 9 | 7 | 2+2+1+1+1+1+1 | PPPPPPP |
| 83 | 9 | 6 | 3+2+1+1+1+1 | PPPPPP |
| 84 | 9 | 7 | 3+1+1+1+1+1+1 | PPPPPPP |
| 85 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 86 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 87 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 88 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 89 | 9 | 7 | 3+1+1+1+1+1+1 | PPPPPPP |
| 90 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 91 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 92 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 93 | 9 | 9 | 1+1+1+1+1+1+1+1+1 | PPPPPPPPP |
| 94 | 9 | 7 | 3+1+1+1+1+1+1 | PPPPPPP |
| 95 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 96 | 9 | 7 | 2+2+1+1+1+1+1 | PPPPPPP |
| 97 | 9 | 9 | 1+1+1+1+1+1+1+1+1 | PPPPPPPPP |
| 98 | 9 | 9 | 1+1+1+1+1+1+1+1+1 | PPPPPPPPP |
| 99 | 9 | 8 | 2+1+1+1+1+1+1+1 | PPPPPPPP |
| 100 | 9 | 9 | 1+1+1+1+1+1+1+1+1 | PPPPPPPPP |

## Summary

- Occupied cells: 8 in records 1-12; 9 in records 13-100.
- Components per shape: 5 to 9;
  every shape has more than one component.
- Largest component size: 4.
- Shapes whose components are all paths: 98 of 100.
- Shapes containing a cycle component: 0.
- Shapes containing a branching (N) component: 2
  (records 57 and 64; each has exactly one N component, a T-junction).

### Distinct component-size patterns

10 distinct patterns (component sizes as a multiset, largest first):

| Pattern | Count |
|---|---|
| 2+1+1+1+1+1+1+1 | 30 |
| 3+1+1+1+1+1+1 | 17 |
| 2+2+1+1+1+1+1 | 12 |
| 1+1+1+1+1+1+1+1 | 11 |
| 3+2+1+1+1+1 | 10 |
| 4+1+1+1+1+1 | 9 |
| 1+1+1+1+1+1+1+1+1 | 7 |
| 4+2+1+1+1 | 2 |
| 2+2+1+1+1+1 | 1 |
| 3+2+2+1+1 | 1 |

### Most common patterns

The six most frequent patterns cover 89 of 100 shapes:

- 2+1+1+1+1+1+1+1: 30
- 3+1+1+1+1+1+1: 17
- 2+2+1+1+1+1+1: 12
- 1+1+1+1+1+1+1+1: 11
- 3+2+1+1+1+1: 10
- 4+1+1+1+1+1: 9

### Structural families

- All 100 shapes are forests of small components: every component is a
  path of size 1-4, except for two shapes (records 57, 64) that each
  contain one branching component of size 4.
- No shape contains a cycle.
- The shapes fall into a small number of structural families: 98 of 100
  are pure path-forests, and the 10 size patterns are dominated by
  six patterns (89 of 100 shapes).
