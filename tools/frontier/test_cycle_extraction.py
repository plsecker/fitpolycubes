#!/usr/bin/env python3
"""
Regression tests for macro cycle extraction from physical tilings.

Covers:
1. pieces spanning multiple layers;
2. pure-shift final edges;
3. edge-relative z coordinates;
4. repeated cycles;
5. exact state transitions;
6. exact physical coverage.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from tools.frontier.extract_cycle_from_tiling import (
    extract_cycle,
    parse_solution,
)
from tools.frontier.macro_construction import (
    load_cycle_data,
    construct_tiling,
    validate_construction,
    get_generators,
)


def test_extract_5x8x6():
    """Extract the 5×8×6 cycle and verify structure."""
    placements = parse_solution("data/solutions_s_5x8x6.dat")
    result = extract_cycle(5, 8, 6, placements)

    assert result["length"] == 6
    assert result["states"][0] == 0
    assert result["states"][-1] == 0
    assert result["gate_index"] is not None
    assert len(result["edges"]) == 6

    # Verify edge structure: pure-shift last edge, others have pieces
    for i, e in enumerate(result["edges"]):
        if i < 5:
            assert e["piece_count"] > 0, f"edge {i} has no pieces"
        else:
            assert e["piece_count"] == 0, f"last edge should be pure shift"

    # Verify all pieces sum to 48
    total_pieces = sum(e["piece_count"] for e in result["edges"])
    assert total_pieces == 48

    print("  PASS: 5×8×6 extraction (6 edges, gate at",
          result["gate_index"], ", 48 pieces)")


def test_extract_5x6x4():
    """Extract the 5×6×4 cycle."""
    placements = parse_solution("data/solutions_s_5x6x4.dat")
    result = extract_cycle(5, 6, 4, placements)

    assert result["length"] == 4
    assert result["states"][0] == 0
    assert result["states"][-1] == 0
    assert result["gate_index"] is not None
    total_pieces = sum(e["piece_count"] for e in result["edges"])
    assert total_pieces == 24

    print("  PASS: 5×6×4 extraction (4 edges, gate at",
          result["gate_index"], ", 24 pieces)")


def test_extract_4x10x6():
    """Extract the 4×10×6 cycle (new discovery)."""
    placements = parse_solution("data/solutions_s_4x10x6.dat")
    result = extract_cycle(4, 10, 6, placements)

    assert result["length"] == 6
    assert result["states"][0] == 0
    assert result["states"][-1] == 0
    assert result["gate_index"] is not None
    total_pieces = sum(e["piece_count"] for e in result["edges"])
    assert total_pieces == 48

    print("  PASS: 4×10×6 extraction (6 edges, gate at",
          result["gate_index"], ", 48 pieces)")


def test_edge_relative_z():
    """Verify concrete placements use edge-relative z coordinates."""
    placements = parse_solution("data/solutions_s_5x8x6.dat")
    result = extract_cycle(5, 8, 6, placements)

    for i, e in enumerate(result["edges"]):
        for pl in e["concrete_placements"]:
            for (x, y, z_rel) in pl:
                assert 0 <= z_rel <= 2, (
                    f"edge {i}: z_rel={z_rel} out of range"
                )

    print("  PASS: edge-relative z coordinates (all in [0,2])")


def test_repeated_cycles():
    """Verify repeated-cycle construction produces valid tilings."""
    for cs_file, a, b, gens in [
        ("tools/frontier/_5x8_concrete_cycles.json", 5, 8, [6]),
        ("tools/frontier/_4x10_concrete_cycles.json", 4, 10, [6, 10]),
        ("tools/frontier/_5x6_concrete_cycles.json", 5, 6, [4, 29, 46, 47]),
    ]:
        data = load_cycle_data(cs_file)
        assert get_generators(data) == gens, f"{cs_file}: bad generators"
        gen = min(gens)
        for z in [gen, 2 * gen, 3 * gen]:
            pl = construct_tiling(z, cycle_data=data)
            r = validate_construction(pl, a=a, b=b, z=z)
            assert r["valid"], f"{a}x{b}x{z}: construction invalid"
            assert r["actual_pieces"] == a * b * z // 5
            assert r["actual_cells"] == a * b * z
        print(f"  PASS: {a}x{b} repeated cycles through z={3*gen}")


def test_coverage_exact():
    """Verify extracted cycles reconstruct the original tiling exactly."""
    for sol_file, a, b, z in [
        ("data/solutions_s_5x8x6.dat", 5, 8, 6),
        ("data/solutions_s_5x6x4.dat", 5, 6, 4),
        ("data/solutions_s_4x10x6.dat", 4, 10, 6),
    ]:
        placements = parse_solution(sol_file)
        result = extract_cycle(a, b, z, placements)

        # Reconstruct all cells from the cycle's concrete placements
        all_cells = set()
        for k, e in enumerate(result["edges"]):
            for pl in e["concrete_placements"]:
                cells = tuple(
                    sorted((x, y, k + z_rel) for (x, y, z_rel) in pl)
                )
                # Each placement is a valid S pentacube (5 cells)
                assert len(cells) == 5
                for c in cells:
                    assert c not in all_cells, f"overlap at {c}"
                    all_cells.add(c)

        expected = {(x, y, k) for x in range(a) for y in range(b)
                    for k in range(z)}
        assert all_cells == expected, f"{a}x{b}x{z}: cells mismatch"
        assert len(all_cells) == a * b * z
        print(f"  PASS: {a}x{b}x{z} exact coverage ({len(all_cells)} cells)")


if __name__ == "__main__":
    print("Testing extract_cycle_from_tiling.py...")
    print()

    test_extract_5x8x6()
    test_extract_5x6x4()
    test_extract_4x10x6()
    test_edge_relative_z()
    test_repeated_cycles()
    test_coverage_exact()

    print()
    print("All tests passed!")