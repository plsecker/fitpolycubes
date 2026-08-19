#!/usr/bin/env python3
"""
Enumerate and analyse ALL 129-edge macro walks from 17293822637554016271
to 0 inside the 478-state SCC, using the persisted SCC data.

The reconstruction (reconstruct_130_path.py) found that the number of
129-edge walks from the entry to 0 within the SCC is 2048, i.e. the
macro-level path is NOT unique.  This script:

1. Loads the persisted SCC states and SCC-restricted succ map
   (/tmp/opencode/scc_130_states.npy, scc_130_succ.npy).
2. Recomputes the walk-count DP (must reproduce 2048).
3. Enumerates every walk.
4. Verifies every walk: 129 edges, starts at the entry, ends at 0,
   every edge in the SCC-restricted succ map.
5. Analyses the walk family:
   - how many walks are simple paths (no repeated states)
   - how many contain the known 20-cycle as a contiguous subpath
   - state usage: which SCC states appear in how many walks
   - the set of distinct edges used across all walks
6. Saves all walks to /tmp/opencode/walks_130.txt for the realization
   counting step.
"""

from __future__ import annotations

import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

REPO_ROOT = Path("/home/philip/Work/fitpolycubes")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from solvers.s_z_frontier_packed import WORD_MASK

ENTRY = 17293822637554016271
TARGET = 0
L = 129

SCC_STATES = Path("/tmp/opencode/scc_130_states.npy")
SCC_SUCC = Path("/tmp/opencode/scc_130_succ.npy")
WALKS_OUT = Path("/tmp/opencode/walks_130.txt")
RESULTS_OUT = Path("/tmp/opencode/analyze_130_walks_results.txt")

# Known 20-cycle post-shift states (macro_edge_realizations.py PATH).
CYCLE20 = [
    6163195513375031274,
    13835058072323104239,
    3993075831,
    55840897340952456,
    9838132153049676753,
    2089671021646321023,
    13523993509333176,
    54046496222498049,
    3430478137537398,
    2691607028413209,
    4934612199136503,
    612490719515897646,
    16285016559841080657,
    217229141722890951,
    6729013160573166,
    2297949969,
    1224979683048584328,
    17294878168733286543,
    4294967295,
    0,
]


def load_sub_succ(path: Path):
    succ_arr = np.load(path)
    succ = {}
    i = 0
    n = len(succ_arr)
    while i < n:
        src = int(succ_arr[i])
        num = int(succ_arr[i + 1])
        succ[src] = set(int(x) for x in succ_arr[i + 2:i + 2 + num])
        i += 2 + num
    return succ


def count_walks(sub_succ, target, L):
    C = {u: [0] * (L + 1) for u in sub_succ}
    C[target][0] = 1
    for d in range(1, L + 1):
        for u in sub_succ:
            total = 0
            for v in sub_succ[u]:
                total += C[v][d - 1]
            C[u][d] = total
    return C


def enumerate_all_walks(C, sub_succ, entry, target, L):
    """Enumerate every walk of length L from entry to target."""
    walks = []

    def rec(u, d, path):
        if d == 0:
            if u == target:
                walks.append(list(path))
            return
        for v in sub_succ[u]:
            if C[v][d - 1] > 0:
                path.append(v)
                rec(v, d - 1, path)
                path.pop()

    rec(entry, L, [entry])
    return walks


def cycle_rotations():
    n = len(CYCLE20)
    return [CYCLE20[i:] + CYCLE20[:i] + [CYCLE20[i]] for i in range(n)]


