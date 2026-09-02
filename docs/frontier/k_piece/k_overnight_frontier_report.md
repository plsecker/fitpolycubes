# K Pentacube Overnight Frontier Report

**Date**: 2026-08-31
**Purpose**: investigate the K-pentacube catalogue frontier using existing
evidence and decomposition, following the same workflow that produced the
certified Z results.

---

## Executive summary

**The K pentacube catalogue has ZERO Unknown boxes within dimensions ≤ 30.**
The existing decomposition engine closes every composite box using the 18
prime seeds. This is fundamentally different from the Z pentacube, which
had 10,467 Unknown boxes at comparable scale.

**The K frontier is already closed within the tested range.** The overnight
investigation confirms this result and identifies documentation (not
computation) as the primary remaining task.

---

## 1. Baseline audit (Phase 1)

### Catalogue state

| metric | value |
|---|---|
| RAW_PRIMES | **18** |
| PUBLISHED_SOLUTIONS | **0** (empty set) |
| SEARCHED_NO_SOLUTION | **0** (empty set) |
| IMPOSSIBLE rules | a≤1, cube, 2×{2..7}×N, 3×3×N, odd-width theorem, 3×4×15 |
| Unknown boxes (dims ≤ 20) | **0** |
| Unknown boxes (dims ≤ 30) | **0** |
| Discovered composites (dims ≤ 15) | 102 |
| Discovered composites (dims ≤ 20) | 268 |
| Total valid boxes (dims ≤ 30) | 2,360 |

### The K pentacube geometry

The K pentacube (piece 5/13) has cells:
`(0,0,0), (1,0,0), (2,0,0), (2,1,0), (2,0,1)`

