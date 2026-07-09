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
from catalogues.registry import CATALOGUES
from solvers.decomp import classify, closes
import solvers.decomp as decomp


def audit_catalogue(catalogue_name, max_dimension=20, limit=None):
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
    
    # Print family information
    print(f"\nFamily information:")
    print("-" * 30)
    for (a, b), family in catalogue.row_families.items():
        period_str = str(family.period) if family.period is not None else "unknown"
        print(f"  ({a},{b}): seeds={family.seeds}, period={period_str}")
    
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
    def print_section(title, items, limit):
        print(f"\nAUDIT {title}")
        print("-" * 30)
        count = len(items)
        print(f"Count: {count}")
        
        if not items:
            print("No issues found")
            return

        display_items = items[:limit] if limit is not None else items

        for box, node in display_items:
            label = node.__class__.__name__ if hasattr(node, '__class__') else "Unknown"
            print(f"  {box} -> {label}")

        if limit is not None and count > limit:
            print(f"  ... and {count - limit} more")

    print_section("A: Prime mismatches", prime_mismatches, limit)
    print_section("B: Unproven composites", unproven_composites, limit)
    print_section("C: Discovered composites", discovered_composites, limit)
    
    # Audit D: Published solutions
    print("\nAUDIT D: Published solutions")
    print("-" * 30)
    
    published = list(catalogue.published_solutions)
    print(f"Count: {len(published)}")
    
    if published:
        display_items = published[:limit] if limit is not None else published
        for box in display_items:
            print(f"  {box}")
        if limit is not None and len(published) > limit:
            print(f"  ... and {len(published) - limit} more")
    
    print("\n" + "=" * 50)
    print(f"Audit complete for {catalogue_name}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Audit polycube catalogues")
    parser.add_argument("catalogue", help="Catalogue name (F, N)")
    parser.add_argument("--max-dim", type=int, default=15, help="Maximum dimension to test")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of cases per section")
    args = parser.parse_args()
    
    catalogue_name = args.catalogue.upper()
    audit_catalogue(catalogue_name, args.max_dim, args.limit)


if __name__ == "__main__":
    main()
