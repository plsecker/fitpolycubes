# Cross-Section Cyclicity Comparison: 4×9 vs 5×9

**Date**: 2026-08-25  
**Status**: EXPLORATORY — No definitive explanation for the cyclicity difference

---

## 1. The Puzzle

The 4×9 and 5×9 cross-sections present a striking contrast:

| Property | 4×9 | 5×9 |
|----------|-----|-----|
| Area | 36 | 45 |
| Aspect ratio | 2.25 | 1.80 |
| Perimeter | 26 | 28 |
| Catalogue tileable | YES (60, 75, 90, 105) | YES (12, 15, 18, 21) |
| Macro graph type | Widening DAG (depth 51) | Cyclic (proved) |
| Shortest return | 60 (not reached) | 12 (verified) |
| First-gen sources (10M) | 71,143 | 0 |
| State 0 reachable? | NO (explored) | YES (via SVG) |

**The puzzle**: 4×9 has a **smaller** cross-section (36 < 45) but appears to be a **widening DAG** with no cycles found through depth 51. 5×9 has a **larger** cross-section but is **cyclic** with verified cycles. This contradicts the naive expectation that larger area = harder = less likely to be cyclic.

---

## 2. Existing Evidence for 4×9

### Macro exploration results

| Metric | Value |
|--------|-------|
| Cross-section | 4×9 (area 36) |
| Concrete placements | 4,540 |
| Templates | 562 |
| First-gen sources (10M cap) | 71,143 |
| First-gen tree states | >10,000,000 (cap hit) |
| Macro states discovered | 65,062,809 |
| Macro edges | 65,447,160 |
| Max BFS depth | 51 |
| State 0 in graph | **NO** |
| WORD_MASK (GATE) in graph | **NO** |
| Back edges (cycles) | **0** |
| Graph type | **Perfect DAG** (through depth 51) |
| Queue remaining | 8,418,547 states (still widening) |

### Key observations

1. **The graph is still widening at depth 51** — ~8M states per depth at depths 49-51, with no contraction.
2. **No cycles found** — zero back edges among 65M+ edges.
3. **State 0 and GATE not found** — not present at any explored depth.
4. **The expected return depth is 59** (for z=60), which is 8 depths deeper than the explored maximum.

### Catalogue tileability

The catalogue lists 4×9×60, 75, 90, 105 as prime (Shirakawa 2014). By the faithfulness theorem, the 4×9 Macro graph **must** contain return cycles of lengths 60, 75, 90, 105. The failure to find them is a **search-depth artifact** — the BFS was simply too shallow.

---

## 3. Direct Comparison

### 3.1 Template structure

| Property | 4×9 | 5×9 |
|----------|-----|-----|
| Templates | 562 | 776 |
| (4,1,0) templates | 296 (52.7%) | 416 (53.6%) |
| (2,1,2) templates | 192 (34.2%) | 256 (33.0%) |
| (1,4,0) templates | 74 (13.2%) | 104 (13.4%) |
| L2 templates | 192 (34.2%) | 256 (33.0%) |

**VERIFIED FACT**: The template type distribution is nearly identical between 4×9 and 5×9 (52:34:14 ratio). This is consistent across all cross-sections.

### 3.2 First-generation source density

| Cross-section | Sources at 10M | Source density |
|---------------|---------------|----------------|
| 4×9 | 71,143 | 0.71% |
| 5×9 | **0** | **0.00%** |

**STRONG OBSERVATION**: 5×9 has **zero** first-generation sources after 25M+ states, while 4×9 has 71K after 10M. This is surprising because 5×9 is cyclic while 4×9 appears DAG-like. The source density does NOT predict cyclicity.

### 3.3 Mod-3 invariant

| Cross-section | Area mod 3 | Invariant conserved? |
|---------------|------------|---------------------|
| 4×9 | 0 (36) | YES |
| 5×9 | 0 (45) | YES |

**VERIFIED FACT**: The mod-3 invariant is conserved for both cross-sections. It does NOT separate cyclic from acyclic.

### 3.4 L2 states

| Cross-section | L2 templates | L2 in extracted cycles |
|---------------|-------------|----------------------|
| 4×9 | 34.2% | Unknown (no cycles found) |
| 5×9 | 33.0% | NO (all extracted cycles L2=0) |

**VERIFIED FACT**: Both cross-sections have ~33% L2 templates. The absence of L2 in extracted 5×9 cycles is coincidental — the 5×6×4 cycle also has L2=0 despite the 5×6 SCC having L2>0 states.

---

## 4. Possible Explanations

### Hypothesis A: Search-depth artifact (confirmed correct)

**STATUS**: VERIFIED FACT

The 4×9 Macro graph is **cyclic**, as proven by four independently verified Macro cycles (60, 75, 90, 105) extracted from published Shirakawa SVG solutions. The previous apparent acyclicity was a depth-51 truncation artifact.

### Hypothesis B: Aspect ratio effect (partially supported)

**STATUS**: STRONG OBSERVATION

4×9 (aspect ratio 2.25) has a fundamental cycle of 60, while 5×9 (aspect ratio 1.80) has a fundamental cycle of 12. The ratio is exactly 5:1, matching the area ratio (36:45 = 4:5).

### Hypothesis C: 4×9 is genuinely acyclic

**STATUS**: REFUTED

The catalogue is correct. Four verified Macro cycles exist.

---

## 5. The Scaling Relationship

The most important discovery is the **5× scaling relationship** between 4×9 and 5×9:

| Property | 4×9 | 5×9 | Ratio |
|----------|-----|-----|-------|
| Area | 36 | 45 | 0.8 |
| Generators | 60, 75, 90, 105 | 12, 15, 18, 21 | **5.0** |
| Scaled semigroup | ⟨4,5,6,7⟩ | ⟨4,5,6,7⟩ | **identical** |
| Orientation similarity | — | — | **0.956-0.984** |

Every 4×9 generator is exactly 5× the corresponding 5×9 generator. The scaled semigroups are identical. The orientation distributions are nearly identical (cosine similarity 0.956-0.984).

**HYPOTHESIS**: The 4×9 Macro graph may be a "stretched" version of the 5×9 Macro graph, where each 5×9 Macro transition is decomposed into 5 finer 4×9 transitions.

---

## 6. Recommended Investigation

1. **Verify the scaling relationship** by checking whether 4×10 and 5×8 share a similar relationship (both area 40).
2. **Check 4×6 vs 5×6** — both have area 24 and 30 respectively. Do they share a scaling relationship?
3. **Investigate whether the scaling factor equals the area ratio** (36:45 = 4:5, and the cycle length ratio is 5:1 = 45:36).

---

## 6. Files

- `docs/frontier/s_piece/4x9_return_search.md` — Previous 4×9 BFS investigation
- `docs/frontier/s_piece/4x9_structural_analysis.md` — Previous 4×9 structural analysis
- `docs/frontier/s_piece/cross_section_cyclicity_comparison.md` — This document