#!/usr/bin/env python3
"""
Search for structural invariants of S-pentacube macro graphs.

Given a macro graph (from checkpoint or edge file), tests candidate
invariants across all edges:

1. Linear layer-count functionals: I = a|L0| + b|L1| + c|L2| mod m
2. Conservation, monotonicity, or fixed-delta behaviour.

Usage:
    python3 tools/frontier/macro_invariant_search.py --a 4 --b 5 \
        --edges data/frontier/s_4x5_edges.txt
    python3 tools/frontier/macro_invariant_search.py --a 5 --b 6 \
        --checkpoint /tmp/survey_5x6_v2.ckpt
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.frontier.macro_generalized import (
    load_checkpoint,
    build_templates_general,
    layer_mask_general,
)


def load_edges_from_file(path: Path, a: int, b: int) -> list[tuple[int, int]]:
    """Load edges from a text file: 'src -> dst dst dst...' per line."""
    edges = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or "->" not in line:
                continue
            src_str, dsts_str = line.split("->", 1)
            src = int(src_str.strip())
            for dst_str in dsts_str.split():
                edges.append((src, int(dst_str)))
    return edges


def load_edges_from_checkpoint(path: Path) -> list[tuple[int, int]]:
    """Load edges from a macro checkpoint."""
    ckpt = load_checkpoint(path)
    edges = []
    for src, dsts in ckpt["succ"].items():
        for dst in dsts:
            edges.append((src, dst))
    return edges


def test_invariant(
    edges: list[tuple[int, int]],
    a: int,
    b: int,
    alpha: int,
    beta: int,
    gamma: int,
    m: int,
    include_state0: bool = False,
) -> dict:
    """Test whether I = (a|L0| + b|L1| + c|L2|) mod m is conserved, monotone,
    or has constant delta across all edges."""
    NCELLS = a * b

    def I(state: int) -> int:
        p0 = bin(layer_mask_general(state, 0, NCELLS)).count("1")
        p1 = bin(layer_mask_general(state, 1, NCELLS)).count("1")
        p2 = bin(layer_mask_general(state, 2, NCELLS)).count("1")
        return (alpha * p0 + beta * p1 + gamma * p2) % m

    deltas = Counter()
    violations = 0
    checked = 0
    for src, dst in edges:
        if not include_state0 and src == 0:
            continue
        d = (I(dst) - I(src)) % m
        deltas[d] += 1
        checked += 1

    conserved = len(deltas) == 1 and deltas[0] == checked
    constant_delta = len(deltas) == 1

    return {
        "alpha": alpha,
        "beta": beta,
        "gamma": gamma,
        "m": m,
        "conserved": conserved,
        "constant_delta": constant_delta,
        "deltas": dict(deltas),
        "checked": checked,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Search for macro graph invariants"
    )
    parser.add_argument("--a", type=int, required=True)
    parser.add_argument("--b", type=int, required=True)
    parser.add_argument("--edges", type=str, help="Edge file path")
    parser.add_argument("--checkpoint", type=str, help="Checkpoint path")
    parser.add_argument(
        "--include-state0",
        action="store_true",
        help="Include edges from state 0 (default: excluded)",
    )
    args = parser.parse_args()

    if args.edges:
        edges = load_edges_from_file(Path(args.edges), args.a, args.b)
    elif args.checkpoint:
        edges = load_edges_from_checkpoint(Path(args.checkpoint))
    else:
        print("Error: need --edges or --checkpoint", file=sys.stderr)
        return 1

    print(f"Cross-section: {args.a}×{args.b}")
    print(f"Edges tested: {len(edges)}")
    print()

    print("=== Linear layer-count invariants ===")
    print("Searching I = (α|L0| + β|L1| + γ|L2|) mod m over all edges...")
    print()

    conserved_found = []
    for m in [2, 3, 5]:
        for alpha in range(m):
            for beta in range(m):
                for gamma in range(m):
                    if (alpha, beta, gamma) == (0, 0, 0):
                        continue
                    result = test_invariant(
                        edges, args.a, args.b, alpha, beta, gamma, m,
                        include_state0=args.include_state0,
                    )
                    if result["conserved"]:
                        conserved_found.append(result)
                        print(
                            f"  CONSERVED: I = {alpha}|L0| + {beta}|L1| + "
                            f"{gamma}|L2| mod {m}  ({result['checked']} edges)"
                        )
                    elif result["constant_delta"]:
                        d = list(result["deltas"].keys())[0]
                        print(
                            f"  CONSTANT Δ={d}: I = {alpha}|L0| + {beta}|L1| + "
                            f"{gamma}|L2| mod {m}"
                        )

    if not conserved_found:
        print("  No non-trivial linear layer-count invariants found.")

    # Monotonicity check for the total cell count
    print()
    print("=== Monotonicity of total occupancy ===")
    NCELLS = args.a * args.b
    increasing = 0
    decreasing = 0
    equal = 0
    for src, dst in edges:
        ps = sum(bin(layer_mask_general(src, i, NCELLS)).count("1") for i in range(3))
        pd = sum(bin(layer_mask_general(dst, i, NCELLS)).count("1") for i in range(3))
        if pd > ps:
            increasing += 1
        elif pd < ps:
            decreasing += 1
        else:
            equal += 1
    print(f"  Edges where occupancy increases: {increasing}")
    print(f"  Edges where occupancy decreases: {decreasing}")
    print(f"  Edges where occupancy equal:     {equal}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())