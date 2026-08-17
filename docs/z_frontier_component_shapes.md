# Z-Frontier: Distinct Connected-Component Shapes

Source: the 4-neighbor connected components of the 100 layer-1
frontier shapes (states from `docs/z_frontier_state_stats_1m.md`,
lines 140-239; per-shape structure in
`docs/z_frontier_shape_structure.md`).

## Canonicalization

- Components are canonicalized by translation only: each component
  is shifted so its minimum x and minimum y are 0.
- No rotation, no reflection.
- Two components are the same shape iff one is a translation of the
  other within the 4x8 grid.

## Result

- Total components across the 100 shapes: 729.
- Distinct component shapes: 17.

## Frequency of each shape (in order of first appearance)

| # | Size | Count | Shape |
|---|---|---|---|
| 1 | 1 | 620 | first seen record 1, component 1<br>`#` |
| 2 | 2 | 43 | first seen record 2, component 2<br>`#<br>#` |
| 3 | 2 | 27 | first seen record 15, component 6<br>`##` |
| 4 | 3 | 5 | first seen record 17, component 5<br>`###` |
| 5 | 4 | 3 | first seen record 19, component 1<br>`#.<br>#.<br>##` |
| 6 | 3 | 7 | first seen record 20, component 1<br>`#<br>#<br>#` |
| 7 | 3 | 6 | first seen record 24, component 4<br>`##<br>.#` |
| 8 | 3 | 6 | first seen record 28, component 2<br>`.#<br>##` |
| 9 | 3 | 3 | first seen record 29, component 2<br>`#.<br>##` |
| 10 | 4 | 1 | first seen record 39, component 1<br>`.#<br>##<br>#.` |
| 11 | 4 | 1 | first seen record 43, component 2<br>`..#<br>###` |
| 12 | 4 | 1 | first seen record 45, component 1<br>`#<br>#<br>#<br>#` |
| 13 | 4 | 1 | first seen record 57, component 1<br>`.#.<br>###` |
| 14 | 3 | 1 | first seen record 60, component 2<br>`##<br>#.` |
| 15 | 4 | 2 | first seen record 62, component 2<br>`###<br>#..` |
| 16 | 4 | 1 | first seen record 64, component 3<br>`###<br>.#.` |
| 17 | 4 | 1 | first seen record 67, component 4<br>`##<br>.#<br>.#` |

## Largest component shapes

Largest component size: 4 cells.

Distinct shapes of size 4: 8.

Shape 1 (count 3, first seen record 19, component 1):

```
#.
#.
##
```

Shape 2 (count 1, first seen record 39, component 1):

```
.#
##
#.
```

Shape 3 (count 1, first seen record 43, component 2):

```
..#
###
```

Shape 4 (count 1, first seen record 45, component 1):

```
#
#
#
#
```

Shape 5 (count 1, first seen record 57, component 1):

```
.#.
###
```

Shape 6 (count 2, first seen record 62, component 2):

```
###
#..
```

Shape 7 (count 1, first seen record 64, component 3):

```
###
.#.
```

Shape 8 (count 1, first seen record 67, component 4):

```
##
.#
.#
```

