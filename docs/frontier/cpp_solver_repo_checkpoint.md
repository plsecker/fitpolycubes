# C++ Solver Repository Checkpoint

**Date**: 2026-09-03
**Purpose**: establish a clean, reproducible baseline for the C++ polycube
solver before any further algorithmic experiment. This document records the
exact git state, the provenance of every benchmark result, the conceptual
separation of the uncommitted solver work, and the exact commands to rebuild
the intended benchmark solver.

---

## 1. HEAD and git state

| item | value |
|---|---|
| branch | `frontier-solutions` |
| HEAD | `b714c938420259e1a069a3f21b87f19bb6b02fd5` ("Add validated Z frontier DP implementations", 2026-08-30) |
| committed `solvers/solver.cpp` | old **bare N-piece kernel** (391 lines; `Usage: solver X Y Z`; loads `placements_N_XxYxZ.txt`; **no** piece CLI, `--symmetry`, `--connectivity`, `--dump`, or `max_nodes`) |
| committed solver.cpp sha256 | `aab1576f8a758b33dae2f64357405aa81845079e32860f4bd80663d491848c92` |
| working-tree `solvers/solver.cpp` | 1558 lines, **uncommitted** (sha256 `e0fc0fa233d91f2be5d7bccc99937245047b42cc16730478543fe5fa7164362b`) |

`git log -- solvers/solver.cpp` shows a single commit (`7b1ba4c phase2
begin`); `git diff 7b1ba4c HEAD -- solvers/solver.cpp` is empty, so the
committed solver.cpp is identical at `7b1ba4c` and `b714c93`. **All** of the
phase-2 infrastructure, the sound symmetry, the centre-pair extension, and
the colour/region-pruning research code are **uncommitted working-tree
changes** (1253 insertions / 85 deletions vs HEAD).

The working tree also contains many **unrelated uncommitted changes from
other sessions** (catalogues, docs, tools, scripts, placement files). These
are intentionally **not** part of this checkpoint and are **not** committed
here.

---

## 2. Binary identities (preserved in `/tmp/opencode`)

| binary | sha256 | mtime | source state |
|---|---|---|---|
| `solver_base` | `9c9b7efb53f93887564ef48086b4754345b1669b0e59a3a9c56866caaa3f7773` | 2026-09-02 16:08 | committed HEAD source (old N-piece kernel) |
| `solver_new` | `2cd82dac6c513e91e7a867d37cdb2bf46d3da7bf96f7df4229fde8c35bac7032` | 2026-09-02 15:45 | phase-2 working tree (piece CLI, `--symmetry` corner scheme, `--connectivity`, `--dump`, `max_nodes`; **no** colour code) |
| `solver_v2` | `08cea9916d7637b745c15e05deb8fc3acb09c515e30a3a48159efdf406d7410f` | 2026-09-02 16:22 | phase-2 + **sound symmetry** (centre for all-odd, corner/G₀ for even-dim); **no** colour code, **no** centre-pair |
| `solver_v3` | `216b1ffd44d71a08501023cc40d1f3d9c0ca28c94fa06a4a14ed0769e05e5b4e` | 2026-09-02 22:49 | phase-2 + sound symmetry + **centre-pair** + **colour/region-pruning research** |
| `solver_audit` | `eadb2dbbe254d7dd3c62cf67ea1d9301c7cfebdd7109fe82216b449079474270` | 2026-09-03 09:06 | current working-tree `solvers/solver.cpp` (A+B+C, with runtime counters) |

These binaries are preserved for provenance and are **not** deleted.

---

## 3. Benchmark → binary → result mapping

All node counts are exact and deterministic. Wall times carry ~±20 % noise
(4-core box under external load).

| benchmark | binary | nodes | solutions | depth | wall |
|---|---|---|---|---|---|
| V 5×5×9 baseline (flags off) | `solver_new` | 43,621,737 | 1,120 | 45/45 | 45.1 s |
| V 5×5×9 `--symmetry` | `solver_v2` | 7,816,207 | 140 | 45/45 | 9.0 s |
| V 5×5×9 `--symmetry` (re-run) | `solver_v3` | 7,816,207 | 140 | 45/45 | 9.3 s (byte-identical dump) |
| W 5×5×17 baseline (flags off) | `solver_new` | 264,277,986 | 0 | 84/85 | 475 s |
| W 5×5×17 `--symmetry` | `solver_v2` | 38,024,562 | 0 | 84/85 | 73.9 s |
| Z 4×11×15 baseline (flags off, 200M cap) | `solver_new` | 200,000,073 | 0 | 106/132 | 581 s |
| Z 4×11×15 `--symmetry` centre-pair (200M cap) | `solver_v3` | 200,000,064 | 0 | 107/132 | 556 s |
| Z 4×11×15 `--symmetry` corner (20M cap, no-op) | `solver_v2` | 20,000,063 | 0 | — | — |
| P 1×4×5 `--symmetry` centre-pair | `solver_v3` | 19 | 3 | — | — |

Centre-pair setup on Z (from `solver_v3`/current): |G| = 8; anchor cells
(329, 330); 48 anchor placements, 34 removed; 848 S-tuple candidates → 125
canonical; runtime 52,413 joint checks / 30,867 prunes in 200M nodes.

