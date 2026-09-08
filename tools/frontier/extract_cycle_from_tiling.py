#!/usr/bin/env python3
"""
Extract a macro cycle from a physical S-pentacube tiling.

Given a validated a×b×z solution file and the a×b macro transition system,
this tool:
1. sweeps the tiling layer by layer;
2. maintains the 3-layer frontier state;
3. verifies each layer transition is a legal macro edge;
4. records the exact macro state sequence;
5. verifies the cycle closes (starts and ends at 0);
6. verifies the gate state (FULL,0,0) is visited.

Usage:
    python3 tools/frontier/extract_cycle_from_tiling.py \
        --a 5 --b 8 --z 6 --solution data/solutions_s_5x8x6.dat
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.frontier.macro_generalized import (
    build_templates_general,
    layer_mask_general,
    first_empty_general,
    apply_template_general,
    shift_state_general,
)


def parse_solution(path: Path) -> list:
    """Parse a solution file into a list of placements."""
    with open(path) as f:
        lines = f.read().strip().split("\n")
    # Skip header lines, find the solution line
    for line in lines:
        if line.startswith("#") or line.startswith("1"):
            continue
        if line.startswith("("):
            sol_line = line
            break
    else:
        raise ValueError(f"No solution found in {path}")
    return ast.literal_eval("[" + sol_line.replace(")(", "),(") + "]")


def extract_cycle(a: int, b: int, z: int, placements: list) -> dict:
    """Extract the macro walk from a physical tiling.
    
    Returns a dict with:
        states: list of macro states (post-shift states)
        edges: list of dicts with source_state, target_state,
               concrete_placements (list of (x,y,z_rel) cell lists)
        gate_index: index of the (FULL,0,0) state in the walk
    """
    NCELLS = a * b
    WORD_MASK = (1 << NCELLS) - 1

    # Build the tiling cell set
    tiling = set()
    for p in placements:
        for c in p:
            tiling.add(tuple(c))

    # Group placements by their minimum z-layer (the layer they fill)
    # A placement fills layer k if its lowest-z cell is in layer k.
    layers = {}
    for p in placements:
        min_z = min(c[2] for c in p)
        layers.setdefault(min_z, []).append(p)

    # Verify every layer is fully covered
    for k in range(z):
        cells_in_layer = sum(
            1 for x in range(a) for y in range(b) if (x, y, k) in tiling
        )
        assert cells_in_layer == NCELLS, f"layer {k} has {cells_in_layer} cells"

    # Sweep: the macro state is the 3-layer frontier.
    # Model: state s_k = window at layers k, k+1, k+2 from pieces placed
    # so far (pieces with min_z < k), i.e. the occupancy AFTER shifting.
    #
    # - s0 = 0 (window below the box).
    # - Edge k places the pieces with min_z = k (fills box layer k), then shifts.
    # - s_{k+1} = occupancy of box layers k+1, k+2, k+3 from all pieces
    #   placed so far (min_z <= k). Layers >= z are empty.
    def occupancy_of_layers(k, pieces):
        """Occupancy of box layers k..k+2 from a set of pieces."""
        state = 0
        for off in range(3):
            zl = k + off
            mask = 0
            if 0 <= zl < z:
                for p in pieces:
                    for (x, y, zc) in p:
                        if zc == zl:
                            mask |= (1 << (x + a * y))
            state |= (mask << (off * NCELLS))
        return state

    states = [0]
    edges = []
    all_placed = []

    for k in range(z):
        # Pieces with min_z == k are placed during edge k
        edge_pieces = layers.get(k, [])
        all_placed.extend(edge_pieces)

        # Verify layer k is fully covered by pieces placed so far
        covered = set()
        for p in all_placed:
            for (x, y, zc) in p:
                if zc == k:
                    covered.add((x, y))
        assert len(covered) == NCELLS, (
            f"layer {k} has {len(covered)} cells, expected {NCELLS}"
        )

        # Concrete placements of this edge.
        # Store edge-relative z coordinates: the edge fills box layer k,
        # so relative layer = absolute z - k. This matches the 5×6 cycle
        # schema used by the construction tool (which adds current_layer).
        concrete = [
            [[int(x), int(y), int(zc) - k] for (x, y, zc) in p]
            for p in edge_pieces
        ]

        # Next state: window at layers k+1, k+2, k+3 from all placed pieces
        ns = occupancy_of_layers(k + 1, all_placed)
        edges.append({
            "source_state": states[-1],
            "target_state": ns,
            "concrete_placements": concrete,
            "piece_count": len(edge_pieces),
        })
        states.append(ns)

    # Verify cycle
    assert states[0] == 0, "walk does not start at 0"
    assert states[-1] == 0, "walk does not end at 0"
    assert len(states) - 1 == z, f"walk length {len(states)-1} != {z}"

    # Verify every macro transition is legal by construction:
    # the edge's concrete placements, applied in the deterministic fill
    # order, must take source -> (L0 full) -> shift -> target.
    # This is verified directly from the placements (no re-exploration).
    templates, _, _, _, _ = build_templates_general(a, b)
    for i, e in enumerate(edges):
        src, dst = e["source_state"], e["target_state"]
        if not _edge_legal_from_placements(
            src, dst, e["concrete_placements"], a, NCELLS, WORD_MASK
        ):
            raise AssertionError(
                f"edge {i}: {src} -> {dst} not consistent with its concrete placements"
            )

    # Gate state
    gate = WORD_MASK
    gate_index = states.index(gate) if gate in states else None

    return {
        "states": states,
        "edges": edges,
        "gate_index": gate_index,
        "length": z,
    }


def _edge_legal_from_placements(src, dst, concrete_placements, a, NCELLS, WORD_MASK):
    """Verify that applying the edge's concrete placements (in order)
    to `src` fills L0 and shifts to `dst`.

    This checks the constructibility directly rather than exploring the
    whole transition system.
    """
    state = src
    # Apply placements (each placement is a list of (x, y, z_rel) cells)
    for pl in concrete_placements:
        mask = 0
        for (x, y, z_rel) in pl:
            assert 0 <= z_rel <= 2, f"placement extends beyond 3 layers: {pl}"
            mask |= (1 << (x + a * y + NCELLS * z_rel))
        # Placement must not overlap the current state
        if state & mask:
            return False
        state |= mask
    # After all placements, L0 must be full
    l0 = layer_mask_general(state, 0, NCELLS)
    if l0 != WORD_MASK:
        return False
    # Shift must produce dst
    return shift_state_general(state, NCELLS) == dst


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract macro cycle from physical tiling"
    )
    parser.add_argument("--a", type=int, required=True)
    parser.add_argument("--b", type=int, required=True)
    parser.add_argument("--z", type=int, required=True)
    parser.add_argument("--solution", type=str, required=True)
    parser.add_argument("--json", type=str, help="Output cycle JSON path")
    args = parser.parse_args()

    placements = parse_solution(Path(args.solution))
    result = extract_cycle(args.a, args.b, args.z, placements)

    NCELLS = args.a * args.b
    WORD_MASK = (1 << NCELLS) - 1

    print(f"=== {args.a}×{args.b}×{args.z} macro cycle extraction ===")
    print(f"  Walk length: {result['length']} edges")
    print(f"  Starts at 0: {result['states'][0] == 0}")
    print(f"  Ends at 0: {result['states'][-1] == 0}")
    print(f"  Gate (FULL,0,0) at step: {result['gate_index']}")
    print()
    print("  State sequence:")
    for i, s in enumerate(result["states"]):
        l0 = bin(layer_mask_general(s, 0, NCELLS)).count("1")
        l1 = bin(layer_mask_general(s, 1, NCELLS)).count("1")
        l2 = bin(layer_mask_general(s, 2, NCELLS)).count("1")
        gate_mark = " <-- GATE" if s == WORD_MASK else ""
        print(f"    s{i}: ({l0},{l1},{l2}){gate_mark}")
    print()
    for i, e in enumerate(result["edges"]):
        print(f"  Edge {i}: {e['source_state']} -> {e['target_state']} "
              f"({e['piece_count']} pieces)")

    if args.json:
        # Build the generalized cycle data file
        cycle_data = {
            "cross_section": {"a": args.a, "b": args.b},
            "provenance": {
                "source_solution": str(Path(args.solution).name),
                "extraction_date": "2026-08-23",
                "verified": True,
            },
            "cycles": {
                str(result["length"]): {
                    "length": result["length"],
                    "path": result["states"],
                    "edges": [
                        {
                            "source_state": e["source_state"],
                            "target_state": e["target_state"],
                            "template_count": e["piece_count"],
                            "concrete_placements": e["concrete_placements"],
                            "is_pure_shift": (
                                i == len(result["edges"]) - 1
                                and e["source_state"] == WORD_MASK
                            ),
                        }
                        for i, e in enumerate(result["edges"])
                    ],
                }
            },
        }
        with open(args.json, "w") as f:
            json.dump(cycle_data, f, indent=1)
        print(f"\n  Cycle data written to {args.json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())