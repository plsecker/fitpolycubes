# Post-Checkpoint Review of `solvers/solver.cpp` vs `ebd28c4`

**Date**: 2026-09-03
**Scope**: review ONLY the current working-tree `solvers/solver.cpp` against
the checkpoint commit `ebd28c4`. No file was modified, reverted, committed,
or reformatted. No catalogue or documentation files were touched apart from
creating this report. No solver experiments or long benchmarks were run.

**Key question**: Is the current `solver.cpp` a legitimate evolution of the
checkpoint, or should it be restored to `ebd28c4` before proceeding?

---

## 1. Exact diff summary versus `ebd28c4`

| metric | value |
|---|---|
| checkpoint file | `ebd28c4:solvers/solver.cpp`, 1558 lines, sha256 `e0fc0fa2…` |
| current file | `solvers/solver.cpp`, 1581 lines, sha256 `fc41da77…` |
| diff | **23 insertions, 0 deletions** (purely additive) |
| hunks | 2, both inside `static int setup_symmetry(...)` |
| files changed | 1 (`solvers/solver.cpp`) |

The two hunks:

- **Hunk 1** (current lines 843–853): `SYM_DEBUG`-gated diagnostic output
  inside the centre-pair static-pruning loop.
- **Hunk 2** (current lines 875–886): an early-return guard that skips the
  generic single-row canonical filter when `g_sym.pair_mode` is true, plus a
  block comment explaining why.

No other lines differ. The colour/region-pruning code, CLI options, counters,
runtime joint check, and all other algorithms are byte-identical to the
checkpoint.

---

## 2. Logical grouping of the changes

### Group A — `SYM_DEBUG` diagnostic output (hunk 1)

Inside the centre-pair static over-approximation loop, when a placement
covering an anchor cell is deactivated (`active_rows[r] = 0`), the code now
prints `SYM-REMOVED <row>`; after the loop it prints `SYM-KEPT` followed by
the list of kept anchor placements. All output is gated behind
`getenv("SYM_DEBUG")`, so it has **zero effect** on solver behaviour unless
that environment variable is set.

- **Location**: `setup_symmetry`, centre-pair static-pruning block.
- **Effect on behaviour**: none unless `SYM_DEBUG` is set.
- **Purpose**: diagnostic visibility into which anchor placements the
  centre-pair scheme keeps/removes.

### Group B — centre-pair early-return guard (hunk 2)

A guard is added immediately after the centre-pair block sets
`g_sym.maps`, `g_sym.active`, and `g_sym.anchor_cell`:

```cpp
if (g_sym.pair_mode) {
    return static_cast<int>(g_sym.pair_pruned_rows);
}
```

