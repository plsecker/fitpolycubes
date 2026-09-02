#!/usr/bin/env python3
"""
Complete Macro-closure analysis for the V pentacube on small cross-sections.

Phase 6/8/9 machinery for docs/frontier/v_piece/v_macro_investigation.md.

Computes, for piece V on cross-section a×b (default 3×5):
  - complete reachable macro graph (first-generation completeness asserted);
  - all SCCs, recurrent SCCs, transient states;
  - SCC(0): size, edges, out-degree distribution;
  - graph period of SCC(0) (classic BFS-delta method) and via cycle-length gcd;
  - all *primitive* simple-cycle lengths through state 0 (exhaustive DFS,
    sound only because SCC(0) is small);
  - terminal-predecessor structure of state 0 (gate analysis, Phase 9);
  - numerical semigroup of primitive cycle lengths;
  - JSON dump for data/frontier/v_piece/.

Usage:
    python3 tools/frontier/v_piece/analyze_v_closure.py [--a 3 --b 5] [--out PATH]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from collections import Counter, deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.frontier.macro_explorer import macro_closure
from tools.frontier.piece_utils import layer_mask


# ---------------------------------------------------------------------------
# Graph helpers (piece-agnostic)
# ---------------------------------------------------------------------------

def reverse_graph(succ: dict[int, set[int]]) -> dict[int, set[int]]:
    rev: dict[int, set[int]] = {}
    for src, dsts in succ.items():
        for dst in dsts:
            rev.setdefault(dst, set()).add(src)
    return rev


def tarjan_sccs(succ: dict[int, set[int]]) -> list[list[int]]:
    """Iterative Tarjan over the explicit successor map."""
    index_counter = 0
    index: dict[int, int] = {}
    lowlink: dict[int, int] = {}
    on_stack: set[int] = set()
    stack: list[int] = []
    result: list[list[int]] = []

    for root in succ:
        if root in index:
            continue
        work = [(root, iter(sorted(succ.get(root, ()))))]
        index[root] = lowlink[root] = index_counter
        index_counter += 1
        stack.append(root)
        on_stack.add(root)
        while work:
            v, it = work[-1]
            advanced = False
            for w in it:
                if w not in index:
                    index[w] = lowlink[w] = index_counter
                    index_counter += 1
                    stack.append(w)
                    on_stack.add(w)
                    work.append((w, iter(sorted(succ.get(w, ())))))
                    advanced = True
                    break
                elif w in on_stack:
                    lowlink[v] = min(lowlink[v], index[w])
            if advanced:
                continue
            work.pop()
            if work:
                pv = work[-1][0]
                lowlink[pv] = min(lowlink[pv], lowlink[v])
            if lowlink[v] == index[v]:
                comp = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    comp.append(w)
                    if w == v:
                        break
                result.append(sorted(comp))
    return result


def scc_period(succ: dict[int, set[int]], nodes: set[int]) -> int:
    """Classic period: gcd over edges of (dist[v]-dist[u]-1) from a BFS tree."""
    root = next(iter(nodes))
    dist = {root: 0}
    q = deque([root])
    while q:
        u = q.popleft()
        for v in succ.get(u, ()):
            if v in nodes and v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    g = 0
    for u in nodes:
        for v in succ.get(u, ()):
            if v in nodes:
                g = math.gcd(g, dist[v] - dist[u] - 1)
    return g if g > 0 else 1


def all_simple_cycles_through_zero(
    succ: dict[int, set[int]], scc_nodes: set[int], max_len_cap: int = 10_000
) -> list[list[int]]:
    """Exhaustive simple-cycle enumeration starting and ending at 0.

    Exponential in principle; sound here because SCC(0) is small.
    Returns each cycle as node list [0, x1, ..., 0].
    """
    cycles: list[list[int]] = []
    path: list[int] = [0]
    on_path = {0}

    def dfs(cur: int):
        if len(path) > max_len_cap:
            raise RuntimeError("cycle search exceeded cap")
        for nxt in sorted(succ.get(cur, ())):
            if nxt not in scc_nodes:
                continue
            if nxt == 0:
                cycles.append(path[:] + [0])
            elif nxt not in on_path:
                path.append(nxt)
                on_path.add(nxt)
                dfs(nxt)
                path.pop()
                on_path.discard(nxt)

    dfs(0)
    return cycles


def cycle_length_spectrum(cycles: list[list[int]]) -> Counter:
    return Counter(len(c) - 1 for c in cycles)


def primitive_lengths(lengths: set[int]) -> list[int]:
    """Minimal generators: drop any length that is a nonneg combination of others."""
    gens: list[int] = []
    for l in sorted(lengths):
        if l == 0:
            continue
        # check representability by current gens (bounded DP)
        reach = {0}
        frontier = True
        reps = {0}
        # bounded search up to l
        possible = False
        stack = [0]
        seen = set()
        while stack:
            x = stack.pop()
            for g in gens:
                y = x + g
                if y == l:
                    possible = True
                    stack = []
                    break
                if y < l and y not in seen:
                    seen.add(y)
                    stack.append(y)
            if possible:
                break
        if not possible:
            gens.append(l)
    return gens


def semigroup_membership(gens: list[int], limit: int) -> tuple[set[int], list[int]]:
    """Return (representable numbers ≤ limit, gaps ≤ limit)."""
    reach = {0}
    frontier = [0]
    while frontier:
        nxt = []
        for x in frontier:
            for g in gens:
                y = x + g
                if y <= limit and y not in reach:
                    reach.add(y)
                    nxt.append(y)
        frontier = nxt
    gaps = [n for n in range(limit + 1) if n not in reach]
    return reach, gaps


# ---------------------------------------------------------------------------
# Gate / terminal structure (Phase 9)
# ---------------------------------------------------------------------------

def analyze_terminal_predecessors(
    succ: dict[int, set[int]], NCELLS: int
) -> dict:
    """Classify predecessors of state 0."""
    rev = reverse_graph(succ)
    preds = sorted(rev.get(0, set()))
    WM = (1 << NCELLS) - 1
    rows = []
    for p in preds:
        l0 = layer_mask(p, 0, NCELLS)
        l1 = layer_mask(p, 1, NCELLS)
        l2 = layer_mask(p, 2, NCELLS)
        rows.append({
            "state": p,
            "l0_popcount": bin(l0).count("1"),
            "l1_popcount": bin(l1).count("1"),
            "l2_popcount": bin(l2).count("1"),
            "l1_empty": l1 == 0,
            "l2_empty": l2 == 0,
            "is_gate_FULL000": p == WM,
        })
    return {
        "predecessor_count": len(preds),
        "predecessors": rows,
        "all_have_l1_l2_empty": all(r["l1_empty"] and r["l2_empty"] for r in rows),
        "any_is_classic_gate": any(r["is_gate_FULL000"] for r in rows),
        "distinct_l0_popcounts": sorted({r["l0_popcount"] for r in rows}),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", type=int, default=3)
    ap.add_argument("--b", type=int, default=5)
    ap.add_argument("--max-states", type=int, default=20_000_000)
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()

    t0 = time.perf_counter()
    macro_seen, succ, sources, stats = macro_closure(
        args.piece_letter if hasattr(args, "piece_letter") else "V",
        args.a, args.b,
        max_states=args.max_states, verbose=False,
    )
    closure_s = time.perf_counter() - t0

    assert stats["zero_reachable"], "V must be cyclic on this cross-section"
    assert not stats["first_gen_cap_hit"] and not stats["macro_cap_hit"], \
        "closure incomplete — refusing to analyse"

    NCELLS = stats["NCELLS"]
    nodes = set(macro_seen)

    # ---- SCCs ----
    t1 = time.perf_counter()
    sccs = tarjan_sccs(succ)
    sccs_sorted = sorted(sccs, key=len, reverse=True)
    cyclic_sccs = []
    for comp in sccs:
        if len(comp) > 1:
            cyclic_sccs.append(comp)
        else:
            u = comp[0]
            if u in succ.get(u, ()):
                cyclic_sccs.append(comp)
    transient = sum(len(c) for c in sccs if c not in cyclic_sccs)

    # ---- SCC(0) ----
    comp_of = {}
    for i, comp in enumerate(sccs):
        for u in comp:
            comp_of[u] = i
    scc0 = set(sccs[comp_of[0]])
    scc0_edges = sum(len([v for v in succ.get(u, ()) if v in scc0]) for u in scc0)

    # ---- period ----
    period = scc_period(succ, scc0)

    # ---- cycles through 0 ----
    cycles = all_simple_cycles_through_zero(succ, scc0)
    spec = cycle_length_spectrum(cycles)
    lengths = sorted(spec)
    prims = primitive_lengths(set(lengths))
    g_cd = 0
    for l in lengths:
        g_cd = math.gcd(g_cd, l)

    # ---- out-degree distribution within whole graph and SCC(0) ----
    outdeg_all = Counter(len(succ.get(u, ())) for u in nodes)
    outdeg_scc0 = Counter(
        len([v for v in succ.get(u, ()) if v in scc0]) for u in scc0
    )

    # ---- gate structure ----
    gates = analyze_terminal_predecessors(succ, NCELLS)

    # ---- semigroup ----
    reach, gaps = semigroup_membership(prims, 120)

    analysis = {
        "piece": "V",
        "cross_section": {"a": args.a, "b": args.b},
        "closure": {
            "complete": True,
            "concrete_placements": stats["concrete_placements"],
            "templates": stats["target_templates"],
            "first_gen_sources": stats["first_gen_sources"],
            "first_gen_tree_states": stats["first_gen_tree_states"],
            "macro_states": len(nodes),
            "macro_edges": stats["macro_edges"],
            "total_intermediate": stats["total_intermediate"],
            "closure_seconds": round(closure_s, 3),
            "analysis_seconds": round(time.perf_counter() - t1, 3),
        },
        "sccs": {
            "count": len(sccs),
            "cyclic_count": len(cyclic_sccs),
            "sizes_top10": [len(c) for c in sccs_sorted[:10]],
            "transient_states": transient,
        },
        "scc0": {
            "size": len(scc0),
            "internal_edges": scc0_edges,
            "period_bfs": period,
            "period_cycle_gcd": g_cd,
            "simple_cycle_count": len(cycles),
            "cycle_length_spectrum": {str(k): v for k, v in sorted(spec.items())},
            "primitive_lengths": prims,
            "shortest_cycle": min(lengths),
            "period_lt_shortest_cycle": period < min(lengths),
            "out_degree_distribution": {str(k): v for k, v in sorted(outdeg_scc0.items())},
        },
        "graph_out_degree_distribution": {str(k): v for k, v in sorted(outdeg_all.items())},
        "terminal_predecessors": gates,
        "semigroup": {
            "generators_primitive": prims,
            "gcd": g_cd,
            "representable_up_to_120_sample": sorted(x for x in reach if x <= 40),
            "gaps_up_to_40": [x for x in gaps if x <= 40],
        },
        "cycles_first5": [[str(x) for x in c] for c in cycles[:5]],
    }

    print(json.dumps({k: v for k, v in analysis.items() if k != "cycles_first5"},
                     indent=2)[:4000])

    out = args.out or str(
        REPO_ROOT / f"data/frontier/v_piece/v_{args.a}x{args.b}_closure_analysis.json")
    with open(out, "w") as f:
        json.dump(analysis, f, indent=2)
    print("\nwrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
