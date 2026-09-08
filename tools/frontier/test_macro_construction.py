#!/usr/bin/env python3
"""
Regression tests for the generalized macro construction certificate tool.

Tests ensure that the 5×6 infinite-family theorem cannot silently regress,
and that the generalized interface works with arbitrary cycle data.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from tools.frontier.macro_construction import (
    construct_tiling,
    decompose_thickness,
    is_representable,
    validate_construction,
    generate_certificate,
    load_cycle_data,
    get_generators,
)

# Default 5×6 generators (derived from cycle data)
_GENERATORS = [4, 29, 46, 47]
_CYCLE_DATA = load_cycle_data()


def test_representable_values():
    """Verify that semigroup-positive values are correctly identified."""
    representable = [4, 8, 12, 16, 20, 24, 28, 29, 32, 33, 36, 37, 40, 41,
                     44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 100]
    nonrepresentable = [1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19,
                        21, 22, 23, 25, 26, 27, 30, 31, 34, 35, 38, 39, 42, 43]
    
    for z in representable:
        assert is_representable(z, _GENERATORS), f"{z} should be representable"
        assert decompose_thickness(z, _GENERATORS) is not None, f"{z} decomposition failed"
    
    for z in nonrepresentable:
        assert not is_representable(z, _GENERATORS), f"{z} should NOT be representable"
        assert decompose_thickness(z, _GENERATORS) is None, f"{z} should not decompose"
    
    print(f"  PASS: {len(representable)} representable, {len(nonrepresentable)} nonrepresentable")


def test_construct_and_validate(z: int):
    """Construct and validate a tiling for 5×6×z."""
    placements = construct_tiling(z, cycle_data=_CYCLE_DATA)
    result = validate_construction(placements, a=5, b=6, z=z)
    
    assert result["valid"], f"5×6×{z}: validation failed: {result['errors']}"
    assert result["actual_pieces"] == 6 * z, f"5×6×{z}: expected {6*z} pieces, got {result['actual_pieces']}"
    assert result["actual_cells"] == 30 * z, f"5×6×{z}: expected {30*z} cells, got {result['actual_cells']}"
    assert result["invalid_shapes"] == 0, f"5×6×{z}: {result['invalid_shapes']} invalid shapes"
    assert result["overlaps"] == 0, f"5×6×{z}: {result['overlaps']} overlaps"
    assert result["missing_cells"] == 0, f"5×6×{z}: {result['missing_cells']} missing cells"
    
    print(f"  PASS: 5×6×{z} — {result['actual_pieces']} pieces, {result['actual_cells']} cells")


def test_basic_construction():
    """Test basic construction for key thicknesses."""
    for z in [4, 8, 28, 29, 44, 45, 46, 47, 48, 100]:
        test_construct_and_validate(z)


def test_matches_solver_solutions():
    """Verify macro construction matches exact-cover solver solutions for z=4 and z=8."""
    import ast
    from pathlib import Path
    
    # Load solver solution for z=4
    solver_path = Path("data/solutions_s_5x6x4.dat")
    if solver_path.exists():
        with open(solver_path) as f:
            lines = f.read().strip().split("\n")
        sol_line = lines[2]
        parsed = ast.literal_eval("[" + sol_line.replace(")(", "),(") + "]")
        solver_placements = set(tuple(sorted(p)) for p in parsed)
        
        macro_placements = set(construct_tiling(4, cycle_data=_CYCLE_DATA))
        assert solver_placements == macro_placements, f"z=4: macro != solver"
        print(f"  PASS: 5×6×4 macro matches solver solution")
    
    # Load solver solution for z=8
    solver_path8 = Path("data/solutions_s_5x6x8_numba.txt")
    if not solver_path8.exists():
        solver_path8 = Path("/tmp/s_5x6x8_numba.txt")
    if solver_path8.exists():
        with open(solver_path8) as f:
            lines = f.read().strip().split("\n")
        sol_line = lines[2]
        parsed = ast.literal_eval("[" + sol_line.replace(")(", "),(") + "]")
        solver_placements = set(tuple(sorted(p)) for p in parsed)
        
        macro_placements = set(construct_tiling(8, cycle_data=_CYCLE_DATA))
        assert solver_placements == macro_placements, f"z=8: macro != solver"
        print(f"  PASS: 5×6×8 macro matches solver solution")


def test_decomposition_correctness():
    """Verify decompositions sum to z and use valid generator counts."""
    test_zs = [4, 8, 12, 16, 20, 24, 28, 29, 33, 36, 40, 44, 45, 46, 47, 48, 100]
    generators = _GENERATORS
    
    for z in test_zs:
        decomp = decompose_thickness(z, generators)
        assert decomp is not None, f"Failed to decompose {z}"
        
        total = sum(length * count for length, count in decomp.items())
        assert total == z, f"Decomposition of {z}: sum = {total}"
        
        for g in decomp:
            assert g in generators, f"Decomposition of {z} uses invalid generator {g}"
        
        # Verify counts are non-negative integers
        for g, c in decomp.items():
            assert isinstance(c, int) and c >= 0, f"Invalid count for {g}: {c}"
    
    print(f"  PASS: {len(test_zs)} decompositions verified")


def test_certificate_generation():
    """Test certificate generation produces valid output."""
    for z in [44, 45]:
        cert = generate_certificate(z, cycle_data=_CYCLE_DATA)
        assert cert["thickness"] == z
        assert cert["validation"]["valid"]
        assert cert["decomposition_counts"] is not None
        assert "provenance" in cert
        assert cert["construction"]["method"] == "macro_cycle_concatenation"
        print(f"  PASS: certificate for 5×6×{z} generated")


def test_nonrepresentable_raises():
    """Verify that nonrepresentable z raises ValueError."""
    for z in [1, 2, 3, 5, 43]:
        try:
            construct_tiling(z, cycle_data=_CYCLE_DATA)
            assert False, f"{z} should have raised ValueError"
        except ValueError:
            pass
    print(f"  PASS: nonrepresentable z raises ValueError")


def test_generalized_interface():
    """Test the generalized interface with explicit cycle data."""
    # Load cycle data via path
    cycle_path = os.path.join(
        os.path.dirname(__file__), "_5x6_concrete_cycles.json"
    )
    data = load_cycle_data(cycle_path)
    
    assert data["cross_section"] == (5, 6)
    assert get_generators(data) == [4, 29, 46, 47]
    assert "4" in data["cycles"]
    assert "29" in data["cycles"]
    assert "46" in data["cycles"]
    assert "47" in data["cycles"]
    
    # Verify cycle data structure
    for length, cycle in data["cycles"].items():
        assert cycle["length"] == int(length)
        assert cycle["path"][0] == 0, f"Cycle {length}: path doesn't start at 0"
        assert cycle["path"][-1] == 0, f"Cycle {length}: path doesn't end at 0"
        assert len(cycle["edges"]) == cycle["length"], (
            f"Cycle {length}: {len(cycle['edges'])} edges != length {cycle['length']}"
        )
        # Last edge must be pure shift
        assert cycle["edges"][-1]["is_pure_shift"], (
            f"Cycle {length}: last edge not pure shift"
        )
        assert cycle["edges"][-1]["template_count"] == 0, (
            f"Cycle {length}: last edge has templates"
        )
        # No other edge is a pure shift
        for i, edge in enumerate(cycle["edges"][:-1]):
            assert not edge["is_pure_shift"], (
                f"Cycle {length}: edge {i} is pure shift but not last"
            )
            assert edge["template_count"] > 0, (
                f"Cycle {length}: edge {i} has 0 templates"
            )
    
    # Test explicit path construction
    placements = construct_tiling(44, cycle_path=cycle_path)
    result = validate_construction(placements, a=5, b=6, z=44)
    assert result["valid"], f"5×6×44 via path: validation failed"
    
    print("  PASS: generalized interface with explicit cycle data path")


def test_cycle_data_schema():
    """Verify the cycle data schema is well-formed and documented."""
    data = _CYCLE_DATA
    
    # Cross-section present (processed form: tuple)
    assert data["cross_section"] == (5, 6)
    
    # Provenance present
    assert "provenance" in data
    assert "verified_cycle_lengths" in data["provenance"]
    assert data["provenance"]["verified_cycle_lengths"] == [4, 29, 46, 47]
    
    # Cycles present with all lengths
    assert "cycles" in data
    assert set(data["cycles"].keys()) == {"4", "29", "46", "47"}
    
    print("  PASS: cycle data schema well-formed")


if __name__ == "__main__":
    print("Testing macro_construction.py (generalized)...")
    print()
    
    test_representable_values()
    test_basic_construction()
    test_matches_solver_solutions()
    test_decomposition_correctness()
    test_certificate_generation()
    test_nonrepresentable_raises()
    test_generalized_interface()
    test_cycle_data_schema()
    
    print()
    print("All tests passed!")