#!/usr/bin/env python3
"""
Extract the complete 20-layer path from the empty frontier state 0 back
to state 0 described in docs/s_z_frontier_length_analysis.md, including
the S placements used to complete each layer.

Reconstruction only:
  * the 20 post-shift states are taken verbatim from the doc;
  * the placements for each layer are recovered by a targeted BFS within
    that layer's placement interval (bounded by the interval size, at
    most ~40K states) -- NOT a new exhaustive search of the state space;
  * the solver (solvers/s_z_frontier_packed.py) is NOT modified; its
    pure functions are reused with identical semantics.
"""

from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

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

# Post-shift states of the 20-layer path, verbatim from
# docs/s_z_frontier_length_analysis.md (steps 0..19).
PATH_STATES = [
    6163195513375031274,   # 0: source (post-shift after first generation)
    13835058072323104239,  # 1
    3993075831,            # 2
    55840897340952456,     # 3
    9838132153049676753,   # 4
    2089671021646321023,   # 5
    13523993509333176,     # 6
    54046496222498049,     # 7
    3430478137537398,      # 8
    2691607028413209,      # 9
    4934612199136503,      # 10
    612490719515897646,    # 11
    16285016559841080657,  # 12
    217229141722890951,    # 13
    6729013160573166,      # 14
    2297949969,            # 15
    1224979683048584328,   # 16
    17294878168733286543,  # 17
    4294967295,            # 18 = WORD_MASK
    0,                     # 19 = empty frontier
]

# First-generation pre-shift state (from the doc): 0 -> [14 placements]
# -> p0 -> source, with p0 >> 32 == source.
P0 = 0x558811aa57ffffeaffffffff


