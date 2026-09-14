# George B-9 / B-M Letter Mapping (2026-09-15 nomenclature fix)

**Status:** authoritative reference for the B/M lettering swap.
**Applies to:** `common/registry.py`, `catalogues/*_catalogue.py`, all tools, docs, and
historical results that mention piece letters B or M.

## The swap in one line

The repo's **internal** piece letters `B` and `M` are **swapped** relative to the external
Sicherman / Künzell / Shirakawa lettering:

| repo letter | shape (description) | parity | Sicherman | Künzell | Sillke | Shirakawa | catalogue module |
|---|---|---|---|---|---|---|---|
| **B** | "junction": 3-bar + side cube + top cube at the middle | 4 even + 1 odd | **M** | 51 | qu5.51 | 5-18 | `catalogues.m_catalogue` |
| **M** | "tip": 3-bar + cube on the middle + cube on top of that | 3 even + 2 odd | **B** | 82 | qu5.82 | 5-19 | `catalogues.b_catalogue` |

Equivalently under the corrected mapping, `PENTACUBES["B"]` is the tip piece and `PENTACUBES["M"]` is the junction piece.

## Why the swap exists

The catalogue files `catalogues/{letter}_catalogue.py` are named by **Sicherman's** letters
(`b_catalogue` = Sicherman B = the tip = Shirakawa 5-19; `m_catalogue` = Sicherman M = the
junction = Shirakawa 5-18). The repo's internal piece letters were assigned independently
and ended up inverted for this pair. The registry's `kurnell` / `shirakawa_*` fields for B
and M were swapped accordingly (fixed 2026-09-15); the coordinate arrays were always
correct and are unchanged.

## Evidence chain

1. **Geometry reconciliation** (`data/ck6_reuse/b_v15_george_geometry_reconciliation.json`):
   George's published "M 3" figure (his page letter M) is *the same 15-cell shape* as our
   B-V15-S1 target (`oh-0216334782e8` / `p24-0216334782e8`, bbox 3×5×5), and his own
   published colouring is a tiling by three copies of the piece the repo calls **B**.
   Repo-M has **0** covers of that target; repo-B has **2**.
2. **Piece-identity cross-check** (`data/ck6_reuse/b_v15_piece_identity_crosscheck.txt`):
   every B-V15-S1 placement is a proper rotation of repo B and of no other registry piece.
3. **Odd-box parity criterion** (`tools/verify_sicherman_odd_boxes.py`): the junction
   (4E+1O) tiles **no** odd box (Sicherman M: "impossible"); the tip (3E+2O) tiles odd
   boxes, smallest 5×7×7 (Sicherman B: (5,7,7)). The catalogue minima agree exactly:
   `b_catalogue.MINIMAL_ODD = Box(5,7,7)`, `m_catalogue.MINIMAL_ODD = None`.
4. **Shirakawa transcriptions** (`shirakawa/B.md` = 5-19 = tip = qu5.82; `shirakawa/M.md`
   = 5-18 = junction = qu5.51): the 5-19 page lists the tip's odd primes (5×7×7, 3×13×15,
   …); the 5-18 page lists the junction's even boxes (6×11×15, 7×8×20, …) and no odd box.

## Consequences for claims

* Our **B-V15-S1** (3 junction pieces) is **congruent to George's published "M 3" figure**
  — a known shape + known tiling, an independent confirmation of his result, **not** an
  improvement. The 14 **B-V25-\*** constructions (5 junction pieces) are *larger* than his
  3-piece M minimum; the page lists minima only, so they are "no match on page".
* **L-V25-S1** (5 L pieces vs his 11) remains the only genuine improvement over the
  published minimum.
* George's "B 9" oddity (the sharding-bug counterexample, `oh-109166b4c83a`) is a **tip**
  piece figure = repo **M**; the 12 covers are repo-M covers.

## Guardrails

* `tools/check_piece_registry.py` cross-checks the B/M catalogue linkage via the odd-box
  criterion (junction ↔ `m_catalogue` with `MINIMAL_ODD=None`; tip ↔ `b_catalogue` with
  `MINIMAL_ODD` set).
* `tools/verify_sicherman_odd_boxes.py` runs the same parity guard before comparing.
* `tools/frontier/sicherman_c5nodd_compare.py` now maps repo letters directly without any translation layer.
* `tools/frontier/test_bm_nomenclature.py` locks the whole mapping down as a regression
  test (parity, aliases, catalogue linkage, odd-box minima, B-9 covers, B-V15-S1
  congruence, George-row lookup).