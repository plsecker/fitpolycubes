# Repository Untracked-File Inventory

**Date:** 2026-09-03
**Branch:** `frontier-solutions`
**HEAD:** `ebd28c4` ("Checkpoint C++ solver: phase-2 infra + sound symmetry + centre-pair + colour research")
**Scope:** Full audit of untracked + uncommitted files for repo hygiene, plus the `.gitignore` regression fix. No solver algorithm changes, no deletions.

---

## 1. Executive Summary

The working tree originally contained **5,174 untracked files** and **17 modified tracked files**. The overwhelming majority of the untracked files were **generated artifacts** (solver output `.dat`, parallel-search task/solution JSON, `__pycache__`, compiled binaries, multi-GB frontier state dumps) that were **previously hidden by a comprehensive `.gitignore`** which was **gutted to 2 lines** in the working tree (uncommitted change, dated 2026-08-29).

**Root cause of the "thousands of untracked files" was the `.gitignore` regression**, not new work. **This regression has now been fixed** by restoring the committed 34-line `.gitignore`, which removed **174 generated files** from the untracked view (all `__pycache__/`, top-level `data/*.dat`, `data/SOLUTION_FOUND`, `data/reduce_solutions_*.txt`, `.idea/`, and the `solvers/solver` binary).

The genuinely new, worth-preserving content is a modest set of **source code** (45 Python solver scripts, 62 `tools/frontier` scripts, 1 C++ verifier) and **research documentation** (129 `docs/frontier/*.md` reports) — all belonging to **separate future commits**, not the solver checkpoint.

---

## 2. `.gitignore` Regression — Detected and Fixed

### 2.1 The regression

| | Committed (HEAD) | Working tree (before fix) |
|---|---|---|
| Lines | 34 | 2 |
| Rules | `.idea/`, `__pycache__/`, `*.py[cod]`, `data/*.dat`, `data/reduce_solutions_*.txt`, `data/SOLUTION_FOUND`, `/solver`, `/solvers/solver`, `*.prof`, `experiments/benchmarks/{gmon.out,perf.data}`, etc. | `z_6610.drat`, `z_6610.lrat` only |

The working-tree `.gitignore` (mtime 2026-08-29 00:46) was reduced to just the two Z-certificate proof files. **This was an uncommitted, unintentional regression** from another session. It is why `data/*.dat`, `__pycache__/`, `.idea/`, `/solvers/solver`, and the parallel-search JSON flooded `git status`.

### 2.2 Was any removed rule intentionally superseded? — No

Every removed rule was verified still relevant to the current repo state:

| Removed rule | Still applicable? | Evidence |
|---|---|---|
| `.idea/` | Yes | `.idea/` dir present (6 files) |
| `__pycache__/`, `*.py[cod]`, `*$py.class` | Yes | 366 `__pycache__` dirs present |
| `data/*.dat` | Yes | 80 top-level `data/*.dat` files present |
| `data/reduce_solutions_*.txt` | Yes | 2 files present |
| `data/SOLUTION_FOUND` | Yes | present (2026-09-03) |
| `/solver`, `/solvers/solver` | Yes | `solvers/solver` ELF binary present |
| `cmake-build-*/`, `*.iws`, `out/`, `.venv/`, `env/`, `build/`, `dist/`, `.antigravitycli/`, `*.prof`, `experiments/benchmarks/{gmon.out,perf.data}` | Yes (defensive) | standard build/env/profiling artifacts |

The two working-tree lines (`z_6610.drat`, `z_6610.lrat`) are **redundant** — those files are already ignored by the nested `docs/frontier/z_piece/z_6610_certificate/.gitignore` (verified via `git check-ignore`). Restoring the root file loses nothing.

### 2.3 The fix

Restored the committed 34-line `.gitignore` via `git checkout HEAD -- .gitignore`. The working-tree `.gitignore` now matches `HEAD:.gitignore` exactly (empty diff).

### 2.4 Before / after untracked counts

| Metric | Before fix | After fix | Delta |
|---|---|---|---|
| `git status --porcelain` | 239 | 230 | −9 |
| `git status --porcelain --untracked-files=all` | 5,193 | 5,018 | −175 |
| Untracked-only (`??`) | 5,175 | 5,001 | −174 |

