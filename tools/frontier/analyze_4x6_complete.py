#!/usr/bin/env python3
"""
Complete 4×6 Macro state-graph analysis for S-pentacube.

Computes:
- Full macro closure (known to be complete: 31,738 states)
- SCC decomposition (Kosaraju)
- Cycle enumeration
- Return path analysis
- Tileable thicknesses
"""
from __future__ import annotations

import json
import math
import sys
import time
from collections import deque, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements

A, B = 4, 6
NCELLS = A * B
WORD_MASK = (1 << NCELLS) - 1

# ============================================================================
# Helper functions (from macro_generalized.py)
# ============================================================================

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

# ============================================================================
# SCC computation (Kosaraju)
# ============================================================================

def compute_sccs(succ, all_nodes):
    """Compute all SCCs using Kosaraju's algorithm (two-pass)."""
    rev = {s: set() for s in all_nodes}
    for s, dsts in succ.items():
        for d in dsts:
            rev[d].add(s)

    visited = set()
    order = []

    def dfs1(node):
        stack = [(node, 0)]
        while stack:
            n, state = stack.pop()
            if state == 0:
                if n in visited:
                    continue
                visited.add(n)
                stack.append((n, 1))
                for nxt in sorted(succ.get(n, [])):
                    if nxt not in visited:
                        stack.append((nxt, 0))
            else:
                order.append(n)

    for n in all_nodes:
        if n not in visited:
            dfs1(n)

    visited2 = set()
    sccs = []

    def dfs2(node, scc):
        stack = [node]
        while stack:
            n = stack.pop()
            if n in visited2:
                continue
            visited2.add(n)
            scc.add(n)
            for nxt in sorted(rev.get(n, [])):
                if nxt not in visited2:
                    stack.append(nxt)

    for n in reversed(order):
        if n not in visited2:
            scc = set()
            dfs2(n, scc)
            sccs.append(scc)

    return sccs


def find_cycles_in_scc(scc_nodes, succ):
    """Find all simple cycles in an SCC."""
    scc_set = set(scc_nodes)
    adj = {n: sorted([s for s in succ.get(n, []) if s in scc_set]) for n in scc_nodes}

    cycles = []
    for start in sorted(scc_nodes):
        stack = [(start, [start], {start})]
        while stack:
            node, path, visited = stack.pop()
            for nxt in adj.get(node, []):
                if nxt == start and len(path) > 1:
                    canon = tuple(path)
                    cycles.append(canon)
                elif nxt not in visited and nxt > start:
                    stack.append((nxt, path + [nxt], visited | {nxt}))

    seen_cycles = set()
    unique_cycles = []
    for c in cycles:
        m = min(c)
        idx = c.index(m)
        normalized = c[idx:] + c[1:idx+1]
        if normalized not in seen_cycles:
            seen_cycles.add(normalized)
            unique_cycles.append(normalized)

    return unique_cycles


# ============================================================================
# Main analysis
# ============================================================================

