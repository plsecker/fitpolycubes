#!/usr/bin/env python3
"""
Test the corrected predecessor function on a single state.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from solvers.v_5x5_macro import (
    build_templates, layer_mask, first_empty, apply_template,
    shift_state, WORD_MASK, NCELLS, pack_layers
)
from solvers.v_5x5_bidirectional_correct import (
    explore_forward, find_predecessors_correct
)


def main():
    print("=" * 70)
    print("TEST CORRECTED PREDECESSOR FUNCTION")
    print("=" * 70)
    print()
    
    # Build templates
    print("Building templates...")
    templates, _, _, _, _ = build_templates()
    print(f"  Templates built")
    print()
    
    # Test with state 0
    print("Testing predecessor function for state 0...")
    start_time = time.time()
    predecessors = find_predecessors_correct(0, templates)
    elapsed = time.time() - start_time
    
    print(f"  Found {len(predecessors)} predecessors in {elapsed:.1f}s")
    print()
    
    # Verify that these are correct
    print("Verifying predecessors...")
    verified = 0
    failed = 0
    
    for P in predecessors:
        successors = explore_forward(P, templates)
        if 0 in successors:
            verified += 1
        else:
            failed += 1
            print(f"  ERROR: {P} is not a predecessor of 0")
    
    print(f"  Verified: {verified}")
    print(f"  Failed: {failed}")
    print()
    
    if failed > 0:
        print("ERROR: Predecessor function is not correct!")
        return 1
    
    # Show some examples
    print("Example predecessors:")
    for i, P in enumerate(list(predecessors)[:5]):
        print(f"  {i+1}. {P}")
        print(f"     layer0: {layer_mask(P, 0):025b}")
        print(f"     layer1: {layer_mask(P, 1):025b}")
        print(f"     layer2: {layer_mask(P, 2):025b}")
    print()
    
    print("=" * 70)
    print("✓ Predecessor function is correct")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
