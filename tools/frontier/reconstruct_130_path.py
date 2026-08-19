#!/usr/bin/env python3
"""
Reconstruct the 129-edge macro path from 17293822637554016271 to 0
using the existing 30M-state checkpoint data.

Background
----------
The SCC-aware analysis of the 30M-state macro closure
(scc_aware_analysis.py, results in /tmp/opencode/scc_aware_analysis_results.txt)
found exactly one (source, entry, DAG-distance, SCC-distance) combination
achieving the target distance 129 for the 4x8x130 box:

    source = entry = 17293822637554016271
    DAG distance = 0
    SCC distance = 129

so the 129-edge path lies entirely inside the 478-state SCC containing
state 0, s* and WORD_MASK.

This script reconstructs that path from the checkpoint data, verifies
every edge, and analyses the path structure inside the SCC.

Data used
---------
/tmp/opencode/macro130_checkpoints/
    macro_seen.npy   sorted uint64 array, 30,000,015 macro states
    succ.npy         flat uint64 (source, n, succ...) markers, 29,902,891 edges
    dist.npy         flat uint64 (state, distance) pairs (not needed here)
    queue.npy        BFS queue (not needed here)
    counters.txt     totals

The checkpoint succ map was produced by the capped closure (1M
intermediate states per source).  succ[0] is patched with the complete
succ[0] (331,765 successors) exactly as in scc_aware_analysis.py.

Method
------
1. Load checkpoint succ map + macro state list.
2. Patch succ[0] with the complete succ[0].
3. Tarjan SCC over all 30M states; extract the SCC containing 0.
4. Compute SCC-internal distance sets R[u] = {d : 0 reachable from u in
   d steps within the SCC} (same iteration as scc_aware_analysis.py).
5. Count walks of length 129 from the entry to 0 within the SCC (DP).
6. Reconstruct the walk(s); if exactly one, it is the unique macro path.
7. Verify every edge twice:
   a. structural:  b in recorded succ[a]
   b. ground truth: re-derive explore_source(a) from the templates and
      check b is in the result; also check the re-derived set equals the
      recorded one (completeness / no 1M-cap truncation).
8. Analyse the path inside the SCC: repeated states, cycle
   decomposition, occurrence of the known 20-cycle as a subpath, and
   the distance profile along the path.

The mathematical Macro definitions are NOT modified.
"""

from __future__ import annotations

import sys
import time
from collections import Counter, deque
from pathlib import Path

import numpy as np

REPO_ROOT = Path("/home/philip/Work/fitpolycubes")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from solvers.s_z_frontier_packed import (
    WORD_MASK,
    apply_template,
    build_templates,
    first_empty,
    layer_mask,
    shift_state,
)

from tools.frontier.scc_aware_analysis import (
    MAX_INTERMEDIATE_0,
    S_STAR,
    compute_scc_internal_distances,
    explore_source,
    tarjan_scc,
)

CHECKPOINT_DIR = Path("/tmp/opencode/macro130_checkpoints")
ENTRY = 17293822637554016271
TARGET = 0
L = 129  # number of macro edges (N = L + 1 = 130 layers)
OUT = Path("/tmp/opencode/reconstruct_130_path_results.txt")

# Known 20-cycle post-shift states (macro_edge_realizations.py PATH):
# edge 1: 0 -> PATH[0]; edge k (2..20): PATH[k-2] -> PATH[k-1].
# As a state sequence the cycle is [0, PATH[0], ..., PATH[18], 0].
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
assert len(CYCLE20) == 20
assert CYCLE20[18] == WORD_MASK and CYCLE20[19] == 0


def load_succ(path: Path) -> dict:
    """Load the flat (source, n, succ...) checkpoint array into a dict of sets."""
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


