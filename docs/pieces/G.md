# G Piece Record (no catalogue module)

## Summary

`G` is one of the three registered pieces (with `I` and `X`) that has **no catalogue module** (`catalogue_module=None` in `common/registry.py`). Its identified Shirakawa page is **5-28**:

- Authoritative source: `https://puzzlewillbeplayed.com/Shirakawa/5-28.html`
- The previous registry mapping (`shirakawa_url` → `5-32.html`, `shirakawa_piece=22`) was a **repository error**; it is recorded below for the audit trail.
- `G` remains documented but **not machine-catalogued**: no `catalogue_module`, no `RAW_PRIMES`, no impossibility rules, no solver classifications.

## Identification (common/registry.py)

- Letter: `G`
- Coordinates: `(0,0,0), (1,0,0), (1,1,0), (1,1,1), (2,1,1)`
- kurnell: `36` (unchanged; no independently established evidence requires a separate correction)
- `catalogue_module`: `None`
- `shirakawa_url`: `https://puzzlewillbeplayed.com/Shirakawa/5-28.html`
- `shirakawa_piece`: `28`

## Catalogue status

No catalogue module exists for `G` in this repository, so there are no `RAW_PRIMES`, impossibility rules, families, or solver-based classifications for it. None are asserted here. `G` stays `catalogue_module=None`.

## Chirality

Sicherman identifies **G / G′** as a chiral pair of pentacubes: this piece has a chiral counterpart, **G′**, in Sicherman's classification, and the two are mirror-image handed forms — one image cannot be repositioned to make the other. Source: George Sicherman, "Pentacube Nomenclature", https://sicherman.net/c5nomen/index.html (last revised 2024-01-19; pair table confirmed 2026-08-10). The Reconciliation table there lists exactly six mirror pairs, `EE′ SS′ JJ′ RR′ HH′ GG′`; `G′` is the primed (opposite-handedness) member of this pair and is not separately registered or documented in this repository. No other chiral pair is attributed to this piece. This relationship is recorded independently of the Shirakawa 5-28 identification below and does not alter it.

**Repository treatment of chirality.** `G` has no catalogue module (`catalogue_module=None`), so there is no catalogue or solver data for which handedness could matter; the general repository convention — 24 orientation-preserving rotations only (`RM`, `common/rotmatrix.py`), reflections not considered equivalent by the solver, and no explicit modelling of primed pieces — is documented in the `E`, `S`, `J`, `R`, and `H` piece records.

## Reference transcription: Shirakawa 5-28

Source: `shirakawa/5-28.md` (lossless transcription of `https://puzzlewillbeplayed.com/Shirakawa/5-28.html`; `shirakawa/G.md` now carries the same content under the correct header).

Substantiated facts from the 5-28 page:

- **3D**: all "XxYxZ" entries are 0 — the piece tiles **no 3D box** (credited to Postl 1998).
- **4D**: minimal prime is **2×3×4×5** (3 solutions, credited to Shirakawa 2014).
- **5D**: single entry **2×2×3×3×5** (credited to Shirakawa 2014).
- **\*D**: `2×…×2×N` is impossible in arbitrary dimensions (credited to Shirakawa 2014).
- Page last updated: Feb 18, 2015; author `k16@chiba.email.ne.jp`.

This is consistent with `G` having no machine catalogue: a piece with no 3D box cannot be classified by this repository's 3D tiling catalogues.

## History / audit note: the old 5-32 mapping was a repository error

As found on 2026-08-10, `common/registry.py` mapped `G` to `shirakawa_url=5-32.html` with `shirakawa_piece=22`. That mapping was incorrect on two counts:

1. **Wrong page**: `shirakawa_piece=22` is `Q`'s value; `G`'s page is 5-28, not 5-32.
2. **`shirakawa/G.md` was a mislabeled copy of the 5-22 (Q) transcription** (its body was the 5-22 table: 2x2x5 … 5x7x7, all Sillke 1993, which is `Q`'s data). It has been replaced by the correct 5-28 transcription.

The 5-32 page itself (4D only, four prime entries credited to Shirakawa 2015, "Complete.", Apr 13 2015) is unrelated to `G` and is documented in `shirakawa/5-32.md`.

Additional pre-existing note (unchanged, still open): Sillke's results page has no entry numbered 36 (the list jumps from 35 to 37), so no Sillke box list is associated with `kurnell=36`. This does not affect the corrected Shirakawa identification.

## Sources consulted

- Live Shirakawa pages fetched 2026-08-10: `index.html` (complete page list), `5-28.html`, `5-32.html`, `5-22.html` (to cross-check Q).
- Repository files read: `common/registry.py`, `shirakawa/5-28.md`, `shirakawa/5-32.md`, `shirakawa/G.md`, `catalogues/q_catalogue.py`, `docs/pieces/Q.md`.
- Sillke's results page (`http://www.mathematik.uni-bielefeld.de/~sillke/results.html`) fetched 2026-08-10. Individual `PENTA/qu5.N` pages (e.g. `qu5.36`) were not retrievable (404/403) at fetch time.

## Not asserted

No source classification of `G` (prime / impossible / not-boxable) is asserted, and no mathematical catalogue or solver data is claimed. `G` remains not machine-catalogued.