def cells_of_template(template: int) -> list[tuple[int, int, int]]:
    """Occupied (x, y, z) cells of a packed 96-bit template."""
    cells: list[tuple[int, int, int]] = []

    for z in range(3):
        mask = layer_mask(template, z)

        while mask:
            b = mask & -mask
            cell = b.bit_length() - 1
            cells.append((cell % 4, cell // 4, z))
            mask ^= b

    return cells


def placements_to_state(
    start: int,
    target: int,
    templates: dict,
) -> list[tuple[int, int]]:
    """
    Targeted BFS from start to target within the placement interval
    (placements only, no shifts).  Returns the list of (anchor_cell,
    template) applied, in order.
    """
    parent: dict[int, tuple[int, int, int]] = {}
    seen: set[int] = {start}
    queue: deque[int] = deque([start])

    while queue:
        state = queue.popleft()

        if state == target:
            seq: list[tuple[int, int]] = []
            cur = state

            while cur in parent:
                prev, anchor, template = parent[cur]
                seq.append((anchor, template))
                cur = prev

            seq.reverse()
            return seq

        if layer_mask(state, 0) == WORD_MASK:
            continue  # pre-shift state: no further placements

        anchor = first_empty(layer_mask(state, 0))

        for template in templates[anchor]:
            nxt = apply_template(state, template)

            if nxt is None or nxt in seen:
                continue

            seen.add(nxt)
            parent[nxt] = (state, anchor, template)
            queue.append(nxt)

    raise RuntimeError(f"no placement path from {start} to {target}")


def simulate(
    start: int,
    placements: list[tuple[int, int]],
) -> int:
    """Re-apply the placements from start; returns the resulting state."""
    state = start

    for anchor, template in placements:
        assert first_empty(layer_mask(state, 0)) == anchor
        nxt = apply_template(state, template)
        assert nxt is not None, "placement overlaps"
        state = nxt

    return state


def fmt_cells(cells: list[tuple[int, int, int]]) -> str:
    return " ".join(f"({x},{y},{z})" for x, y, z in cells)


def main() -> int:
    print("Building templates...", flush=True)
    templates, concrete_count = build_templates()
    total_templates = sum(len(v) for v in templates.values())
    print(
        f"  concrete placements={concrete_count} "
        f"target templates={total_templates}",
        flush=True,
    )

    source = PATH_STATES[0]
    assert shift_state(P0) == source, "p0 >> 32 must equal the source"

    # ---- Layer 1: first-generation segment 0 -> p0 -> source ----
    fg_placements = placements_to_state(0, P0, templates)
    assert simulate(0, fg_placements) == P0

    # ---- Layers 2..20: macro edges PATH_STATES[i] -> PATH_STATES[i+1] ----
    layers: list[dict] = []

    for i in range(len(PATH_STATES) - 1):
        u = PATH_STATES[i]
        v = PATH_STATES[i + 1]
        p = WORD_MASK | (layer_mask(v, 0) << 32) | (layer_mask(v, 1) << 64)
        placements = placements_to_state(u, p, templates)
        assert simulate(u, placements) == p
        assert shift_state(p) == v
        layers.append(
            {
                "layer": i + 2,
                "u": u,
                "v": v,
                "p": p,
                "placements": placements,
            }
        )

    # ---- Report ----
    total_placements = len(fg_placements) + sum(
        len(l["placements"]) for l in layers
    )

    print()
    print("=== COMPLETE 20-LAYER PATH: 0 -> ... -> 0 ===")
    print(f"Post-shift states in order ({len(PATH_STATES)} states):")

    for i, s in enumerate(PATH_STATES):
        print(
            f"  step {i:2d}: {s}  "
            f"(L0={layer_mask(s, 0):#010x} L1={layer_mask(s, 1):#010x} "
            f"L2={layer_mask(s, 2):#010x})"
        )

    print()
    print("=== LAYER 1 (first generation) ===")
    print(f"  transition: 0 -> [{len(fg_placements)} placements] -> p0 -> source")
    print(f"  p0 = {P0:#x}")
    print(
        f"  p0 layers: L0={layer_mask(P0, 0):#010x} "
        f"L1={layer_mask(P0, 1):#010x} L2={layer_mask(P0, 2):#010x}"
    )
    print(f"  p0 >> 32 == source: {shift_state(P0) == source}")
    print("  placements:")

    for j, (anchor, template) in enumerate(fg_placements, 1):
        print(
            f"    {j:2d}. anchor=({anchor % 4},{anchor // 4}) "
            f"cells={fmt_cells(cells_of_template(template))}"
        )

    for l in layers:
        print()
        print(f"=== LAYER {l['layer']} (macro edge) ===")
        print(f"  transition: {l['u']} -> [{len(l['placements'])} placements] -> p -> {l['v']}")
        print(f"  pre-shift p = {l['p']:#x}")
        print(
            f"  p layers: L0={layer_mask(l['p'], 0):#010x} "
            f"L1={layer_mask(l['p'], 1):#010x} L2={layer_mask(l['p'], 2):#010x}"
        )
        print(f"  p >> 32 == v: {shift_state(l['p']) == l['v']}")
        print("  placements:")

        for j, (anchor, template) in enumerate(l["placements"], 1):
            print(
                f"    {j:2d}. anchor=({anchor % 4},{anchor // 4}) "
                f"cells={fmt_cells(cells_of_template(template))}"
            )

    print()
    print("=== TOTALS ===")
    print(f"Total S placements: {total_placements}")
    print(f"  layer 1 (first generation): {len(fg_placements)}")
    print(
        f"  layers 2..20 (macro edges): "
        f"{sum(len(l['placements']) for l in layers)}"
    )
    print(f"Total layers completed: 20")
    print(f"Final state: {PATH_STATES[-1]}")
    print(f"Final state is exactly 0: {PATH_STATES[-1] == 0}")

    # ---- Verification ----
    print()
    print("=== VERIFICATION ===")
    ok = True

    # 1. first-gen segment
    check = simulate(0, fg_placements) == P0 and shift_state(P0) == source
    ok &= check
    print(f"  first-gen: 0 -> placements -> p0 -> source: {check}")

    # 2. each macro edge
    for l in layers:
        check = (
            simulate(l["u"], l["placements"]) == l["p"]
            and shift_state(l["p"]) == l["v"]
        )
        ok &= check
        print(
            f"  layer {l['layer']}: u -> placements -> p -> v: {check}"
        )

    # 3. final state
    check = PATH_STATES[-1] == 0
    ok &= check
    print(f"  final state == 0: {check}")

    # 4. full path: concatenate all placements and shifts
    state = 0
    state = simulate(state, fg_placements)
    state = shift_state(state)
    assert state == source

    for l in layers:
        state = simulate(state, l["placements"])
        state = shift_state(state)
        assert state == l["v"]

    print(f"  full simulation 0 -> ... -> 0 returns exactly 0: {state == 0}")
    ok &= state == 0
    print(f"  ALL CHECKS PASSED: {ok}")

    # ---- Dump machine-readable results ----
    out = Path("/tmp/opencode/s_4x8x20_frontier_cycle_results.txt")
    lines = [
        f"path_states={PATH_STATES}",
        f"p0={P0}",
        f"firstgen_placements={len(fg_placements)}",
        f"total_placements={total_placements}",
        f"total_layers=20",
        f"final_state={PATH_STATES[-1]}",
        f"final_is_zero={PATH_STATES[-1] == 0}",
        f"all_checks_passed={ok}",
    ]

    for l in layers:
        lines.append(
            f"layer{l['layer']}_placements={len(l['placements'])}"
        )

    out.write_text("\n".join(lines) + "\n")
    print(f"\nResults written to {out}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())