def main():
    print("=" * 70)
    print("COMPLETE 4×6 S-PENTACUBE MACRO STATE GRAPH ANALYSIS")
    print("=" * 70)
    print()
    t0 = time.perf_counter()

    # Build templates
    print("Building templates...")
    templates, NCELLS, WORD_MASK, concrete_count, total_templates = build_templates_general(A, B)
    print(f"  NCELLS={NCELLS}, state size={3*NCELLS} bits")
    print(f"  Concrete placements: {concrete_count}")
    print(f"  Target templates: {total_templates}")
    print()

    # Phase 1: First generation
    print("Computing first-generation sources...")
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
    print(f"  First-gen sources: {len(sources)}")
    print(f"  First-gen tree states: {len(seen)}")
    print()

    # Phase 2: Macro closure
    print("Computing macro closure...")
    macro_seen = set(sources)
    macro_queue = deque(sources)
    succ = {}
    total_intermediate = 0

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
        total_intermediate += len(explore_seen) - 1
        if successors:
            succ[src] = successors
        for s in successors:
            if s not in macro_seen:
                macro_seen.add(s)
                macro_queue.append(s)

    print(f"  Macro states: {len(macro_seen)}")
    print(f"  Macro edges: {sum(len(v) for v in succ.values())}")
    print(f"  Total intermediate: {total_intermediate}")
    print(f"  State 0 reachable: {0 in macro_seen}")
    print()

    # Graph statistics
    print("--- Graph Statistics ---")
    out_degrees = [len(succ.get(s, [])) for s in macro_seen]
    print(f"  Max out-degree: {max(out_degrees)}")
    print(f"  Mean out-degree: {sum(out_degrees)/len(out_degrees):.2f}")
    print(f"  Zero-out-degree states: {sum(1 for d in out_degrees if d == 0)}")

    in_degrees = defaultdict(int)
    for s, dsts in succ.items():
        for d in dsts:
            in_degrees[d] += 1
    for s in macro_seen:
        if s not in in_degrees:
            in_degrees[s] = 0
    in_deg_list = list(in_degrees.values())
    print(f"  Max in-degree: {max(in_deg_list)}")
    print(f"  Mean in-degree: {sum(in_deg_list)/len(in_deg_list):.2f}")
    print(f"  Zero-in-degree states: {sum(1 for d in in_deg_list if d == 0)}")
    print()

    # SCC decomposition
    print("--- SCC Decomposition (Kosaraju) ---")
    sccs = compute_sccs(succ, macro_seen)
    print(f"  Total SCCs: {len(sccs)}")

    nontrivial = [scc for scc in sccs if len(scc) > 1]
    trivial = [scc for scc in sccs if len(scc) == 1]
    print(f"  Trivial SCCs: {len(trivial)}")
    print(f"  Nontrivial SCCs: {len(nontrivial)}")

    for i, scc in enumerate(sccs):
        scc_list = sorted(scc)
        internal_edges = sum(1 for s in scc for t in succ.get(s, []) if t in scc)
        outgoing_edges = sum(1 for s in scc for t in succ.get(s, []) if t not in scc)
        is_trapping = outgoing_edges == 0
        has_0 = 0 in scc
        cycles_here = find_cycles_in_scc(scc_list, succ) if len(scc) > 1 else []
        cyc_len = sorted(set(len(c) for c in cycles_here))
        print(f"  SCC #{i}: {len(scc)} states, {internal_edges} internal, "
              f"{outgoing_edges} outgoing, "
              f"{'TRAPPING' if is_trapping else 'non-trapping'}, "
              f"{'contains 0' if has_0 else ''}"
              f"{', cycles: ' + str(cyc_len) if cyc_len else ''}")

    # Find SCC containing 0
    scc0 = None
    scc0_idx = None
    for i, scc in enumerate(sccs):
        if 0 in scc:
            scc0 = scc
            scc0_idx = i
            break

    print(f"\n  SCC of 0: SCC #{scc0_idx}, {len(scc0)} states")
    print(f"  States in SCC of 0: {sorted(scc0)}")
    print()

    # Cycles in SCC of 0
    print("--- Cycles in SCC of 0 ---")
    cycles0 = find_cycles_in_scc(scc0, succ)
    print(f"  Simple cycles found: {len(cycles0)}")
    for c in cycles0:
        print(f"    Length {len(c)}: {' -> '.join(str(s) for s in c)}")
    cycle_lengths = sorted(set(len(c) for c in cycles0))
    print(f"  Cycle lengths: {cycle_lengths}")
    if cycle_lengths:
        gcd_cycles = math.gcd(*cycle_lengths) if len(cycle_lengths) > 1 else cycle_lengths[0]
        print(f"  GCD of cycle lengths: {gcd_cycles}")
    print()

    # Check if SCC of 0 has all cycles
    all_scc_cycles = []
    for scc in nontrivial:
        all_scc_cycles.extend(find_cycles_in_scc(scc, succ))
    all_cycle_lengths = sorted(set(len(c) for c in all_scc_cycles))
    print(f"  Total cycles across all SCCs: {len(all_scc_cycles)}")
    print(f"  All cycle lengths: {all_cycle_lengths}")
    print()

    # Return path analysis
    print("--- Return Path Analysis ---")
    distances = {0: {0}}
    queue = deque([0])
    processed = set()
    while queue:
        state = queue.popleft()
        if state in processed: continue
        processed.add(state)
        for nxt in succ.get(state, []):
            for d in distances[state]:
                nd = d + 1
                if nxt not in distances:
                    distances[nxt] = set()
                if nd not in distances[nxt]:
                    distances[nxt].add(nd)
                    queue.append(nxt)

    return_lengths = sorted(distances.get(0, set()))
    positive_returns = [r for r in return_lengths if r > 0]
    print(f"  Return lengths from 0 to 0: {positive_returns}")
    print(f"  Shortest positive return: {min(positive_returns) if positive_returns else 'N/A'}")
    if positive_returns:
        gcd_returns = math.gcd(*positive_returns) if len(positive_returns) > 1 else positive_returns[0]
        print(f"  GCD of return lengths: {gcd_returns}")
    print()

    # Tileable N
    print("--- Tileable N ---")
    print(f"  Tileable N: {positive_returns}")
    print(f"  Total tileable thicknesses: {len(positive_returns)}")
    print()

    # Depth distribution
    print("--- Depth Distribution ---")
    depth = {}
    queue = deque()
    for s in sources:
        depth[s] = 0
        queue.append(s)
    while queue:
        state = queue.popleft()
        for nxt in succ.get(state, []):
            if nxt not in depth:
                depth[nxt] = depth[state] + 1
                queue.append(nxt)
    max_depth = max(depth.values()) if depth else 0
    print(f"  Max depth from sources: {max_depth}")
    depth_dist = defaultdict(int)
    for d in depth.values():
        depth_dist[d] += 1
    for d in sorted(depth_dist.keys()):
        print(f"    Depth {d}: {depth_dist[d]} states")
    print()

    # Condensation graph
    print("--- Condensation Graph ---")
    scc_of = {}
    for i, scc in enumerate(sccs):
        for s in scc:
            scc_of[s] = i
    cond_edges = defaultdict(set)
    for s, dsts in succ.items():
        si = scc_of[s]
        for d in dsts:
            di = scc_of[d]
            if si != di:
                cond_edges[si].add(di)
    print(f"  Condensation edges: {sum(len(v) for v in cond_edges.values())}")
    print(f"  Condensation is a DAG (by construction)")
    print()

    # Out-degree distribution
    print("--- Out-Degree Distribution ---")
    deg_counts = defaultdict(int)
    for d in out_degrees:
        deg_counts[d] += 1
    for d in sorted(deg_counts.keys()):
        print(f"  Out-degree {d}: {deg_counts[d]} states")
    print()

    # ========================================================================
    # Save data
    # ========================================================================
    print("--- Saving Data ---")
    data_dir = REPO_ROOT / "data" / "frontier"
    data_dir.mkdir(parents=True, exist_ok=True)

    state_list = sorted(macro_seen)

    # States
    with open(data_dir / "s_4x6_states.txt", "w") as f:
        for s in state_list:
            f.write(f"{s}\n")
    print(f"  States: {data_dir / 's_4x6_states.txt'}")

    # Edges
    with open(data_dir / "s_4x6_edges.txt", "w") as f:
        for src in sorted(succ.keys()):
            dsts = sorted(succ[src])
            f.write(f"{src} -> {' '.join(str(d) for d in dsts)}\n")
    print(f"  Edges: {data_dir / 's_4x6_edges.txt'}")

    # SCCs
    with open(data_dir / "s_4x6_sccs.txt", "w") as f:
        for i, scc in enumerate(sccs):
            scc_list = sorted(scc)
            internal_edges = sum(1 for s in scc for t in succ.get(s, []) if t in scc)
            outgoing_edges = sum(1 for s in scc for t in succ.get(s, []) if t not in scc)
            is_trapping = outgoing_edges == 0
            f.write(f"SCC {i}: {len(scc_list)} states, {internal_edges} internal, "
                    f"{outgoing_edges} outgoing, "
                    f"{'trapping' if is_trapping else 'non-trapping'}, "
                    f"{'contains 0' if 0 in scc else ''}\n")
            for s in scc_list:
                f.write(f"  {s}\n")
    print(f"  SCCs: {data_dir / 's_4x6_sccs.txt'}")

    # Cycles
    with open(data_dir / "s_4x6_cycles.txt", "w") as f:
        f.write(f"Total simple cycles: {len(all_scc_cycles)}\n")
        f.write(f"Cycle lengths: {all_cycle_lengths}\n")
        if all_cycle_lengths:
            gcd_all = math.gcd(*all_cycle_lengths) if len(all_cycle_lengths) > 1 else all_cycle_lengths[0]
            f.write(f"GCD of cycle lengths: {gcd_all}\n")
        f.write("\n--- Cycles ---\n")
        for i, c in enumerate(all_scc_cycles):
            f.write(f"Cycle {i+1} (len={len(c)}): {' -> '.join(str(s) for s in c)}\n")
    print(f"  Cycles: {data_dir / 's_4x6_cycles.txt'}")

    # Returns
    with open(data_dir / "s_4x6_returns.txt", "w") as f:
        f.write(f"Positive return lengths from 0 to 0: {positive_returns}\n")
        f.write(f"Shortest positive return: {min(positive_returns) if positive_returns else 'N/A'}\n")
        f.write(f"Total distinct return lengths: {len(positive_returns)}\n")
        if positive_returns:
            gcd_returns = math.gcd(*positive_returns) if len(positive_returns) > 1 else positive_returns[0]
            f.write(f"GCD of return lengths: {gcd_returns}\n")
        f.write(f"\nTileable N: {positive_returns}\n")
    print(f"  Returns: {data_dir / 's_4x6_returns.txt'}")

    # Summary JSON
    summary = {
        "a": A, "b": B,
        "NCELLS": NCELLS,
        "state_size_bits": 3 * NCELLS,
        "concrete_placements": concrete_count,
        "target_templates": total_templates,
        "first_gen_sources": len(sources),
        "first_gen_tree_states": len(seen),
        "total_states": len(macro_seen),
        "total_edges": sum(len(v) for v in succ.values()),
        "total_intermediate": total_intermediate,
        "max_out_degree": max(out_degrees),
        "max_in_degree": max(in_deg_list),
        "zero_out_degree_count": sum(1 for d in out_degrees if d == 0),
        "zero_in_degree_count": sum(1 for d in in_deg_list if d == 0),
        "scc_count": len(sccs),
        "nontrivial_scc_count": len(nontrivial),
        "trivial_scc_count": len(trivial),
        "scc0_id": scc0_idx,
        "scc0_size": len(scc0),
        "scc0_internal_edges": sum(1 for s in scc0 for t in succ.get(s, []) if t in scc0),
        "cycle_count": len(all_scc_cycles),
        "cycle_lengths": all_cycle_lengths,
        "positive_returns": positive_returns,
        "shortest_return": min(positive_returns) if positive_returns else None,
        "tileable_N": positive_returns,
        "max_depth": max_depth,
        "elapsed": time.perf_counter() - t0,
    }
    with open(data_dir / "s_4x6_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  Summary: {data_dir / 's_4x6_summary.json'}")

    print(f"\nTotal elapsed: {time.perf_counter() - t0:.2f}s")
    print("\nDone!")

    return summary, sccs, scc0, cycles0, positive_returns

if __name__ == "__main__":
    main()