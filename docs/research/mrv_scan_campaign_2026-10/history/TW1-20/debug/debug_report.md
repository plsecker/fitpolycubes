# TW1-20 DEBUG — Linked-List Fix Verification

**Date:** 2026-10-16 (Pacific/Auckland)
**Scope:** Verify `reactivate_row()` head-insertion fix in the isolated TW1-20 candidate before any performance benchmarks.
**No commits, deploys, merges, or worktree modifications were made.**

---

## 1. Preservation of the original failing candidate

The original failing source hash (`d23bf97e9158906d73f3c93dedc5bee44f5f3da7b077225778fe90e150c54107`) is recorded in `tw20_report.md` / `debug/original_tw20_report.md`. The file with that hash no longer exists on disk (current `solver_active_x.cpp` already contains the fix); the hash is preserved via the report.

Preserved artifacts under `/tmp/pentacube-bench/tw20/debug/`:

| Artifact | Path | SHA256 / note |
|---|---|---|
| Original failing release binary (pre-guard, hangs) | `debug/original_solver_active_x_BIN` | `f57debb24a033db6b038cdc4ac0771d8c55096ab42d0ad6b5dfccd27f60fbcc1` |
| Original debug binary (with cycle guards, aborts) | `debug/original_solver_active_x_debug_BIN` | `5255d705dca526953d5a32d086d53b180c3f2aab58f6466a7b10e6ba293af901` |
| Baseline binary (copy) | `debug/solver_baseline_BIN` | `79dff337875560de88f2501a602e8aeebabc26220a61197204adf910c95ebc47` |
| Pre-debug candidate source copy | `debug/solver_active_x_BEFORE_DEBUG.cpp` | fixed-source hash (see §3) |
| Baseline source copy | `debug/solver_coalesced_baseline.cpp` | `a4fdcf12…` |
| Original report + logs | `debug/original_tw20_report.md`, `debug/build_active_x.log`, `debug/active_x_v5x5x6.log` (empty, 0 bytes) | as found |

All further work was done only in `/tmp/pentacube-bench/tw20/` (isolated candidate) and `debug/` (invariant build). No workspace worktrees were modified.

---

## 2. Audit of `reactivate_row()` / `deactivate_row()` and every caller

Source audited: `/tmp/pentacube-bench/tw20/solver_active_x.cpp` (fixed, §3).

### 2.1 `deactivate_row()` (lines 117–127) — CORRECT

```cpp
void deactivate_row(int r) {
    for (int j = 0; j < CELLS_PER_PLACEMENT; ++j) {
        const int inc = row_incidence[r * CELLS_PER_PLACEMENT + j];
        const int c = inc_cell[inc];
        const int n = inc_next[inc];
        const int p = inc_prev[inc];
        if (n >= 0) inc_prev[n] = p;
        if (p >= 0) inc_next[p] = n;
        else head[c] = n;  // inc was head
    }
}
```

- Previous node's `next` updated, or `head[c]` updated when removing the head. ✓
- Next node's `prev` updated. ✓
- Removed incidence is unreachable from the list (both neighbours bypass it). Stale `inc_next/inc_prev` values remain on the removed incidence itself but are overwritten on reinsertion. ✓

### 2.2 `reactivate_row()` (lines 130–142) — FIX PRESENT

```cpp
void reactivate_row(int r) {
    for (int j = 0; j < CELLS_PER_PLACEMENT; ++j) {
        const int inc = row_incidence[r * CELLS_PER_PLACEMENT + j];
        const int c = inc_cell[inc];
        inc_prev[inc] = -1;            // incidence is now at head
        inc_next[inc] = head[c];
        if (head[c] >= 0) inc_prev[head[c]] = inc;
        head[c] = inc;
    }
}
```

Head-insertion checklist:
- `inc_prev[inc] == -1` ✓ (the fix line)
- `inc_next[inc]` = previous head ✓
- Previous head's `inc_prev` → `inc` ✓
- `head[c]` → `inc` ✓

**Root-cause hypothesis:** the original failing version omitted `inc_prev[inc] = -1`. A reactivated incidence kept its stale `prev` pointer. If that stale `prev` pointed into the same cell's list (e.g. the incidence was not the head when removed, or was reactivated while its old predecessor was still linked), forward traversal via `inc_next` could re-enter an already-visited node → cycle → propagator `for (inc = head[c]; inc >= 0; inc = inc_next[inc])` never terminates. `deactivate_row` on a corrupted list then propagates the corruption (wrong `head[c]`, mismatched pairs).

### 2.3 Every caller

