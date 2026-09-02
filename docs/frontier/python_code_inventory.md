# Untracked Python Code Inventory — `solvers/` and `tools/frontier/`

**Date:** 2026-09-03
**Scope:** Lightweight mechanical inventory of untracked `.py` files under `solvers/` and `tools/frontier/`. No files modified, deleted, renamed, moved, or committed. No `.gitignore` changes. No deep scientific-value assessment — only obvious categories and shortlists for later review.

**Method:** For each file, collected mechanically: path, line count, top-level classes, top-level functions, project-module imports, and whether the filename/module is referenced by any `docs/frontier/*.md` document (simple filename/path substring match).

---

## 1. Counts

### 1.1 By directory

| Directory | Count |
|---|---|
| `solvers/` | 45 |
| `tools/frontier/` | 62 |
| **Total** | **107** |

### 1.2 By category

| Category | Count |
|---|---|
| verifier / certificate tool | 31 |
| frontier analysis tool | 24 |
| solver implementation | 21 |
| one-off research script | 13 |
| test | 10 |
| wrapper / launcher | 4 |
| catalogue / decomposition tool | 3 |
| benchmark / experiment driver | 1 |
| unknown | 0 |
| **Total** | **107** |

### 1.3 By directory × category

| Category | `solvers/` | `tools/frontier/` |
|---|---|---|
| verifier / certificate | 17 | 14 |
| solver implementation | 15 | 6 |
| frontier analysis | 1 | 23 |
| one-off research | 9 | 4 |
| test | 0 | 10 |
| wrapper / launcher | 3 | 1 |
| catalogue / decomposition | 0 | 3 |
| benchmark / experiment | 0 | 1 |

### 1.4 Referenced by `docs/frontier/*.md`

| | Count |
|---|---|
| Referenced in docs | 66 |
| Not referenced in docs | 41 |

---

## 2. Compact Table

`path | lines | category | notable dependency/function | referenced by docs?`

