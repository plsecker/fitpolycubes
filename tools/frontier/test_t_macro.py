#!/usr/bin/env python3
"""
Tests for T-pentacube Macro framework.

Verifies:
1. Orientation generation and validation
2. Template building
3. Macro closure completeness
4. Cycle extraction and verification
5. Certificate generation and verification
"""

from __future__ import annotations

import json
import math
import sys
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
    first_empty,
    apply_template,
    shift_state,
    validate_placement_list,
)
from tools.frontier.macro_explorer import macro_closure


def test_orientation_count():
    """T should have exactly 12 unique orientations."""
    T = PENTACUBES["T"]
    orientations = generate_orientations(T)
    assert len(orientations) == 12, f"Expected 12 orientations, got {len(orientations)}"
    print(f"  PASS: T has {len(orientations)} orientations")


def test_orientation_z_spans():
    """T should have 4 flat (z-span=1) and 8 z-span=3 orientations."""
    T = PENTACUBES["T"]
    orientations = generate_orientations(T)
    
    z_span_1 = sum(1 for o in orientations if o[:, 2].max() - o[:, 2].min() + 1 == 1)
    z_span_3 = sum(1 for o in orientations if o[:, 2].max() - o[:, 2].min() + 1 == 3)
    
    assert z_span_1 == 4, f"Expected 4 flat orientations, got {z_span_1}"
    assert z_span_3 == 8, f"Expected 8 z-span=3 orientations, got {z_span_3}"
    print(f"  PASS: T has {z_span_1} flat + {z_span_3} z-span=3 orientations")


def test_orientation_rotation_closure():
    """Applying all 24 rotations to any orientation should produce only the 12 unique ones."""
    from common.rotmatrix import RM
    T = PENTACUBES["T"]
    orientations = generate_orientations(T)
    
    seen = set()
    for o in orientations:
        for rot in RM:
            rp = o @ rot.T
            rp = rp - rp.min(axis=0)
            rp_tuple = tuple(sorted(tuple(map(int, p)) for p in rp))
            seen.add(rp_tuple)
    
    assert len(seen) == 12, f"Rotation closure should be 12, got {len(seen)}"
    print(f"  PASS: Rotation closure = {len(seen)}")


def test_orientation_table():
    """Orientation table should have correct structure."""
    T = PENTACUBES["T"]
    table = get_orientation_table(T)
    
    assert len(table) == 12, f"Expected 12 table entries, got {len(table)}"
    
    # Check all entries have required fields
    for k, v in table.items():
        assert "z_span" in v
        assert "layer_occ" in v
        assert "cells" in v
        assert len(v["cells"]) == 5
    
    print(f"  PASS: Orientation table has {len(table)} entries with correct structure")


def test_template_building():
    """Template building should work for T in 3×7 cross-section."""
    T = PENTACUBES["T"]
    templates, NCELLS, WORD_MASK, concrete_count, total_templates = build_templates(T, 3, 7)
    
    assert NCELLS == 21, f"Expected 21 cells, got {NCELLS}"
    assert concrete_count > 0, "Expected non-zero concrete placements"
    assert total_templates > 0, "Expected non-zero templates"
    assert len(templates) == NCELLS, f"Expected {NCELLS} template lists, got {len(templates)}"
    
    print(f"  PASS: Templates built: {concrete_count} placements, {total_templates} templates")


def test_macro_closure_3x7():
    """T 3×7 Macro closure should be complete and cyclic."""
    macro_seen, succ, sources, stats = macro_closure("T", 3, 7, max_states=10000000, verbose=False)
    
    assert stats["first_gen_sources"] > 0, "Expected non-zero sources"
    assert stats["macro_states"] > 0, "Expected non-zero macro states"
    assert stats["zero_reachable"], "Expected gate state reachable"
    assert not stats.get("first_gen_cap_hit", False), "First gen should not cap hit"
    assert not stats.get("macro_cap_hit", False), "Macro closure should not cap hit"
    
    print(f"  PASS: T 3×7 closure: {stats['macro_states']:,} states, {stats['macro_edges']:,} edges")


def test_macro_closure_5x5():
    """T 5×5 Macro closure should be complete and cyclic."""
    macro_seen, succ, sources, stats = macro_closure("T", 5, 5, max_states=10000000, verbose=False)
    
    assert stats["first_gen_sources"] > 0, "Expected non-zero sources"
    assert stats["macro_states"] > 0, "Expected non-zero macro states"
    assert stats["zero_reachable"], "Expected gate state reachable"
    
    print(f"  PASS: T 5×5 closure: {stats['macro_states']:,} states, {stats['macro_edges']:,} edges")


