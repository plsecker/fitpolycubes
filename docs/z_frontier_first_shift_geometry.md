# Z-Frontier: Geometry of the First Four Layer-Shift States

Source: the first four layer-shift records in
`docs/z_frontier_state_stats_1m.md` (lines 140-143), byte-identical to
the 100k run. Their processed indices are 27,259 / 27,386 / 27,488 /
28,454 (see `docs/z_frontier_shift_states.md`).

## Decoding convention

From `solvers/s_z_frontier_packed.py`:

- Bits 0-31 = layer 0, 32-63 = layer 1, 64-95 = layer 2, 96-127 = layer 3.
- Within a layer, bit = x + 4y: x = column 0-3 (left to right),
  y = row 0-7 (top to bottom).
- A layer shift fires when layer 0 equals `WORD_MASK` (0xFFFFFFFF,
  all 32 cells occupied); the recorded state is the pre-shift state.
- Grids below use `F` = occupied, `-` = empty.

## The four states

| # | Packed state (decimal) | Packed state (hex) | Layer 0 | Layer 1 | Layer 2 | Layer 3 |
|---|---|---|---|---|---|---|
| 1 | 4774536927590219775 | 0x42429009FFFFFFFF | 0xFFFFFFFF | 0x42429009 | 0x00000000 | 0x00000000 |
| 2 | 10378985188876091391 | 0x90099009FFFFFFFF | 0xFFFFFFFF | 0x90099009 | 0x00000000 | 0x00000000 |
| 3 | 405482339087417343 | 0x05A09009FFFFFFFF | 0xFFFFFFFF | 0x05A09009 | 0x00000000 | 0x00000000 |
| 4 | 10396579573943762943 | 0x90481209FFFFFFFF | 0xFFFFFFFF | 0x90481209 | 0x00000000 | 0x00000000 |

## Layer 0 (identical in all four states)

All 32 cells occupied — this is the shift trigger.

```
FFFF
FFFF
FFFF
FFFF
FFFF
FFFF
FFFF
FFFF
```

## Layer 1 (per state)

State 1 — 0x42429009 (8 cells):

```
F--F
----
----
F--F
-F--
--F-
-F--
--F-
```

State 2 — 0x90099009 (8 cells):

```
F--F
----
----
F--F
F--F
----
----
F--F
```

State 3 — 0x05A09009 (8 cells):

```
F--F
----
----
F--F
----
-F-F
F-F-
----
```

State 4 — 0x90481209 (8 cells):

```
F--F
----
-F--
F---
---F
--F-
----
F--F
```

## Layers 2 and 3 (identical in all four states)

Empty:

```
----
----
----
----
----
----
----
----
```

## Visible common structure and differences

Common to all four states:

- Layer 0 is fully occupied (32/32 cells); layers 2 and 3 are empty.
- Layer 1 is sparse (8 cells each) and contains the same corner pair in
  row 0 — cells (0,0) and (3,0) — and the same corner pair in row 3 —
  cells (0,3) and (3,3). The top half of layer 1 (rows 0-3) is
  therefore identical across all four states.
- In the low 16 bits of layer 1, all four states share the pattern
  `0x9009` (states 1-3) or `0x1209` (state 4), i.e. bits 0, 3, 12, 15
  plus one extra bit (17, 16, 21, 9 respectively).

Differences (all in the lower half of layer 1, rows 4-7, plus one
extra cell in rows 2-4):

- State 1: a diagonal chain in rows 4-7 — (1,4), (2,5), (1,6), (2,7).
- State 2: full corner pairs in rows 4 and 7 — (0,4), (3,4), (0,7), (3,7).
- State 3: a 2x2 block in rows 5-6 — (1,5), (3,5), (0,6), (2,6).
- State 4: scattered cells — (1,2), (3,4), (2,5), (0,7), (3,7).

No further structure is asserted beyond what is visible in these four
states.