This returns from `setup_symmetry` **before** the generic single-row
canonical filter ("Canonical restriction on placements covering the anchor
cell") runs. The block comment explains that the generic filter is **not
sound** for the centre-pair scheme: group elements may swap the two anchor
cells, so a row's orbit-minimum image can cover the *other* pair cell, and
deleting the row on that basis destroys whole solution orbits (observed on
chiral H 5×5×6: 21.8% of solution orbits lost).

- **Location**: `setup_symmetry`, immediately after the centre-pair block.
- **Effect on behaviour**: changes the `--symmetry` path for centre-pair
  cases (exactly one even dimension). The generic single-row canonical
  filter is no longer applied in `pair_mode`.
- **Purpose**: correctness fix — makes the centre-pair scheme sound in
  general.

---

## 3. Provenance / timeline evidence

### Timeline

| event | timestamp |
|---|---|
| `ebd28c4` committed (checkpoint, A+B+C) | 2026-09-03 09:57:45 |
| `cpp_solver_repo_checkpoint.md` written | 2026-09-03 10:18 |
| `solver_audit` binary built (pre-change working tree) | 2026-09-03 09:06 |
| `solver_checkpoint` binary + `solver_checkpoint_src.cpp` built | 2026-09-03 09:57 |
| **current `solver.cpp` modified** | **2026-09-03 11:19** |
| inventory commit `6703167` | 2026-09-03 11:11 |
| python-tools commit `0ba21cd` | 2026-09-03 11:13 |

The current `solver.cpp` mtime (11:19) is **after** the checkpoint commit
(09:57) and after the checkpoint doc (10:18). The change is therefore
**post-checkpoint work**, not part of the checkpoint.

### Parallel-session colour/region-pruning code

The checkpoint doc (`cpp_solver_repo_checkpoint.md`) records that the
colour/region-pruning research code (`--region-prune=colour-global|colour|
propagate`, `--research-deadends`, `Propagator` struct) came from a
**separate session** and is flag-gated OFF by default.

Verification: the colour/region code is **byte-identical** between the
checkpoint and the current file (60 occurrences of `region-prune|region_prune|
colour|Propagator|research-deadends` in both; the diff contains **no**
colour/region lines). **The parallel-session code is unchanged** and is not
part of the current diff.

### The H 5×5×6 21.8% observation

The "chiral H 5×5×6: 21.8% of solution orbits lost" claim appears **only** in
the code comment (current lines 878–883). It is **not** documented in any
repo doc and is not present in the checkpoint. This is a new post-checkpoint
finding. The `SYM_DEBUG` env var also appears only in the current code.

### Checkpoint source backup

`/tmp/opencode/solver_checkpoint_src.cpp` (sha256 `e0fc0fa2…`) matches the
committed `ebd28c4:solvers/solver.cpp` exactly, confirming the checkpoint
source backup is the committed state.

---

## 4. Analysis of the centre-pair change (Group B)

### What the checkpoint did

At the checkpoint, in `pair_mode`:

1. The centre-pair block enumerated realisable S-tuples and kept the
   tuple-canonical ones (sound).
2. It applied the static over-approximation (deactivate placements covering
   an anchor cell that participates in no canonical tuple) — sound.
3. It then **fell through** to the generic single-row canonical filter
   ("Canonical restriction on placements covering the anchor cell"), which
   canonicalised each placement covering `anchor_cell` (= `cell_neg`)
   against `g_sym.maps` — the **full** preservation-checked group (the
   `else` branch that restricts to the fixing subgroup `g0` is not taken in
   `pair_mode`).

### Why the generic filter is unsound in `pair_mode`

The full group may contain elements that swap `cell_neg` and `cell_pos`. For
a placement `r` covering `cell_neg`, its orbit-minimum image (over the full
group) can cover `cell_pos` instead. The generic filter compares `sigs[r]`
(the placement's own signature) against the orbit-minimum `best`. If the
orbit-minimum image covers `cell_pos`, then `best` is a *different*
placement's signature, so `sigs[r] != best` and the filter deletes `r` —
even though `r` is part of a canonical tuple. This destroys whole solution
orbits.

### Why the checkpoint's P 1×4×5 validation still passed

The checkpoint doc reports P 1×4×5 as sound (0/6 orbits lost). This is
consistent: for the flat achiral P piece, the full group fixes `cell_neg`
(no element swaps the two anchor cells), so the generic filter happened to
be sound for that specific case. The unsoundness only manifests when the
group actually swaps the anchor cells (e.g. chiral H 5×5×6). The checkpoint
validation was therefore **incomplete** — it did not cover a case where the
generic filter is unsound.

### Effect of the fix

The current guard makes the centre-pair scheme sound in general by skipping
the generic filter in `pair_mode`. The tuple-canonical static filter plus the
runtime joint check (both unchanged) are the complete, sound restriction.

**Caveat**: the fix may change the documented `--symmetry` results for
centre-pair cases (Z 4×11×15, P 1×4×5) if the generic filter was firing for
those cases at the checkpoint. Since the fix makes the scheme sound, any new
result is the correct one, but the documented numbers in
`solver_symmetry_centre_pair.md` and `cpp_solver_repo_checkpoint.md` would
need re-verification if the generic filter was removing placements there.
This is a documentation follow-up, not a reason to reject the change.

---

## 5. Classification of each change

| group | change | classification | rationale |
|---|---|---|---|
| A | `SYM_DEBUG` diagnostic output | **DEBUG/EXPERIMENTAL BUT WORTH PRESERVING** | Inert by default (env-gated); useful diagnostic for the centre-pair pruning; no behavioural effect unless `SYM_DEBUG` is set. |
| B | centre-pair early-return guard | **LEGITIMATE POST-CHECKPOINT WORK** | Genuine correctness fix: makes the centre-pair scheme sound in general by skipping the unsound generic single-row canonical filter in `pair_mode`. Small, focused, purely additive. |

No change is classified as ACCIDENTAL / UNINTENDED or UNCERTAIN.

---

## 6. Answers to the specific review questions

- **Is the centre-pair symmetry implementation unchanged from the
  checkpoint?** **No.** Group B changes it: the checkpoint applied the
  generic single-row canonical filter in `pair_mode` (unsound); the current
  code skips it. The tuple-canonical filter, static over-approximation, and
  runtime joint check are unchanged.
- **Has the colour/region-pruning code changed?** **No.** Byte-identical to
  the checkpoint.
- **Any new solver algorithms, heuristics, pruning, counters, CLI options,
  or experimental code added after `ebd28c4`?** No new algorithms,
  heuristics, counters, or CLI options. The only additions are the
  `SYM_DEBUG` diagnostic output (Group A) and the centre-pair early-return
  guard (Group B). No new pruning logic beyond skipping the unsound generic
  filter in `pair_mode`.
- **Did any changes come from the parallel session?** **No.** The parallel
  session's colour/region-pruning code is unchanged. The current diff is new
  post-checkpoint work (mtime 11:19, after the checkpoint at 09:57).

---

## 7. Recommendations

| group | recommendation |
|---|---|
| A — `SYM_DEBUG` diagnostic output | **COMMIT** (or keep as-is; it is inert and useful). |
| B — centre-pair early-return guard | **COMMIT** — it is a legitimate correctness fix that makes the centre-pair scheme sound. |

**Final recommendation for the whole file: COMMIT.**

The current `solver.cpp` is a **legitimate evolution** of the checkpoint. The
change is small (23 additive lines), confined to the centre-pair symmetry
path, and represents a genuine correctness improvement plus inert diagnostic
tooling. It does not touch the colour/region-pruning code, the flags-off
path, CLI options, or any other algorithm. It should **not** be restored to
`ebd28c4`.

**Follow-up (not blocking):** re-verify the documented `--symmetry` results
for centre-pair cases (Z 4×11×15, P 1×4×5) against the fixed code, since the
generic filter may have been removing placements for those cases at the
checkpoint. Update `solver_symmetry_centre_pair.md` and
`cpp_solver_repo_checkpoint.md` if the numbers change. Also consider
documenting the H 5×5×6 21.8% finding (currently only in the code comment).