| path | lines | category | notable dependency/function | docs? |
|---|---|---|---|---|
| `solvers/s_z_frontier_compact_pure.py` | 565 | frontier | rss_mb, cell_id, first_empty · `common.polycube_utils` | YES |
| `solvers/t_3x15_macro_feasibility.py` | 81 | oneoff | cell_id, layer_mask, first_empty · `common.polycube_utils` | YES |
| `solvers/v_5x5_bidirectional.py` | 394 | solver | explore_forward, find_predecessors, bidirectional_search · `solvers.v_5x5_macro` | no |
| `solvers/v_5x5_bidirectional_correct.py` | 291 | solver | explore_forward, find_predecessors_correct, bidirectional_search · `solvers.v_5x5_macro` | no |
| `solvers/v_5x5_bidirectional_simple.py` | 102 | wrapper | main · `solvers.v_5x5_macro` | no |
| `solvers/v_5x5_completion_pruning.py` | 297 | solver | count_bits, check_volume_divisibility, check_layer_capacity · `solvers.v_5x5_macro` | no |
| `solvers/v_5x5_depth9_paths.py` | 174 | oneoff | explore_to_shift, count_paths_depth_limited · `solvers.v_5x5_macro` | no |
| `solvers/v_5x5_forward_baseline.py` | 144 | solver | forward_search_baseline · `solvers.v_5x5_macro` | no |
| `solvers/v_5x5_forward_only.py` | 174 | solver | explore_to_shift · `solvers.v_5x5_macro` | YES |
| `solvers/v_5x5_full_reconstruction.py` | 330 | verifier | reconstruct_placements_from_path, find_transition_sequence · `solvers.v_5x5_macro` | YES |
| `solvers/v_5x5_macro.py` | 548 | solver | cell_id, layer_mask, first_empty · `common.polycube_utils` | YES |
| `solvers/v_5x5_path_counting.py` | 134 | oneoff | compute_forward_sets_with_counts · `solvers.v_5x5_macro` | YES |
| `solvers/v_5x5_predecessor_debug.py` | 260 | oneoff | explore_forward, find_all_paths_depth_6, dfs · `solvers.v_5x5_macro` | no |
| `solvers/v_5x5_predecessor_simple.py` | 197 | oneoff | explore_forward, find_first_n_paths, dfs · `solvers.v_5x5_macro` | no |
| `solvers/v_5x5_symmetry_reduction.py` | 344 | solver | reconstruct_placements_from_path, find_transition_sequence · `solvers.v_5x5_macro` | YES |
| `solvers/v_5x5_test_predecessor.py` | 80 | wrapper | main · `solvers.v_5x5_macro` | no |
| `solvers/v_5x5_tiling_reconstruction.py` | 185 | verifier | find_path_to_state, enumerate_all_paths, dfs · `solvers.v_5x5_macro` | no |
| `solvers/v_5x5x6_calibration.py` | 168 | oneoff | explore_to_shift, count_macro_paths_depth_6 · `solvers.v_5x5_macro` | no |
| `solvers/v_5x5x6_complete_analysis.py` | 315 | verifier | template_to_placements, find_path_to_successor, reconstruct_tiling · `solvers.v_5x5_macro` | no |
| `solvers/v_5x5x6_exclusion_validation.py` | 385 | verifier | canonicalize_tiling, get_box_symmetries_5x5x6, apply_symmetry · `solvers.v_5x5_macro` | no |
| `solvers/v_5x5x6_fast_check.py` | 257 | verifier | template_to_placements, find_path_to_successor, reconstruct_tiling · `solvers.v_5x5_macro` | no |
| `solvers/v_5x5x6_investigation.py` | 222 | oneoff | explore_to_shift_with_path, enumerate_macro_paths_depth_6, dfs · `solvers.v_5x5_macro` | no |
| `solvers/v_5x5x6_quick_check.py` | 103 | wrapper | main · `solvers.v_5x5x6_quick_diag` | no |
| `solvers/v_5x5x6_quick_diag.py` | 207 | verifier | template_to_placements, find_path_to_successor, reconstruct_tiling · `solvers.v_5x5_macro` | no |
| `solvers/v_5x5x6_sample_check.py` | 153 | oneoff | find_all_paths, dfs · `solvers.v_5x5_macro` | no |
| `solvers/v_5x5x6_symmetry_check.py` | 161 | verifier | apply_box_symmetry, normalize_box, canonicalize_under_symmetry · `solvers.v_5x5x6_quick_diag` | no |
| `solvers/v_5x5x6_verify.py` | 126 | verifier | verify_tiling · `solvers.v_5x5x6_quick_diag` | no |
| `solvers/v_5x5x9_complete_analysis.py` | 526 | verifier | parse_solution_file, verify_tiling, canonicalize | YES |
| `solvers/v_5x5x9_exhaustive_search.py` | 719 | solver | cell_id, layer_mask, first_empty · `common.polycube_utils` | YES |
| `solvers/v_5x5x9_george_reconciliation.py` | 293 | verifier | parse_solution_file, canonicalize, generate_v4_group | no |
| `solvers/v_5x5x9_orbit_analysis.py` | 282 | verifier | parse_solution_file, canonicalize_tiling, get_box_symmetries_5x5x9 | no |
| `solvers/v_5x5x9_quick_search.py` | 330 | solver | parse_solution_file, canonicalize_tiling, get_box_symmetries_5x5x9 · `solvers.v_5x5_macro` | YES |
| `solvers/v_5x5x9_rz_constrained_search.py` | 446 | solver | rz_transform, solve_exact_cover, solve_unrestricted · `common.rotmatrix` | no |
| `solvers/v_5x5x9_second_tiling_search.py` | 343 | solver | parse_solution_file, canonicalize_tiling, get_box_symmetries_5x5x9 · `solvers.v_5x5_macro` | no |
| `solvers/v_5x5x9_symmetry_audit.py` | 352 | verifier | parse_solution_file, canonicalize_tiling, verify_tiling | YES |
| `solvers/v_5x5x9_symmetry_audit_independent.py` | 470 | verifier | parse_solution_file, canonicalize, apply_transform · `common.polycube_utils` | no |
| `solvers/v_5x5x9_three_conventions.py` | 118 | verifier | load, can, group_v4 | YES |
| `solvers/v_5x5x9_v4_completeness.py` | 100 | verifier | parse_sols, apply_rot, verify | YES |
| `solvers/v_5x5x9_v4_diagnostic.py` | 95 | oneoff | parse_solution_file, canonicalize, apply_rot | YES |
| `solvers/w_5x7_macro.py` | 547 | solver | cell_id, layer_mask, first_empty · `common.polycube_utils` | YES |
| `solvers/w_5x7x9_certificate_validator.py` | 394 | verifier | canonicalize, verify_tiling, checksum | YES |
| `solvers/w_5x7x9_deviation_search.py` | 142 | solver | parse, can, ap · `common.polycube_utils` | YES |
| `solvers/w_5x7x9_sat_search.py` | 98 | solver | parse, can, gs · `common.polycube_utils` | YES |
| `solvers/w_5x7x9_second_orbit.py` | 151 | verifier | parse_solution, canonicalize, generate_box_symmetries | YES |
| `solvers/w_5x7x9_z3_search.py` | 135 | solver | parse, can, ap · `common.polycube_utils` | YES |
| `tools/frontier/analyze_4x4_4x7.py` | 264 | frontier | make_shifted_template_general, build_templates_general · `common.polycube_utils` | no |
| `tools/frontier/analyze_4x5_complete.py` | 509 | frontier | make_shifted_template_general, build_templates_general · `common.polycube_utils` | YES |
| `tools/frontier/analyze_4x6_complete.py` | 509 | frontier | make_shifted_template_general, build_templates_general · `common.polycube_utils` | YES |
| `tools/frontier/analyze_parallel_30m.py` | 134 | frontier | load_closure_data, find_129_walks, dfs · `tools.frontier.scc_aware_analysis` | no |
| `tools/frontier/benchmark_scaling.py` | 135 | benchmark | run_benchmark | no |
| `tools/frontier/characterize_4x5_scc.py` | 555 | frontier | load_graph, layer_mask, layer_masks_str · `common.polycube_utils` | no |
| `tools/frontier/check_macro_certificate_independent.py` | 213 | verifier | perm_sign, rotation_images, congruent | YES |
| `tools/frontier/compare_4x5_4x6_deep.py` | 426 | frontier | make_shifted_template_general, build_templates_general · `common.polycube_utils` | YES |
| `tools/frontier/compare_4x5_4x6_orientation.py` | 556 | frontier | make_shifted_template_general, build_templates_general · `common.polycube_utils` | YES |
| `tools/frontier/compare_area40_cycles.py` | 338 | frontier | s_orientation_id, analyze_cycle, transform_placement · `tools.frontier.macro_construction` | YES |
| `tools/frontier/convert_4x9_checkpoint.py` | 170 | oneoff | convert_checkpoint, verify_conversion | no |
| `tools/frontier/debug_4x5_scc.py` | 246 | oneoff | make_shifted_template_general, build_templates_general · `common.polycube_utils` | no |
| `tools/frontier/demo_macro_orientation.py` | 67 | wrapper | main · `tools.frontier.macro_orientation` | YES |
| `tools/frontier/extract_cycle_from_tiling.py` | 274 | frontier | parse_solution, extract_cycle, occupancy_of_layers · `tools.frontier.macro_generalized` | YES |
| `tools/frontier/macro_4x9_resume.py` | 300 | solver | signal_handler, build_templates, layer_mask · `common.polycube_utils` | no |
| `tools/frontier/macro_4x9_return_search.py` | 342 | solver | signal_handler, build_templates_general, layer_mask · `common.polycube_utils` | no |
| `tools/frontier/macro_4x9_structural.py` | 277 | frontier | build_templates, layer_mask, first_empty · `common.polycube_utils` | YES |
| `tools/frontier/macro_4x9_targeted.py` | 297 | solver | build_templates, layer_mask, first_empty · `common.polycube_utils` | YES |
| `tools/frontier/macro_certificate.py` | 331 | verifier | _generate_s_orientations, validate_placement_list, validate_certificate_file | YES |
| `tools/frontier/macro_certificate_generic_checker.py` | 310 | verifier | perm_sign, rotation_images, require | YES |
| `tools/frontier/macro_certify_box.py` | 157 | verifier | certify_box · `tools.frontier.extract_cycle_from_tiling` | YES |
| `tools/frontier/macro_closure_engine.py` | 815 | frontier | CompactStateSet, CompactSuccMap · `common.registry` | YES |
| `tools/frontier/macro_construction.py` | 820 | solver | load_cycle_data, get_generators, decompose_thickness · `tools.frontier.macro_generalized` | YES |
| `tools/frontier/macro_explorer.py` | 586 | frontier | save_checkpoint, load_checkpoint, signal_handler · `common.registry` | YES |
| `tools/frontier/macro_gate_search.py` | 149 | frontier | one_edge_successors, gate_search · `tools.frontier.macro_generalized` | YES |
| `tools/frontier/macro_invariant_search.py` | 185 | frontier | load_edges_from_file, load_edges_from_checkpoint, test_invariant · `tools.frontier.macro_generalized` | no |
| `tools/frontier/macro_local_period.py` | 230 | frontier | LocalPeriodAnalyzer · `tools.frontier.macro_generalized` | YES |
| `tools/frontier/macro_orientation.py` | 253 | frontier | MacroOrientation · `tools.frontier.macro_orientation` | YES |
| `tools/frontier/macro_preflight.py` | 177 | oneoff | estimate_tractability · `tools.frontier.macro_generalized` | YES |
| `tools/frontier/macro_scc_period.py` | 205 | frontier | compute_period_classic, compute_period_classes, collapse_deterministic | YES |
| `tools/frontier/macro_semigroup.py` | 226 | frontier | compute_semigroup, print_report | YES |
| `tools/frontier/macro_state_structure.py` | 99 | frontier | analyze, counts · `tools.frontier.macro_generalized` | no |
| `tools/frontier/piece_utils.py` | 420 | frontier | generate_orientations, get_orientation_table, build_templates · `common.polycube_utils` | YES |
| `tools/frontier/reconstruct_4x5x6_tiling.py` | 287 | verifier | make_shifted_template_general, build_templates_general · `common.polycube_utils` | no |
| `tools/frontier/reconstruct_4x6x5_tiling.py` | 348 | verifier | make_shifted_template_general, build_templates_general · `common.polycube_utils` | YES |
| `tools/frontier/solve_10x10x4.py` | 68 | solver | run_solver_inner · `common.polycube_utils` | YES |
| `tools/frontier/solve_box_numba.py` | 140 | solver | _run_solver, solve_box · `common.algorithm_x_numba` | no |
| `tools/frontier/t_piece/pack_t_5x5x12_walk.py` | 300 | verifier | require, perm_sign, rotation_images | YES |
| `tools/frontier/t_piece/t3xn_cyclicity.py` | 199 | frontier | flat_t_tileable, check_cyclicity · `common.registry` | YES |
| `tools/frontier/t_piece/t_macro_preflight.py` | 152 | oneoff | estimate_method · `common.registry` | YES |
| `tools/frontier/test_checkpoint_debug.py` | 119 | test | extract_metric | no |
| `tools/frontier/test_cycle_extraction.py` | 164 | test | test_extract_5x8x6, test_extract_5x6x4, test_extract_4x10x6 · `tools.frontier.extract_cycle_from_tiling` | YES |
| `tools/frontier/test_macro_construction.py` | 226 | test | test_representable_values, test_construct_and_validate · `tools.frontier.macro_construction` | YES |
| `tools/frontier/test_macro_orientation.py` | 267 | test | TestEnumerateOrientations, TestChooseOrientation · `tools.frontier.macro_orientation` | YES |
| `tools/frontier/test_macro_semigroup.py` | 113 | test | test_semigroup_4_29_46_47, test_semigroup_6 · `tools.frontier.macro_semigroup` | YES |
| `tools/frontier/test_parallel_checkpoint.py` | 155 | test | run_command, extract_metrics | no |
| `tools/frontier/test_t_macro.py` | 430 | test | test_orientation_count, test_macro_closure_3x7 · `common.registry` | YES |
| `tools/frontier/test_v_macro.py` | 321 | test | test_v_orientation_count, test_v_achiral · `common.registry` | YES |
| `tools/frontier/v_piece/analyze_v_closure.py` | 367 | frontier | reverse_graph, tarjan_sccs, scc_period · `tools.frontier.macro_explorer` | no |
| `tools/frontier/v_piece/test_v_certificate_rejection.py` | 115 | test | run_layer_a, run_claims, mutate | YES |
| `tools/frontier/v_piece/v_claim_verifier.py` | 194 | verifier | load_json, layer_b_gate_check, classify | YES |
| `tools/frontier/v_piece/v_exact_walk_lengths.py` | 134 | frontier | main · `tools.frontier.macro_explorer` | YES |
| `tools/frontier/v_piece/v_faithfulness_replay_5x5x6.py` | 236 | verifier | load_solutions, window_state, old_piece_cells · `common.registry` | YES |
| `tools/frontier/v_piece/v_witness_extraction.py` | 355 | verifier | part_a, window, realize_edge · `common.registry` | no |
| `tools/frontier/validate_t_macro_walk.py` | 254 | verifier | fill_successors, extract_walk, enc · `common.registry` | YES |
| `tools/frontier/verify_macro_proof.py` | 302 | verifier | verify_source_enumeration, verify_scc_period, verify_semigroup · `tools.frontier.macro_generalized` | YES |
| `tools/frontier/verify_tiling_identity.py` | 307 | verifier | make_shifted_template_general, build_templates_general · `common.polycube_utils` | YES |
| `tools/frontier/z_piece/build_promotion_doc.py` | 335 | catalogue | to_shape, leaves · `solvers.decomp` | YES |
| `tools/frontier/z_piece/build_promotion_patch.py` | 366 | catalogue | build_patched_text, scan_classes, section_count · `catalogues.base` | YES |
| `tools/frontier/z_piece/promotion_evidence.py` | 427 | catalogue | parse_page3d, _collect_leaves · `solvers.decomp` | YES |
| `tools/frontier/z_piece/test_z_frontier_closures.py` | 275 | test | TestTruthTablesUntouched, TestPageEvidenceTable · `solvers.decomp` | YES |
| `tools/frontier/z_piece/validate_proof_tree.py` | 74 | verifier | _dims, _cut_lengths, validate | YES |

