#!/usr/bin/env python3
"""
Debug script to verify the 4×5 SCC structure.
"""
from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements

A, B = 4, 5
NCELLS = A * B
WORD_MASK = (1 << NCELLS) - 1

# Reuse the helper functions
def make_shifted_template_general(placement_cells, target_z, a, b):
    NCELLS = a * b
    LAYERS = 3
    min_z = min(z for _, _, z in placement_cells)
    shifted_masks = [0] * LAYERS
    target_rel = target_z - min_z
    for x, y, z in placement_cells:
        rel = z - min_z - target_rel
        if rel < 0 or rel >= LAYERS:
            return None
        cell_id = x + a * y
        shifted_masks[rel] |= (1 << cell_id)
    state = 0
    for i, mask in enumerate(shifted_masks):
        state |= (mask << (i * NCELLS))
    return state

def build_templates_general(a, b):
    raw, _ = generate_placements(PENTACUBES["S"], (a, b, 20), break_symmetry=False)
    NCELLS = a * b
    result = {cell: [] for cell in range(NCELLS)}
    seen = {cell: set() for cell in range(NCELLS)}
    concrete_count = len(raw)
    for placement in raw.values():
        cells = tuple(placement)
        for x, y, z in cells:
            target = x + a * y
            packed = make_shifted_template_general(cells, z, a, b)
            if packed is None: continue
            if packed in seen[target]: continue
            seen[target].add(packed)
            result[target].append(packed)
    total_templates = sum(len(v) for v in result.values())
    return result, NCELLS, WORD_MASK, concrete_count, total_templates

def layer_mask_general(state, layer, NCELLS):
    return (state >> (layer * NCELLS)) & ((1 << NCELLS) - 1)

def first_empty_general(mask, NCELLS):
    WORD_MASK = (1 << NCELLS) - 1
    missing = WORD_MASK & ~mask
    if not missing: return -1
    low = missing & -missing
    return low.bit_length() - 1

def apply_template_general(state, template):
    if state & template: return None
    return state | template

def shift_state_general(state, NCELLS):
    return state >> NCELLS

# Build the graph
print("Building templates...")
templates, NCELLS, WORD_MASK, concrete_count, total_templates = build_templates_general(A, B)
print(f"  Templates: {total_templates}")

# First generation
seen = {0}
queue = deque([0])
sources = set()

while queue:
    state = queue.popleft()
    if layer_mask_general(state, 0, NCELLS) == WORD_MASK:
        sources.add(shift_state_general(state, NCELLS))
        continue
    target = first_empty_general(layer_mask_general(state, 0, NCELLS), NCELLS)
    for template in templates[target]:
        nxt = apply_template_general(state, template)
        if nxt is None or nxt in seen: continue
        seen.add(nxt)
        queue.append(nxt)

print(f"  Sources: {len(sources)}")

# Macro closure
macro_seen = set(sources)
macro_queue = deque(sources)
succ = {}

while macro_queue:
    src = macro_queue.popleft()
    successors = set()
    explore_seen = {src}
    explore_queue = deque([src])
    
    while explore_queue:
        state = explore_queue.popleft()
        if layer_mask_general(state, 0, NCELLS) == WORD_MASK:
            successors.add(shift_state_general(state, NCELLS))
            continue
        target = first_empty_general(layer_mask_general(state, 0, NCELLS), NCELLS)
        for template in templates[target]:
            nxt = apply_template_general(state, template)
            if nxt is None or nxt in explore_seen: continue
            explore_seen.add(nxt)
            explore_queue.append(nxt)
    
    if successors:
        succ[src] = successors
    
    for s in successors:
        if s not in macro_seen:
            macro_seen.add(s)
            macro_queue.append(s)

print(f"  Macro states: {len(macro_seen)}")
print(f"  Macro edges: {sum(len(v) for v in succ.values())}")

# SCC using networkx? No, we'll use a simple reverse-graph approach

# Build reverse graph
rev_succ = {s: set() for s in macro_seen}
for s, dsts in succ.items():
    for d in dsts:
        rev_succ[d].add(s)

