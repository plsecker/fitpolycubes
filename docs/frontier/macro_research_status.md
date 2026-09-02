# Macro Research Status

**Date**: 2026-08-26
**Scope**: cross-piece status of the Macro proof programme (S, T, V, W).
This is the living top-level status page; per-piece history stays in
`docs/frontier/<piece>/`.

---

## Piece programmes

| Piece | Cross-sections with COMPLETE closures | Global theorems (family-wide) | Certificates | Notes |
|-------|----------------------------------------|-------------------------------|--------------|-------|
| S | 4×5, 5×6, 4×8 (+4×8×130/140 walk programs) | 4×8 parity/period-10 theorem; semigroup results | S 4×5×6 witness (v1) | historical base of the method |
| T | 3×7, 3×8*, 5×5, 5×5(cyclicity) | 3×7 GLOBAL (period 20); **3×8 period 5 proven 2026-08-26** (*closure re-run to completion) | 5 witnesses v1 + cyclicity certificates | flat-orientation gate theory |
| V | **3×5** (2026-08-26: 0.28 s, complete) | **3×5 family GLOBAL**: tileable ⟺ z ∈ {6,8} ∪ even ≥ 12 | 2 new v1 witnesses + claim verifier | mixed gate discovery; faithfulness replay on 144 exhaustive tilings |
| W | — (chiral-machinery demo only) | — | W 5×7×9 solution-01 walks (2 files, positive controls) | achirality correction recorded |

## Framework milestones

1. Generic piece infrastructure (`tools/frontier/piece_utils.py`,
   `macro_explorer.py`) — validated on three geometries.
2. Certificate format v1 + stdlib-only isolated Layer-A checker +
   negative-testing discipline (`docs/frontier/macro_certificate_format.md`).
3. Claim-level verifier introduced with the V port
   (`tools/frontier/v_piece/v_claim_verifier.py`): CATALOGUE ONLY <
   VERIFIED CYCLE < SCC-LOCAL < GLOBAL, mechanically enforced against evidence.
4. Exact-walk-length post-analysis (`tools/frontier/v_piece/v_exact_walk_lengths.py`)
   promoted to a standard post-closure step.
5. Complexity preflight: strategy selection transfers across pieces;
   state-count prediction does not (V benchmark). Generalization open.

## Key standing corrections (do not regress)

* Macro walks are NOT in bijection with raw tilings (144→80 on V 5×5×6);
  never report walk counts as tiling counts.
* Repo-root `placements_*.txt` files are placement catalogues, not witnesses.
* All planar pentacubes tested so far are achiral in 3D (W note,
  `macro_certificate_format.md` §8); chirality machinery still required for
  genuinely chiral pieces (e.g. S rejects mirrored placements by design).

## Current frontier / next actions

1. **V 5×5**: measure first-gen sources before committing; published odd prime
   9 predicts period 1 (contrast with 3×5's period 2).
2. **V 4×5**: six consecutive published primes (6–11) — richest semigroup test.
3. Preflight model generalization (flat fraction, template density, footprint class).
4. S full packed-tile witness remains future work (per certificate-format doc §8).

## Wall statement (permanent documentation)

Any "≈1M-state wall" figures quoted in older documents refer to the then-current
implementation/hardware/search-strategy combination, not to a mathematical
state-space boundary. Example: T 3×8 was "bounded at 200K states" until a
higher-limit run completed it at 916K states within minutes on 2026-08-26.

## Pointers

* Per-piece surveys/investigations: `docs/frontier/{s,t,v}_piece/`
* Methodology: `docs/frontier/macro_proof_methodology.md` (§18 = V addendum)
* Results data: `data/frontier/{s,t,v}_piece/`, certificates under
  `data/frontier/certificates/` and piece directories
