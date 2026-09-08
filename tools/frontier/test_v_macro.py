#!/usr/bin/env python3
"""
Tests for V-pentacube Macro framework.

Phase 2 (orientation infrastructure) plus later-phase macro checks.
V-specific expectations are derived from docs/frontier/v_piece/v_source_survey.md
and data/frontier/v_piece/v_orientation_table.json — none are carried over
from S or T by assumption.

Run:
    python3 tools/frontier/test_v_macro.py
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter, deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.registry import PENTACUBES
from tools.frontier.piece_utils import (
    generate_orientations,
    get_orientation_table,
    get_orientation_set,
    build_templates,
    layer_mask,
    validate_placement_list,
)
from tools.frontier.macro_explorer import macro_closure


# ---------------------------------------------------------------------------
# Phase 2: orientation infrastructure
# ---------------------------------------------------------------------------

def test_v_orientation_count():
    """V has exactly 12 unique proper-rotation orientations."""
    oris = generate_orientations(PENTACUBES["V"])
    assert len(oris) == 12, f"Expected 12 orientations, got {len(oris)}"
    print(f"  PASS: V has {len(oris)} orientations")


def test_v_achiral():
    """Reflection closure must add nothing: mirror ⊂ proper-rotation orbit."""
    proper = get_orientation_set(PENTACUBES["V"])
    with_refl = get_orientation_set(PENTACUBES["V"], include_reflections=True)
    assert with_refl == proper, "V should be achiral (planar pentacube)"
    print("  PASS: V is achiral (reflections add no orientations)")


def test_v_rotation_closure():
    """All 24 rotations of any orientation must stay inside the 12-element set."""
    from common.rotmatrix import RM
    oris = generate_orientations(PENTACUBES["V"])
    seen = set()
    for o in oris:
        for rot in RM:
            rp = o @ rot.T
            rp = rp - rp.min(axis=0)
            seen.add(tuple(sorted(tuple(map(int, p)) for p in rp)))
    assert len(seen) == 12, f"Rotation closure should be 12, got {len(seen)}"
    print(f"  PASS: rotation closure = {len(seen)}")


def test_v_z_span_distribution():
    """V must have 4 flat and 8 z-span=3 orientations; no z-span=2."""
    zc = Counter(
        int(o[:, 2].max() - o[:, 2].min() + 1)
        for o in generate_orientations(PENTACUBES["V"])
    )
    assert zc[1] == 4 and zc[3] == 8 and 2 not in zc, f"Unexpected z-spans: {dict(zc)}"
    print(f"  PASS: z-span distribution {dict(zc)}")


def test_v_no_middle_heavy_profiles():
    """No standing V orientation may have its 3-cell layer in the middle.

    Geometric reason (survey §2): when one arm stands vertically the other arm
    lies entirely in the corner's layer, so the 3-cell layer always contains
    the corner and sits at a z-end. This is a genuine V/T distinction.
    """
    table = get_orientation_table(PENTACUBES["V"])
    middle_heavy = [k for k, v in table.items()
                    if v["z_span"] == 3 and v["layer_occ"][1] == 3]
    assert not middle_heavy, f"Middle-heavy profiles found: {middle_heavy}"
    profs = Counter(tuple(v["layer_occ"]) if v["z_span"] == 1 else tuple(v["layer_occ"][:3])
                    for v in table.values())
    expected = {(5, 0, 0): 4, (3, 1, 1): 4, (1, 1, 3): 4}
    assert dict(profs) == expected, f"Profile census mismatch: {dict(profs)}"
    print(f"  PASS: no [1,3,1] profiles; census = {dict(profs)}")


def test_v_standing_footprint_is_3_strip():
    """Every standing orientation occupies a full 3×1 or 1×3 footprint."""
    table = get_orientation_table(PENTACUBES["V"])
    for k, v in table.items():
        if v["z_span"] == 3:
            assert (v["x_span"], v["y_span"]) in {(3, 1), (1, 3)}, \
                f"{k} footprint {v['x_span']}x{v['y_span']}"
    print("  PASS: all standing footprints are 3×1/1×3 strips")


def test_v_orientation_table_json():
    """The committed orientation table must match a fresh recomputation."""
    path = REPO_ROOT / "data/frontier/v_piece/v_orientation_table.json"
    assert path.exists(), "v_orientation_table.json missing"
    doc = json.loads(path.read_text())
    fresh = get_orientation_table(PENTACUBES["V"])
    assert doc["orientation_count"] == len(fresh) == 12
    assert doc["chiral"] is False
    assert doc["z_span_distribution"] == {"1": 4, "3": 8}
    assert doc["middle_heavy_profiles_present"] is False
    for k, v in fresh.items():
        assert doc["orientations"][k]["cells"] == v["cells"], f"{k} cells drifted"
        assert doc["orientations"][k]["layer_occ"] == v["layer_occ"]
    print("  PASS: committed orientation table matches recomputation")


def test_v_template_building_3x5():
    """Template building works for V on the target first cross-section 3×5."""
    templates, NCELLS, WM, concrete_count, total_templates = build_templates(
        PENTACUBES["V"], 3, 5)
    assert NCELLS == 15
    assert concrete_count > 0 and total_templates > 0
    assert total_templates == 172, f"Expected 172 templates, got {total_templates}"
    print(f"  PASS: 3×5 templates: {concrete_count} placements, {total_templates} templates")


def test_v_templates_match_orientations():
    """Every packed template must decode to a genuine V orientation."""
    orientation_set = get_orientation_set(PENTACUBES["V"])
    templates, NCELLS, _, _, _ = build_templates(PENTACUBES["V"], 3, 5)
    invalid = 0
    for tlist in templates.values():
        for t in tlist:
            cells = []
            for layer in range(3):
                mask = layer_mask(t, layer, NCELLS)
                for cid in range(NCELLS):
                    if mask & (1 << cid):
                        cells.append((cid % 3, cid // 3, layer))
            arr = sorted(cells)
            mx, my, mz = (min(c[i] for c in arr) for i in range(3))
            canon = tuple(sorted((x - mx, y - my, z - mz) for x, y, z in arr))
            if canon not in orientation_set:
                invalid += 1
    assert invalid == 0, f"{invalid} invalid templates"
    print("  PASS: every 3×5 template decodes to a genuine V orientation")


def test_v_placement_validation_roundtrip():
    """validate_placement_list accepts a known-good V 5×5×6 tiling fragment
    structure check and rejects a corrupted one (bounds violation)."""
    # Minimal synthetic check on a single flat placement inside 3×5×1
    ok = validate_placement_list(
        [[(0, 0, 0), (1, 0, 0), (2, 0, 0), (0, 1, 0), (0, 2, 0)]],
        get_orientation_set(PENTACUBES["V"]), 3, 5, 1,
    )
    assert ok["invalid_shapes"] == 0 and ok["out_of_bounds"] == 0
    bad = validate_placement_list(
        [[(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 1, 0), (2, 2, 0)]],  # W shape!
        get_orientation_set(PENTACUBES["V"]), 3, 5, 1,
    )
    assert bad["invalid_shapes"] == 1, "W-shaped placement must be rejected"
    print("  PASS: placement validation accepts V and rejects non-V geometry")


# ---------------------------------------------------------------------------
# Phases 6-10: closure, period, gate structure, certificates
# ---------------------------------------------------------------------------

def _closure_3x5():
    return macro_closure("V", 3, 5, max_states=20_000_000, verbose=False)


def test_v_closure_3x5_complete_and_cyclic():
    """V 3×5 closure must complete and be cyclic."""
    macro_seen, succ, sources, stats = _closure_3x5()
    assert stats["zero_reachable"], "V 3×5 must be cyclic"
    assert not stats["first_gen_cap_hit"] and not stats["macro_cap_hit"]
    assert stats["macro_states"] == 4543, f"state count drifted: {stats['macro_states']}"
    assert stats["macro_edges"] == 5494
    assert len(sources) == 220
    print(f"  PASS: V 3×5 closure complete: {stats['macro_states']} states, "
          f"{stats['macro_edges']} edges")


def test_v_exact_achievable_set_matches_catalogue():
    """Exact walk lengths must equal {6,8} ∪ {even ≥ 12} up to the bound.

    This encodes the GLOBAL 3×5 classification: primes 6 and 8 achieved,
    odd impossible, 4 impossible, 10 impossible (published facts).
    """
    path = REPO_ROOT / "data/frontier/v_piece/v_3x5_exact_walk_lengths.json"
    d = json.loads(path.read_text())
    ach = set(d["achievable_lengths"])
    bound = d["bound"]
    expected = {z for z in range(bound + 1)
                if z % 2 == 0 and z >= 6 and z != 10}
    assert ach == expected, "achievable set deviates from {6,8}∪{even≥12}"
    cc = d["catalogue_cross_check"]
    assert cc["primes_6_and_8_achieved"]
    assert cc["published_impossible_4_absent"]
    assert cc["published_impossible_10_absent"]
    assert cc["no_odd_lengths"]
    print(f"  PASS: achievable set = {{6,8}} ∪ {{even ≥ 12}} up to {bound} "
          f"(matches published catalogue)")


def test_v_period_lt_shortest_cycle():
    """V must reproduce period(2) < shortest-cycle(6)."""
    d = json.loads((REPO_ROOT / "data/frontier/v_piece/v_3x5_closure_analysis.json").read_text())
    s0 = d["scc0"]
    assert s0["size"] == 243
    assert s0["period_bfs"] == 2 and s0["period_cycle_gcd"] == 2
    assert s0["primitive_lengths"] == [6, 8]
    assert s0["shortest_cycle"] == 6
    assert s0["period_lt_shortest_cycle"] is True
    print("  PASS: period 2 < shortest cycle 6; primitives [6,8]")


def test_v_mixed_gate_structure():
    """pred(0) must contain BOTH the classic gate and flat partial states."""
    d = json.loads((REPO_ROOT / "data/frontier/v_piece/v_3x5_closure_analysis.json").read_text())
    tp = d["terminal_predecessors"]
    assert tp["predecessor_count"] == 5
    assert tp["all_have_l1_l2_empty"]
    assert tp["any_is_classic_gate"], "classic gate must be present for V 3×5"
    partial = [r for r in tp["predecessors"] if not r["is_gate_FULL000"]]
    assert len(partial) == 4 and all(r["l0_popcount"] == 10 for r in partial)
    print("  PASS: mixed gate: 1 classic + 4 flat-completable partial preds")


def test_v_multiple_cyclic_islands():
    """V 3×5 must show 13 cyclic SCCs (1 main + 12 escape-basin six-cycles)."""
    d = json.loads((REPO_ROOT / "data/frontier/v_piece/v_3x5_closure_analysis.json").read_text())
    assert d["sccs"]["cyclic_count"] == 13
    assert d["sccs"]["sizes_top10"][0] == 243
    assert all(s == 6 for s in d["sccs"]["sizes_top10"][1:])
    print("  PASS: 13 cyclic SCCs: main 243 + twelve 6-cycles")


def test_v_cycle_certificates_layer_a_valid():
    """Both realized cycle certificates must pass the isolated generic checker."""
    import subprocess
    import tempfile
    checker = REPO_ROOT / "tools/frontier/macro_certificate_generic_checker.py"
    for name in ("v_3x5x6_macro_cycle_certificate.json",
                 "v_3x5x8_macro_cycle_certificate.json"):
        p = REPO_ROOT / "data/frontier/v_piece" / name
        assert p.exists(), f"{name} missing"
        r = subprocess.run(
            [sys.executable, "-I", str(checker), str(p)],
            capture_output=True, text=True, cwd=tempfile.gettempdir(),
        )
        assert r.returncode == 0, f"{name} failed Layer A:\n{r.stdout}"
        assert "INVALID" not in r.stdout
    print("  PASS: v_3x5x6 and v_3x5x8 certificates Layer-A VALID (isolated)")


def test_v_certificate_rejection_suite():
    """All mutation/overclaim negative controls must be rejected."""
    import subprocess
    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools/frontier/v_piece/test_v_certificate_rejection.py")],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"rejection suite failed:\n{r.stdout}"
    print("  PASS: 6 mutations/overclaims rejected, 2 positive controls pass")


# ---------------------------------------------------------------------------
# Later phases are appended below as they are completed.
# ---------------------------------------------------------------------------

def run_all_tests():
    tests = [
        ("V orientation count", test_v_orientation_count),
        ("V achirality", test_v_achiral),
        ("V rotation closure", test_v_rotation_closure),
        ("V z-span distribution", test_v_z_span_distribution),
        ("V no middle-heavy profiles", test_v_no_middle_heavy_profiles),
        ("V standing footprint strips", test_v_standing_footprint_is_3_strip),
        ("V orientation table JSON", test_v_orientation_table_json),
        ("V template building 3×5", test_v_template_building_3x5),
        ("V templates match orientations", test_v_templates_match_orientations),
        ("V placement validation roundtrip", test_v_placement_validation_roundtrip),
        ("V closure 3×5 complete+cyclic", test_v_closure_3x5_complete_and_cyclic),
        ("V exact achievable set = catalogue", test_v_exact_achievable_set_matches_catalogue),
        ("V period < shortest cycle", test_v_period_lt_shortest_cycle),
        ("V mixed gate structure", test_v_mixed_gate_structure),
        ("V multiple cyclic islands", test_v_multiple_cyclic_islands),
        ("V cycle certificates Layer-A valid", test_v_cycle_certificates_layer_a_valid),
        ("V certificate rejection suite", test_v_certificate_rejection_suite),
    ]
    passed = failed = 0
    print("V-Pentacube Macro Tests")
    print("=" * 50)
    print()
    for name, fn in tests:
        try:
            fn()
            print(f"  ✓ {name}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {name}: {e}")
            failed += 1
    print()
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    raise SystemExit(0 if success else 1)