def explore_source_capped(source, templates, max_intermediate):
    """Like explore_source but reports whether the intermediate cap was hit."""
    successors = set()
    seen = {source}
    queue = deque([source])
    capped = False

    while queue:
        if len(seen) - 1 >= max_intermediate:
            capped = True
            break

        state = queue.popleft()

        if layer_mask(state, 0) == WORD_MASK:
            successors.add(shift_state(state))
            continue

        target = first_empty(layer_mask(state, 0))

        for template in templates[target]:
            nxt = apply_template(state, template)

            if nxt is None or nxt in seen:
                continue

            seen.add(nxt)
            queue.append(nxt)

    return successors, capped


def count_walks(sub_succ, target, L):
    """C[u][d] = number of walks of length d from u to target within the SCC."""
    C = {u: [0] * (L + 1) for u in sub_succ}
    C[target][0] = 1

    for d in range(1, L + 1):
        for u in sub_succ:
            total = 0
            for v in sub_succ[u]:
                total += C[v][d - 1]
            C[u][d] = total

    return C


def reconstruct_unique(C, sub_succ, entry, target, L):
    """Backtrack the unique walk (valid only when C[entry][L] == 1)."""
    path = [entry]
    u = entry

    for d in range(L, 0, -1):
        cands = [v for v in sub_succ[u] if C[v][d - 1] == 1]
        assert len(cands) == 1, f"not unique at step {L - d}: {cands}"
        v = cands[0]
        path.append(v)
        u = v

    assert u == target
    return path


def enumerate_walks(C, sub_succ, entry, target, L, cap=1000):
    """Enumerate all walks of length L from entry to target (pruned by C)."""
    walks = []

    def rec(u, d, path):
        if len(walks) >= cap:
            return
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


def verify_edges(path, succ, templates):
    """Verify every edge: recorded succ + ground-truth re-derivation."""
    results = []

    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        recorded = b in succ.get(a, set())

        derived, capped = explore_source_capped(a, templates, MAX_INTERMEDIATE_0)
        ground_truth = b in derived
        complete = derived == succ.get(a, set())

        results.append({
            "i": i,
            "a": a,
            "b": b,
            "recorded": recorded,
            "ground_truth": ground_truth,
            "complete": complete,
            "capped": capped,
            "n_derived": len(derived),
        })

        print(
            f"  edge {i:3d}: {a} -> {b}  "
            f"recorded={recorded} ground_truth={ground_truth} "
            f"complete={complete} capped={capped} n_derived={len(derived)}",
            flush=True,
        )

    return results


def decompose_walk(path):
    """
    Greedy decomposition of a walk into prefix + cycles + suffix.
    Returns a list of (kind, start, end) with kind in
    {'prefix', 'cycle', 'suffix'}; each cycle is a closed sub-walk
    (path[start] == path[end]).
    """
    segments = []
    seen = {}
    seg_start = 0
    n = len(path)

    for i, s in enumerate(path):
        if s in seen:
            j = seen[s]
            if seg_start < j:
                segments.append(("prefix", seg_start, j))
            segments.append(("cycle", j, i))
            seg_start = i
            seen = {s: i}
        else:
            seen[s] = i

    if seg_start < n:
        segments.append(("suffix", seg_start, n))

    return segments


def cycle_rotations():
    """All 20 rotations of the known 20-edge cycle as 21-state sequences."""
    n = len(CYCLE20)
    return [CYCLE20[i:] + CYCLE20[:i] + [CYCLE20[i]] for i in range(n)]


def analyze_path(path, R, scc_0):
    """Structural analysis of the reconstructed path inside the SCC."""
    n = len(path)

    # 1. repeated states
    counts = Counter(path)
    repeated = {
        s: [i for i, x in enumerate(path) if x == s]
        for s, c in counts.items() if c > 1
    }

    # 2. greedy cycle decomposition
    segments = decompose_walk(path)

    # 3. known 20-cycle as a subpath (all rotations)
    rotations = cycle_rotations()
    occurrences = []
    for i in range(n - 20):
        window = path[i:i + 21]
        for r, rot in enumerate(rotations):
            if window == rot:
                occurrences.append((i, r))

    # 4. distance profile along the path
    profile = [sorted(R.get(s, set())) for s in path]

    # 5. all states on the path must be in the SCC
    all_in_scc = all(s in scc_0 for s in path)

    return {
        "n_states": n,
        "repeated": repeated,
        "segments": segments,
        "cycle20_occurrences": occurrences,
        "profile": profile,
        "all_in_scc": all_in_scc,
    }