def main() -> int:
    t0 = time.perf_counter()

    print("Loading persisted SCC data...", flush=True)
    scc = set(int(x) for x in np.load(SCC_STATES))
    sub_succ = load_sub_succ(SCC_SUCC)
    print(f"  SCC states: {len(scc)}", flush=True)
    print(f"  SCC edges: {sum(len(v) for v in sub_succ.values())}", flush=True)

    # sanity: all 20-cycle states in the SCC?
    cycle_in_scc = [s for s in CYCLE20 if s not in scc]
    print(f"  20-cycle states in SCC: {len(CYCLE20) - len(cycle_in_scc)}/20", flush=True)
    if cycle_in_scc:
        print(f"  NOT in SCC: {cycle_in_scc}", flush=True)

    print("Computing walk-count DP...", flush=True)
    C = count_walks(sub_succ, TARGET, L)
    count = C[ENTRY][L]
    print(f"  walks of length {L}: {count}", flush=True)
    assert count == 2048, f"expected 2048, got {count}"

    print("Enumerating all walks...", flush=True)
    walks = enumerate_all_walks(C, sub_succ, ENTRY, TARGET, L)
    print(f"  enumerated: {len(walks)}", flush=True)
    assert len(walks) == count

    print("Verifying every walk...", flush=True)
    bad = []
    for wi, w in enumerate(walks):
        if len(w) != L + 1 or w[0] != ENTRY or w[-1] != TARGET:
            bad.append((wi, "endpoints/length"))
            continue
        for a, b in zip(w, w[1:]):
            if b not in sub_succ.get(a, set()):
                bad.append((wi, (a, b)))
                break
    print(f"  walks with invalid edges: {len(bad)}", flush=True)
    if bad[:5]:
        print(f"  first bad: {bad[:5]}", flush=True)

    print("Analysing walk family...", flush=True)
    # simple paths?
    n_simple = sum(1 for w in walks if len(set(w)) == len(w))
    print(f"  simple paths (no repeated states): {n_simple}/{len(walks)}", flush=True)

    # repeated-state stats
    repeat_stats = Counter()
    for w in walks:
        counts = Counter(w)
        repeat_stats[sum(1 for c in counts.values() if c > 1)] += 1
    print(f"  walks by number of repeated states: {dict(sorted(repeat_stats.items()))}", flush=True)

    # 20-cycle occurrences
    rotations = cycle_rotations()
    n_with_cycle = 0
    occ_details = []
    for wi, w in enumerate(walks):
        found = None
        for i in range(len(w) - 20):
            window = w[i:i + 21]
            for r, rot in enumerate(rotations):
                if window == rot:
                    found = (i, r)
                    break
            if found:
                break
        if found:
            n_with_cycle += 1
            occ_details.append((wi, found))
    print(f"  walks containing the 20-cycle as subpath: {n_with_cycle}/{len(walks)}", flush=True)
    if occ_details[:5]:
        print(f"  first occurrences: {occ_details[:5]}", flush=True)

    # state usage
    usage = Counter()
    for w in walks:
        usage.update(set(w))
    print(f"  distinct states used across all walks: {len(usage)}", flush=True)
    top = usage.most_common(10)
    print(f"  top states by walk usage: {top}", flush=True)

    # distinct edges
    edges = set()
    for w in walks:
        for a, b in zip(w, w[1:]):
            edges.add((a, b))
    print(f"  distinct edges across all walks: {len(edges)}", flush=True)

    # save walks
    with open(WALKS_OUT, "w") as f:
        f.write(f"# {len(walks)} walks of length {L} from {ENTRY} to {TARGET}\n")
        for wi, w in enumerate(walks):
            f.write(f"walk_{wi}=" + ",".join(str(s) for s in w) + "\n")

    # results file
    lines = [
        f"num_walks={len(walks)}",
        f"num_simple_paths={n_simple}",
        f"walks_with_20cycle_subpath={n_with_cycle}",
        f"distinct_states_used={len(usage)}",
        f"distinct_edges={len(edges)}",
        f"all_walks_valid={len(bad) == 0}",
        f"cycle20_states_in_scc={len(CYCLE20) - len(cycle_in_scc)}/20",
    ]
    for s, c in sorted(usage.items()):
        lines.append(f"usage_{s}={c}")
    RESULTS_OUT.write_text("\n".join(lines) + "\n")

    print()
    print("=== SUMMARY ===", flush=True)
    print(f"  walks: {len(walks)}", flush=True)
    print(f"  simple paths: {n_simple}", flush=True)
    print(f"  walks with 20-cycle subpath: {n_with_cycle}", flush=True)
    print(f"  distinct states used: {len(usage)}", flush=True)
    print(f"  distinct edges: {len(edges)}", flush=True)
    print(f"  walks saved to {WALKS_OUT}", flush=True)
    print(f"  results written to {RESULTS_OUT}", flush=True)
    print(f"  elapsed: {time.perf_counter() - t0:.1f}s", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())