---

## 3. Obvious Keep — substantial / reusable (strong commit candidates)

Core engines, shared libraries, and substantial analysis/verification tools (≥300 lines, or clearly reusable modules). These are the strongest candidates for committing.

| path | lines | category | why |
|---|---|---|---|
| `tools/frontier/macro_construction.py` | 820 | solver | construction engine (core) |
| `tools/frontier/macro_closure_engine.py` | 815 | frontier | closure engine, `CompactStateSet`/`CompactSuccMap` (core) |
| `solvers/v_5x5x9_exhaustive_search.py` | 719 | solver | exhaustive parallel search, `MacroCache` (core) |
| `tools/frontier/macro_explorer.py` | 586 | frontier | closure explorer (core) |
| `solvers/s_z_frontier_compact_pure.py` | 565 | frontier | frontier state machine + hash storage |
| `tools/frontier/compare_4x5_4x6_orientation.py` | 556 | frontier | orientation comparison |
| `tools/frontier/characterize_4x5_scc.py` | 555 | frontier | SCC characterization |
| `solvers/v_5x5_macro.py` | 548 | solver | macro graph engine — **imported by many v_5x5\* scripts** |
| `solvers/w_5x7_macro.py` | 547 | solver | macro graph engine for W |
| `solvers/v_5x5x9_complete_analysis.py` | 526 | verifier | complete V analysis |
| `tools/frontier/analyze_4x6_complete.py` | 509 | frontier | SCC analysis |
| `tools/frontier/analyze_4x5_complete.py` | 509 | frontier | SCC analysis |
| `solvers/v_5x5x9_symmetry_audit_independent.py` | 470 | verifier | independent symmetry audit |
| `solvers/v_5x5x9_rz_constrained_search.py` | 446 | solver | rz-constrained exact cover |
| `tools/frontier/piece_utils.py` | 420 | frontier | **shared piece utilities — imported by many tools** |
| `tools/frontier/compare_4x5_4x6_deep.py` | 426 | frontier | deep comparison |
| `tools/frontier/z_piece/promotion_evidence.py` | 427 | catalogue | promotion evidence |
| `solvers/w_5x7x9_certificate_validator.py` | 394 | verifier | certificate validator |
| `solvers/v_5x5_bidirectional.py` | 394 | solver | bidirectional search |
| `solvers/v_5x5x6_exclusion_validation.py` | 385 | verifier | orbit exclusion validation |
| `tools/frontier/v_piece/analyze_v_closure.py` | 367 | frontier | V closure analysis |
| `tools/frontier/z_piece/build_promotion_patch.py` | 366 | catalogue | promotion patch builder |
| `tools/frontier/v_piece/v_witness_extraction.py` | 355 | verifier | witness extraction |
| `solvers/v_5x5x9_symmetry_audit.py` | 352 | verifier | symmetry audit |
| `tools/frontier/reconstruct_4x6x5_tiling.py` | 348 | verifier | tiling reconstruction |
| `solvers/v_5x5_symmetry_reduction.py` | 344 | solver | symmetry-reduced search |
| `solvers/v_5x5x9_second_tiling_search.py` | 343 | solver | second tiling search |
| `tools/frontier/macro_4x9_return_search.py` | 342 | solver | resumable return search |
| `tools/frontier/compare_area40_cycles.py` | 338 | frontier | cycle comparison |
| `tools/frontier/z_piece/build_promotion_doc.py` | 335 | catalogue | promotion doc builder |
| `tools/frontier/macro_certificate.py` | 331 | verifier | certificate validation |
| `solvers/v_5x5x9_quick_search.py` | 330 | solver | quick search |
| `solvers/v_5x5_full_reconstruction.py` | 330 | verifier | full reconstruction |
| `solvers/v_5x5x6_complete_analysis.py` | 315 | verifier | complete V6 analysis |
| `tools/frontier/macro_certificate_generic_checker.py` | 310 | verifier | generic certificate checker |
| `tools/frontier/verify_tiling_identity.py` | 307 | verifier | tiling identity verifier |
| `tools/frontier/verify_macro_proof.py` | 302 | verifier | proof verifier |
| `tools/frontier/t_piece/pack_t_5x5x12_walk.py` | 300 | verifier | T walk pack verifier |
| `tools/frontier/macro_4x9_resume.py` | 300 | solver | resumable search |

