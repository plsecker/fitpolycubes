#!/usr/bin/env python3
"""
Structural analysis of 4×4 and 4×7 S-pentacube macro graphs.
"""
from __future__ import annotations

import sys
import math
from collections import deque, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements

def make_shifted_template_general(placement_cells, target_z, a, b):
    NCELLS = a * b
    min_z = min(z for _, _, z in placement_cells)
    shifted_masks = [0] * 3
    target_rel = target_z - min_z
    for x, y, z in placement_cells:
        rel = z - min_z - target_rel
        if rel < 0 or rel >= 3:
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
    return result, NCELLS, concrete_count, total_templates

def layer_mask(state, layer, NCELLS):
    return (state >> (layer * NCELLS)) & ((1 << NCELLS) - 1)

def first_empty(mask, NCELLS):
    WORD_MASK = (1 << NCELLS) - 1
    missing = WORD_MASK & ~mask
    if not missing: return -1
    low = missing & -missing
    return low.bit_length() - 1

def apply_template(state, template):
    if state & template: return None
    return state | template

def shift_state(state, NCELLS):
    return state >> NCELLS

def count_bits(mask):
    return bin(mask).count("1")

def analyze_cross_section(a, b, label):
    print(f"\n{'='*70}")
    print(f"ANALYSIS: {label} (a={a}, b={b})")
    print(f"{'='*70}")
    
    templates, NCELLS, concrete_count, total_templates = build_templates_general(a, b)
    WORD_MASK = (1 << NCELLS) - 1
    
    print(f"  NCELLS={NCELLS}, state size={3*NCELLS} bits")
    print(f"  Concrete placements: {concrete_count}")
    print(f"  Target templates: {total_templates}")
    
    # Template analysis
    print(f"\n  Template analysis:")
    for cell in range(NCELLS):
        n_templates = len(templates[cell])
        if n_templates > 0:
            first_t = templates[cell][0]
            l0 = (first_t >> (0 * NCELLS)) & WORD_MASK
            l1 = (first_t >> (1 * NCELLS)) & WORD_MASK
            l2 = (first_t >> (2 * NCELLS)) & WORD_MASK
            print(f"    Cell {cell} ({cell%a},{cell//a}): {n_templates} templates (L0:{count_bits(l0)} L1:{count_bits(l1)} L2:{count_bits(l2)})")
    
    # Analyze first-gen sources
    seen = {0}
    queue = deque([0])
    sources = set()
    source_layer_masks = []
    
    while queue:
        state = queue.popleft()
        if layer_mask(state, 0, NCELLS) == WORD_MASK:
            shifted = shift_state(state, NCELLS)
            sources.add(shifted)
            source_layer_masks.append((
                layer_mask(shifted, 0, NCELLS),
                layer_mask(shifted, 1, NCELLS),
                layer_mask(shifted, 2, NCELLS),
            ))
            continue
        target = first_empty(layer_mask(state, 0, NCELLS), NCELLS)
        for template in templates[target]:
            nxt = apply_template(state, template)
            if nxt is None or nxt in seen: continue
            seen.add(nxt)
            queue.append(nxt)
    
    print(f"\n  First-gen: {len(sources)} sources, {len(seen)} tree states")
    
    # Analyze source layer patterns
    if source_layer_masks:
        patterns = defaultdict(int)
        for l0, l1, l2 in source_layer_masks:
            pattern = (count_bits(l0), count_bits(l1), count_bits(l2))
            patterns[pattern] += 1
        print(f"  Source layer patterns:")
        for pattern, count in sorted(patterns.items(), key=lambda x: -x[1]):
            print(f"    (L0={pattern[0]}, L1={pattern[1]}, L2={pattern[2]}): {count} sources")
        
        # Check proportion with L2=0
        l2_zero = sum(1 for _, _, l2 in source_layer_masks if l2 == 0)
        print(f"  Sources with L2=0: {l2_zero}/{len(source_layer_masks)}")
    
    # Macro closure analysis
    macro_seen = set(sources)
    macro_queue = deque(sources)
    succ = {}
    node_count = 0
    
    while macro_queue:
        src = macro_queue.popleft()
        successors = set()
        explore_seen = {src}
        explore_queue = deque([src])
        
        while explore_queue:
            state = explore_queue.popleft()
            if layer_mask(state, 0, NCELLS) == WORD_MASK:
                successors.add(shift_state(state, NCELLS))
                continue
            target = first_empty(layer_mask(state, 0, NCELLS), NCELLS)
            for template in templates[target]:
                nxt = apply_template(state, template)
                if nxt is None or nxt in explore_seen: continue
                explore_seen.add(nxt)
                explore_queue.append(nxt)
        
        if successors:
            succ[src] = successors
        
        for s in successors:
            if s not in macro_seen:
                macro_seen.add(s)
                macro_queue.append(s)
    
    print(f"\n  Macro closure: {len(macro_seen)} states, {sum(len(v) for v in succ.values())} edges")
    print(f"  State 0 in graph: {0 in macro_seen}")
    
    # Check for cycles
    # Build reverse graph
    rev = {s: set() for s in macro_seen}
    for s, dsts in succ.items():
        for d in dsts:
            rev[d].add(s)
    
    # Check if graph is a DAG via topological sort
    in_deg = {s: 0 for s in macro_seen}
    for s, dsts in succ.items():
        for d in dsts:
            in_deg[d] += 1
    
    q = deque([s for s in macro_seen if in_deg[s] == 0])
    order = []
    while q:
        node = q.popleft()
        order.append(node)
        for nxt in succ.get(node, []):
            in_deg[nxt] -= 1
            if in_deg[nxt] == 0:
                q.append(nxt)
    
    is_dag = len(order) == len(macro_seen)
    print(f"  Graph is DAG: {is_dag}")
    
    if not is_dag:
        # Find SCCs (Kosaraju)
        visited = set()
        order2 = []
        for n in sorted(macro_seen):
            if n not in visited:
                stack = [(n, 0)]
                while stack:
                    node, state = stack.pop()
                    if state == 0:
                        if node in visited: continue
                        visited.add(node)
                        stack.append((node, 1))
                        for nxt in sorted(succ.get(node, [])):
                            if nxt not in visited:
                                stack.append((nxt, 0))
                    else:
                        order2.append(node)
        
        visited2 = set()
        nontrivial = 0
        for n in reversed(order2):
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
                if len(scc) > 1:
                    nontrivial += 1
                    print(f"  Nontrivial SCC: {len(scc)} states")
                    if 0 in scc:
                        print(f"    ** Contains state 0 **")
        
        print(f"  Nontrivial SCCs: {nontrivial}")
    
    # Depth distribution
    depth = {}
    q = deque()
    for s in sources:
        depth[s] = 0
        q.append(s)
    while q:
        state = q.popleft()
        for nxt in succ.get(state, []):
            if nxt not in depth:
                depth[nxt] = depth[state] + 1
                q.append(nxt)
    
    if depth:
        max_depth = max(depth.values())
        print(f"  Max depth from sources: {max_depth}")
        
        depth_dist = defaultdict(int)
        for d in depth.values():
            depth_dist[d] += 1
        print(f"  Depth distribution:")
        for d in sorted(depth_dist.keys()):
            print(f"    Depth {d}: {depth_dist[d]} states")
    
    return macro_seen, succ, sources

# Run analysis
analyze_cross_section(4, 4, "4×4")
analyze_cross_section(4, 7, "4×7")