George package - CK6 oddity improvements for the B and L pentacubes
===================================================================

Prepared from the completed Stage 5L search via the Stage 5N/5O
small-positive catalogue and the Stage 5P George comparison.
Nothing was sent externally; the running V45->V35 search was not
touched (single process, one CPU, trivial memory).

Contents
--------
  b_v15/
    B-V15-S1_target.png      target-only render (voxel cubes)
    B-V15-S1_tiling_i.png    one render per verified tiling (2 files), copies distinctly coloured
    coordinates.txt       target + all placements, plain text
    witness.json          compact machine-readable witness
    report.txt            full human-readable evidence report
    george_ready.txt      one-line summary for George
  l_v25/
    L-V25-S1_target.png      target-only render (voxel cubes)
    L-V25-S1_tiling_i.png    one render per verified tiling (4 files), copies distinctly coloured
    coordinates.txt       target + all placements, plain text
    witness.json          compact machine-readable witness
    report.txt            full human-readable evidence report
    george_ready.txt      one-line summary for George
  summary.txt             the two George-ready statements

Independent verification performed (both constructions)
-------------------------------------------------------
  volume; face connectivity; complete CK6 subgroup (4 affine
  symmetries, kinds {identity, c2_diag, inversion, mirror_diag},
  Lunnon class CK6); exact symmetry order 4 (no stronger
  symmetry); exact tiling count recomputed by per-target exact
  cover; every placement a proper orientation of the pentacube;
  copies disjoint; union exactly the target; rendered cube
  counts match the coordinates exactly.

Source of the published minima
------------------------------
  George Sicherman, "Pentacube Oddities with Inverse/Diagonal Symmetry",
  https://sicherman.net/c5odd/c5nodd.html
  table "Achiral Pentacubes", page revision 2026-09-05;
  local cache data/ck6_reuse/sicherman_cache/c5odd/c5nodd.html; comparison record
  data/ck6_reuse/stage5p_george_comparison.json (Stage 5P).

