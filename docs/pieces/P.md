# P Piece Catalogue Record

## Summary

Catalogue record for the P-pentomino (5/4). The catalogue contains 3 prime boxes and minimal impossibility rules. No audit has been performed against the Shirakawa source.

## Catalogue Overview

The P-pentomino catalogue (`catalogues/p_catalogue.py`) tracks tiling and packing data for the P piece in 3D boxes.

## Authoritative Published Sources

- **Primary Source**: Shirakawa's Box Packing Collection (P)
- **URL**: `https://puzzlewillbeplayed.com/Shirakawa/P.html`
- **Credits**: Sillke, Klarner (1969).
- **Status**: The page is brief, listing only a few configurations.

## Catalogue Contents

### RAW_PRIMES (3 entries)

- `Box(1, 2, 5)` — 2D minimal prime
- `Box(1, 7, 15)` — 2D prime (7x15, 33,631 solutions, credited to Klarner 1969)
- `Box(3, 3, 5)` — discovered by solver

### SEARCHED_NO_SOLUTION

Empty.

### ROW_FAMILIES / WIDTH_SPLITS

Empty.

### Published Solutions

None.

## Impossibility Rules

- `a == 1, b == 3` (`1×3×N`): `3xZ_impossible`
- `a == 1, b == 5, c` odd (`1×5×odd`): `1x5xu_odd_impossible`
- Volume not a multiple of 5: `volume_not_multiple_of_5`

## Shirakawa Transcription Notes

`shirakawa/P.md` is sparse. It lists only:
- 2D 1-sided and 2D minimal prime 2x5
- 2D free: 7x15 (33,631 solutions, prime, Klarner 1969)
- 3D: 3x3x5 (153 solutions, prime, Sillke)
- No 4D data

## Remaining Open Questions

- The Shirakawa P page is very brief. The catalogue's 3 primes align with the transcription, but a full audit has not been run.
- The solver-discovered prime `Box(3, 3, 5)` matches the Shirakawa-published 3D entry.

## Audit History

- **2026-08-10**: Added `MINIMAL_ODD` and `MINIMAL_EVEN` metadata identifying the smallest RAW_PRIME in each parity class, or `None` where no such RAW_PRIME exists. Metadata only; `RAW_PRIMES` and mathematical rules unchanged.
