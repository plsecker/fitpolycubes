# S Pentacube 4×8×130 — Macro Investigation (preserved results)

## Purpose

This directory preserves the complete S-pentacube 4×8×130 Macro
investigation: the 30,000,015-state Macro closure, the 2048
reconstructed 129-edge Macro walks, the low-level realization analysis
(2048 actual tilings), and the exact match against Shirakawa's
published solution.

Authoritative write-up: [`result.md`](result.md).
Checkpoint (not in Git): [`checkpoint.md`](checkpoint.md).

## Key result

- **Exactly 2048** distinct 129-edge Macro walks from
  `17293822637554016271` to `0` inside the 478-state SCC of the
  30,000,015-state Macro closure.
- Every one of the 317 used Macro edges has **exactly 1** low-level
  placement realization, so the 2048 walks correspond bijectively to
  **2048 actual tilings** of the 4×8×130 box with 832 S pentacubes
  (4160 cells; certificate PASS).
- **Shirakawa's published 4×8×130 tiling is exactly one of our 2048
  tilings: walk 311, symmetry = identity** (no rotation/reflection/
  translation).  Independently verified by deriving the MacroState
  sequence directly from Shirakawa's 832-piece placement data.

## Exact git commit(s)

Recorded at commit time (branch: `frontier-solutions`).  The
preservation commit adds this directory, the retained scripts, and the
result artifacts.

## Required scripts (`tools/frontier/`)

| Script | Role | Status |
|---|---|---|
| `scc_aware_analysis.py` | 30M Macro closure + SCC analysis | tracked |
| `complete_succ_0.py` | complete `succ[0]` (331,765 first-gen sources) | tracked |
| `reconstruct_130_path.py` | reconstruct all 2048 walks (exact DP over SCC) | added |
| `analyze_130_walks.py` | walk-family statistics | added |
| `macro_edge_realizations_130.py` | edge realizations + tiling certificate | added |
| `compare_shirakawa_130.py` | Shirakawa SVG → tiling → walk comparison | added |

## Results (`results/`)

| File | Content |
|---|---|
| `scc_aware_analysis_results.txt` | 30M closure + SCC summary (exact figures) |
| `reconstruct_130_path_results.txt` | entry/target, R-sets, 2048-walk reconstruction summary |
| `reconstruct_130_path_run.log` | reconstruction run log |
| `walks_130.txt` | all 2048 walks, one per line, 130 states each |
| `analyze_130_walks_results.txt` | walk statistics (292/478 states, 316/514 edges, no 20-cycle subpaths) |
| `analyze_130_walks_run.log` | statistics run log |
| `macro_edge_realizations_130_results.txt` | 317 edges × 1 realization; 832/4160 certificate PASS |
| `macro_edge_realizations_130_run.log` | realization run log |
| `edge_realizations_130.txt` | per-edge realization counts (all 1) |
| `scc_130_states.npy` | the 478 SCC states (uint64) |
| `scc_130_succ.npy` | SCC-internal successor lists (flat [source, n, succ…]) |
| `shirakawa_tiling_130.txt` | Shirakawa's tiling in canonical coordinates (832 pieces) |
| `shirakawa_comparison_results.txt` | match result: walk 311, identity |
| `shirakawa_walk311_details.txt` | walk-311 state list + branch points |
| `5-15-4x8x130.svg` / `.svgz` | source diagram (puzzlewillbeplayed.com, Shirakawa 2014) |

## How to reproduce

1. **30M closure** (hours, ~11 GB RAM): `scc_aware_analysis.py`
   (max_states = 30,000,000) → checkpoint in
   `/tmp/opencode/macro130_checkpoints/` (see `checkpoint.md`).
2. **Complete `succ[0]`**: `complete_succ_0.py` (patches the truncated
   checkpoint `succ[0]` with the 331,765 complete first-generation
   sources).
3. **Reconstruct the 2048 walks**: `reconstruct_130_path.py` →
   `walks_130.txt`.
4. **Walk statistics**: `analyze_130_walks.py`.
5. **Realizations + certificate**: `macro_edge_realizations_130.py`
   (317 edges, all exactly 1 realization; 832 pieces / 4160 cells
   certificate).
6. **Shirakawa match**: `compare_shirakawa_130.py` (needs
   `results/5-15-4x8x130.svg`; expects walk 311, identity symmetry).

## Verification without the checkpoint

- `walks_130.txt`: 2048 lines, each with 130 distinct states.
- Walk 311 in `walks_130.txt` equals the MacroState sequence derived
  from `shirakawa_tiling_130.txt` (see `shirakawa_walk311_details.txt`).
- `macro_edge_realizations_130_results.txt`: certificate PASS
  (832 placements, 4160 cells, exact 4×8×130 coverage).

## Scope caveat

2048 is exact **for the 30,000,015-state Macro closure**.  It is not a
global proof: the recurrent SCC grew from 226 (15M closure) to 478
(30M closure) states, and Shirakawa's source page makes no uniqueness
claim.  See `result.md` Section I.