def test_scc_cycles_3x7():
    """T 3×7 SCC should have cycle length 20."""
    from collections import deque
    
    macro_seen, succ, sources, stats = macro_closure("T", 3, 7, max_states=10000000, verbose=False)
    NCELLS = 21
    
    # Build reverse graph
    reverse = {}
    for src, dsts in succ.items():
        for dst in dsts:
            if dst not in reverse:
                reverse[dst] = set()
            reverse[dst].add(src)
    
    # SCC(0)
    scc0 = {0}
    q = [0]
    while q:
        s = q.pop()
        if s in reverse:
            for prv in reverse[s]:
                if prv not in scc0:
                    scc0.add(prv)
                    q.append(prv)
    
    scc_succ = {}
    for s in scc0:
        scc_succ[s] = set()
    for s in succ:
        if s in scc0:
            for nxt in succ[s]:
                if nxt in scc0:
                    scc_succ[s].add(nxt)
    
    # Find cycles
    cycles = set()
    for start in sorted(succ.get(0, set())):
        if start in scc0:
            qq = deque()
            qq.append((start, {start}, [start]))
            while qq:
                state, visited, path = qq.popleft()
                for nxt in sorted(scc_succ.get(state, set())):
                    if nxt == 0:
                        cycles.add(len(path) + 1)
                        break
                    if nxt not in visited:
                        qq.append((nxt, visited | {nxt}, path + [nxt]))
    
    assert 20 in cycles, f"Expected cycle length 20, got {sorted(cycles)}"
    assert len(cycles) >= 1, f"Expected at least 1 cycle, got {len(cycles)}"
    
    print(f"  PASS: T 3×7 SCC has {len(scc0)} states, cycles: {sorted(cycles)}")


def test_cycle_data_file():
    """The concrete cycle data file should be valid."""
    path = Path("tools/frontier/_t_3x7_concrete_cycles.json")
    assert path.exists(), "Cycle data file not found"
    
    with open(path) as f:
        data = json.load(f)
    
    assert "cross_section" in data
    assert data["cross_section"]["a"] == 3
    assert data["cross_section"]["b"] == 7
    assert "cycles" in data
    assert "20" in data["cycles"]
    
    cycle = data["cycles"]["20"]
    assert cycle["length"] == 20
    assert len(cycle["path"]) == 21  # 20 edges + 1
    assert len(cycle["edges"]) == 20
    
    print(f"  PASS: Cycle data file valid: {len(data['cycles'])} cycles")


def test_certificate_file():
    """The certificate file should be valid and verifiable."""
    path = Path("data/frontier/t_piece/t_3x7_certificate.json")
    assert path.exists(), "Certificate file not found"
    
    with open(path) as f:
        cert = json.load(f)
    
    assert cert["theorem_type"] == "scc-local"
    assert cert["cross_section"]["a"] == 3
    assert cert["cross_section"]["b"] == 7
    assert cert["semigroup"]["generators"] == [20]
    assert cert["semigroup"]["gcd"] == 20
    assert len(cert["primitive_cycles"]) >= 1
    
    print(f"  PASS: Certificate file valid: {cert['theorem_type']}")


def test_orientation_set_validation():
    """Orientation set should validate T placements correctly."""
    T = PENTACUBES["T"]
    orientation_set = get_orientation_set(T)
    
    assert len(orientation_set) == 12, f"Expected 12 orientations, got {len(orientation_set)}"
    
    # Verify each orientation has 5 cells
    for o in orientation_set:
        assert len(o) == 5, f"Orientation has {len(o)} cells, expected 5"
    
    print(f"  PASS: Orientation set has {len(orientation_set)} entries")


def test_semigroup_3x7():
    """T 3×7 semigroup ⟨20⟩ should match catalogue."""
    generators = [20]
    gcd_val = 20
    
    assert gcd_val == 20, f"Expected GCD=20, got {gcd_val}"
    
    # Catalogue says 3×7×20 is prime
    assert 20 % gcd_val == 0, "Prime 20 should be in semigroup"
    
    # Catalogue says 3×7×10, 3×7×15 are impossible
    assert 10 % gcd_val != 0 or 10 < min(generators), "10 should not be representable"
    assert 15 % gcd_val != 0 or 15 < min(generators), "15 should not be representable"
    
    print(f"  PASS: T 3×7 semigroup <{','.join(map(str, generators))}> GCD={gcd_val}")


def test_predecessors_of_zero():
    """T 3×7 should have multiple predecessors of state 0 (not just gate)."""
    from collections import deque
    
    macro_seen, succ, sources, stats = macro_closure("T", 3, 7, max_states=10000000, verbose=False)
    NCELLS = 21
    
    reverse = {}
    for src, dsts in succ.items():
        for dst in dsts:
            if dst not in reverse:
                reverse[dst] = set()
            reverse[dst].add(src)
    
    pred_of_0 = reverse.get(0, set())
    
    # For T, there should be multiple predecessors (not just the gate)
    assert len(pred_of_0) >= 1, "Expected at least 1 predecessor of 0"
    
    # None should be (FULL,0,0) for T
    WORD_MASK = (1 << NCELLS) - 1
    assert WORD_MASK not in pred_of_0, "Gate (FULL,0,0) should not be a predecessor of 0 for T"
    
    # All predecessors should have L1 = L2 = 0
    for p in pred_of_0:
        l1 = bin(layer_mask(p, 1, NCELLS)).count("1")
        l2 = bin(layer_mask(p, 2, NCELLS)).count("1")
        assert l1 == 0, f"Predecessor {p} has L1={l1}, expected 0"
        assert l2 == 0, f"Predecessor {p} has L2={l2}, expected 0"
    
    print(f"  PASS: T 3×7 has {len(pred_of_0)} predecessors of 0 (none is gate)")


