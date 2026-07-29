# Q Piece Catalogue Record

## Summary

Catalogue record for the Q-pentomino (5/19, same Shirakawa page as B). The catalogue contains 20 prime boxes, 1 searched no-solution entry, and published impossibility rules. No audit has been performed against the Shirakawa source.

## Catalogue Overview

The Q-pentomino catalogue (`catalogues/q_catalogue.py`) tracks tiling and packing data for the Q piece in 3D boxes.

## Authoritative Published Sources

- **Primary Source**: Shirakawa's Box Packing Collection (5-19)
- **URL**: `https://puzzlewillbeplayed.com/Shirakawa/5-19.html`
- **Credits**: Sillke, Postl, Reid, van de Konijnenberg, Shirakawa.
- **Status**: "Complete." (stated on the page).

## Catalogue Contents

### RAW_PRIMES (20 entries)

- `Box(2, 5, 5)` — published minimal prime (Shirakawa/Reid)
- `Box(2, 3, 5)` — discovered by solver
- `Box(2, 2, 15)` — discovered prime (required for decomposition completeness)
- `Box(3, 3, 10)`, `Box(3, 3, 15)`
- `Box(3, 4, 10)`, `Box(3, 4, 15)`
- `Box(3, 5, 6)`, `Box(3, 5, 14)`, `Box(3, 5, 15)`, `Box(3, 5, 16)`, `Box(3, 5, 17)`, `Box(3, 5, 19)`
- `Box(4, 4, 15)`
- `Box(4, 5, 6)`, `Box(4, 5, 9)`
- `Box(5, 5, 6)`, `Box(5, 5, 9)`
- `Box(5, 7, 9)`

### SEARCHED_NO_SOLUTION (1 entry)

- `Box(3, 3, 5)` — confirmed impossible

### ROW_FAMILIES / WIDTH_SPLITS

Empty.

### Published Solutions

None.

## Impossibility Rules

- `a <= 1`: `published_impossible`
- Individual impossible boxes (canonical forms):
  - `3x3x5`, `3x4x5`, `3x5x5`, `3x5x7`, `3x5x8`, `3x5x9`, `3x5x10`, `3x5x11`, `3x5x13`

## Shirakawa Transcription Notes

`shirakawa/5-19.md` (shared with piece B) states:
- "Complete." at the top
- 3D minimal prime is 2x5x5 (1 solution, Reid)
- Many 3D box families explicitly listed as impossible
- 4D data includes six entries (Shirakawa 2015)
- *D section: 2x...x2x[3-4]xN and 2x...x2x6xN impossible in arbitrary dimensions
- Correction: Sillke overlooked 3x16x25, 3x17x25, and 5x9x9; 5x7x8 is composite

## Remaining Open Questions

- Q shares the Shirakawa 5-19 page with B. The catalogue contains data specific to Q that should be cross-referenced with B's catalogue to avoid duplication or inconsistency.
- A full audit comparing `q_catalogue.py` against the detailed 5-19 page data has not been performed.
