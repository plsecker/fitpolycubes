#!/usr/bin/env python3
"""
Deep characterization of the 4×5 S-pentacube SCC of 0.

Reads the complete graph data and produces a detailed structural analysis
of the 11-state SCC, the two 6-cycles, and their geometric interpretation.
"""
from __future__ import annotations

import sys
import math
from collections import defaultdict, deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements

A, B = 4, 5
NCELLS = A * B
WORD_MASK = (1 << NCELLS) - 1

# ============================================================================
# Load the graph
# ============================================================================

def load_graph():
    edges = {}
    with open(REPO_ROOT / "data" / "frontier" / "s_4x5_edges.txt") as f:
        for line in f:
            parts = line.strip().split(" -> ")
            if len(parts) == 2:
                src = int(parts[0])
                dsts = [int(x) for x in parts[1].split()]
                edges[src] = dsts
    states = set()
    with open(REPO_ROOT / "data" / "frontier" / "s_4x5_states.txt") as f:
        for line in f:
            states.add(int(line.strip()))
    return states, edges

# ============================================================================
# Helper functions
# ============================================================================

def layer_mask(state, layer):
    return (state >> (layer * NCELLS)) & WORD_MASK

def layer_masks_str(state):
    """Return a human-readable representation of the 3 layer masks."""
    l0 = layer_mask(state, 0)
    l1 = layer_mask(state, 1)
    l2 = layer_mask(state, 2)
    return l0, l1, l2

def mask_to_grid(mask, a=A, b=B):
    """Convert a layer mask to a 2D grid string."""
    rows = []
    for y in range(b):
        row = ""
        for x in range(a):
            bit = x + a * y
            if mask & (1 << bit):
                row += "█"
            else:
                row += "·"
        rows.append(row)
    return rows

def print_state(state, label=""):
    """Print a state with its layer masks as grids."""
    l0, l1, l2 = layer_masks_str(state)
    print(f"  State {state} {label}")
    print(f"    L0: {l0:020b} (0x{l0:05x})")
    print(f"    L1: {l1:020b} (0x{l1:05x})")
    print(f"    L2: {l2:020b} (0x{l2:05x})")
    grid0 = mask_to_grid(l0)
    grid1 = mask_to_grid(l1)
    grid2 = mask_to_grid(l2)
    for y in range(B):
        print(f"    y={y}: {grid0[y]}  {grid1[y]}  {grid2[y]}")
    print()

def count_bits(mask):
    return bin(mask).count("1")

def first_empty(mask):
    missing = WORD_MASK & ~mask
    if not missing:
        return -1
    low = missing & -missing
    return low.bit_length() - 1