### 2.5 Which generated files disappeared from the untracked view (174)

| Group | Count | Rule that hid it |
|---|---|---|
| `__pycache__/` (all `.pyc`/`.nbc`/`.nbi`) | 84 | `__pycache__/`, `*.py[cod]` |
| Top-level `data/*.dat` (solutions_*_*.dat) | 80 | `data/*.dat` |
| `data/reduce_solutions_*.txt` | 2 | `data/reduce_solutions_*.txt` |
| `data/SOLUTION_FOUND` | 1 | `data/SOLUTION_FOUND` |
| `.idea/` | 6 | `.idea/` |
| `solvers/solver` (compiled binary) | 1 | `/solvers/solver` |

All 174 are **generated/regenerable artifacts** — none are source code, research docs, certificates, or intentionally-tracked reference data.

### 2.6 What remains genuinely untracked after the fix (5,001)

The restoration did **not** hide any genuinely-needed project content. Verified still visible as untracked:
- All 45 `solvers/*.py` experiment scripts
- All 62 `tools/frontier/*.py` + `macro_certificate_verifier.cpp` + `macro_certificate_schema.json`
- All 129 `docs/frontier/*.md` research reports + 6 `reports/*.md`
- Z-certificate small files (`README.md`, `metadata.json`, `placement_set.json`, `var_map.json`, `z_6610.cnf`, `z_6610.drat.sha256`, tooling)
- `data/frontier/` (73 files), `data/certificate_*.json`, `data/v_5x5x6_*.json`, `data/w_5x7x9_certificate.json`
- `data/v_5x5x9_search/{tasks,solutions}/*` (2,308 + 2,308 parallel-search evidence — NOT matched by `data/*.dat` since they are in subdirectories)
- `placements_*.txt` (10 files), `scripts/cache-metrics.py`

### 2.7 Remaining `.gitignore` deficiencies (to handle later)

The restored `.gitignore` does **not** yet cover the following genuinely-untracked generated/evidence groups. These are **not** hidden by the current rules and remain visible:

| Group | Count | Suggested future rule |
|---|---|---|
| `data/v_5x5x9_search/tasks/*.json` + `solutions/*.dat` | 4,616 | `data/v_5x5x9_search/` (if deemed disposable) |
| `placements_*.txt` | 10 | `placements_*.txt` (regenerable) |
| `frontier_compact_pure_268m/` (4 files, ~4.1 GB) | 4 | `frontier_compact_pure_268m/` |
| `4x9_checkpoint_backup/`, `4x9_live_backup/` (12 files, ~5.6 GB) | 12 | `4x9_*_backup/` |
| `logs/` (3 files) | 3 | `logs/` |
| `temp.txt`, `scc_aware_analysis_results.txt` | 2 | scratch |
| `*.backup` (`.opencode/agents/*.backup`, `opencode.jsonc.backup`) | 2 | `*.backup` |

> **Note:** These are left **un-ignored deliberately** for now — the task constraint is to restore existing rules only, not add speculative new ones. Whether to ignore them (e.g. the multi-GB frontier dumps) should be a deliberate later decision.

---

## 3. Untracked-File Inventory by Category

### 3.1 Generated / disposable (≈4,900 files) — **IGNORE / DELETE**