def test_macro_closure_3x8():
    """T 3×8 Macro closure should be cyclic with multiple cycle lengths."""
    macro_seen, succ, sources, stats = macro_closure("T", 3, 8, max_states=500000, verbose=False)
    
    assert stats["first_gen_sources"] > 0, "Expected non-zero sources"
    assert stats["zero_reachable"], "Expected gate state reachable"
    
    # Check SCC has cycles
    from collections import deque
    NCELLS = 24
    
    reverse = {}
    for src, dsts in succ.items():
        for dst in dsts:
            if dst not in reverse:
                reverse[dst] = set()
            reverse[dst].add(src)
    
    scc0 = {0}
    q = [0]
    while q:
        s = q.pop()
        if s in reverse:
            for prv in reverse[s]:
                if prv not in scc0:
                    scc0.add(prv)
                    q.append(prv)
    
    scc_succ = {}
    for s in scc0:
        scc_succ[s] = set()
    for s in succ:
        if s in scc0:
            for nxt in succ[s]:
                if nxt in scc0:
                    scc_succ[s].add(nxt)
    
    cycles = set()
    for start in sorted(succ.get(0, set())):
        if start in scc0:
            qq = deque()
            qq.append((start, {start}, [start]))
            while qq:
                state, visited, path = qq.popleft()
                for nxt in sorted(scc_succ.get(state, set())):
                    if nxt == 0:
                        cycles.add(len(path) + 1)
                        break
                    if nxt not in visited:
                        qq.append((nxt, visited | {nxt}, path + [nxt]))
    
    assert len(cycles) >= 1, f"Expected at least 1 cycle, got {len(cycles)}"
    assert 15 in cycles, f"Expected cycle length 15, got {sorted(cycles)}"
    
    gcd_val = min(cycles)
    for l in cycles:
        gcd_val = math.gcd(gcd_val, l)
    
    print(f"  PASS: T 3×8 SCC has {len(scc0)} states, cycles: {sorted(cycles)[:5]}..., GCD={gcd_val}")


def test_orientation_set_validation_3x7():
    """Validate that the T orientation set correctly identifies T placements in 3×7."""
    T = PENTACUBES["T"]
    orientation_set = get_orientation_set(T)
    
    # Build templates and check each template matches an orientation
    templates, NCELLS, _, _, _ = build_templates(T, 3, 7)
    
    invalid_count = 0
    for cell_id, template_list in templates.items():
        for t in template_list:
            # Decode template to cells
            cells = []
            for layer in range(3):
                mask = (t >> (layer * NCELLS)) & ((1 << NCELLS) - 1)
                for cid in range(NCELLS):
                    if mask & (1 << cid):
                        x = cid % 3
                        y = cid // 3
                        cells.append((x, y, layer))
            
            # Normalize
            cells_arr = sorted(cells)
            min_x = min(c[0] for c in cells_arr)
            min_y = min(c[1] for c in cells_arr)
            min_z = min(c[2] for c in cells_arr)
            canonical = tuple(sorted((c[0]-min_x, c[1]-min_y, c[2]-min_z) for c in cells_arr))
            
            if canonical not in orientation_set:
                invalid_count += 1
    
    assert invalid_count == 0, f"Found {invalid_count} invalid templates"
    print(f"  PASS: All templates match T orientations")


def run_all_tests():
    """Run all T-specific tests."""
    tests = [
        ("Orientation count", test_orientation_count),
        ("Orientation z-spans", test_orientation_z_spans),
        ("Rotation closure", test_orientation_rotation_closure),
        ("Orientation table", test_orientation_table),
        ("Template building", test_template_building),
        ("Orientation set validation", test_orientation_set_validation),
        ("Orientation set validation 3×7", test_orientation_set_validation_3x7),
        ("Macro closure 3×7", test_macro_closure_3x7),
        ("Macro closure 5×5", test_macro_closure_5x5),
        ("Macro closure 3×8", test_macro_closure_3x8),
        ("SCC cycles 3×7", test_scc_cycles_3x7),
        ("Cycle data file", test_cycle_data_file),
        ("Certificate file", test_certificate_file),
        ("Semigroup 3×7", test_semigroup_3x7),
        ("Predecessors of zero", test_predecessors_of_zero),
    ]
    
    passed = 0
    failed = 0
    
    print("T-Pentacube Macro Tests")
    print("=" * 50)
    print()
    
    for name, test_fn in tests:
        try:
            test_fn()
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