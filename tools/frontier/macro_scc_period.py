#!/usr/bin/env python3
"""
Macro SCC period analysis for S-pentacube Macro graphs.

Computes:
- SCC size and edge count
- Graph-theoretic period d = gcd of all closed walk lengths
- Period classes C0, C1, ..., C_{d-1}
- Weighted quotient after collapsing deterministic chains
- Cycle-length gcd (from primitive cycles or observed lengths)
"""

import sys
from collections import defaultdict, deque
import math


def compute_period_classic(succ: dict) -> int:
    """Compute graph period using the classic BFS-distance method.
    
    For a strongly connected directed graph G = (V, E):
    1. Pick arbitrary root r
    2. For each v, let d[v] = distance from r to v in a spanning tree
    3. For each edge u->v, compute delta = d[v] - d[u] - 1
    4. Period = gcd of all such deltas
    
    Returns the period d ≥ 1.
    """
    if not succ:
        return 1
    
    # Collect all vertices
    vertices = set(succ.keys())
    for dsts in succ.values():
        for d in dsts:
            vertices.add(d)
    
    # BFS from an arbitrary root
    root = next(iter(succ.keys()))
    dist = {root: 0}
    q = deque([root])
    parent = {root: None}
    
    while q:
        u = q.popleft()
        for v in succ.get(u, []):
            if v not in dist:
                dist[v] = dist[u] + 1
                parent[v] = u
                q.append(v)
    
    # Compute gcd of cycle closing deltas
    g = 0
    for u in succ:
        if u not in dist:
            continue
        for v in succ.get(u, []):
            if v not in dist:
                continue
            delta = dist[v] - dist[u] - 1
            g = math.gcd(g, delta)
    
    return g if g > 0 else 1


def compute_period_classes(succ: dict) -> tuple:
    """Compute period d and period classes C0..C_{d-1}.
    
    Returns (period, {vertex: class_id}).
    """
    period = compute_period_classic(succ)
    
    if period <= 1:
        return period, {v: 0 for v in set(succ.keys()) for dsts in succ.values() for v in [v] + list(dsts)}
    
    # Compute distances from root
    root = next(iter(succ.keys()))
    dist = {root: 0}
    q = deque([root])
    while q:
        u = q.popleft()
        for v in succ.get(u, []):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    
    # Class = dist[v] mod period
    classes = {}
    for v in dist:
        classes[v] = dist[v] % period
    
    return period, classes


def collapse_deterministic(succ: dict) -> tuple:
    """Collapse out-degree-1 chains into weighted edges.
    
    Returns (quotient_succ, state_to_component, component_weight).
    """
    # Find states with out-degree ≠ 1 (branching/merge points)
    out_deg = {v: len(succ.get(v, [])) for v in set(succ.keys())}
    in_deg = defaultdict(int)
    for u, dsts in succ.items():
        for v in dsts:
            in_deg[v] += 1
    
    # Branching/merge set = states that are NOT simple chain nodes
    all_v = set(succ.keys())
    for dsts in succ.values():
        for d in dsts:
            all_v.add(d)
    
    # Chain nodes: out-degree 1 AND in-degree 1 AND not source/sink
    is_branch = {v: (out_deg.get(v, 0) != 1 or in_deg.get(v, 0) != 1) for v in all_v}
    # Keep state 0 and gate as branch points
    for v in all_v:
        if v == 0:
            is_branch[v] = True
    
    # Build quotient: each branch point maps to itself; chains collapse
    comp_of = {}
    for v in all_v:
        if is_branch[v]:
            comp_of[v] = v
        else:
            comp_of[v] = None  # will be resolved
    
    # Resolve chain membership by following forward
    for v in all_v:
        if comp_of[v] is not None:
            continue
        # Follow forward until branch point
        chain = []
        cur = v
        while cur is not None and comp_of.get(cur) is None:
            chain.append(cur)
            nxt = succ.get(cur, [None])[0] if succ.get(cur, []) else None
            comp_of[cur] = v  # temporary
            cur = nxt
        # All chain nodes map to the final branch point
        target = cur if cur is not None else v
        for c in chain:
            comp_of[c] = target
    
    # Build quotient edges with weights
    quot_succ = defaultdict(list)
    for u in succ:
        cu = comp_of.get(u, u)
        for v in succ[u]:
            cv = comp_of.get(v, v)
            if cu != cv:
                quot_succ[cu].append(cv)
    
    return dict(quot_succ), comp_of


def analyze_scc(name: str, succ: dict, known_cycles: list = None):
    """Full SCC period analysis."""
    if not succ:
        print(f"\n{'='*60}")
        print(f"{name}: NO SCC DATA AVAILABLE")
        print(f"{'='*60}")
        return
    
    period = compute_period_classic(succ)
    _, classes = compute_period_classes(succ)
    
    # Count class sizes
    class_sizes = defaultdict(int)
    for v, c in classes.items():
        class_sizes[c] += 1
    
    # Collapse deterministic chains
    quot_succ, comp_of = collapse_deterministic(succ)
    quot_period = compute_period_classic(quot_succ)
    
    # Cycle-length gcd (from known cycles)
    cycle_gcd = math.gcd(*known_cycles) if known_cycles and len(known_cycles) > 0 else (known_cycles[0] if known_cycles else None)
    
    # Edge and state counts
    n_states = len(set(succ.keys()) | {v for dsts in succ.values() for v in dsts})
    n_edges = sum(len(dsts) for dsts in succ.values())
    n_quot_states = len(quot_succ)
    n_quot_edges = sum(len(dsts) for dsts in quot_succ.values())
    
    print(f"\n{'='*60}")
    print(f"{name}")
    print(f"{'='*60}")
    print(f"  States: {n_states}")
    print(f"  Edges: {n_edges}")
    print(f"  Graph period d: {period}")
    print(f"  Period classes: {dict(sorted(class_sizes.items()))}")
    print(f"  Known primitive cycles: {known_cycles}")
    print(f"  Cycle-length gcd: {cycle_gcd}")
    print(f"  Period = gcd? {'YES' if cycle_gcd and period == cycle_gcd else ('NO - period=' + str(period) + ' gcd=' + str(cycle_gcd))}")
    print(f"  Quotient states: {n_quot_states}")
    print(f"  Quotient edges: {n_quot_edges}")
    print(f"  Quotient period: {quot_period}")
    print(f"  Quotient period = graph period? {'YES' if quot_period == period else 'NO'}")
    print(f"  Deterministic compression ratio: {n_states}/{n_quot_states} = {n_states/n_quot_states:.1f}x")


if __name__ == "__main__":
    # Test with known SCC data
    print("S-Pentacube Macro SCC Period Analysis")
    print("Usage: Import and call analyze_scc(name, succ_dict, known_cycles)")