## 4. Obvious Scratch — tiny wrappers / one-off scripts

Small files (<100 lines) that are thin wrappers, quick probes, or one-off diagnostics. **Note:** "one-off" does not mean worthless — these may still encode useful results, but they are not substantial reusable code.

| path | lines | category | why |
|---|---|---|---|
| `tools/frontier/demo_macro_orientation.py` | 67 | wrapper | demo wrapper |
| `tools/frontier/solve_10x10x4.py` | 68 | solver | tiny box solver |
| `tools/frontier/z_piece/validate_proof_tree.py` | 74 | verifier | tiny proof-tree helper |
| `solvers/v_5x5_test_predecessor.py` | 80 | wrapper | test wrapper |
| `solvers/t_3x15_macro_feasibility.py` | 81 | oneoff | feasibility probe |
| `solvers/v_5x5x9_v4_diagnostic.py` | 95 | oneoff | v4 diagnostic |
| `solvers/w_5x7x9_sat_search.py` | 98 | solver | tiny SAT search |
| `tools/frontier/macro_state_structure.py` | 99 | frontier | tiny state-structure probe |

## 5. Needs Review — everything else

The remaining files are substantial enough or ambiguous enough that they need deliberate review before deciding keep/commit/scratch. This is the bulk of the inventory. They are grouped by category for convenience.

