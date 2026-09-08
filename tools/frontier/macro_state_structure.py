#!/usr/bin/env python3
"""
Analyse post-shift state structure of S-pentacube macro graphs.

For a macro graph (from checkpoint), tabulate the (|L0|, |L1|) occupancy
pairs of post-shift states, source states, and reachable-state sets.
This is a diagnostic for the cyclic-vs-DAG invariant investigation.

Usage:
    python3 tools/frontier/macro_state_structure.py --a 4 --b 5 \
        --checkpoint /tmp/survey_4x5.ckpt
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.frontier.macro_generalized import (
    load_checkpoint,
    layer_mask_general,
)


def analyze(a: int, b: int, ckpt_path: Path) -> None:
    NCELLS = a * b
    ckpt = load_checkpoint(ckpt_path)
    succ = ckpt["succ"]
    sources = ckpt["sources"]

    def counts(state):
        return tuple(
            bin(layer_mask_general(state, i, NCELLS)).count("1")
            for i in range(3)
        )

    # States with successors (the "internal" macro states)
    succ_pairs = Counter(counts(s) for s in succ.keys())

    # Sources
    src_pairs = Counter(counts(s) for s in sources)

    # All macro states (sources + successors + 0)
    all_pairs = Counter()
    for s in succ.keys():
        all_pairs[counts(s)] += 1
    for s in sources:
        all_pairs[counts(s)] += 1
    all_pairs[counts(0)] += 1

    l2_vals = sorted(set(p[2] for p in all_pairs))
    l1_parities = sorted(set(p[1] % 2 for p in all_pairs))
    l0_parities = sorted(set(p[0] % 2 for p in all_pairs))

    print(f"=== {a}×{b} post-shift state structure ===")
    print(f"  succ states: {len(succ)}, sources: {len(sources)}")
    print(f"  L2 values: {l2_vals}")
    print(f"  L1 parities: {l1_parities}")
    print(f"  L0 parities: {l0_parities}")
    print()

    # Reachable set from state 0 (via succ edges)
    reachable = {0}
    queue = [0]
    while queue:
        s = queue.pop()
        for nxt in succ.get(s, ()):
            if nxt not in reachable:
                reachable.add(nxt)
                queue.append(nxt)

    reach_pairs = Counter(counts(s) for s in reachable)
    print(f"  Reachable from 0: {len(reachable)} states")
    print(f"  Reachable L2 values: {sorted(set(p[2] for p in reach_pairs))}")
    print(f"  Reachable (|L0|,|L1|): "
          f"{sorted(set((p[0], p[1]) for p in reach_pairs))}")
    print()
    print(f"  Source (|L0|,|L1|,|L2|) top: {src_pairs.most_common(8)}")
    print(f"  Succ-state (|L0|,|L1|,|L2|) top: {succ_pairs.most_common(8)}")
    print(f"  Reachable (|L0|,|L1|,|L2|) top: {reach_pairs.most_common(8)}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--a", type=int, required=True)
    parser.add_argument("--b", type=int, required=True)
    parser.add_argument("--checkpoint", type=str, required=True)
    args = parser.parse_args()

    analyze(args.a, args.b, Path(args.checkpoint))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())