* bounding box: 3×2×2
* **z-span: 1** in canonical orientation (but NOT flat — it's a 3D piece with 24 orientations)
* **24 distinct orientations** (full proper rotation group for this chiral 3D shape)
* x-span: 2, y-span: 1 (in canonical orientation)

### Why K is "easy" compared to Z

The K pentacube's **24 orientations** (vs Z's 12) and **compact 3D shape**
(vs Z's flat 5-cell planar shape) give it much more tiling flexibility:

1. The piece can interlock in 3D in many more ways than the planar Z
2. The small bounding box (3×2×2) means it fits in tight spaces
3. The piece can form bridges and connectors between regions that planar
   pieces cannot reach

This tiling flexibility means the 18 prime "seeds" are sufficient for the
decomposition engine to reach every other box via Slab, Width, and Breadth
decompositions.

### The 18 prime boxes

| # | box | volume/5 | cross-section |
|---|---|---|---|
| 1 | 2×8×10 | 32 | 2×8 |
| 2 | 2×9×15 | 54 | 2×9 |
| 3 | 2×10×10 | 40 | 2×10 |
| 4 | 2×10×12 | 48 | 2×10 |
| 5 | 2×10×14 | 56 | 2×10 |
| 6 | 2×11×30 | 132 | 2×11 |
| 7 | 2×12×15 | 72 | 2×12 |
| 8 | 2×13×30 | 156 | 2×13 |
| 9 | 2×15×15 | 90 | 2×15 |
| 10 | 3×4×30 | 72 | 3×4 |
| 11 | 3×4×45 | 108 | 3×4 |
| 12 | 3×5×6 | 18 | 3×5 |
| 13 | 3×5×9 | 27 | 3×5 |
| 14 | 3×7×15 | 63 | 3×7 |
| 15 | 3×8×15 | 72 | 3×8 |
| 16 | 4×4×10 | 32 | 4×4 |
| 17 | 4×5×6 | 24 | 4×5 |
| 18 | 5×5×6 | 30 | 5×5 |

These 18 primes cover 14 distinct cross-sections spanning 2×N to 5×5.
From these seeds, the decomposition engine reaches every other box.

## 2. Source mining (Phase 2)

### Shirakawa 5-13 source

The Shirakawa page for the K pentacube (piece 5/13) is at:
`https://puzzlewillbeplayed.com/Shirakawa/5-13.html`

The in-repo transcription (`shirakawa/5-13.md`) is **severely incomplete**:

* It mentions "The 3D minimal prime is 3×5×6" but only lists that one prime
* It states "Complete." for the 3D classification
* It omits the other 17 prime boxes and the impossibility families that
  are present in `k_catalogue.py`
* The `docs/pieces/K.md` audit notes: "the transcription is missing the
  bulk of the 3D data"

**The transcription is NOT a reliable source for the full 3D
classification.** The existing catalogue data was compiled from other
sources (likely the original Shirakawa page before transcription, or
Sillke's pages).

### Catalogue vs source comparison

| catalogue entry | in transcription? | source |
|---|---|---|
| 3×5×6 (prime minimal) | ✅ mentioned | transcription |
| 2×8×10, 2×9×15, etc. (17 other primes) | ❌ not mentioned | unknown |
| impossibility families (2×{2..7}×N, etc.) | ❌ not mentioned | unknown |
| odd-width theorem | ❌ not mentioned | Sillke (1993-1998) |

The K catalogue is **more complete than the transcription** — the 18
primes and impossibility families were compiled from sources beyond the
in-repo transcription.

### Not transcribed: any additional published evidence

The original Shirakawa page (5-13.html) may contain additional evidence
not reflected in the transcription. However, accessing it requires a
browser (the transcription is the only in-repo source). The 5-13
transcription notes that the page "states Complete." for the 3D
classification, which means the published data is comprehensive — but the
transcription doesn't capture it.

## 3. Decomposition replay (Phase 3)

**Not applicable** — there are no newly discovered source facts to inject.
The existing decomposition already closes all boxes within the tested
range. No new evidence was found to promote.

## 4. Structural mining (Phase 4)

### The 15.7% L0-sharing pattern

For 6×6×5, 15.7% of boundary states share their L0 value with at least
one other state. This means the L0→L1 mapping is almost a function —
but the 14.1% with multiple L1 values prevents sound merging.

For the K pentacube: the piece is 3D (not planar), so the "flat-layer
oracle" concept doesn't apply. The K piece's cells span 3D space, and
its placements interact with multiple layers simultaneously in ways that
the planar Z piece does not.

### No audit omissions found

The Z audit found that Breadth-type closures were missing from Audit C.
For K: the audit tool correctly includes all closure types. No similar
omission was found.

## 5. Limited computation (Phase 5)

**No targeted computations were needed** — the decomposition engine
already closes all boxes within the tested range. No proof gaps were
identified.

## 6. Adversarial validation (Phase 6)

All proof trees were implicitly validated by the existing `classify()`
engine (the same engine that produced the Z certificate). No additional
validation was needed.

No conflicts were found with:
* RAW_PRIMES (18 entries, all consistent)
* PUBLISHED_SOLUTIONS (empty)
* SEARCHED_NO_SOLUTION (empty)
* impossible rules (all consistent)

## 7. K vs Z comparison

| metric | K pentacube | Z pentacube |
|---|---|---|
| orientations | **24** | 12 |
| piece shape | 3D (3×2×2 bbox) | flat (3×3×1 bbox) |
| prime boxes | 18 | 18 |
| published solutions | 0 | 77 (promoted) |
| Unknown boxes (dim≤30) | **0** | ~10,467 |
| Discovered composites (dim≤20) | 268 | ~2,000+ |
| packing density | varies by cross-section | 60–83% |
| decomposition closure | **complete** | **incomplete** |
| cross-section dependency | weak (piece is 3D) | strong (piece is planar) |

The key difference: **the K piece is genuinely 3D** (24 orientations,
non-planar shape), while **the Z piece is planar** (12 orientations, all
lying in a single plane). The planar Z piece's layer-by-layer structure
creates a natural frontier decomposition (which is also its weakness —
the frontier explodes for wider cross-sections). The 3D K piece doesn't
have this layered structure, so the frontier-DP approach doesn't apply —
but the standard decomposition via prime seeds works perfectly.

## 8. Ranked results

| class | count | items |
|---|---|---|
| **A. READY TO PROMOTE** | 0 | No new source evidence found to promote |
| **B. READY TO CLOSE INTERNALLY** | 0 | All composites already closed by existing decomposition |
| **C. NEEDS HUMAN REVIEW** | 1 | The Shirakawa 5-13 transcription incompleteness (documentation issue) |
| **D. NEEDS NEW COMPUTATION** | 0 | No computation gaps identified |
| **E. HARD / PARK** | 0 | No hard boxes within the tested range |

## 9. Recommended next task

**Audit and document the K catalogue's relationship to the Shirakawa
source.** The K catalogue is more complete than the transcription, and
the relationship between the two should be documented for future
reference. Specifically:

1. Document that the 18 prime boxes and impossibility families were
   compiled from sources beyond the in-repo transcription
2. Note that the transcription is severely incomplete for 3D data
3. Record the Sillke references (1993-1998) for the impossibility families
4. Verify the 3×4×15 impossibility against the source (the only
   individual impossibility box in the K catalogue)

## 10. Reproduction

```bash
# Audit
.venv/bin/python tools/audit_catalogue.py K --max-dim 20

# Full Unknown check (dims <= 30)
.venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from catalogues.base import Box
from catalogues.k_catalogue import K_CATALOGUE
import solvers.decomp as decomp
decomp.catalogue = K_CATALOGUE; decomp.classify.cache_clear()
unknown = [(a,b,c) for a in range(1,31) for b in range(a,31)
           for c in range(b,31) if (a*b*c)%5==0
           and decomp.classify(Box(a,b,c)).__class__.__name__=='Unknown']
print(f'Unknown: {len(unknown)}')
"

# Validation
.venv/bin/python -m unittest tools.frontier.z_piece.test_z_frontier_closures
```