### 5.1 Verifier / certificate tools (needs review)

| path | lines | docs? |
|---|---|---|
| `solvers/v_5x5x9_george_reconciliation.py` | 293 | no |
| `solvers/v_5x5x9_orbit_analysis.py` | 282 | no |
| `solvers/v_5x5x6_fast_check.py` | 257 | no |
| `solvers/v_5x5x6_quick_diag.py` | 207 | no |
| `solvers/v_5x5_tiling_reconstruction.py` | 185 | no |
| `solvers/v_5x5x6_symmetry_check.py` | 161 | no |
| `solvers/w_5x7x9_second_orbit.py` | 151 | YES |
| `solvers/v_5x5x6_verify.py` | 126 | no |
| `solvers/v_5x5x9_three_conventions.py` | 118 | YES |
| `solvers/v_5x5x9_v4_completeness.py` | 100 | YES |
| `tools/frontier/v_piece/v_faithfulness_replay_5x5x6.py` | 236 | YES |
| `tools/frontier/check_macro_certificate_independent.py` | 213 | YES |
| `tools/frontier/v_piece/v_claim_verifier.py` | 194 | YES |
| `tools/frontier/macro_certify_box.py` | 157 | YES |
| `tools/frontier/reconstruct_4x5x6_tiling.py` | 287 | no |
| `tools/frontier/validate_t_macro_walk.py` | 254 | YES |

