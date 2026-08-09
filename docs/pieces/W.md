# W Piece Catalogue Record

## Summary

Catalogue record for the W-pentomino (5/10). The catalogue contains a large number of prime boxes across many families, 20 searched no-solution entries, and extensive published impossibility families. The Shirakawa source declares "3D Complete."

## Catalogue Overview

The W-pentomino catalogue (`catalogues/w_catalogue.py`) tracks tiling and packing data for the W piece in 3D boxes.

## Authoritative Published Sources

- **Primary Source**: Shirakawa's Box Packing Collection (W)
- **URL**: `https://puzzlewillbeplayed.com/Shirakawa/W.html`
- **Credits**: Sillke (1994), Postl (1998), Shirakawa (2014-2015).
- **Status**: "3D Complete."

## Catalogue Contents

### RAW_PRIMES (113 entries)

Organised by box family:

- **3x7**: 3x7x20, 3x7x25, 3x7x30, 3x7x35
- **3x8**: 3x8x15, 3x8x20, 3x8x25
- **3x9**: 3x9x15, 3x9x20, 3x9x25
- **3x10**: 3x10x11 through 3x10x21 (11 entries)
- **3x11-15**: 3x11x15, 3x12x15, 3x13x15, 3x14x15, 3x15x15
- **4x5**: 4x5x19, 4x5x24, 4x5x26, 4x5x28-37, 4x5x39-42, 4x5x44, 4x5x46 (19 entries)
- **4x6**: 4x6x10, 4x6x15
- **4x7**: 4x7x15, 4x7x20, 4x7x25
- **4x8**: 4x8x10, 4x8x15
- **4x9**: 4x9x10, 4x9x15
- **4x10**: 4x10x10, 4x10x11, 4x10x13, 4x10x15
- **4x11**: 4x11x15
- **5x5**: 5x5x14, 5x5x16, 5x5x18-27, 5x5x29, 5x5x31 (14 entries)
- **5x6**: 5x6x6 through 5x6x11 (6 entries)
- **5x7**: 5x7x9, 5x7x10, 5x7x11, 5x7x13, 5x7x14
- **5x8**: 5x8x8, 5x8x9, 5x8x10, 5x8x11, 5x8x13
- **5x9**: 5x9x9, 5x9x10, 5x9x11
- **5x10**: 5x10x10, 5x10x11
- **5x11**: 5x11x11
- **7x7**: 7x7x10, 7x7x15
- **7x8**: 7x8x10

### SEARCHED_NO_SOLUTION (20 entries)

Explicitly listed impossible by Sillke:

- `3x7x5`, `3x7x10`, `3x7x15`
- `4x7x10`
- `3x8x10`, `3x9x10`, `3x10x10`
- `5x5x5` through `5x5x13`, `5x5x15` (11 entries)
- `5x7x7`, `5x7x8`

### ROW_FAMILIES / WIDTH_SPLITS

Empty.

### Published Solutions

None.

## Impossibility Rules

Published impossible families:

- `a <= 1`: impossible
- Volume not a multiple of 5: impossible
- `b == 2` or `a == 2`: impossible
- `a == 3, b in {3, 4, 5, 6}` (`3xNx{3,4,5,6}`): impossible
- `a == 4, b == 4` (`4x4xN`): impossible
- `a == 4, c in {3, 4}` (`4xNx{3,4}`): impossible
- `(a, b) == (3, 3)` (`3x3xZ`): impossible
- `(a, b) == (3, 7), c in {5, 10, 15}`: impossible
- `(a, b) == (4, 5), 1 <= c <= 18`: impossible
- `(a, b) == (4, 5), c in {20, 21, 22, 23, 25, 27}`: impossible

Published individual impossible boxes:

- `3x7x5`, `3x7x10`, `3x7x15`, `4x7x10`

## Shirakawa Transcription Notes

`shirakawa/W.md` confirms:
- "3D Complete."
- 3D minimal prime is 5x6x6 (2 solutions, Sillke 1994)
- Many 3D boxes explicitly listed as impossible (3x[3-6]xN, 3x7x10, 3x7x15, 4x[4-9]xN)
- 4x5xN family documented with individual lengths from 19 to 46
- 4D data credited to Shirakawa (2015)

## Remaining Open Questions

- A formal validation and audit run has not been performed on this catalogue.
- The 3D 2-sided data in the Shirakawa transcription is not reflected in the catalogue (out of scope per project convention).

## Audit History

- **2026-08-10**: Added `MINIMAL_ODD` and `MINIMAL_EVEN` metadata identifying the smallest RAW_PRIME in each parity class, or `None` where no such RAW_PRIME exists. Metadata only; `RAW_PRIMES` and mathematical rules unchanged.
