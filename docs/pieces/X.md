# X Piece Record (no catalogue module)

## Summary

`X` is the X-pentomino (5/12 in the standard pentomino enumeration; one central cell with four arms). It is registered in `common/registry.py` with `catalogue_module=None`. Sillke's list entry states the X-pentomino is **not boxable**, and Shirakawa's collection has **no page for it at all**. This record contains only substantiated facts; no classification is asserted.

## Identification (common/registry.py)

- Letter: `X`
- Coordinates: `(1,0,0), (0,1,0), (1,1,0), (1,2,0), (2,1,0)` (center cell `(1,1,0)` plus four arms)
- kurnell: `50`
- `catalogue_module`: `None`
- `shirakawa_url`: `https://puzzlewillbeplayed.com/Shirakawa/X.html` (dead — returned 404 on 2026-08-10)
- `shirakawa_piece`: `12`

## Catalogue status

No catalogue module exists for `X` in this repository, so there are no `RAW_PRIMES`, impossibility rules, families, or solver-based classifications for it. None are asserted here.

## Published sources

- **Shirakawa: no page.** The collection index (`https://puzzlewillbeplayed.com/Shirakawa/index.html`, fetched 2026-08-10) lists pentomino pages starting at 5/2 (L) and numbered pages 5/13 onward; there is no 5/12 page. Direct fetches of `X.html` and `5-12.html` returned 404. The absence is consistent with Sillke's "not boxable" assessment (nothing to report).
- **Sillke (results page, linked from every Shirakawa page):** "50 - X-Pentomino (not boxable)" — the X-pentomino tiles no box. (The registry's kurnell number 50 matches this Sillke list entry.)
- Elementary observation (for context only, not a source claim): every placement of the X covers one cell of one checkerboard color and four of the other, so any region it tiles must have a color imbalance divisible by 3 — which no box has. This is the standard explanation for the "not boxable" status.

## Repository artifacts

- No transcription exists (`shirakawa/X.md` absent).
- No solver scratch files for `X` are present in the working tree.

## Sources consulted

- Live Shirakawa pages fetched 2026-08-10: `index.html` (complete page list); direct fetches of `X.html` and `5-12.html` returned 404.
- Sillke's results page (`http://www.mathematik.uni-bielefeld.de/~sillke/results.html`) fetched 2026-08-10. Individual `PENTA/qu5.N` pages (e.g. `qu5.50`) were not retrievable (404/403) at fetch time.
- Repository files read: `common/registry.py`.

## Not asserted

No prime / impossible / solution-count classification is asserted for `X`. The only claim about its box-packing status is Sillke's: not boxable.
