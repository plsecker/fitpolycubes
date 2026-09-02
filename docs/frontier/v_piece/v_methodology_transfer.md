# V-Pentacube Methodology Transfer: S / T / V Comparison

**Date**: 2026-08-26
**Status**: COMPLETE — three-piece comparison, the central scientific objective
**Data basis**: complete closures S 4×5/5×6, T 3×7/3×8/5×5 (3×8 re-run to
completion 2026-08-26), V 3×5; exhaustive V 5×5×6 replay.

Classification per feature: **UNIVERSAL** (transfers unchanged across all
pieces tested), **PIECE-SPECIFIC** (genuinely differs; must be measured per
piece), **NOT YET DETERMINED**.

---

## 1. Component-by-component comparison

| Component | S | T | V | Classification |
|-----------|---|---|---|----------------|
| Orientation generation (24 proper rotations, dedupe) | 12 oris | 12 oris | 12 oris | **UNIVERSAL** (machinery); counts PIECE-SPECIFIC |
| Achirality handling | chiral! mirror ∉ orbit | achiral | achiral | machinery **UNIVERSAL**; chirality status PIECE-SPECIFIC |
| Template building (bottom-cell normalization) | ✓ | ✓ | ✓ | **UNIVERSAL** |
| Macro state depth = 3 layers | z-span ≤ 2…3 | max 3 | max 3 (measured) | sufficiency argument UNIVERSAL for pentacubes; per-piece measurement mandatory |
| Faithfulness ⟺ closed walk | proven | proven | proven + 144-tiling replay | **UNIVERSAL** (proof is piece-agnostic) |
| Walk→tiling injectivity | — | — | **refuted on real data (144 tilings → 80 walks)** | NEVER assume injective — **UNIVERSAL caution** |
| Fill-then-shift edge semantics | ✓ | ✓ | ✓ | **UNIVERSAL** |
| Gate structure | single gate (FULL,∅,∅) only | partial-only (classic gate absent on tested sections) | **MIXED**: classic gate + 4 flat partials | **PIECE-SPECIFIC** |
| Generalized cyclicity criterion (L1=L2=∅ + flat coverability) | reduces to gate | needed | needed and instantiated by both classes | statement **UNIVERSAL**; instantiation PIECE-SPECIFIC |
| Cheap first-gen cyclicity test (no closure) | n/a (gate) | yes | available but unnecessary at 3×5 scale | NOT YET DETERMINED (cost trade-offs) |
| SCC period vs shortest cycle | S 4×8: 10 < 20 | T 3×7: 20=20; 5×5: 12=12; **3×8: 5<15 (now complete)** | **2 < 6** | phenomenon recurring; values PIECE-SPECIFIC |
| Numerical semigroup | ⟨20⟩, ⟨4,29,46,47⟩… | ⟨20⟩, ⟨12⟩, gcd-5 family | **⟨6,8⟩ with isolated gap 10** | construction UNIVERSAL; structure PIECE-SPECIFIC |
| Witness extraction source | SVGs | none | native exhaustive solution sets | pipeline UNIVERSAL; sources piece-specific |
| Certificate framework | Layer A generic | 5 witnesses v1 | 2 witnesses v1 + claim verifier | **UNIVERSAL** (format + checker piece-blind) |
| Complexity prediction (preflight) | calibrated on S | calibrated on T families | **failed state-count transfer; strategy only** | model needs general features — NOT YET DETERMINED |
| Multiple cyclic SCCs ("escape basins") | 1 @ area 20; 15 @ area 30 | 1 @ areas 21–24 | **13 already at area 15** | occurs universally at scale; small-area count PIECE-SPECIFIC |

## 2. What transferred unchanged (the load-bearing universals)

1. The **faithfulness theorem and its two-line proof sketch** — no piece content.
2. The **state model**: 3-layer bitmask window; justified per piece by measuring
   max z-span (V required this check even though it passed).
3. The **closure engine**, checkpointing, SCC/period tooling, exact-walk-length
   post-analysis — ran on V with zero modifications.
4. The **certificate format + isolated checker + negative-testing discipline** —
   third geometry certified without touching the checker.
5. The **claim taxonomy** (GLOBAL/SCC-LOCAL/VERIFIED CYCLE/CATALOGUE ONLY) —
   enforced now by an actual verifier, not just prose discipline.

## 3. What is genuinely piece-specific

1. **Orientation geometry**: identical counts (12) hide different structures —
   S has no flats, T has middle-heavy standers, V has neither z-span-2 nor
   [1,3,1]. Every downstream difference traces here.
2. **Gate/terminal structure**: three pieces, three distinct pred(0) shapes.
   There is no single "the gate"; there is a per-piece terminal theorem.
3. **Recurrent-core size at fixed density**: 11 / 39 / 243 at ≈ comparable
   template-per-cell — tractability is not a function of area alone.
4. **Cycle-length arithmetic**: ⟨6,8⟩ with gap 10 (V) is a semigroup shape not
   seen in S/T families so far.

## 4. Not yet determined

1. Whether V's mixed gate persists on larger sections (5×5, 4×5).
2. Whether V 5×5 has period 1 (predicted by published odd prime 5×5×9).
3. Portable complexity features for preflight (flat-fraction? standing
   footprint class? template density moments?).
4. Whether any pentacube requires >3 frontier layers (all 12 currently measured
   ≤ 3; proof that this holds for every pentacube would make depth checks
   vestigial).

## 5. Corrections propagated by this transfer

* Historical V calibration interpretation refuted (walks are many-to-one; see
  `v_macro_faithfulness.md` §3). No S/T conclusions affected.
* T 3×8 upgraded from inferred to **proven period 5** via completed closure
  (side result of the comparative benchmark run).
* Placement files in repo root reclassified as placement *catalogues*, not
  witness data.

## 6. Recommendations (unchanged in spirit from T's list, now evidence-based)

1. Always measure orientation/z-span before assuming state depth.
2. Always run the exact-walk-length post-analysis after closure — it converts
   cycles into family classifications nearly for free.
3. Never report raw-tiling counts from macro walks alone (realizations are
   one-to-many).
4. Keep certificates self-contained; test rejection paths on every new piece.