| Call site | Code | Assessment |
|---|---|---|
| Placement deactivation | lines 1690–1695: `if (active_rows[other]) { active_rows[other]=0; deactivated_rows.push_back(other); if (g_prune_propagate) g_active_x.deactivate_row(other); }` | Guarded by `active_rows`, so no double-deactivation. ✓ |
| Rollback restoration | lines 1765–1770: `for (int q : deactivated_rows) { active_rows[q]=1; if (g_prune_propagate) g_active_x.reactivate_row(q); }` | Restores exactly the rows deactivated at this level, in forward (not reverse) order. Each row restored once. Order reversal vs removal is real (see §4) but invariant-safe. ✓ |
| Symmetry pre-deactivation | lines 2196–2200: after `g_active_x.init(...)`, `deactivate_row(r)` for every `!active_rows[r]` | `init` builds full lists, then symmetry-killed rows are removed once. ✓ |
| Parallel worker (`parallel_worker`, lines 1914–2006) | Applies task prefixes to private `ac`/`ar` copies; **never touches `g_active_x`**; then calls `search()` which uses thread-local `g_active_x` | **Unsafe combination:** with `--parallel` + `--region-prune=propagate`, workers would traverse a stale/shared ActiveX. All tests here are single-threaded; parallel+propagate was not verified and must not be benchmarked without a fix. See §7. |

### 2.4 Evidence confirming the cycle root cause

| Test | Result |
|---|---|
| Original release binary, config B, 10 s timeout | **EXIT 124 (hang)** — `debug/original_B_stdout.txt` empty, no output. Corruption detected via timeout only (no guards in that build). |
| Original debug binary (`solver_active_x_debug`), config B | **EXIT 134 (abort)**: `ACTIVE-X INFINITE LINK2 DETECTED: e=101 head=2680` (`debug/debugbin_stderr.txt`). Concrete cycle diagnostic, not a timeout inference. |
| Fixed source (`solver_active_x.cpp` 42fad94b), config B | **EXIT 0**, full results, byte-identical counters to baseline (see §5). |
| Invariant build, full V exhaustive with per-removal+restore checks | **EXIT 0**, `ACTIVEX-INVARIANT setup OK`, no abort (§6). |

The fix converts a hang (release) / abort (guarded debug) into a clean, counter-identical run.

---

## 3. Exact fix and source hashes

The fix is one line in `reactivate_row()` (plus the pre-existing correct neighbours):

```cpp
inc_prev[inc] = -1;  // incidence is now at head
```

| Item | Path | SHA256 |
|---|---|---|
| Coalesced baseline source | `/tmp/pentacube-bench/tw20/solver_coalesced.cpp` | `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278` |
| Fixed candidate source | `/tmp/pentacube-bench/tw20/solver_active_x.cpp` | `42fad94bb9cabeafc379e50b58f8e6816c0aa545a48ed178145febb15ef7bed9` |
| Fixed candidate binary (fresh `-Ofast -march=native -flto`) | `/tmp/pentacube-bench/tw20/solver_active_x` | `fe8ea52f126494df8f7e90d61797c30cfb9992309e480eac65811fa2c3f15e9b` |
| Fresh baseline binary | `/tmp/pentacube-bench/tw20/solver_baseline` | `79dff337875560de88f2501a602e8aeebabc26220a61197204adf910c95ebc47` |
| Invariant-build source | `debug/solver_active_x_invariant.cpp` | `ef8054f0b1a78781dc6a6fa0532e84aba37d1e804b6dc76634bdc3e4d254eb57` |
| Invariant-build binary (`-g -O0`) | `debug/solver_active_x_invariant` | `0f214d7f9dc3412ed4ba32bcead067ceff0a449202c78c40cb0c0e9410ead580` |
| Compiler | `g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` | — |

Build logs: `debug/build_baseline_fresh.log`, `debug/build_active_x_fresh.log`, `debug/build_invariant.log`. Hash manifest: `debug/SOURCE_HASHES_FINAL.txt`.

Note: the fixed source still emits `DEBUG: Initializing ActiveX...` lines on stderr whenever propagate is on. Harmless for correctness; stderr should be ignored in counter diffs.

---

## 4. Traversal-order semantics

- **CSR order:** `build_x_csr()` appends rows in placement order, so each cell's CSR segment is ascending row order.
- **ActiveX initial order:** `init()` inserts rows `0..nr-1` at the head, so each list starts in **reverse** placement order (highest row first).
- **Steady-state order:** every `deactivate`/`reactivate` cycle reinserts at the head, so the list is MRU-first, not placement-order. Rollback restores `deactivated_rows` in forward order, which further reverses relative removal order.
- **Conclusion:** head reinsertion does **not** preserve CSR traversal order. This was not assumed away.