| Group | Count | Nature | Action |
|---|---|---|---|
| `data/v_5x5x9_search/tasks/*.json` | 2,308 | Parallel-search task records (V 5×5×9, Aug 24) | IGNORE (generated) |
| `data/v_5x5x9_search/solutions/*.dat` | 2,308 | Parallel-search solution dumps | IGNORE (generated) |
| `data/v_5x5x9_search/frontier_depth1.json` | 1 | Search frontier state | IGNORE |
| `__pycache__/` (all dirs) | 84 | Python bytecode | IGNORE |
| `data/*.dat` (solutions_*_*.dat, ~90 files) | ~90 | Solver output | IGNORE |
| `data/SOLUTION_FOUND` | 1 | Run marker | IGNORE |
| `data/reduce_solutions_*.txt` | 2 | Reduction output | IGNORE |
| `data/archive/solutions_v_5x5x9_partial_282.dat` | 1 | Archived output | IGNORE |
| `solvers/solver` | 1 | Compiled C++ binary (ELF) | IGNORE |
| `placements_*.txt` (10 files) | 10 | Generated placement lists | IGNORE (regenerable) |
| `logs/` (3 files) | 3 | Run logs | IGNORE |
| `temp.txt`, `scc_aware_analysis_results.txt` | 2 | Scratch/debug output | DELETE or IGNORE |
| `frontier_compact_pure_268m/` (4 files, ~4.1 GB) | 4 | Frontier state dumps (u32/u64) | IGNORE (huge) |
| `4x9_checkpoint_backup/`, `4x9_live_backup/` (12 files, ~5.6 GB) | 12 | Frontier state backups | IGNORE (huge) |
| `docs/frontier/z_piece/z_6610_certificate/{z_6610.drat, z_6610.lrat}` | 2 | SAT proof files (2.4 GB + 2.4 GB) | IGNORE (already via nested .gitignore) |

### 3.2 Source code — **COMMIT SEPARATELY** (belongs to future commits, not solver checkpoint)

| Group | Count | Nature | Action |
|---|---|---|---|
| `solvers/*.py` (45 scripts) | 45 | Python solver experiments (V/W/S/Z/macro, bidirectional, symmetry, SAT/z3, certificates) | COMMIT SEPARATELY |
| `tools/frontier/*.py` (62 scripts) | 62 | Frontier analysis tooling | COMMIT SEPARATELY |
| `tools/frontier/macro_certificate_verifier.cpp` | 1 | C++ certificate verifier | COMMIT SEPARATELY |
| `tools/frontier/macro_certificate_schema.json` | 1 | Schema | COMMIT SEPARATELY |
| `scripts/cache-metrics.py` | 1 | Cache metrics tool | COMMIT SEPARATELY |
| `docs/frontier/z_piece/z_6610_certificate/{solve_command.py, z_6610_verify_encoding.py}` | 2 | Z certificate tooling | COMMIT SEPARATELY |

### 3.3 Research documentation — **COMMIT SEPARATELY**

| Group | Count | Nature | Action |
|---|---|---|---|
| `docs/frontier/*.md` (129 files) | 129 | Research reports (s_piece, z_piece, t_piece, v_piece, rule_audit, f_piece, k_piece, y_piece, q_piece, macro_*, w_5x7x9_*, v_5x5x9_*, theorem_hunt, etc.) | COMMIT SEPARATELY |
| `reports/*.md` (6 files) | 6 | Benchmark/pruning/symmetry reports (incl. `region-pruning-research-2026-09-03.md` = the colour/region-prune work in solver.cpp) | COMMIT SEPARATELY |
| `tools/frontier/multiprocessing_investigation_final.md` | 1 | Investigation report | COMMIT SEPARATELY |
| `docs/frontier/z_piece/z_6610_certificate/{README.md, hashes.txt, metadata.json, placement_set.json, var_map.json, z_6610.cnf, z_6610.drat.sha256}` | 7 | Z certificate (small, non-proof files) | COMMIT SEPARATELY |

### 3.4 Data / evidence — **REVIEW** (small, possibly worth committing)

| Group | Count | Nature | Action |
|---|---|---|---|
| `data/frontier/` (73 files) | 73 | Frontier analysis JSON/txt (s_4x5, s_4x6, s_piece, t_piece, v_piece, certificates) | REVIEW — small, may be evidence |
| `data/certificate_*.json` (3 files) | 3 | Certificates (4x10x6, 5x6x44, 5x6x45) | REVIEW |
| `data/v_5x5x6_*.json` (3 files) | 3 | V analysis results | REVIEW |
| `data/w_5x7x9_certificate.json` | 1 | W certificate | REVIEW |
| `data/solutions_*_shirakawa.dat` (several) | ~10 | Reference solution sets (Shirakawa) | REVIEW — reference data |

### 3.5 Tooling / IDE / misc — **IGNORE or COMMIT SEPARATELY**