def main() -> int:
    t0 = time.perf_counter()

    print("Building templates...", flush=True)
    templates, _ = build_templates()

    print("Loading checkpoint succ map...", flush=True)
    succ = load_succ(CHECKPOINT_DIR / "succ.npy")
    macro_seen = np.load(CHECKPOINT_DIR / "macro_seen.npy")
    print(f"  succ sources: {len(succ):,}", flush=True)
    print(f"  macro states: {len(macro_seen):,}", flush=True)

    print("Recomputing complete succ[0]...", flush=True)
    complete_succ_0 = explore_source(0, templates, MAX_INTERMEDIATE_0)
    print(f"  complete succ[0]: {len(complete_succ_0):,}", flush=True)
    succ[0] = complete_succ_0

    print("Running Tarjan SCC over all macro states...", flush=True)
    t1 = time.perf_counter()
    sccs = tarjan_scc(macro_seen, succ)
    print(f"  {len(sccs):,} SCCs in {time.perf_counter() - t1:.1f}s", flush=True)

    scc_0 = None
    for scc in sccs:
        if TARGET in scc:
            scc_0 = set(scc)
            break
    assert scc_0 is not None, "state 0 not in any SCC"

    print(f"  SCC containing 0: size {len(scc_0)}", flush=True)
    print(f"  contains s*: {S_STAR in scc_0}", flush=True)
    print(f"  contains WORD_MASK: {WORD_MASK in scc_0}", flush=True)
    print(f"  contains entry: {ENTRY in scc_0}", flush=True)

    # Persist the SCC and its restricted succ map for follow-up analyses
    # (walk enumeration, realization counting) without re-running Tarjan.
    scc_arr = np.array(sorted(scc_0), dtype=np.uint64)
    np.save("/tmp/opencode/scc_130_states.npy", scc_arr, allow_pickle=False)
    sub_succ_data = []
    for u in sorted(scc_0):
        sub_succ_data.append(u)
        succs = sorted(succ.get(u, set()) & scc_0)
        sub_succ_data.append(len(succs))
        sub_succ_data.extend(succs)
    np.save(
        "/tmp/opencode/scc_130_succ.npy",
        np.array(sub_succ_data, dtype=np.uint64),
        allow_pickle=False,
    )
    print(f"  saved SCC states and restricted succ to /tmp/opencode/", flush=True)

    print("Computing SCC-internal distances to 0...", flush=True)
    R = compute_scc_internal_distances(scc_0, succ, TARGET, L)
    print(f"  distances for {len(R)} states", flush=True)
    print(f"  R[entry] = {sorted(R.get(ENTRY, set()))}", flush=True)
    assert L in R.get(ENTRY, set()), "distance 129 not in R[entry]"

    print("Counting walks of length 129 from entry to 0 within SCC...", flush=True)
    sub_succ = {u: succ.get(u, set()) & scc_0 for u in scc_0}
    C = count_walks(sub_succ, TARGET, L)
    count = C[ENTRY][L]
    print(f"  number of 129-edge walks: {count}", flush=True)

    if count == 1:
        path = reconstruct_unique(C, sub_succ, ENTRY, TARGET, L)
        walks = [path]
    else:
        walks = enumerate_walks(C, sub_succ, ENTRY, TARGET, L, cap=1000)
        print(f"  enumerated {len(walks)} walks (cap 1000)", flush=True)
        path = walks[0]

    assert len(path) == L + 1, f"path has {len(path)} states, expected {L + 1}"
    assert path[0] == ENTRY and path[-1] == TARGET

    print("Verifying every edge...", flush=True)
    edge_results = verify_edges(path, succ, templates)

    print("Analyzing path structure...", flush=True)
    analysis = analyze_path(path, R, scc_0)

    # ---------------- report ----------------
    lines = []
    lines.append(f"entry={ENTRY}")
    lines.append(f"target={TARGET}")
    lines.append(f"num_edges={L}")
    lines.append(f"num_states={len(path)}")
    lines.append(f"scc_size={len(scc_0)}")
    lines.append(f"scc_contains_s_star={S_STAR in scc_0}")
    lines.append(f"scc_contains_word_mask={WORD_MASK in scc_0}")
    lines.append(f"scc_contains_entry={ENTRY in scc_0}")
    lines.append(f"r_entry={sorted(R.get(ENTRY, set()))}")
    lines.append(f"num_129_walks={count}")
    lines.append(f"path_unique={count == 1}")
    lines.append(f"all_path_states_in_scc={analysis['all_in_scc']}")

    for i, s in enumerate(path):
        lines.append(f"path_{i}={s}")

    for r in edge_results:
        lines.append(
            f"edge_{r['i']}_a={r['a']} "
            f"edge_{r['i']}_b={r['b']} "
            f"edge_{r['i']}_recorded={r['recorded']} "
            f"edge_{r['i']}_ground_truth={r['ground_truth']} "
            f"edge_{r['i']}_complete={r['complete']} "
            f"edge_{r['i']}_capped={r['capped']} "
            f"edge_{r['i']}_n_derived={r['n_derived']}"
        )

    lines.append(f"repeated_states={len(analysis['repeated'])}")
    for s, idxs in sorted(analysis["repeated"].items()):
        lines.append(f"repeat_{s}={idxs}")

    lines.append(f"segments={[(k, a, b) for k, a, b in analysis['segments']]}")
    lines.append(f"cycle20_occurrences={analysis['cycle20_occurrences']}")

    OUT.write_text("\n".join(lines) + "\n")

    # ---------------- console summary ----------------
    print()
    print("=== RECONSTRUCTED 129-EDGE MACRO PATH ===", flush=True)
    for i, s in enumerate(path):
        print(f"  M{i:3d} = {s}  ({s:#x})", flush=True)

    print()
    print("=== EDGE VERIFICATION ===", flush=True)
    ok = all(
        r["recorded"] and r["ground_truth"] and r["complete"] and not r["capped"]
        for r in edge_results
    )
    print(f"  all 129 edges recorded: {all(r['recorded'] for r in edge_results)}", flush=True)
    print(f"  all 129 edges ground-truth: {all(r['ground_truth'] for r in edge_results)}", flush=True)
    print(f"  all recorded succ complete (no cap truncation): {all(r['complete'] for r in edge_results)}", flush=True)
    print(f"  any cap hit during re-derivation: {any(r['capped'] for r in edge_results)}", flush=True)
    print(f"  VERIFICATION: {'PASS' if ok else 'FAIL'}", flush=True)

    print()
    print("=== PATH STRUCTURE INSIDE SCC ===", flush=True)
    print(f"  all path states in SCC: {analysis['all_in_scc']}", flush=True)
    print(f"  repeated states: {len(analysis['repeated'])}", flush=True)
    for s, idxs in sorted(analysis["repeated"].items()):
        print(f"    {s} ({s:#x}): indices {idxs}", flush=True)

    print(f"  greedy decomposition:", flush=True)
    for kind, a, b in analysis["segments"]:
        print(f"    {kind:6s} [{a:3d}..{b:3d}] length {b - a}", flush=True)

    if analysis["cycle20_occurrences"]:
        print(f"  known 20-cycle occurs as subpath at:", flush=True)
        for i, r in analysis["cycle20_occurrences"]:
            print(f"    start index {i}, rotation {r}", flush=True)
    else:
        print(f"  known 20-cycle does NOT occur as a contiguous subpath", flush=True)

    print()
    print(f"  distance profile (R[u] along the path):", flush=True)
    for i, s in enumerate(path):
        print(f"    M{i:3d} {s}  R={analysis['profile'][i]}", flush=True)

    print()
    print(f"Results written to {OUT}", flush=True)
    print(f"Total elapsed: {time.perf_counter() - t0:.1f}s", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())