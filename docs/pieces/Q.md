# Q Piece Catalogue Record

## Summary

Catalogue record for the Q-pentomino (Shirakawa **5-22**, kurnell 61). The catalogue contains 6 published one-sided prime boxes, no searched no-solution entries, and published impossibility rules. Audited against the live Shirakawa source and Sillke's qu5.61.

## Catalogue Overview

The Q-pentomino catalogue (`catalogues/q_catalogue.py`) tracks tiling and packing data for the Q piece in 3D boxes.

## Authoritative Published Sources

- **Primary Source**: Shirakawa's Box Packing Collection (5-22)
- **URL**: `https://puzzlewillbeplayed.com/Shirakawa/5-22.html`
- **Credits**: Sillke (1993), Shirakawa.
- **Status**: "Complete." (stated on the page).
- **Sillke**: `http://www.mathematik.uni-bielefeld.de/~sillke/PENTA/qu5.61` (complete)

> Note: Q is on page **5-22**, not 5-19. Page 5-19 belongs to piece B.

## Catalogue Contents

### RAW_PRIMES (6 entries)

All one-sided 3D primes, all Sillke 1993 / Shirakawa 5-22:

- `Box(2, 2, 5)` — prime minimal
- `Box(2, 3, 5)` — prime
- `Box(3, 7, 25)` — prime
- `Box(3, 9, 15)` — prime
- `Box(5, 5, 9)` — prime
- `Box(5, 7, 7)` — prime

Sillke also lists the one-sided 4D prime `3x3x3x5`, which is out of scope for this 3D catalogue.

### SEARCHED_NO_SOLUTION

Empty. All published impossibilities are encoded in `impossible_reason`.

### ROW_FAMILIES / WIDTH_SPLITS

Empty.

### Published Solutions

None.

## Impossibility Rules

All from Sillke qu5.61 (consistent with Shirakawa 5-22):

- `3x3xN` for all N — `published_impossible` (Sillke A: 3x3xZ strip, two sides open)
- `3x5xN` with N odd — `published_impossible` (Sillke B: 3x5xu, u odd)
- `5x5x5`, `5x5x7`, `3x7x15` — `published_impossible` (Sillke C)

## Shirakawa Transcription Notes

No lossless transcription exists for 5-22 in `shirakawa/`. The live page states "Complete." and lists exactly the six one-sided 3D primes above (all Sillke 1993), plus the 4D prime 3x3x3x5. It lists no impossible rows.

## Audit History

- **2026-08-06**: Re-audited from scratch. Removed 13 unsupported solver-discovered primes (including `3x3x10`, `3x3x15`, `3x5x6`, `4x5x6`, `5x7x9`, and the incorrect `2x5x5`), added the missing published primes `2x2x5`, `3x7x25`, `3x9x15`, `5x7x7`, and rebuilt `impossible_reason` to the published Sillke rules. The catalogue's smallest odd box is now `5x5x9`, matching Sicherman's published minimum.

## Remaining Open Questions

- None outstanding for the 3D catalogue. The 4D prime `3x3x3x5` is documented but not representable in this 3D catalogue.