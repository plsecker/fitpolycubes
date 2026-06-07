#!/usr/bin/env python3
"""
Proof Audit Tool for Polycube Decomposition System

Finds surprising cases and mismatches between catalogues and solver.
"""

import os
import sys

# Set up path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from catalogues.base import Box
from catalogues.f_catalogue import F_CATALOGUE
from catalogues.n_catalogue import N_CATALOGUE
from solvers.decomp import classify, CATALOGUES, closes
import solvers.decomp as decomp


def audit_catalogue(catalogue_name, max_dimension=20):
    """Audit catalogue for surprising cases."""
    
    if catalogue_name not in CATALOGUES:
        print(f"Error: No catalogue found for '{catalogue_name}'")
        return
    
    catalogue = CATALOGUES[catalogue_name]
    
    # Set up decomp globals
    decomp.PIECE_NAME = catalogue_name
    decomp.PIECE_SIZE = 5
    decomp.catalogue = catalogue
    decomp.classify.cache_clear()
    
    print(f"Auditing catalogue: {catalogue_name}")
    print("=" * 50)
    
    prime_mismatches = []
    unproven_composites = []
    discovered_composites = []
    
    # Generate test boxes up to max_dimension
    test_boxes = []
    for a in range(1, max_dimension + 1):
        for b in range(a, max_dimension + 1):
            for c in range(b, max_dimension + 1):
                if (a * b * c) % 5 == 0:  # Valid volume for pentacube
                    test_boxes.append(Box(a, b, c))
    
    print(f"Testing {len(test_boxes)} boxes...")
    
    for box in test_boxes:
        node = classify(box)
        node_type = node.__class__.__name__
        
        # Audit A: Catalogue says prime, solver returns Generator
        if box in catalogue.primes and node_type == 'Generator':
            prime_mismatches.append((box, node))
        
        # Audit B: Catalogue says composite (not prime, not impossible), solver returns Unknown
        is_prime = box in catalogue.primes
        is_impossible = catalogue.impossible_reason(box) is not None
        is_searched_no_solution = box in catalogue.searched_no_solution
        
        if not is_prime and not is_impossible and not is_searched_no_solution and node_type == 'Unknown':
            unproven_composites.append((box, node))
        
        # Audit C: Solver discovers closed proof for unlisted box
        if not is_prime and closes(node) and node_type in ['Generator', 'Slab', 'Width']:
            discovered_composites.append((box, node))
    
    # Report results
    print(f"\nAUDIT A: Prime mismatches")
    print("-" * 30)
    if prime_mismatches:
        print(f"PRIME_MISMATCH: {len(prime_mismatches)} cases")
        for box, node in prime_mismatches[:10]:  # Show first 10
            print(f"  {box} -> {node.__class__.__name__}")
        if len(prime_mismatches) > 10:
            print(f"  ... and {len(prime_mismatches) - 10} more")
    else:
        print("No prime mismatches found")
    
    print(f"\nAUDIT B: Unproven composites")
    print("-" * 30)
    if unproven_composites:
        print(f"UNPROVEN_COMPOSITE: {len(unproven_composites)} cases")
        for box, node in unproven_composites[:10]:
            print(f"  {box} -> Unknown")
        if len(unproven_composites) > 10:
            print(f"  ... and {len(unproven_composites) - 10} more")
    else:
        print("No unproven composites found")
    
    print(f"\nAUDIT C: Discovered composites")
    print("-" * 30)
    if discovered_composites:
        print(f"DISCOVERED_COMPOSITE: {len(discovered_composites)} cases")
        for box, node in discovered_composites[:10]:
            print(f"  {box} -> {node.__class__.__name__}")
        if len(discovered_composites) > 10:
            print(f"  ... and {len(discovered_composites) - 10} more")
    else:
        print("No new composites discovered")
    
    print("\n" + "=" * 50)
    print(f"Audit complete for {catalogue_name}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Audit polycube catalogues")
    parser.add_argument("catalogue", help="Catalogue name (F, N)")
    parser.add_argument("--max-dim", type=int, default=15, help="Maximum dimension to test")
    args = parser.parse_args()
    
    catalogue_name = args.catalogue.upper()
    audit_catalogue(catalogue_name, args.max_dim)


if __name__ == "__main__":
    main()