### 5.2 Frontier analysis tools (needs review)

| path | lines | docs? |
|---|---|---|
| `tools/frontier/analyze_4x4_4x7.py` | 264 | no |
| `tools/frontier/macro_4x9_structural.py` | 277 | YES |
| `tools/frontier/extract_cycle_from_tiling.py` | 274 | YES |
| `tools/frontier/macro_orientation.py` | 253 | YES |
| `tools/frontier/macro_local_period.py` | 230 | YES |
| `tools/frontier/macro_semigroup.py` | 226 | YES |
| `tools/frontier/macro_scc_period.py` | 205 | YES |
| `tools/frontier/t_piece/t3xn_cyclicity.py` | 199 | YES |
| `tools/frontier/macro_invariant_search.py` | 185 | no |
| `tools/frontier/macro_gate_search.py` | 149 | YES |
| `tools/frontier/v_piece/v_exact_walk_lengths.py` | 134 | YES |
| `tools/frontier/analyze_parallel_30m.py` | 134 | no |

### 5.3 Solver implementations (needs review)

| path | lines | docs? |
|---|---|---|
| `solvers/v_5x5_bidirectional_correct.py` | 291 | no |
| `solvers/v_5x5_completion_pruning.py` | 297 | no |
| `solvers/v_5x5_forward_only.py` | 174 | YES |
| `solvers/v_5x5_forward_baseline.py` | 144 | no |
| `tools/frontier/macro_4x9_targeted.py` | 297 | YES |
| `tools/frontier/solve_box_numba.py` | 140 | no |
| `solvers/w_5x7x9_deviation_search.py` | 142 | YES |
| `solvers/w_5x7x9_z3_search.py` | 135 | YES |

