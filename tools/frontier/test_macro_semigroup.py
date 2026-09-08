#!/usr/bin/env python3
"""
Tests for the macro semigroup analysis tool.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from tools.frontier.macro_semigroup import compute_semigroup


def test_semigroup_4_29_46_47():
    """Test the 5×6 semigroup <4, 29, 46, 47>."""
    result = compute_semigroup([4, 29, 46, 47], max_check=200)
    
    assert result["generators"] == [4, 29, 46, 47]
    assert result["frobenius_number"] == 43
    assert result["conductor"] == 44
    assert result["apery_set"] == {0: 0, 1: 29, 2: 46, 3: 47}
    assert result["verification"]["all_representable_above_conductor"] == True
    
    # Check specific representable values
    for n in [4, 8, 12, 16, 20, 24, 28, 29, 32, 33, 36, 37, 40, 41, 44, 45, 46, 47]:
        assert result["representability_table"][n]["representable"], f"{n} should be representable"
    
    # Check specific nonrepresentable values
    for n in [1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19, 21, 22, 23, 25, 26, 27, 30, 31, 34, 35, 38, 39, 42, 43]:
        assert not result["representability_table"][n]["representable"], f"{n} should NOT be representable"
    
    print(f"  PASS: <4,29,46,47> Frobenius={result['frobenius_number']}, Conductor={result['conductor']}")


def test_semigroup_6():
    """Test the 4×5 semigroup <6> (GCD=6, not a numerical semigroup)."""
    result = compute_semigroup([6], max_check=50)
    
    assert result["generators"] == [6]
    # <6> has GCD=6, so it's not a numerical semigroup with finite Frobenius
    # All multiples of 6 are representable
    for n in [6, 12, 18, 24, 30]:
        assert result["representability_table"][n]["representable"]
    # Non-multiples of 6 are not representable
    for n in [1, 2, 3, 4, 5, 7, 8, 9, 10, 11]:
        assert not result["representability_table"][n]["representable"]
    
    print(f"  PASS: <6> (GCD=6, infinite gaps)")


def test_semigroup_5_10():
    """Test the 4×6 semigroup <5, 10> (GCD=5)."""
    result = compute_semigroup([5, 10], max_check=50)
    
    assert result["generators"] == [5, 10]
    # <5,10> = all multiples of 5, GCD=5, infinite gaps
    for n in [5, 10, 15, 20, 25]:
        assert result["representability_table"][n]["representable"]
    for n in [1, 2, 3, 4, 6, 7, 8, 9]:
        assert not result["representability_table"][n]["representable"]
    
    print(f"  PASS: <5,10> (GCD=5, infinite gaps)")


def test_semigroup_20_130():
    """Test the 4×8 semigroup <20, 130> (GCD=10)."""
    result = compute_semigroup([20, 130], max_check=300)
    
    assert result["generators"] == [20, 130]
    assert result["gcd"] == 10
    # GCD=10, so Frobenius and conductor are None (infinite gaps)
    assert result["frobenius_number"] is None
    assert result["conductor"] is None
    # All multiples of 10 >= 120 should be representable
    for n in [120, 130, 140, 150, 200, 260]:
        if n <= 300:
            assert result["representability_table"][n]["representable"], f"{n} should be representable"
    
    print(f"  PASS: <20,130> (GCD=10, infinite gaps)")


def test_empty_generators():
    """Test that empty generators raises error."""
    try:
        compute_semigroup([])
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    print("  PASS: empty generators raises ValueError")


def test_single_generator():
    """Test single generator (GCD > 1, infinite gaps)."""
    result = compute_semigroup([7], max_check=30)
    assert result["gcd"] == 7
    assert result["frobenius_number"] is None
    assert result["conductor"] is None
    
    print(f"  PASS: <7> (GCD=7, infinite gaps)")


if __name__ == "__main__":
    print("Testing macro_semigroup.py...")
    print()
    
    test_semigroup_4_29_46_47()
    test_semigroup_6()
    test_semigroup_5_10()
    test_semigroup_20_130()
    test_empty_generators()
    test_single_generator()
    
    print()
    print("All tests passed!")