**Equivalence demonstration (beyond solution counts):**
- The Propagator dedupes rows with the per-run `kill[]` stamp and returns only a boolean (contradiction or not); the killed set and degree decrements are order-independent, with only early-exit timing order-dependent.
- Full deterministic-counter comparison (nodes, dead ends, solutions, connectivity checks/prunes, centre-pair checks/prunes, colour-component rejections, propagation rejections, forced placements processed, max depth, and the 32-bucket genuine-new rejection histogram) is **identical** between baseline and fixed candidate on V exhaustive, KSSref 10M-cap, and W 2.5M-cap (§6).
- Forced-placement comparison (`DEBUG_COMPARE=1`, V 5×5×6, 5000-node cap): all **4884 `D <depth> <col> <nforced>` lines identical**, full outputs identical modulo timing (`debug/forced_baseline.txt` vs `debug/forced_candidate.txt`).
- Hence traversal-order difference is empirically immaterial for these workloads and flags. **Residual concern:** any future logic that depends on visitation order (e.g. tie-breaking, ordered kill processing with side effects) would need order-preserving restore; none exists today.

---

## 5. Failure configurations A, B, C (actual exit statuses)

Placement file: `/home/philip/Work/fitpolycubes/placements_V_5x5x6.txt` (SHA256 `dc22870d…`). Correct CLI syntax: `solver PIECE X Y Z placements_file [max_nodes] [flags]`.

### A. Connectivity + symmetry, propagation DISABLED
```
solver V 5 5 6 placements_V_5x5x6.txt --connectivity --symmetry
```
| Binary | Exit | Nodes | Solutions | Dead ends | Max depth |
|---|---|---|---|---|---|
| Baseline | 0 | 93440 | 18 | 34236 | 30/30 |
| Fixed candidate | 0 | 93440 | 18 | 34236 | 30/30 |
- Logs: `debug/configA_baseline_stdout.txt`, `debug/configA_candidate_stdout.txt` (stderr empty both). Diffs excluding timing: **identical**.
- Note: ActiveX is inert here (`g_prune_propagate=false` gates all `deactivate/reactivate` calls), so this config cannot exhibit the cycle; it guards against regressions in the shared search path.

### B. Connectivity + symmetry, propagation ENABLED
```
solver V 5 5 6 placements_V_5x5x6.txt --connectivity --symmetry --region-prune=propagate
```
| Binary | Exit | Nodes | Solutions | Dead ends | Propagation rejections (forced) |
|---|---|---|---|---|---|
| Baseline | 0 | 70033 | 18 | 34236 | 14452 (42099) |
| Fixed candidate | 0 | 70033 | 18 | 34236 | 14452 (42099) |
| Original release binary | **124 (timeout/hang)** | — | — | — | — |
| Original debug binary | **134 (abort: `ACTIVE-X INFINITE LINK2 DETECTED: e=101 head=2680`)** | — | — | — | — |
- Logs: `debug/configB_*`, `debug/original_B_*`, `debug/debugbin_*`. Baseline↔candidate diffs excluding timing: **identical**.

### C. Connectivity + colour + propagate + symmetry
```
solver V 5 5 6 placements_V_5x5x6.txt --connectivity --region-prune=colour --region-prune=propagate --symmetry
```
| Binary | Exit | Nodes | Solutions | Dead ends | Colour-comp rej. | Propagation rej. (forced) |
|---|---|---|---|---|---|---|
| Baseline | 0 | 70033 | 18 | 34236 | 0 | 14452 (42099) |
| Fixed candidate | 0 | 70033 | 18 | 34236 | 0 | 14452 (42099) |
- Logs: `debug/configC_*`. Diff excluding timing: **identical**.

---

## 6. Required correctness tests vs freshly built coalesced baseline

Flags for all: `--connectivity --symmetry --region-prune=propagate`. Placement files: V `placements_V_5x5x6.txt` (`dc22870d…`), KSSref `placements_KSSref_5x5x5.txt` (`9786dd43…`), W `placements_W_5x7x9.txt` (`a7a421cd…`). All diffs exclude `Time:` / `Nodes/sec` / `Solutions/sec` only.

| Test | Baseline (exit 0) | Fixed candidate (exit 0) | Match |
|---|---|---|---|
| V 5×5×6 exhaustive | 70033 nodes, 18 sol, 34236 dead ends, depth 30/30, conn 70015/pruned 2569, pair 2587/1013, prop 14452 (forced 42099), histogram identical | same | **✓ identical** (`debug/correct_V_*`) |
| KSSref 5×5×5, cap 10000000 | 10000068 nodes, 0 sol, 6335178 dead ends, depth 24/25, conn 9999999/pruned 3070835, prop 1297394 (forced 2464552), histogram identical | same | **✓ identical** (`debug/correct_KSS_*`) |
| W 5×7×9, cap 2500000 | 2500040 nodes, 0 sol, 1136291 dead ends, depth 58/63, conn 2499999/pruned 233966, prop 564316 (forced 1525974), histogram identical | same | **✓ identical** (`debug/correct_W_*`) |

