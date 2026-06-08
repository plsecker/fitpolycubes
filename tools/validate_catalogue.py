#!/usr/bin/env python3                                                                                           
"""                                                                                                              
Catalogue Validation Tool for Polycube Decomposition System                                                      

Validates catalogue integrity and consistency.                                                                   
"""

import os
import sys
from collections import Counter

# Set up path for imports                                                                                        
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from catalogues.base import Box
from catalogues.f_catalogue import F_CATALOGUE
from catalogues.n_catalogue import N_CATALOGUE
from solvers.decomp import classify, CATALOGUES
import solvers.decomp as decomp


def validate_catalogue(catalogue_name):
    """Validate a catalogue with comprehensive checks."""

    if catalogue_name not in CATALOGUES:
        print(f"Error: No catalogue found for '{catalogue_name}'")
        return False

    catalogue = CATALOGUES[catalogue_name]

    # Set up decomp globals for this piece                                                                       
    decomp.PIECE_NAME = catalogue_name
    decomp.PIECE_SIZE = 5  # All pentacubes have size 5                                                          
    decomp.catalogue = catalogue
    decomp.classify.cache_clear()

    print(f"Validating catalogue: {catalogue_name}")
    print("=" * 50)

    all_passed = True

    # CHECK 1: Prime boxes classify as Prime                                                                     
    print("\nCHECK 1: Prime boxes classify as Prime")
    print("-" * 40)

    prime_failures = []
    for box in catalogue.primes:
        node = classify(box)
        if not hasattr(node, '__class__') or node.__class__.__name__ != 'Prime':
            prime_failures.append((box, node))

    if prime_failures:
        print(f"FAILED: {len(prime_failures)} primes don't classify as Prime:")
        for box, node in prime_failures:
            print(f"  {box} -> {node.__class__.__name__}")
        all_passed = False
    else:
        print(f"PASSED: All {len(catalogue.primes)} primes classify correctly")

        # CHECK 2: Prime boxes are not impossible
    print("\nCHECK 2: Prime boxes are not impossible")
    print("-" * 40)

    impossible_primes = []
    for box in catalogue.primes:
        reason = catalogue.impossible_reason(box)
        if reason is not None:
            impossible_primes.append((box, reason))

    if impossible_primes:
        print(f"FAILED: {len(impossible_primes)} primes marked impossible:")
        for box, reason in impossible_primes:
            print(f"  {box} -> {reason}")
        all_passed = False
    else:
        print(f"PASSED: No primes marked impossible")

        # CHECK 3: Row generator lengths are prime
    print("\nCHECK 3: Row generator lengths are prime")
    print("-" * 40)

    generator_failures = []
    total_generators = 0

    # Only validate ROW_FAMILIES seeds - they represent prime lengths
    for (a, b), family in catalogue.row_families.items():
        for g in family.seeds:
            total_generators += 1
            test_box = Box(a, b, g)
            node = classify(test_box)
            if not hasattr(node, '__class__') or node.__class__.__name__ != 'Prime':
                generator_failures.append((test_box, node))

    if generator_failures:
        print(f"FAILED: {len(generator_failures)} row generators don't classify as Prime:")
        for box, node in generator_failures:
            print(f"  {box} -> {node.__class__.__name__}")
        all_passed = False
    else:
        print(f"PASSED: All {total_generators} row generators classify as Prime")

        # CHECK 4: Canonical duplicates
    print("\nCHECK 4: Canonical duplicates")
    print("-" * 40)

    # Get raw primes from the catalogue module                                                                   
    if catalogue_name == 'F':
        from catalogues.f_catalogue import RAW_PRIMES
    elif catalogue_name == 'N':
        from catalogues.n_catalogue import RAW_PRIMES
    else:
        RAW_PRIMES = set()

    raw_count = len(RAW_PRIMES)
    canonical_count = len(catalogue.primes)

    print(f"Raw prime entries: {raw_count}")
    print(f"Unique prime boxes: {canonical_count}")

    if raw_count > canonical_count:
        print(f"INFO: {raw_count - canonical_count} duplicates collapsed after canonicalization")

        # Find the duplicates                                                                                    
        canonical_map = {}
        for box in RAW_PRIMES:
            canonical = box.canonical()
            if canonical not in canonical_map:
                canonical_map[canonical] = []
            canonical_map[canonical].append(box)

        duplicates = {k: v for k, v in canonical_map.items() if len(v) > 1}
        if duplicates:
            print("Duplicate groups:")
            for canonical, originals in duplicates.items():
                print(f"  {canonical} <- {originals}")

    print("\n" + "=" * 50)
    if all_passed:
        print(f"✓ Catalogue {catalogue_name} validation PASSED")
    else:
        print(f"✗ Catalogue {catalogue_name} validation FAILED")

    return all_passed


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate polycube catalogues")
    parser.add_argument("catalogue", help="Catalogue name (F, N)")
    args = parser.parse_args()

    catalogue_name = args.catalogue.upper()
    success = validate_catalogue(catalogue_name)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()                                                                                                       
