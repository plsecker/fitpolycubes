# I Piece Record (no catalogue module)

## Summary

`I` is the straight 1x5 bar (I-pentomino, 5/1 in the standard pentomino enumeration). It is registered in `common/registry.py` with `catalogue_module=None`. Neither canonical source reports any non-trivial prime box for it: Sillke's list entry is "only the pentacube itself", and Shirakawa's collection has **no page for it at all**. This record contains only substantiated facts; no classification is asserted.

## Identification (common/registry.py)

- Letter: `I`
- Coordinates: `(0,0,0), (1,0,0), (2,0,0), (3,0,0), (4,0,0)` (straight bar)
- kurnell: `10`
- `catalogue_module`: `None`
- `shirakawa_url`: `https://puzzlewillbeplayed.com/Shirakawa/I.html` (dead — returned 404 on 2026-08-10)
- `shirakawa_piece`: `1`

## Catalogue status

No catalogue module exists for `I` in this repository, so there are no `RAW_PRIMES`, impossibility rules, families, or solver-based classifications for it. None are asserted here.

## Published sources

- **Shirakawa: no page.** The collection index (`https://puzzlewillbeplayed.com/Shirakawa/index.html`, fetched 2026-08-10) lists pentomino pages starting at 5/2 (L): L, Y, P, U, V, T, N, F, W, Z, then numbered pages 5/13 onward. There is no 5/1 page. Direct fetches of `I.html`, `X.html`, and `5-1.html` all returned 404. The absence is consistent with Sillke's assessment that the I-pentomino has no non-trivial prime boxes (nothing to report).
- **Sillke (results page, linked from every Shirakawa page):** "10 - I-Pentomino (only the pentacube itself)" — i.e. the only prime box is the trivial 1x1x5 pentacube; there are no non-trivial prime boxes. (The registry's kurnell number 10 matches this Sillke list entry.)

## Repository artifacts

- No transcription exists (`shirakawa/I.md` absent).
- An untracked solver scratch file `data/reduce_solutions_hybrid_i_1x5x5_1x5x5.txt` (referencing untracked source `data/solutions_hybrid_i_1x5x5.dat`) is present in the working tree from solver experiments. It is experimental scratch, not validated catalogue data, and no classification is asserted from it here.

## Sources consulted

- Live Shirakawa pages fetched 2026-08-10: `index.html` (complete page list); direct fetches of `I.html` and `5-1.html` returned 404.
- Sillke's results page (`http://www.mathematik.uni-bielefeld.de/~sillke/results.html`) fetched 2026-08-10. Individual `PENTA/qu5.N` pages (e.g. `qu5.10`) were not retrievable (404/403) at fetch time.
- Repository files read: `common/registry.py`.

## Not asserted

No prime / impossible / solution-count classification is asserted for `I`. The only claim about its box-packing status is Sillke's: the pentacube itself is the only prime box.
