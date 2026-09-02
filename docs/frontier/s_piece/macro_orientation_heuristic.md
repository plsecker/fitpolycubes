# Macro Orientation Selection Heuristic

**Date**: 2026-08-23  
**Status**: **ESTABLISHED** — empirical heuristic supported by project measurements

---

## 1. The Problem

For a rectangular target box X × Y × Z, the Macro technique can be applied
with any of the three dimensions as the longitudinal (thickness) direction.
The cross-section is the product of the other two dimensions.

The choice of slicing direction dramatically affects the Macro state-space
size and computational tractability. The same physical tiling problem can
produce state graphs differing by **3,000× or more** depending on the
orientation chosen.

## 2. The Heuristic

> **For a rectangular target box, choose the Macro slicing direction with
> the smallest cross-section area as the default orientation.**

This is a **practical heuristic** supported by project measurements, not a
theorem about Macro state-space complexity.

## 3. Empirical Validation: 4×5×6

The same physical 4×5×6 S-pentacube box was measured in all three
orientations:

| Cross-section | Area | Macro states | Runtime | Complete? |
|---|---|---|---|---|
| **4×5** | **20** | **1,538** | **0.46 s** | **YES** |
| **4×6** | **24** | **31,738** | **1.63 s** | **YES** |
| **5×6** | **30** | **5,000,227+** | **229 s** | **NO** (cap hit) |

### 3.1 Scaling

| Area increase | State increase | Factor |
|---|---|---|
| 20 → 24 (+20%) | 1,538 → 31,738 | **20.6×** |
| 24 → 30 (+25%) | 31,738 → 5,000,000+ | **158×+** |
| 20 → 30 (+50%) | 1,538 → 5,000,000+ | **3,250×+** |

The state space grows **super-exponentially** with cross-section area.
A 50% increase in area produces a 3,000×+ increase in state space.

## 4. Implementation

The orientation-selection helper is in `tools/frontier/macro_orientation.py`.

### 4.1 Basic Usage

```python
from tools.frontier.macro_orientation import choose_macro_orientation

# Get all orientations sorted by area (best first)
orientations = choose_macro_orientation((4, 5, 6))
# orientations[0] = 4×5 area=20 (best)
# orientations[1] = 4×6 area=24
# orientations[2] = 5×6 area=30 (worst)

# Get just the best orientation
best = choose_macro_orientation((4, 5, 6), recommend=True)
# best.cross_section_dims = (4, 5)
# best.cross_section_area = 20
# best.thickness = 6
```

### 4.2 CLI Usage

```bash
python3 -m tools.frontier.macro_orientation 4 5 6
```

### 4.3 Warning Levels

The helper provides heuristic warning levels based on cross-section area:

| Area | Warning | Expected tractability |
|---|---|---|
| ≤ 20 | **small** | Likely tractable (seconds) |
| 21–24 | **moderate** | Tractable (seconds to minutes) |
| 25–28 | **large** | Benchmark first; expect minutes |
| 29–30 | **very large** | Expect rapid growth; may not complete |
| ≥ 31 | **extreme** | Likely infeasible for complete closure |

These thresholds are based on the S-pentacube measurements and should be
treated as empirical guidelines, not proven bounds.

## 5. Examples

| Box | Best cross-section | Area | Warning | Notes |
|---|---|---|---|---|
| 4×5×6 | 4×5 | 20 | small | Complete in 0.46 s |
| 4×8×20 | 4×8 | 32 | extreme | 15M cap hit; best of bad options |
| 4×8×130 | 4×8 | 32 | extreme | Same cross-section as 4×8×20 |
| 4×9×60 | 4×9 | 36 | extreme | 10M cap hit |
| 4×10×10 | 4×10 | 40 | extreme | 10M cap hit |
| 5×6×29 | 5×6 | 30 | very large | 5M cap hit in 229 s |
| 5×9×12 | 5×9 | 45 | extreme | Likely infeasible |
| 7×8×30 | 7×8 | 56 | extreme | Likely infeasible |

## 6. Caveats

1. **This is an empirical heuristic, not a theorem.** The scaling law is
   based on measurements from a single piece (S-pentacube) in a single
   box (4×5×6). Other pieces may behave differently.

2. **The warning levels are conservative.** They are calibrated to the
   S-pentacube data and may be too pessimistic or too optimistic for
   other pieces.

3. **The heuristic does not account for piece geometry.** Some pieces may
   have smaller state spaces in certain orientations due to their shape,
   independent of cross-section area.

4. **The heuristic does not account for the thickness dimension.** A very
   thin box (thickness 1 or 2) may be tractable even with a large
   cross-section, because the Macro graph is shallow.

5. **Always benchmark first.** For any new piece or box, run a bounded
   feasibility test before committing to a full closure.

## 7. Related Files

| File | Description |
|---|---|
| `tools/frontier/macro_orientation.py` | Orientation-selection helper |
| `tools/frontier/test_macro_orientation.py` | Unit tests (29 tests) |
| `tools/frontier/demo_macro_orientation.py` | Demo on representative examples |
| `docs/frontier/s_piece/4x5_vs_4x6_vs_5x6_macro_orientation.md` | Three-orientation comparison |
| `docs/frontier/macro_method.md` | General Macro method documentation |