### 5.4 One-off research scripts (needs review)

| path | lines | docs? |
|---|---|---|
| `solvers/v_5x5_predecessor_debug.py` | 260 | no |
| `solvers/v_5x5x6_investigation.py` | 222 | no |
| `solvers/v_5x5_predecessor_simple.py` | 197 | no |
| `solvers/v_5x5_depth9_paths.py` | 174 | no |
| `solvers/v_5x5x6_calibration.py` | 168 | no |
| `solvers/v_5x5x6_sample_check.py` | 153 | no |
| `solvers/v_5x5_path_counting.py` | 134 | YES |
| `tools/frontier/debug_4x5_scc.py` | 246 | no |
| `tools/frontier/macro_preflight.py` | 177 | YES |
| `tools/frontier/convert_4x9_checkpoint.py` | 170 | no |
| `tools/frontier/t_piece/t_macro_preflight.py` | 152 | YES |

### 5.5 Tests (needs review — likely keep)

| path | lines | docs? |
|---|---|---|
| `tools/frontier/test_t_macro.py` | 430 | YES |
| `tools/frontier/test_v_macro.py` | 321 | YES |
| `tools/frontier/test_macro_orientation.py` | 267 | YES |
| `tools/frontier/test_macro_construction.py` | 226 | YES |
| `tools/frontier/test_cycle_extraction.py` | 164 | YES |
| `tools/frontier/test_parallel_checkpoint.py` | 155 | no |
| `tools/frontier/test_checkpoint_debug.py` | 119 | no |
| `tools/frontier/v_piece/test_v_certificate_rejection.py` | 115 | YES |
| `tools/frontier/test_macro_semigroup.py` | 113 | YES |
| `tools/frontier/z_piece/test_z_frontier_closures.py` | 275 | YES |

### 5.6 Wrappers / benchmark (needs review)

| path | lines | category | docs? |
|---|---|---|---|
| `solvers/v_5x5_bidirectional_simple.py` | 102 | wrapper | no |
| `solvers/v_5x5x6_quick_check.py` | 103 | wrapper | no |
| `tools/frontier/benchmark_scaling.py` | 135 | benchmark | no |

---

## 6. Summary

- **107 untracked Python files** inventoried (45 `solvers/`, 62 `tools/frontier/`).
- **0 unknown** — every file mechanically classified into one of 8 categories.
- **Obvious keep:** ~40 substantial/reusable files (core engines, shared libraries, substantial verifiers/analyses).
- **Obvious scratch:** 8 tiny wrappers/one-offs (<100 lines).
- **Needs review:** the remaining ~59 files, grouped by category in §5.

**Caveats:**
- "One-off" does **not** mean worthless — one-off experiments may encode valuable results and should be reviewed, not discarded.
- The docs-reference column is a simple filename/path substring match against `docs/frontier/*.md`; it is a hint, not a completeness guarantee.
- No files were modified, deleted, renamed, moved, or committed. No `.gitignore` changes were made.