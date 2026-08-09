# Y Piece Catalogue Record

## Summary

Catalogue record for the Y-pentomino (5/3). The catalogue contains a large number of prime boxes (including 2D families with thickness 1), 39 searched no-solution entries, and published impossibility rules. The Shirakawa source declares "2D Complete. 3D Complete. 4D Complete."

## Catalogue Overview

The Y-pentomino catalogue (`catalogues/y_catalogue.py`) tracks tiling and packing data for the Y piece in 2D, 3D, and 4D boxes.

## Authoritative Published Sources

- **Primary Source**: Shirakawa's Box Packing Collection (Y)
- **URL**: `https://puzzlewillbeplayed.com/Shirakawa/Y.html`
- **Credits**: Golomb (1966), Scherer (1979), Klarner (1970), Bitner (1974), Haselgrove (1974), Sillke (1992), Bouwkamp (1990).
- **Status**: "2D Complete. 3D Complete. 4D Complete."

## Catalogue Contents

### RAW_PRIMES

The catalogue contains two groups of primes:

**3D primes (21 entries):**

- `Box(2, 4, 10)`, `Box(2, 4, 15)`
- `Box(2, 5, 6)`, `Box(2, 5, 8)`, `Box(2, 5, 11)`, `Box(2, 5, 13)`, `Box(2, 5, 15)`
- `Box(2, 7, 10)`, `Box(2, 7, 15)`
- `Box(3, 4, 5)`, `Box(3, 5, 9)`, `Box(3, 5, 11)`, `Box(3, 6, 10)`, `Box(3, 6, 15)`, `Box(3, 7, 10)`, `Box(3, 7, 15)`
- `Box(4, 4, 5)`, `Box(4, 5, 5)`
- `Box(5, 5, 5)`, `Box(5, 5, 6)`, `Box(5, 5, 7)`, `Box(5, 7, 7)`

**2D primes (thickness 1, generated via set operations):**

- `10 x n` families: `Box(1,10,5)`, `Box(1,10,14)`, and arithmetic progressions for n ≡ 3 (mod 5) ≥ 23 and n ≡ 2 (mod 5) ≥ 27
- `15 x n` families: `Box(1,15,14)` through `Box(1,15,17)`, and arithmetic progressions for n ≡ 9,1,2,3 (mod 10)
- `20 x n` families: `Box(1,20,9)`, and arithmetic progressions for n ≡ 3,2 (mod 5)
- `25 x n` families: `Box(1,25,17)`, `Box(1,25,18)`, and n ≡ 2 (mod 10) ≥ 22
- `30 x n` families: `Box(1,30,9)`, and n ≡ 3 (mod 5) ≥ 13
- `35 x n` families: `Box(1,35,11)`, `Box(1,35,13)`, `Box(1,35,18)`

### SEARCHED_NO_SOLUTION (39 entries)

2D thickness-1 entries:

- `1x2x{5,10,15}`, `1x3x{5,10,15}`, `1x4x{5,10,15}`
- `1x5x{5,6,7,8,9,11,12,13,14,15}`
- `1x6x{10,15}`, `1x7x{10,15}`, `1x8x{10,15}`, `1x9x{10,15}`
- `1x10x{11,12,13}`, `1x11x15`, `1x12x15`, `1x13x15`

3D entries:

- `2x2x{5,10,15}`, `2x3x{5,10,15}`, `2x4x5`, `2x5x{5,7}`
- `3x3x{5,10,15}`, `3x5x{5,6,7}`

### ROW_FAMILIES / WIDTH_SPLITS

Empty (note: published infinite solution families are known but not yet reduced to finite prime-generator families).

### Published Solutions

None.

## Impossibility Rules

- `a <= 0`: impossible
- `a == 1, b <= 4` (`1xNxN` with N ≤ 4): impossible
- `(a, b, c) == (2, 5, 4)`: impossible
- `(a, b, c) == (2, 5, 9)`: impossible

## Shirakawa Transcription Notes

`shirakawa/Y.md` confirms:
- "2D Complete. 3D Complete. 4D Complete."
- Credits span Golomb (1966) through Bouwkamp (1990)
- 2D section includes largest solution counts (Y-90x12 exceeds 10^16 solutions)
- 3D data includes 5x5x5 (1,264 solutions)
- 4D data: 2x2x4x5 and 2x2x5x9 (Sillke 1992)

## Remaining Open Questions

- A formal validation and audit run has not been performed on this catalogue.
- The 2D prime families are generated programmatically via set operations; their correctness depends on the arithmetic progression logic being correct.
- Published infinite solution families exist but have not been reduced to finite prime-generator families (ROW_FAMILIES is empty).

## Audit History

- **2026-08-10**: Added `MINIMAL_ODD` and `MINIMAL_EVEN` metadata identifying the smallest RAW_PRIME in each parity class, or `None` where no such RAW_PRIME exists. Metadata only; `RAW_PRIMES` and mathematical rules unchanged.
