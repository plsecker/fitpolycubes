# R Piece Catalogue Record

## Summary

Catalogue record for the R-pentomino (5/26). The catalogue contains 52 prime boxes and extensive published impossibility families. No audit has been performed against the Shirakawa source.

## Catalogue Overview

The R-pentomino catalogue (`catalogues/r_catalogue.py`) tracks tiling and packing data for the R piece in 3D boxes.

## Authoritative Published Sources

- **Primary Source**: Shirakawa's Box Packing Collection (5-26)
- **URL**: `https://puzzlewillbeplayed.com/Shirakawa/5-26.html`
- **Credits**: Shirakawa (2014-2015), Postl (1998).
- **Status**: No explicit "Complete" statement is given.

## Catalogue Contents

### RAW_PRIMES (52 entries)

Organised by box family:

- **4x7**: 4x7x30, 4x7x35, 4x7x40, 4x7x45, 4x7x50, 4x7x55
- **4x8**: 4x8x10 (prime minimal), 4x8x15
- **4x9**: 4x9x20, 4x9x25
- **4x10**: 4x10x12, 4x10x13, 4x10x14, 4x10x15
- **4x11-13**: 4x11x15, 4x12x15, 4x13x15
- **5x6**: 5x6x12 through 5x6x23 (12 entries)
- **5x7**: 5x7x16
- **5x8**: 5x8x8 (Postl 1998, prime minimal), 5x8x11, 5x8x12, 5x8x13, 5x8x14, 5x8x15
- **5x10**: 5x10x10, 5x10x11, 5x10x12, 5x10x13, 5x10x14, 5x10x15
- **6x6**: 6x6x15, 6x6x20, 6x6x25
- **6x7**: 6x7x10, 6x7x15
- **6x8**: 6x8x10, 6x8x15
- **6x9**: 6x9x10, 6x9x15
- **6x10**: 6x10x10, 6x10x11
- **7x8**: 7x8x10, 7x8x15

### SEARCHED_NO_SOLUTION

Empty.

### ROW_FAMILIES / WIDTH_SPLITS

Empty.

### Published Solutions

None.

## Impossibility Rules

Published impossible families (Shirakawa):

- `a <= 1`: impossible
- `a == 2` (`2xMxN`): impossible
- `a == 3` (`3xMxN`): impossible
- `a == 4, 4 <= b <= 6` (`4x[4-6]xN`): impossible
- `a == 4, b == 7, c in {10, 15, 20, 25}` (`4x7x{10,15,20,25}`): impossible
- `a == 5, b == 5` (`5x5xN`): impossible
- `a == 5, b == 6, c <= 11` (`5x6x[6-11]`): impossible
- `a == 5, b == 7, c <= 14` (`5x7x[7-14]`): impossible
- `a == 6, b == 6, c == 10` (`6x6x10`): impossible

## Shirakawa Transcription Notes

`shirakawa/R.md` is a lossless transcription of the 5-26 page. It confirms:
- `2x[2-16]xN` impossible (Shirakawa 2014)
- `2x17xN` entries from 20 to 150 all impossible
- `2x[18-20]xN` impossible
- `3xMxN` impossible
- `4x[4-6]xN` impossible
- `4x7x{10,15,20,25}` impossible
- `5x5xN` impossible
- `5x6x[6-11]` impossible
- `5x7x[7-14]` impossible
- `6x6x10` impossible
- All prime boxes listed with solution counts and credits

## Remaining Open Questions

- A formal validation and audit run has not been performed on this catalogue.
- The 3D 2-sided section in the Shirakawa transcription contains additional data not reflected in the catalogue (2-sided variants are out of scope per project convention).

## Audit History

- **2026-08-10**: Added `MINIMAL_ODD` and `MINIMAL_EVEN` metadata identifying the smallest RAW_PRIME in each parity class, or `None` where no such RAW_PRIME exists. Metadata only; `RAW_PRIMES` and mathematical rules unchanged.