Note on KSSref counts: the TW18 log (`10000070`-cap) shows 10000070/6335406; this task used cap `10000000` for **both** binaries, so the valid comparison is baseline↔candidate at identical cap — which matches exactly. The 2-node offset vs the old log is a cap artifact, not a divergence.

**Forced-placement comparison:** `DEBUG_COMPARE=1`, V 5000-node cap — 4884 `D` lines identical, full outputs identical modulo timing.

**ActiveX invariant validation** (`debug/solver_active_x_invariant`, `ACTIVEX_INVARIANT=1 ACTIVEX_INVARIANT_EVERY=1`):
- Checks per cell: forward traversal terminates within incidence count; no duplicates; no cycles; consistent next/prev pairs; head `prev == -1`; incidence/cell/row indices in bounds.
- Across cells: every active row has all 5 incidences reachable; inactive rows have none reachable.
- Checked at setup, after every row removal, and after every restoration (including rollback paths).
- Results: setup `ACTIVEX-INVARIANT setup OK`; 20k-node run exit 0 (`debug/invariant_small_*`); **full V exhaustive exit 0** (`debug/invariant_full_*`: 70033 nodes, 18 sol, 34236 dead ends, prop 14452/42099). No invariant failure, no timeout reliance.

---

## 7. Remaining traversal-order / rollback concerns

1. **Order is not preserved (accepted, demonstrated equivalent).** MRU-head order differs from CSR placement order. All deterministic counters and forced-placement traces match, so no functional dependence on order exists in the current propagator. Do not reintroduce order-sensitive logic without an order-preserving restore.
2. **Rollback restores in forward order.** `for (int q : deactivated_rows)` reinserts in deactivation order rather than reverse. Safe for the invariant and empirically equivalent, but reverse-order restore would more closely mirror a stack discipline; consider it if order preservation is ever required.
3. **`--parallel` + `--region-prune=propagate` is unverified and likely broken.** `parallel_worker` never maintains `g_active_x` yet calls `search()` which traverses the thread-local ActiveX. Do not run parallel+propagate correctness or performance tests without fixing worker ActiveX setup/teardown.
4. **Stale pointers on detached incidences.** `deactivate_row` leaves `inc_next/inc_prev` on the removed incidence; correctness relies on `reactivate_row` overwriting both. Any future removal path that reads a detached incidence's links without reinsertion would be unsafe.
5. **Residual stderr noise.** `DEBUG: Initializing ActiveX...` prints on every propagate run; strip before any log-diff automation that includes stderr.

---

## 8. Verdict: is ActiveX ready for performance testing?

**Yes — correctness-wise, ActiveX is ready for performance testing.** The cycle root cause is confirmed with a concrete abort diagnostic, the one-line fix is verified by exhaustive invariant checks on every removal/restore path, all three failure configurations exit 0 with counter-identical results, and V/KSSref/W correctness plus forced-placement traces all match the freshly built coalesced baseline exactly.

**Expectation warning (not a correctness block):** the prior TW1-20 report already measured the fixed design as consistently slower (median −7.86% on W 5×7×9 2.5M). The five-pair performance benchmark was **not** run per instructions; when it is run, expect it to re-confirm REJECT on performance grounds, not correctness.

---

## 9. Key artifact paths

- Report (this file): `/tmp/pentacube-bench/tw20/debug/debug_report.md`
- Fixed source / binary: `/tmp/pentacube-bench/tw20/solver_active_x.cpp`, `/tmp/pentacube-bench/tw20/solver_active_x`
- Baseline source / binary: `/tmp/pentacube-bench/tw20/solver_coalesced.cpp`, `/tmp/pentacube-bench/tw20/solver_baseline`
- Invariant source / binary: `debug/solver_active_x_invariant.cpp`, `debug/solver_active_x_invariant`
- Config logs: `debug/configA_*`, `debug/configB_*`, `debug/configC_*`, `debug/original_B_*`, `debug/debugbin_*`
- Correctness logs: `debug/correct_V_*`, `debug/correct_KSS_*`, `debug/correct_W_*`, `debug/forced_*`
- Invariant logs: `debug/invariant_small_*`, `debug/invariant_full_*`
- Hashes: `debug/SOURCE_HASHES_FINAL.txt`