# Verify: for state 0, find all states that can reach 0 and all states reachable from 0
print("\n--- Reachability analysis ---")

# Forward reachable from 0
fwd = {0}
fwd_q = deque([0])
while fwd_q:
    s = fwd_q.popleft()
    for d in succ.get(s, []):
        if d not in fwd:
            fwd.add(d)
            fwd_q.append(d)

# Backward reachable to 0 (reverse graph)
bwd = {0}
bwd_q = deque([0])
while bwd_q:
    s = bwd_q.popleft()
    for p in rev_succ.get(s, []):
        if p not in bwd:
            bwd.add(p)
            bwd_q.append(p)

# SCC containing 0 = intersection of forward and backward reachable
scc0 = fwd & bwd
print(f"  States reachable FROM 0: {len(fwd)}")
print(f"  States that can reach 0: {len(bwd)}")
print(f"  Intersection (SCC of 0): {len(scc0)} states")

if len(scc0) <= 20:
    print(f"  SCC states: {sorted(scc0)}")
else:
    scc_list = sorted(scc0)
    print(f"  First 10 SCC states: {scc_list[:10]}")
    print(f"  Last 10 SCC states: {scc_list[-10:]}")

# Check internal edges in SCC of 0
internal_edges = 0
for s in scc0:
    for d in succ.get(s, []):
        if d in scc0:
            internal_edges += 1
print(f"  Internal edges in SCC of 0: {internal_edges}")

# Check if SCC of 0 has cycles
# Use DFS from each state
print("\n--- Cycle detection in SCC of 0 ---")
scc_list = sorted(scc0)

def find_cycles_in_scc(scc_nodes, succ):
    """Find all simple cycles in the SCC."""
    scc_set = set(scc_nodes)
    adj = {n: sorted([s for s in succ.get(n, []) if s in scc_set]) for n in scc_nodes}
    
    cycles = []
    
    for start in scc_nodes:
        # DFS from start, looking for paths back to start
        stack = [(start, [start], {start})]
        while stack:
            node, path, visited = stack.pop()
            for nxt in adj.get(node, []):
                if nxt == start and len(path) > 1:
                    cycles.append(tuple(path))
                elif nxt not in visited and nxt > start:
                    # Only go to nodes > start to avoid duplicate cycles
                    stack.append((nxt, path + [nxt], visited | {nxt}))
    
    return cycles

cycles = find_cycles_in_scc(scc_list, succ)
print(f"  Simple cycles found: {len(cycles)}")
for c in cycles:
    print(f"    Cycle length {len(c)}: {' -> '.join(str(s) for s in c)}")

# Check the return path of length 6
print("\n--- Return path of length 6 ---")
path_6 = [0, 584134000665, 146100961245, 51590094948, 13086687222, 1048575, 0]
print(f"  Path: {' -> '.join(str(s) for s in path_6)}")
for i in range(len(path_6) - 1):
    s, t = path_6[i], path_6[i+1]
    has_edge = t in succ.get(s, set())
    print(f"    {s} -> {t}: {'YES' if has_edge else 'NO'}")
    if not has_edge:
        print(f"      succ[{s}] = {succ.get(s, set())}")

# Is each state in the path in the SCC of 0?
print("\n  SCC membership of path states:")
for s in path_6:
    print(f"    {s}: {'IN SCC' if s in scc0 else 'NOT IN SCC'}")

# Check 2-state SCCs
print("\n--- Verify 2-state SCCs ---")
# Find all pairs of states that are mutually reachable
mutual_pairs = []
for s in macro_seen:
    for d in succ.get(s, []):
        if d > s and s in rev_succ.get(d, set()) and s in succ.get(d, set()):
            # Check if they form a 2-cycle
            # Also check if they form a 2-SCC (mutual reachability)
            # Forward reachable from s (within {s, d})
            # Backward reachable to s (within {s, d})
            pass
            mutual_pairs.append((s, d))

print(f"  Mutual 2-cycles (a<->b): {len(mutual_pairs)}")
for s, d in mutual_pairs[:10]:
    print(f"    {s} <-> {d}")