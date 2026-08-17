# S 4x8x10 Baseline

Solver: `solvers/solver` (C++ exact-cover, current build, 8 workers).
Placements: `tools/export_placements.py S --box 4 8 10` (1824 placements).

| Metric | Value |
|---|---|
| Placements loaded | 1,824 |
| Nodes | 10,241,321 |
| Dead ends | 3,405,033 |
| Solutions | 0 |
| Max depth | 59 |
| Elapsed | 10.0 s |
| Nodes/sec | ~1.02 M |
| Completed | Yes (exit 0, exhaustive) |

Result: **S does not tile 4x8x10** — consistent with the catalogue
(`catalogues/s_catalogue.py`: `4x8x{10,30,50,70,90,110}` = 0, Shirakawa 2014).
Max depth 59 < 64 pieces, so no branch ever completed a tiling.
Deterministic: three runs gave identical node/dead-end/solution counts.