# V Piece Catalogue Record

## Summary

Catalogue record for the V-pentomino (5/6). The catalogue contains 29 prime boxes and extensive published impossibility families. The Shirakawa source declares "3D Complete."

## Catalogue Overview

The V-pentomino catalogue (`catalogues/v_catalogue.py`) tracks tiling and packing data for the V piece in 3D boxes.

## Authoritative Published Sources

- **Primary Source**: Shirakawa's Box Packing Collection (V)
- **URL**: `https://puzzlewillbeplayed.com/Shirakawa/V.html`
- **Credits**: Sillke (1993), Shirakawa (2014-2015).
- **Status**: "3D Complete. 4D Complete except for 4x5x5x5 and 5x5x5x5."

## Catalogue Contents

### RAW_PRIMES (29 entries)

Organised by box family:

- **3x5**: 3x5x6, 3x5x8
- **4x5**: 4x5x6, 4x5x7, 4x5x8, 4x5x9, 4x5x10, 4x5x11
- **5x5**: 5x5x6, 5x5x9, 5x5x10, 5x5x11, 5x5x13, 5x5x14
- **5x7**: 5x7x7, 5x7x9
- **3x10**: 3x10x9, 3x10x10, 3x10x11, 3x10x13
- **3x15**: 3x15x9, 3x15x11, 3x15x13
- **3x20**: 3x20x7
- **3x25**: 3x25x7
- **3x30**: 3x30x7
- **3x35**: 3x35x7

Note: Several entries are commented out in the source with notes like "have 4,5,6" indicating they are canonical duplicates of existing entries.

### SEARCHED_NO_SOLUTION

Empty.

### ROW_FAMILIES / WIDTH_SPLITS

Empty (commented-out family definitions exist in the source but are not active).

### Published Solutions

None.

## Impossibility Rules

Published impossible families:

- `a <= 1`: impossible
- `a == b == c` (cube): impossible
- `a == 2, b == c` (`2xNxN`): impossible (NxN is impossible)
- `(a, b) == (3, 3)` (`3x3xN`): impossible (dies out after 7 steps)
- `(a, b) == (3, 4)` (`3x4xN`): impossible (dies out after 15 steps)
- `(a, b) == (3, 5), c` odd (`3x5xu` odd): impossible

Published individual impossible boxes:

- `3x5x4`, `3x5x10`
- `4x4x5`, `4x5x5`
- `5x5x5`, `5x5x7`, `5x5x8`
- `3x7x10`, `3x7x15`

## Shirakawa Transcription Notes

`shirakawa/V.md` confirms:
- "3D Complete. 4D Complete except for 4x5x5x5 and 5x5x5x5."
- 3D minimal prime is 3x5x6 (3 solutions)
- Many 3D boxes explicitly listed as impossible (3x4x5, 3x5x10, 3x7x10, 4x4x5, 4x5x5, 5x5x5)
- Correction: Sillke says 5x5x12 is prime, but it is not; 3x3x3x15 is impossible, but it is possible

## Remaining Open Questions

- A formal validation and audit run has not been performed on this catalogue.
- The 3D 2-sided and 4D/5D data in the Shirakawa transcription are not reflected in the catalogue (out of scope per project convention for 2-sided; 4D/5D not yet catalogued).

## Audit History

- **2026-08-10**: Added `MINIMAL_ODD` and `MINIMAL_EVEN` metadata identifying the smallest RAW_PRIME in each parity class, or `None` where no such RAW_PRIME exists. Metadata only; `RAW_PRIMES` and mathematical rules unchanged.