def cell_coord(bit, a=A):
    return (bit % a, bit // a)

# ============================================================================
# Build the SCC of 0
# ============================================================================

def compute_scc_of_0(states, edges):
    """Compute the SCC containing state 0 using Kosaraju."""
    # Build reverse graph
    rev = {s: set() for s in states}
    for s, dsts in edges.items():
        for d in dsts:
            rev[d].add(s)
    
    # First pass
    visited = set()
    order = []
    for n in sorted(states):
        if n not in visited:
            stack = [(n, 0)]
            while stack:
                node, state = stack.pop()
                if state == 0:
                    if node in visited: continue
                    visited.add(node)
                    stack.append((node, 1))
                    for nxt in sorted(edges.get(node, [])):
                        if nxt not in visited:
                            stack.append((nxt, 0))
                else:
                    order.append(node)
    
    # Second pass
    visited2 = set()
    sccs = []
    for n in reversed(order):
        if n not in visited2:
            scc = set()
            stack = [n]
            while stack:
                node = stack.pop()
                if node in visited2: continue
                visited2.add(node)
                scc.add(node)
                for nxt in sorted(rev.get(node, [])):
                    if nxt not in visited2:
                        stack.append(nxt)
            sccs.append(scc)
    
    # Find SCC of 0
    for scc in sccs:
        if 0 in scc:
            return scc
    return None


def find_cycles_in_scc(scc_nodes, edges):
    """Find all simple cycles in the SCC."""
    scc_set = set(scc_nodes)
    adj = {n: sorted([s for s in edges.get(n, []) if s in scc_set]) for n in scc_nodes}
    
    cycles = []
    for start in sorted(scc_nodes):
        stack = [(start, [start], {start})]
        while stack:
            node, path, visited = stack.pop()
            for nxt in adj.get(node, []):
                if nxt == start and len(path) > 1:
                    cycles.append(tuple(path))
                elif nxt not in visited and nxt > start:
                    stack.append((nxt, path + [nxt], visited | {nxt}))
    
    # Deduplicate by rotating to min element
    seen = set()
    unique = []
    for c in cycles:
        m = min(c)
        idx = c.index(m)
        norm = c[idx:] + c[1:idx+1]
        if norm not in seen:
            seen.add(norm)
            unique.append(norm)
    return unique


# ============================================================================
# Main analysis
# ============================================================================

def main():
    print("=" * 70)
    print("4×5 S-PENTACUBE SCC OF 0 — DEEP CHARACTERIZATION")
    print("=" * 70)
    print()
    
    states, edges = load_graph()
    scc0 = compute_scc_of_0(states, edges)
    scc0_list = sorted(scc0)
    
    print(f"SCC of 0: {len(scc0)} states")
    print()
    
    # ========================================================================
    # Phase 1: Full state characterization
    # ========================================================================
    print("=" * 70)
    print("PHASE 1: FULL STATE CHARACTERIZATION")
    print("=" * 70)
    print()
    
    for s in scc0_list:
        l0, l1, l2 = layer_masks_str(s)
        n0, n1, n2 = count_bits(l0), count_bits(l1), count_bits(l2)
        total = n0 + n1 + n2
        
        # Outgoing transitions
        out_all = sorted(edges.get(s, []))
        out_in_scc = [d for d in out_all if d in scc0]
        out_out = [d for d in out_all if d not in scc0]
        
        # Incoming transitions
        in_all = []
        for src, dsts in edges.items():
            if s in dsts:
                in_all.append(src)
        in_in_scc = [d for d in in_all if d in scc0]
        in_out = [d for d in in_all if d not in scc0]
        
        # First empty cell
        fe = first_empty(l0)
        fe_coord = cell_coord(fe) if fe >= 0 else "FULL"
        
        print(f"--- State {s} ---")
        print(f"  Layer 0: {n0} cells, mask=0x{l0:05x}")
        print(f"  Layer 1: {n1} cells, mask=0x{l1:05x}")
        print(f"  Layer 2: {n2} cells, mask=0x{l2:05x}")
        print(f"  Total occupied: {total} cells")
        print(f"  First empty (L0): cell {fe} {fe_coord}")
        print(f"  Out-degree: {len(out_all)} total, {len(out_in_scc)} in SCC, {len(out_out)} out of SCC")
        print(f"  In-degree: {len(in_all)} total, {len(in_in_scc)} in SCC, {len(in_out)} out of SCC")
        
        # Grid display
        grid0 = mask_to_grid(l0)
        grid1 = mask_to_grid(l1)
        grid2 = mask_to_grid(l2)
        print(f"  Grid (L0 | L1 | L2):")
        for y in range(B):
            print(f"    y={y}: {grid0[y]} | {grid1[y]} | {grid2[y]}")
        
        # Check if L0 is full (would trigger shift)
        if l0 == WORD_MASK:
            print(f"  ** L0 FULL — would shift immediately **")
        
        print()
    
    # ========================================================================
    # Phase 2: The two cycles
    # ========================================================================
    print("=" * 70)
    print("PHASE 2: THE TWO 6-CYCLES")
    print("=" * 70)
    print()
    
    cycles = find_cycles_in_scc(scc0, edges)
    print(f"Found {len(cycles)} simple cycles in SCC of 0:")
    print()
    
    for i, cycle in enumerate(cycles):
        print(f"--- Cycle {i+1} (length {len(cycle)}) ---")
        print(f"  Path: {' -> '.join(str(s) for s in cycle)}")
        print()
        
        # Verify each edge
        for j in range(len(cycle)):
            src = cycle[j]
            dst = cycle[(j + 1) % len(cycle)]
            has_edge = dst in edges.get(src, [])
            print(f"  Step {j+1}: {src} -> {dst} {'✓' if has_edge else '✗'}")
        
        # Show layer masks for each state in the cycle
        print()
        for j, s in enumerate(cycle):
            l0, l1, l2 = layer_masks_str(s)
            n0, n1, n2 = count_bits(l0), count_bits(l1), count_bits(l2)
            print(f"  State {s} (step {j}): L0={n0}bits L1={n1}bits L2={n2}bits")
        
        print()
    
    # ========================================================================
    # Phase 3: Cycle comparison
    # ========================================================================
    print("=" * 70)
    print("PHASE 3: CYCLE COMPARISON")
    print("=" * 70)
    print()
    
    c1 = cycles[0]
    c2 = cycles[1]
    
    # Check if cycles share any states
    shared = set(c1) & set(c2)
    print(f"Cycle 1 states: {set(c1)}")
    print(f"Cycle 2 states: {set(c2)}")
    print(f"Shared states: {shared}")
    print(f"States unique to cycle 1: {set(c1) - set(c2)}")
    print(f"States unique to cycle 2: {set(c2) - set(c1)}")
    print()
    
    # Check if cycle 2 is a rotation/reversal of cycle 1
    # (they don't share all states, so they can't be rotations)
    print(f"Cycles are disjoint: {len(shared) == 0}")
    print(f"Cycles are identical: {set(c1) == set(c2)}")
    print()
    
    # Check if the two cycles are related by symmetry
    # Look at the layer masks of corresponding states
    print("Layer mask comparison:")
    print(f"  Cycle 1 states have L0 masks: {[layer_mask(s, 0) for s in c1]}")
    print(f"  Cycle 2 states have L0 masks: {[layer_mask(s, 0) for s in c2]}")
    print()
    
    # ========================================================================
    # Phase 4: Compact state description
    # ========================================================================
    print("=" * 70)
    print("PHASE 4: COMPACT STATE DESCRIPTION")
    print("=" * 70)
    print()
    
    # For each state, compute various quantities
    print("State quantities:")
    print(f"  {'State':>15} {'L0bits':>6} {'L1bits':>6} {'L2bits':>6} {'L0mask':>10} {'L1mask':>10} {'L2mask':>10} {'fe':>3}")
    print(f"  {'-'*15} {'-'*6} {'-'*6} {'-'*6} {'-'*10} {'-'*10} {'-'*10} {'-'*3}")
    
    for s in scc0_list:
        l0, l1, l2 = layer_masks_str(s)
        n0, n1, n2 = count_bits(l0), count_bits(l1), count_bits(l2)
        fe = first_empty(l0)
        print(f"  {s:>15} {n0:>6} {n1:>6} {n2:>6} 0x{l0:05x} 0x{l1:05x} 0x{l2:05x} {fe:>3}")
    
    print()
    
    # Check for patterns in the masks
    print("Pattern analysis:")
    print()
    
    # Check if all L2 masks are zero
    l2_nonzero = [s for s in scc0_list if layer_mask(s, 2) != 0]
    print(f"  States with L2 ≠ 0: {len(l2_nonzero)}")
    for s in l2_nonzero:
        l2 = layer_mask(s, 2)
        print(f"    State {s}: L2 = 0x{l2:05x} ({count_bits(l2)} bits)")
    
    # Check if any L0 is full
    l0_full = [s for s in scc0_list if layer_mask(s, 0) == WORD_MASK]
    print(f"  States with L0 = WORD_MASK: {len(l0_full)}")
    for s in l0_full:
        print(f"    State {s}")
    
    # Check total occupied cells
    print()
    print("  Total occupied cells per state:")
    for s in scc0_list:
        l0, l1, l2 = layer_masks_str(s)
        total = count_bits(l0) + count_bits(l1) + count_bits(l2)
        print(f"    State {s}: {total} cells (L0={count_bits(l0)}, L1={count_bits(l1)}, L2={count_bits(l2)})")
    
    # ========================================================================
    # Phase 5: Internal SCC graph structure
    # ========================================================================
    print("=" * 70)
    print("PHASE 5: INTERNAL SCC GRAPH STRUCTURE")
    print("=" * 70)
    print()
    
    # Build the SCC subgraph
    scc_set = set(scc0)
    adj = {s: sorted([d for d in edges.get(s, []) if d in scc_set]) for s in scc0_list}
    
    print("Internal SCC adjacency matrix:")
    print(f"  {'':>15}", end="")
    for s in scc0_list:
        print(f" {s:>15}", end="")
    print()
    
    for s in scc0_list:
        print(f"  {s:>15}", end="")
        for t in scc0_list:
            if t in adj[s]:
                print(f" {'→':>15}", end="")
            else:
                print(f" {'·':>15}", end="")
        print()
    
    print()
    
    # Out-degree within SCC
    print("Out-degree within SCC:")
    for s in scc0_list:
        print(f"  State {s}: {len(adj[s])} internal successors: {adj[s]}")
    
    # In-degree within SCC
    in_adj = {s: [] for s in scc0_list}
    for s in scc0_list:
        for d in adj[s]:
            in_adj[d].append(s)
    print()
    print("In-degree within SCC:")
    for s in scc0_list:
        print(f"  State {s}: {len(in_adj[s])} internal predecessors: {in_adj[s]}")
    
    # ========================================================================
    # Phase 6: Edge analysis — what happens at each step
    # ========================================================================
    print("=" * 70)
    print("PHASE 6: EDGE-LEVEL ANALYSIS OF CYCLE 1")
    print("=" * 70)
    print()
    
    # For cycle 1, show what happens at each step
    c1 = cycles[0]
    print(f"Cycle 1: {' -> '.join(str(s) for s in c1)}")
    print()
    
    for j in range(len(c1)):
        src = c1[j]
        dst = c1[(j + 1) % len(c1)]
        
        l0_src, l1_src, l2_src = layer_masks_str(src)
        l0_dst, l1_dst, l2_dst = layer_masks_str(dst)
        
        print(f"Step {j+1}: {src} -> {dst}")
        print(f"  Source L0: 0x{l0_src:05x} ({count_bits(l0_src)} bits)")
        print(f"  Source L1: 0x{l1_src:05x} ({count_bits(l1_src)} bits)")
        print(f"  Source L2: 0x{l2_src:05x} ({count_bits(l2_src)} bits)")
        
        # The edge corresponds to filling L0 and shifting
        # After shift: new state = (old state with L0 filled) >> NCELLS
        # So dst should equal (src | fill_mask) >> NCELLS where fill_mask fills L0
        
        # We can compute what was added to L0 to make it full
        # L0 must become WORD_MASK, so fill = WORD_MASK ^ l0_src
        fill = WORD_MASK ^ l0_src
        print(f"  Fill mask (cells added to L0): 0x{fill:05x}")
        fill_cells = [cell_coord(b) for b in range(NCELLS) if fill & (1 << b)]
        print(f"  Cells added: {fill_cells}")
        
        # After filling L0 and shifting, the new state should be:
        # (src | fill) >> NCELLS = (src | fill) / 2^NCELLS
        # But src already has L0 = l0_src, so src | fill = src | (WORD_MASK ^ l0_src)
        # Actually, src already has L0 = l0_src, so src | fill = src | (WORD_MASK - l0_src)
        # But we need to be careful: src has L0, L1, L2 packed
        # src = l0_src | (l1_src << NCELLS) | (l2_src << 2*NCELLS)
        # After filling L0: src_filled = WORD_MASK | (l1_src << NCELLS) | (l2_src << 2*NCELLS)
        # After shift: shifted = (l1_src) | (l2_src << NCELLS)
        # So dst should equal l1_src | (l2_src << NCELLS)
        expected_dst = l1_src | (l2_src << NCELLS)
        print(f"  Expected dst (L1|L2 shifted): 0x{expected_dst:015x}")
        print(f"  Actual dst:                   {dst}")
        print(f"  Match: {expected_dst == dst}")
        
        # But wait — the edge also involves placing S pieces to fill L0.
        # The fill mask tells us which cells in L0 need to be filled.
        # The actual dst might differ if the placements also affect L1/L2.
        # Let's check: dst should be the result of applying templates and then shifting.
        # The templates can add cells to L1 and L2 as well.
        # So dst = (l1_src | added_L1) | ((l2_src | added_L2) << NCELLS)
        # where added_L1 and added_L2 come from the templates placed.
        
        # We can compute what was added to L1 and L2:
        added_L1 = l0_dst ^ l1_src  # dst's L0 = old L1 + additions
        added_L2 = l1_dst ^ l2_src  # dst's L1 = old L2 + additions
        print(f"  Added to L1 (from templates): 0x{added_L1:05x}")
        print(f"  Added to L2 (from templates): 0x{added_L2:05x}")
        
        # The total cells added by placements = fill + added_L1 + added_L2
        total_added = count_bits(fill) + count_bits(added_L1) + count_bits(added_L2)
        print(f"  Total cells added by placements: {total_added}")
        print(f"  Number of S pieces: {total_added // 5}")
        print()
    
    # ========================================================================
    # Phase 7: Check if the two cycles produce the same tiling
    # ========================================================================
    print("=" * 70)
    print("PHASE 7: DO THE TWO CYCLES PRODUCE THE SAME TILING?")
    print("=" * 70)
    print()
    
    # The two cycles share state 146100961245. If we start from that state,
    # the two cycles diverge. Let's trace both paths.
    print(f"Cycle 1: {c1}")
    print(f"Cycle 2: {c2}")
    print()
    
    # Find the shared state
    shared = set(c1) & set(c2)
    print(f"Shared states: {shared}")
    
    if shared:
        s_shared = list(shared)[0]
        print(f"Using shared state {s_shared} as reference:")
        
        # Find positions in each cycle
        i1 = c1.index(s_shared)
        i2 = c2.index(s_shared)
        
        # Show the two paths from the shared state
        c1_from_shared = c1[i1:] + c1[:i1]
        c2_from_shared = c2[i2:] + c2[:i2]
        
        print(f"  Cycle 1 from {s_shared}: {' -> '.join(str(s) for s in c1_from_shared)}")
        print(f"  Cycle 2 from {s_shared}: {' -> '.join(str(s) for s in c2_from_shared)}")
        
        # Compare the two paths step by step
        print()
        print("  Step-by-step comparison:")
        for j in range(len(c1_from_shared)):
            s1 = c1_from_shared[j]
            s2 = c2_from_shared[j]
            same = s1 == s2
            print(f"    Step {j}: {s1} vs {s2} {'✓' if same else '✗'}")
    
    print()
    
    # ========================================================================
    # Phase 8: Summary
    # ========================================================================
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    
    print(f"SCC of 0: {len(scc0)} states")
    print(f"Simple cycles: {len(cycles)}")
    for i, c in enumerate(cycles):
        print(f"  Cycle {i+1}: length {len(c)}")
    print(f"Cycle lengths: {sorted(set(len(c) for c in cycles))}")
    print(f"GCD of cycle lengths: {math.gcd(*[len(c) for c in cycles])}")
    print()
    
    # Check if the SCC is "tight" (every state on a cycle)
    on_cycle = set()
    for c in cycles:
        on_cycle.update(c)
    off_cycle = set(scc0) - on_cycle
    print(f"States on at least one cycle: {len(on_cycle)}")
    print(f"States off all cycles: {len(off_cycle)}")
    if off_cycle:
        print(f"  Off-cycle states: {sorted(off_cycle)}")
    
    # Check if the SCC is "simple" (every state has exactly one internal successor)
    for s in scc0_list:
        internal = [d for d in edges.get(s, []) if d in scc_set]
        if len(internal) != 1:
            print(f"  State {s} has {len(internal)} internal successors (not simple)")


if __name__ == "__main__":
    main()