**Flags-off equivalence** (verified with the current build `solver_audit`):
V 5×5×9 full = 43,621,737 / 1,120; W 50M cap = 50,000,052; Z 20M cap =
20,000,063 — all identical to the phase-2 baseline. The colour/region-pruning
code is flag-gated OFF by default and does **not** affect flags-off or
`--symmetry` results.

---

## 4. Conceptual separation of the uncommitted solver work

The uncommitted `solvers/solver.cpp` contains three conceptual layers. They
are **deeply interleaved in a single file** and are committed together here
(see §5 for why they are not split into separate commits).

### A. Phase-2 solver infrastructure
- Piece CLI (`PIECE X Y Z [placements_file] [max_nodes] [flags]`).
- `max_nodes` cap, `--connectivity[=N]` component pruning, `--dump=FILE`.
- The `--symmetry` toggle and the `Connectivity` struct.
- This is the `solver_new` state (phase-2, corner symmetry).

### B. Sound symmetry implementation (incl. centre-pair extension)
- Rewrote symmetry canonicalisation to be sound: centre anchor for all-odd
  boxes (full group), corner/G₀ for even-dim boxes.
- **Centre-pair extension** (this experiment): anchor set S = the two middle
  cells of the single even axis; S-tuple canonicalisation; static
  allowed-set deactivation; runtime joint check. Gated behind `g_sym.pair_mode`.
- This is the `solver_v2` (sound symmetry) + `solver_v3` (centre-pair) work.

### C. Parallel colour/region-pruning research code
- `--region-prune=colour-global`, `--region-prune=colour`,
  `--region-prune=propagate`, `--research-deadends=K`.
- `Propagator` struct, colour globals/counters, colour-component logic fused
  into the connectivity BFS, `choose_best_column` propagate params.
- From a **separate session**; flag-gated OFF by default; does not affect
  the benchmark results.

---

## 5. Why the checkpoint is a single commit (not A/B/C split)

The three layers are interleaved in one file in ways that cannot be split
into buildable intermediate states **without rewriting algorithms**:
- colour-component pruning is fused into `Connectivity::region_tileable`
  and `region_analyse` (removing it requires restoring the pre-colour
  method bodies);
- unit propagation is fused into `choose_best_column`'s signature;
- the sound symmetry **replaces** the corner symmetry (reverting to A's
  corner scheme is a rewrite).

The task constraint "Do not rewrite algorithms" therefore rules out a clean
A/B/C commit split. The checkpoint is committed as the **full current
state (A+B+C)**, which is fully reproducible, with the conceptual separation
documented here. The colour code (C) is flag-gated OFF and does not affect
the intended benchmark solver's behaviour.

---

## 6. Deliberately remaining uncommitted changes

- **Unrelated catalogue/docs/tools/scripts work from other sessions** (e.g.
  `catalogues/*.py`, `common/*.py`, `docs/pieces/*.md`, `tools/*.py`,
  `opencode.jsonc`, `.gitignore`, `docs/frontier/*` research docs, and the
  many untracked `solvers/v_*.py`, `tools/frontier/*`, `placements_*.txt`
  files). These are intentionally **not** committed here.
- The preserved `/tmp/opencode` binaries and logs (kept, not deleted).

---

## 7. Rebuild commands for the intended benchmark solver

The intended benchmark solver is the current working-tree
`solvers/solver.cpp` (A+B+C, colour off by default). Rebuild:

```bash
# no g++ on this machine; use the user-space zig toolchain
python-zig build-exe solvers/solver.cpp -O ReleaseFast -lc -lc++ \
    -femit-bin=/tmp/opencode/solver_checkpoint
```

Sanity checks (short, not the 200M-node Z run):

```bash
# flags-off V 5x5x9 must be 43,621,737 nodes / 1,120 solutions
./solver_checkpoint V 5 5 9 placements_V_5x5x9.txt
# V --symmetry must be 7,816,207 nodes / 140 solutions
./solver_checkpoint V 5 5 9 placements_V_5x5x9.txt --symmetry
# P 1x4x5 --symmetry (centre-pair) must be 19 nodes / 3 solutions
./solver_checkpoint P 1 4 5 placements_P_1x4x5.txt --symmetry
```

Placement files are untracked but present in the repo root
(`placements_V_5x5x9.txt`, `placements_P_1x4x5.txt`, etc.).

---

## 8. Final cleanliness / provenance status

**REPRODUCIBLE.**

- The intended benchmark solver is the committed working-tree
  `solvers/solver.cpp` (A+B+C). Rebuilding it and running the short sanity
  checks reproduces the flags-off V baseline (43,621,737 / 1,120), the V
  `--symmetry` result (7,816,207 / 140), and the P 1×4×5 centre-pair result
  (19 / 3).
- The committed HEAD solver is the old N-piece kernel and was **not** the
  V/W/Z benchmark baseline; the baselines came from the uncommitted
  phase-2 working-tree binary (`solver_new`), now preserved in
  `/tmp/opencode`.
- The colour/region-pruning research code (C) is flag-gated OFF and does not
  affect the benchmark results; it is committed together with A+B because
  separating it would require rewriting fused algorithms (forbidden).
- Unrelated catalogue/docs work from other sessions is deliberately left
  uncommitted.

**Next experiment can safely proceed** from this checkpoint: rebuild with
the command in §7, run with flags off (or `--symmetry`), and the behaviour
is exactly the documented benchmark solver.
