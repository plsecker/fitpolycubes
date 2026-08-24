# W 5×7×9 Solution Source Search

**Date:** 2026-08-21
**Status:** NO CONCRETE SOLUTION AVAILABLE LOCALLY

## Search Results

| Search target | Result |
|---------------|--------|
| Repository `.dat` solution files | **Not found** — no W 5×7×9 `.dat` files exist |
| Repository experiments directory | **Not found** — no W solutions present |
| Shirakawa solution pages | **Not found** — W (= pentomino 5/10) page lists "1+" but no solution link |
| Sicherman odd-box page | **Image only** — shows a W 5×7×9 cross-section image, no machine-readable data |
| Direct exact-cover solver (fast) | **Timed out** (>24 min, 0 solutions) |
| Direct exact-cover solver (numba) | **Timed out** (>10 min, 0 solutions) |
| W Macro solver (first-gen only) | **28M states, 1.36M sources** — state space 175× larger than V 5×5×9 |

## Why the Search is Hard

W in 5×7×9 is significantly harder than V in 5×5×9:

| Metric | V 5×5×9 | W 5×7×9 | Ratio |
|--------|---------|---------|-------|
| Cross-section | 25 cells | 35 cells | 1.4× |
| Tiles | 45 | 63 | 1.4× |
| Placements | 1,164 | 1,828 | 1.6× |
| Templates | 420 | 576 | 1.4× |
| First-gen sources | 9,000 | 1,360,328 | 151× |
| First-gen intermediate states | 159,059 | 28,048,360 | 176× |

The Macro first-generation search for W completed (queue went empty), yielding 1.36M sources. To find a complete depth-9 path, we would need to explore the macro closure through F[2]..F[9], which would be computationally infeasible with current resources.

## Conclusion

No concrete W 5×7×9 tiling is available in this repository, and generating one requires computational resources beyond what is currently available. The combination of larger cross-section (5×7 vs 5×5) and deeper box (9 layers) makes both the direct exact-cover solver and the Macro state-graph approach intractable.

## Files Searched

- `data/solutions_fast_w_5x7x9.dat` — empty (header only)
- `data/solutions_numba_w_5x7x9.dat` — empty (header only)
- All `data/*.dat` files — none contain W 5×7×9
- `experiments/` directory — no W results
- `shirakawa/W.md` — lists 5×7×9 as "1+ prime" (Shirakawa 2014)
- `docs/pieces/W.md` — confirms 5×7×9 is the minimal odd box
- `catalogues/w_catalogue.py` — confirms raw prime
- `https://sicherman.net/c5box/c5oddbox.html` — image available, no data
- `https://puzzlewillbeplayed.com/Shirakawa/W.html` — "1+" listed, no solution pages