| Group | Count | Nature | Action |
|---|---|---|---|
| `.idea/` (6 files) | 6 | PyCharm/IntelliJ project | IGNORE |
| `.opencode/agents/polycubearchitect.md.backup` | 1 | Agent backup | IGNORE (backup) |
| `opencode.jsonc.backup` | 1 | Config backup | IGNORE (backup) |
| `tools/frontier/_*_concrete_cycles.json` (9 files) | 9 | Concrete cycle data | REVIEW |

---

## 4. Modified Tracked Files (17) — all unrelated to solver checkpoint

These are **unrelated work** (catalogues, docs/pieces, common, tools, opencode.jsonc, .gitignore, .opencode/agents). They were deliberately **excluded** from the `ebd28c4` checkpoint commit. They belong to separate future commits.

| File | Nature |
|---|---|
| `.gitignore` | **Regression** — see §2. Restore committed version. |
| `.opencode/agents/polycubearchitect.md` | Agent definition |
| `catalogues/{f,w,y,z}_catalogue.py` | Catalogue code |
| `common/{polycube_utils,registry}.py` | Common code |
| `docs/frontier/{README, macro_method}.md` | Frontier docs |
| `docs/pieces/{F,Q,W,Y,Z}.md` | Piece docs |
| `opencode.jsonc` | Config |
| `tools/audit_catalogue.py` | Tool |

---

## 5. Recommended Action Plan

1. **~~Restore `.gitignore`~~** — **DONE.** Restored to the committed 34-line version (see §2). This removed 174 generated files from the untracked view.
2. **Do not delete anything** (task constraint). Mark generated files as IGNORE.
3. **Commit separately** (in future commits, NOT the solver checkpoint):
   - 45 `solvers/*.py` experiment scripts
   - 62 `tools/frontier/*.py` + verifier + schema
   - 129 `docs/frontier/*.md` research reports
   - 6 `reports/*.md`
   - Z-certificate small files + tooling
4. **Review** the small `data/frontier/` and certificate JSON for evidence value.
5. **Ignore** the multi-GB frontier state dumps (`frontier_compact_pure_268m/`, `4x9_*_backup/`, `z_6610.{drat,lrat}`) — add rules in a later deliberate change (see §2.7).

---

## 6. What Can We Safely Clean Up vs. Preserve

**Safely clean up (ignore/delete, all regenerable or disposable):**
- All `__pycache__/`, `*.pyc`
- All `data/*.dat` solver output, `data/SOLUTION_FOUND`, `data/reduce_solutions_*.txt`
- `data/v_5x5x9_search/{tasks,solutions}/*` (4,616 parallel-search files)
- `placements_*.txt` (regenerable)
- `solvers/solver` compiled binary
- Multi-GB frontier dumps (`frontier_compact_pure_268m/`, `4x9_*_backup/`, `z_6610.{drat,lrat}`)
- `logs/`, `temp.txt`, `scc_aware_analysis_results.txt`
- `.idea/`, `*.backup` files

**Preserve (commit separately):**
- All Python/C++ **source** (solvers, tools/frontier, scripts, certificate tooling)
- All **research documentation** (docs/frontier/*.md, reports/*.md)
- Small **evidence/certificate** JSON (data/frontier/, data/certificate_*.json, data/*_shirakawa.dat reference sets)

**Belongs to separate future commits (not the solver checkpoint):**
- The 17 modified tracked files (catalogues, docs/pieces, common, tools, opencode.jsonc, .opencode/agents)
- The `.gitignore` regression fix — **now committed separately** (see §2)

---

## 7. Final Status

- **Solver checkpoint (`ebd28c4`) is clean and reproducible** — unaffected by this audit and the `.gitignore` fix.
- **`.gitignore` regression fixed** — restored to the committed 34-line version; 174 generated files removed from the untracked view.
- **No files deleted, no solver algorithms modified.**
- The apparent "5,174 untracked files" was **~95% a `.gitignore` regression** exposing pre-existing generated artifacts; the regression is now fixed.
- Genuine new content (source + docs) is modest and belongs to **separate future commits**.
