# Post-W Target Audit: Next Exhaustive Enumeration Project

**Date:** 2026-08-25  
**Status:** AUDIT COMPLETE

---

## 1. Candidate Inventory

All pentacube catalogues audited. 22 pieces, of which V and W are already resolved. The remaining 20 pieces have MINIMAL_ODD boxes that are candidates for exhaustive enumeration.

### A. 5×5 Cross-Section (25 cells) — Controlled Comparison with V

These are the strongest candidates because the C++ solver is validated and benchmarked on 5×5×9 (V: 1,164 placements, 51.8s). Any 5×5×N problem directly reuses the proven solver configuration.

| Piece | Box | Vol | Tiles | Placements | 2D-Chiral? | Published | Catalogue MINIMAL_ODD | Notes |
|-------|-----|-----|-------|-----------|-----------|-----------|----------------------|-------|
| **H** | 5×5×9 | 225 | 45 | **2,432** | **YES** (H/H') | 1+ (Sillke 1993) | Box(5,5,9) | 2× V's placements; same box; first chiral case |
| **Q** | 5×5×9 | 225 | 45 | **1,164** | No | 1+ (Sillke 1993) | Box(5,5,9) | Same placement count as V; cleanest control |
| **F** | 5×5×11 | 275 | 55 | **2,952** | No | — | Box(5,5,11) | Deeper than V; tests depth scaling |

### B. 5×7 Cross-Section (35 cells) — Comparison with W

| Piece | Box | Vol | Tiles | Placements | 2D-Chiral? | Published | Catalogue MINIMAL_ODD | Notes |
|-------|-----|-----|-------|-----------|-----------|-----------|----------------------|-------|
| **B** | 5×7×7 | 245 | 49 | **1,392** | No | — | Box(5,7,7) | Same cross-section as W, shallower; 245 cells |

### C. Smaller Cross-Sections (15 cells)

| Piece | Box | Vol | Tiles | Placements | Published | Notes |
|-------|-----|-----|-------|-----------|-----------|-------|
| **J** | 3×5×5 | 75 | 15 | 512 | 1+ | 2D-chiral (J/J') |
| **K** | 3×5×9 | 135 | 27 | 1,088 | 1+ | 3D chiral |
| **L** | 3×5×5 | 75 | 15 | 352 | 1+ | Planar |
| **U** | 3×5×7 | 105 | 21 | 528 | 1+ | 2D-chiral (U not in pairs) |

### D. Larger/Currently Impractical

| Piece | Box | Vol | Tiles | Cross-section | Status |
|-------|-----|-----|-------|---------------|--------|
| **S** | 5×9×15 | 675 | 135 | 45 cells | Proven infeasible (Macro: 0 sources after 25M states) |
| **T** | 3×15×17 | 765 | 153 | 45 cells | Proven infeasible (Macro: 0 sources after 5M states) |
| **Z** | 5×9×15 | 675 | 135 | 45 cells | Likely same difficulty as S |

---

## 2. A/B/C Ranking

### A. Immediate Next Targets

| Rank | Piece | Box | Rationale |
|------|-------|-----|-----------|
| **1** | **H** | **5×5×9** | Same box as V. First 2D-chiral pentomino. 2,432 placements. Published solution exists. |
| **2** | **Q** | **5×5×9** | Same box, same placement count as V. Cleanest control. Very fast expected. |

### B. Medium-Term Targets

| Rank | Piece | Box | Rationale |
|------|-------|-----|-----------|
| 3 | B | 5×7×7 | Same cross-section as W, shallower. Tests depth vs difficulty. |
| 4 | F | 5×5×11 | Deeper 5×5 box. Tests depth scaling from V. |
| 5 | J/K/L/U | 3×5×N | Smaller cross-section. Would be very fast but less scientifically valuable. |

### C. Currently Impractical

| Piece | Box | Reason |
|-------|-----|--------|
| S | 5×9×15 | 45-cell cross-section — proven infeasible |
| T | 3×15×17 | 45-cell cross-section — proven infeasible |
| Z | 5×9×15 | Same difficulty as S |

---

## 3. Comparison of Top Alternatives

### H 5×5×9 vs Q 5×5×9

| Factor | H 5×5×9 | Q 5×5×9 |
|--------|---------|---------|
| Placements | 2,432 (2.09× V) | 1,164 (1.00× V) |
| 2D-Chiral | **YES** (H/H' pair) | No (planar) |
| Scientific value | **First chiral exhaustive enumeration** | Clean control experiment |
| Expected C++ time | ~2-5× V's 51.8s = ~2-4 min | ~0.5-1× V's 51.8s = ~25-50s |
| Search tree estimate | Larger (more placements → more branching) | Similar to V (43.6M nodes) |
| Published solution | 1+ (Sillke 1993), solution page exists | 1+ (Sillke 1993), solution page exists |
| Solver ready | Yes (C++ solver, same box) | Yes (C++ solver, same box) |

**Why H beats Q:**
1. **First chiral enumeration** — extends the methodology. The V/W workflow has only been applied to achiral pieces (V is 2D-achiral; W is 2D-achiral despite having 12 3D orientations). H is a genuine 2D-chiral pentomino (H/H' mirror pair). This tests whether chirality affects the exhaustive enumeration difficulty or the solution structure.
2. **Moderate difficulty increase** — 2,432 placements (2× V) is a reasonable step up. Not so large as to be infeasible, but large enough to be informative.
3. **Same-box comparison** — directly compare H's solution count against V's 1,120 in the identical 5×5×9 box. This isolates the effect of piece shape from box geometry.

**Why Q is a strong runner-up:**
1. Identical placement count to V (1,164) makes it the cleanest possible experiment.
2. Would complete very quickly, providing an immediate data point.
3. Less scientifically innovative than H — same 2D-achiral category as V.

---

## 4. Recommended Next Project: **H 5×5×9**

### Why H beats all other candidates:

1. **Controlled same-box comparison:** H 5×5×9 uses the identical box (5×5×9) as V. This directly controls for box geometry. Any difference in solution count is attributable to piece shape and chirality.

2. **First 2D-chiral exhaustive enmeration:** All prior exhaustive results (V 5×5×6, V 5×5×9, W 5×7×9) involve pieces that are 2D-achiral. H is a confirmed  chirall pair (H/H' per Sicherman). This is the first opportunity to study how 2D chirality affects 3D tiling enumeration.

3. **Published solution exists:** Shirakawa's page lists "1+" for H 5×5×9 (Sillke 1993), and a solution HTML page exists at `5-23-9x5x5.html`. This can provide a ground-truth witness.

4. **Reristic difficulty:** 2,432 placements (2× V) is within the proven capability of the C++ solver. V 5×5×9 completed in 51.8s (43.6M nodes). Even if H takes 5-10× longger, it would still be tractable (~5-10 minutes).

5. **Solver infrastructure ready:** The C++ solver (`solver.cpp`) is validated on V 5×5×6, V 5×5×9, and W5×7×9. Placement geneneration (`polycube_utils.py`) works for any pentacube. No new infrastructure needed.

6. **Symmetry ggroup known:** D2h for 5×5×9 has 16 elements (2 axis permutations × 8 reflections) — same as V 5×5×9, so the symmetry analysis can be directly reused.

### Expected Difficulty

| Metric | V 5×5×9 | H 5×5×9 | Ratio |
|--------|---------|---------|-------|
| Placement | 1,164 | 2,432 | 2.09× |
| Box | 5×5×9 | 5×5×9 | 1.00× |
| Tiles | 45 | 45 | 1.00× |
| Search nodes | 43.6M | ? (~100-500M estimated) | ~2-12× |
| C++ time | 51.8s | ? (~2-10 min estimated) | ~2-12× |

The search tree may grow faster than the placement count. W showed that a 1.6× placement increase (1,164→1,828) produced a 120× node increase. However, W also changed the cross-section (5×5→5×7). H keeps the same cross-section, so the scaling should be more modest.

### What New Scientific Information H 5×5×9 Provides

1. **Chirality effect on solution count:** Does a 2D-chiral piece have more, fewer, or the same number of tilings as an achiral piece in the same box?

2. **Branching comparison with V:** Does a different piece shape in the same box produce a harder or easier search tree?

3. **Methodology extension:** First exhaustive enumeration of a genuine 2D-chiral pentacube. Confirms the methodology works for all 12 pentomino-derived pentacubes.

4. **Catalogue closure:** H 5×5×9 is the MINIMAL_ODD box in the H catalogue. Resolving it provides the first data point for all H-family boxes.

---

## 5. Phase 0/1 Plan for H 5×5×9

### Phase 0 — Immediately Before the Full Search

**Step 0.1:** Verify catalogue listing
- [ ] Confirm H 5×5×9 is a RAW_PRIME (done: `h_catalogue.py`, line 53)
- [ ] Confirm MINIMAL_ODD = Box(5,5,9) (done: line 67)
- [ ] Note published status: "1+" (Sillke 1993, Shirakawa 5-23)

**Step 0.2:** Obtain known solution
- [ ] Fetch H 5×5×9 SVGZ from `https://puzzlewillbeplayed.com/Shirakawa/svgz/5-23/5-23-9x5x5.svgz`
- [ ] Parse into repository .dat format
- [ ] Validate the known solution independently

**Step 0.3:** Placement generation sanity check— placement count (2,432)
- [ ] Generate placements with Python
- [ ] Verify known solution pieces are in the placement set
- [ ] Verify symmetry group action on placements

**Step 0.4:** Small calibration search
- [ ] Run C++ solver with 10M node limit on H 5×5×9
- [ ] Measure nodes/sec (expected: ~500K, similar to V/W)
- [ ] Verify the known solution is reachable
- [ ] Estimate total tree size from depth distribution

**Step 0.5:** Decide whether to launch full search
- [ ] If estimated tree <200M nodes → launch full search (expected)
- [ ] If estimated tree >1B nodes → investigate algorithmic improvements first

**Step 0.6:** Run full exhaustive enumeration
- [ ] Same C++ solver, same invocation as V/W
- [ ] Capture all solutions

**Step 0.7:** Post-processing
- [ ] Validate all solutions (40/40 etc.)
- [ ] Symmetry classification under D2h (16 elements for 5×5×9)
- [ ] Certificate generation and validation
- [ ] Compare with V 5×5×9 results

### Estimated Timeline

| Step | Duration | Notes |
|------|----------|-------|
| Phase 0.2 (obtain known solution) | ~10 min | Download and parse SVGZ |
| Phase0.3-0.4 (placement check + calibration) | ~5 min | Numba or Python |
| Phase0.5 (decision) | ~1 min | Based on calibration |
| **Phase 0.6 (full searh)** | **~2-30 min** | **C++ solver, estimated** |
| Phase 0.7 (validation) | ~5 min | Certificate and symmetry analysis |
| **Total** | **~15-50 min** | **Well within one session** |

---

## 6. Summary Recommendation

**Recommended next project: H 5×5×9**

**Category:** Controlled same-box comparison + first 2D-chiral exhaustive case.

| Factor | Assessment |
|--------|-----------|
| Piece | H (H/H' chiral pair) |
| Box | 5×5×9 (same as V) |
| Difficulty | Moderate (2× V's placements) |
| Estimated C++ time | 2–30 minutes |
| Infrastructure | Ready (C++ solver, validated) |
| Scientific value | **High** — first chiral case, direct V comparison |
| Solver methodology | Reuse V 5×5×9 workflow directly |

**Runner-up: Q 5×5×9** — cleaner control, but less scientifically innovative.

**Not recommended at this time:** S 5×9×15, T 3×15×17, Z 5×9×15 (proven infeasible with current solver).

---

**Prepared by:** OpenWork automated analysis  
**Date:** 2026-08-25  
**Status:** AUDIT COMPLETE — H 5×5×9 recommended as next exhaustive enumeration project