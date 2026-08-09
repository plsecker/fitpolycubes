# Z Piece Catalogue Record

## Summary

Catalogue record for the Z-pentomino (5/11). The catalogue contains 55 prime boxes and extensive published impossibility families covering small widths. The Shirakawa source is very long and documents the 3D classification systematically.

## Catalogue Overview

The Z-pentomino catalogue (`catalogues/z_catalogue.py`) tracks tiling and packing data for the Z piece in 3D boxes.

## Authoritative Published Sources

- **Primary Source**: Shirakawa's Box Packing Collection (Z)
- **URL**: `https://puzzlewillbeplayed.com/Shirakawa/Z.html`
- **Credits**: Shirakawa (2013-2015), Shindo (1997).
- **Status**: No explicit "Complete" statement is given.

## Catalogue Contents

### RAW_PRIMES (55 entries)

Organised by box family:

- **4x10**: 4x10x50, 4x10x55, 4x10x60, 4x10x65, 4x10x70, 4x10x75, 4x10x80, 4x10x85, 4x10x90, 4x10x95
- **4x11**: 4x11x50
- **4x14**: 4x14x25
- **4x16-22**: 4x16x25, 4x17x25, 4x18x25, 4x19x25, 4x20x20, 4x20x25, 4x21x25, 4x22x25
- **5x8**: 5x8x20, 5x8x35, 5x8x45, 5x8x50
- **5x9**: 5x9x15, 5x9x25, 5x9x35
- **5x10**: 5x10x33, 5x10x36, 5x10x37
- **5x12+**: 5x12x20, 5x12x25, 5x13x25, 5x14x20, 5x14x25, 5x15x17, 5x15x19, 5x16x25, 5x17x20
- **6x***: 6x6x25, 6x7x25, 6x8x25, 6x9x25, 6x10x10 (prime minimal), 6x10x15, 6x11x25, 6x15x15
- **7x***: 7x8x25, 7x9x25, 7x10x10, 7x10x15, 7x11x25
- **8x***: 8x8x25, 8x9x25, 8x10x10, 8x10x15, 8x15x15
- **9x***: 9x10x10
- **10x***: 10x10x10, 10x10x11

### SEARCHED_NO_SOLUTION

Empty.

### ROW_FAMILIES / WIDTH_SPLITS

Empty.

### Published Solutions

None.

## Impossibility Rules

Published impossible families:

- `a <= 2`: impossible
- `a == 3, 3 <= b <= 22` (`3x[3-22]xN`): impossible
- `a == 4, 4 <= b <= 9` (`4x[4-9]xN`): impossible
- `(a, b) == (4, 10), 10 <= c <= 45` (`4x10x[10-45]`): impossible
- `a == 5, b in {5, 6, 7}` (`5x{5,6,7}xN`): impossible
- `a == 7, b == 7` (`7x7xN`): impossible

Published individual impossible boxes:

- `4x10x{10,15,20,25,30,35,40,45}`
- `4x11x25`
- `5x8x{10,15,25,30}`
- `5x9x{10,20}`

## Shirakawa Transcription Notes

`shirakawa/Z.md` confirms:
- No explicit "Complete" statement
- 3D section systematically documents impossibility for small widths
- First solutions at 3x23x150 (after 3x[3-22]xN all impossible)
- 3D minimal prime is 6x10x10 (11+ solutions, Shindo 1997)
- 5x10xN family documented with extraordinary granularity (individual lengths 33-71)
- 4D data extensive (Shirakawa 2013-2014), minimal prime 3x4x5x5
- 5D: single entry 3x3x3x5x5 (Shirakawa 2014)

## Remaining Open Questions

- A formal validation and audit run has not been performed on this catalogue.
- The 3D 2-sided and 4D/5D data in the Shirakawa transcription are not reflected in the catalogue (out of scope per project convention for 2-sided; 4D/5D not yet catalogued).
- The 5x10xN family is documented with extraordinary granularity in the Shirakawa source (individual lengths 33-71) but the catalogue only contains 3 entries (5x10x33, 5x10x36, 5x10x37). The discrepancy may indicate the catalogue is incomplete for this family, or the Shirakawa data may include non-prime entries.

## Audit History

- **2026-08-10**: Added `MINIMAL_ODD` and `MINIMAL_EVEN` metadata identifying the smallest RAW_PRIME in each parity class, or `None` where no such RAW_PRIME exists. Metadata only; `RAW_PRIMES` and mathematical rules unchanged.
