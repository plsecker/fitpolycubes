# Z-Frontier: Layer-1 Shapes of the 100 Layer-Shift States

Source: the 100 layer-shift records in
`docs/z_frontier_state_stats_1m.md` (lines 140-239).

## Decoding convention

From `docs/z_frontier_first_shift_geometry.md` (per
`solvers/s_z_frontier_packed.py`):

- Layer 1 = bits 32-63 of the packed state.
- Within a layer, bit = x + 4y: x = column 0-3 (left to right),
  y = row 0-7 (top to bottom).
- Grids below use `#` = occupied, `.` = empty.

## Result

- **Distinct layer-1 shapes: 100** (out of 100 states).
- **Frequency of each shape: 1** — no two shift states share the same
  layer-1 shape. Every shape occurs exactly once.

## First 10 shapes (in record order)

Record 1:

```
#..#
....
....
#..#
.#..
..#.
.#..
..#.
```

Record 2:

```
#..#
....
....
#..#
#..#
....
....
#..#
```

Record 3:

```
#..#
....
....
#..#
....
.#.#
#.#.
....
```

Record 4:

```
#..#
....
.#..
#...
...#
..#.
....
#..#
```

Record 5:

```
.#..
..#.
.#..
..#.
.#..
..#.
.#..
..#.
```

Record 6:

```
.#..
..#.
.#..
..#.
#..#
....
....
#..#
```

Record 7:

```
.#..
..#.
.#..
..#.
....
.#.#
#.#.
....
```

Record 8:

```
.#..
..#.
#..#
....
....
#..#
.#..
..#.
```

Record 9:

```
.#..
..#.
....
.#.#
#.#.
....
.#..
..#.
```

Record 10:

```
....
.#.#
#.#.
....
.#..
..#.
.#..
..#.
```

## Observed shape features (visible only)

- All 100 shapes are distinct; each occurs exactly once.
- Cell count: 8 cells in records 1-12; 9 cells in records 13-100.
- Row 0: the corner pair `#..#` (cells (0,0) and (3,0)) appears in
  records 1-4 and 13-100; records 5-9 have a single cell (1,0);
  records 10-12 have an empty row 0.
- Row 3: the corner pair `#..#` (cells (0,3) and (3,3)) appears in
  records 1-3, 23-58, 74-78, 84-88 and 96-98; other records vary
  (e.g. `#...` in records 4 and 67-73, `##.#` in 59-61, `###.` in
  62-64, `#.##` in 79-83, `#.#.` in 89-95).
- No further structure is asserted beyond what is visible in the
  decoded grids.