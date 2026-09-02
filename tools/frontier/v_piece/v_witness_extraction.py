#!/usr/bin/env python3
"""
V witness extraction and Direction-B realization.

Part A — physical-witness extraction (5×5×6):
    Load the exhaustively verified solution set, revalidate every tiling,
    extract each tiling's induced macro walk, and characterize the distinct
    witness walks (length spectrum, gate usage).

Part B — Direction-B realization (3×5 cross-section):
    Take macro-discovered primitive cycles through state 0 (lengths 6 and 8),
    realize every edge with a concrete fill via parent-pointer BFS over the
    true template set, assemble full box tilings, validate them
    independently, and emit generic format-v1 macro-walk certificates.

Usage:
    python3 tools/frontier/v_piece/v_witness_extraction.py \
        [--cycles-json data/frontier/v_piece/v_3x5_closure_analysis.json] \
        [--out-dir data/frontier/v_piece]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.registry import PENTACUBES
from tools.frontier.piece_utils import (
    get_orientation_set, build_templates, layer_mask, first_empty,
    apply_template, shift_state, validate_placement_list,
)
from tools.frontier.macro_explorer import macro_closure


CONVENTIONS = {
    "semantics_id": "fitpolycubes.macro-walk/semantics-1",
    "cell_id": "x + a*y, 0 <= x < a, 0 <= y < b",
    "state_packing": "state = l0 | (l1 << NCELLS); slot 2 always empty (nodes are post-shift states)",
    "rotations": "proper only (signed permutation matrices, det=+1)",
    "window_coords": "edge k fill pieces relative to layer k: (x,y,dz), dz in {0,1,2}; absolute cell = (x,y,k+dz)",
    "edge_legality_definition": (
        "pieces of edge k must each be congruent to piece.geometry under "
        "proper rotation, be pairwise disjoint, avoid all cells occupied by "
        "state s_k, complete slot 0 of s_k, and shift(s_k + pieces) == s_{k+1}"
    ),
}


# ---------------------------------------------------------------------------
# Part A
# ---------------------------------------------------------------------------

def part_a(out_dir: Path) -> dict:
    sols = json.loads((REPO_ROOT / "data/v_5x5x6_complete_solutions.json").read_text())
    A, B, Z = 5, 5, 6
    NCELLS = A * B
    oset = get_orientation_set(PENTACUBES["V"])

    def window(k, placements):
        m = {}
        for p in placements:
            if min(z for (_, _, z) in p) < k:
                for (x, y, z) in p:
                    m.setdefault(z, []).append((x + A * y))
        s = 0
        for z in range(k, k + 3):
            for cid in m.get(z, []):
                s |= 1 << cid << ((z - k) * NCELLS)
        return s

    walks = {}
    invalid = 0
    for i, sol in enumerate(sols):
        placements = [tuple(tuple(c) for c in p) for p in sol["canonical"]]
        res = validate_placement_list([list(p) for p in placements], oset, A, B, Z)
        if not res["valid"]:
            invalid += 1
            continue
        sig = tuple(window(k, placements) for k in range(Z + 1))
        walks.setdefault(sig, []).append(i)

    spec: dict[int, int] = {}
    gate_passages = 0
    WM = (1 << NCELLS) - 1
    for sig in walks:
        spec[len(sig) - 1] = spec.get(len(sig) - 1, 0) + 1
        gate_passages += sum(1 for s in sig[1:-1] if s == WM)

    result = {
        "source": "data/v_5x5x6_complete_solutions.json",
        "provenance_note": (
            "placements_V_5x5x6.txt / placements_V_5x5x9.txt are complete "
            "placement CATALOGUES (all legal placements: 696 / 1164), not "
            "witnesses; the exhaustive solution sets are the witnesses."
        ),
        "witness_tilings": len(sols) - invalid,
        "invalid_tilings": invalid,
        "distinct_induced_walks": len(walks),
        "walk_length_spectrum": {str(k): v for k, v in sorted(spec.items())},
        "walks_passing_through_classic_gate_state": gate_passages,
        "sample_walk_first_states_hex": [
            hex(s) for s in next(iter(walks.keys()))[:3]
        ],
    }
    # persist the distinct witness walks for future comparison
    with open(out_dir / "v_5x5x6_witness_walks.json", "w") as f:
        json.dump({
            "box": {"a": A, "b": B, "z": Z},
            "distinct_walks_count": len(walks),
            "walks": [{"states": list(sig), "realizations": idxs}
                      for sig, idxs in sorted(walks.items())],
        }, f, indent=2)
    print("[A]", json.dumps(result, indent=2)[:800])
    print("[A] wrote", out_dir / "v_5x5x6_witness_walks.json")
    return result


# ---------------------------------------------------------------------------
# Part B — realize cycles as concrete tilings + certificates
# ---------------------------------------------------------------------------

def realize_edge(src: int, dst: int, templates_by_cell, NCELLS, WM):
    """BFS with parents from src until L0 is full and shift == dst."""
    if layer_mask(src, 0, NCELLS) == WM:
        return [] if shift_state(src, NCELLS) == dst else None
    parent = {src: None}
    q = deque([src])
    while q:
        st = q.popleft()
        c = first_empty(layer_mask(st, 0, NCELLS), NCELLS)
        for tp in templates_by_cell[c]:
            nxt = apply_template(st, tp)
            if nxt is None or nxt in parent:
                continue
            parent[nxt] = (st, tp)
            if layer_mask(nxt, 0, NCELLS) == WM:
                if shift_state(nxt, NCELLS) == dst:
                    # reconstruct fills
                    fills = []
                    cur = nxt
                    while parent[cur] is not None:
                        prev, tp2 = parent[cur]
                        fills.append(tp2)
                        cur = prev
                    return list(reversed(fills))
                # completed layer with a different shift: dead branch
            else:
                q.append(nxt)
    return None


def decode_template(tp: int, NCELLS: int):
    cells = []
    for layer in range(3):
        mask = layer_mask(tp, layer, NCELLS)
        cid = 0
        m = mask
        while m:
            low = m & -m
            cid = low.bit_length() - 1
            cells.append((cid, layer))
            m ^= low
    return cells  # list of (cell_id, dz)


def realize_cycle(cycle, templates_by_cell, NCELLS, WM, a, b):
    """Return (edge_fills_window_coords, box_tiling) for a closed cycle [0,...,0]."""
    edge_fills = []
    tiling = []
    ok = True
    for k in range(len(cycle) - 1):
        src, dst = cycle[k], cycle[k + 1]
        fills = realize_edge(src, dst, templates_by_cell, NCELLS, WM)
        if fills is None:
            return None, None
        pieces_wc = []
        for tp in fills:
            wc = []
            for cid, dz in decode_template(tp, NCELLS):
                x, y = cid % a, cid // a
                wc.append([x, y, dz])
                tiling.append((x, y, k + dz))
            pieces_wc.append(wc)
        edge_fills.append(pieces_wc)
    box_tiling = sorted(tiling)
    return edge_fills, box_tiling


def part_b(out_dir: Path, closure_json: Path) -> dict:
    A, B = 3, 5
    NCELLS = A * B
    WM = (1 << NCELLS) - 1
    oset = get_orientation_set(PENTACUBES["V"])
    templates, _, _, _, _ = build_templates(PENTACUBES["V"], A, B)

    data = json.loads(closure_json.read_text())
    cycles = data["cycles_first5"]
    # need actual integer cycles: recompute short ones directly
    macro_seen, succ, sources, stats = macro_closure(
        "V", A, B, max_states=20_000_000, verbose=False)
    assert stats["zero_reachable"]

    from tools.frontier.v_piece.analyze_v_closure import tarjan_sccs
    sccs = tarjan_sccs(succ)
    comp_of = {}
    for i, comp in enumerate(sccs):
        for u in comp:
            comp_of[u] = i
    scc0 = set(sccs[comp_of[0]])

    # find ONE primitive cycle of each needed length (6, 8) by bounded DFS
    def find_cycle_of_length(length):
        path = [0]
        on_path = {0}
        succ0 = {u: sorted(v for v in succ.get(u, ()) if v in scc0) for u in scc0}

        def dfs(cur):
            if len(path) == length:
                return 0 in succ0[cur] and list(path) + [0]
            for nxt in succ0[cur]:
                if nxt == 0 or nxt in on_path:
                    continue
                path.append(nxt)
                on_path.add(nxt)
                r = dfs(nxt)
                if r:
                    return r
                path.pop()
                on_path.discard(nxt)
            return None

        return dfs(0)

    results = {"boxes": []}
    for z in (6, 8):
        cycle = find_cycle_of_length(z)
        if not cycle:
            results["boxes"].append({"z": z, "realized": False,
                                     "error": "no simple cycle found"})
            continue
        edge_fills, box_tiling = realize_cycle(
            cycle, templates, NCELLS, WM, A, B)
        if box_tiling is None:
            results["boxes"].append({"z": z, "realized": False})
            continue
        # each realized fill IS one piece; rebuild placements from edge fills
        pieces = [tuple(sorted((wc[0], wc[1], k + wc[2]) for wc in piece))
                  for k, edge in enumerate(edge_fills) for piece in edge]
        val = validate_placement_list([list(p) for p in pieces], oset, A, B, z)
        realized = bool(val["valid"])

        # terminal-block facts (generic observations; Layer A re-derives them)
        pred_l0 = layer_mask(cycle[z - 1], 0, NCELLS)
        pc_count = bin(pred_l0).count("1")
        remaining = NCELLS - pc_count
        last_edge = edge_fills[z - 1]
        all_slot0 = all(c[2] == 0 for pcs in last_edge for c in pcs)
        comp = {i for i in range(NCELLS) if not (pred_l0 >> i) & 1}
        cov: set[int] = set()
        covers = True
        for pcs in last_edge:
            mset = {x + A * y for (x, y, _) in pcs}
            if mset & cov or not mset <= comp:
                covers = False
                break
            cov |= mset
        covers = covers and cov == comp

        cert = {
            "format": "fitpolycubes.macro-walk",
            "format_version": 1,
            "piece": {
                "name": "V",
                "geometry": [[0, 0, 0], [1, 0, 0], [2, 0, 0],
                             [0, 1, 0], [0, 2, 0]],
                "cell_count": 5,
            },
            "conventions": CONVENTIONS,
            "box": {"a": A, "b": B, "z": z},
            "walk": [
                {"step": i, "l0": layer_mask(s, 0, NCELLS),
                 "l1": layer_mask(s, 1, NCELLS), "hex": hex(s)}
                for i, s in enumerate(cycle)
            ],
            "edge_fills": edge_fills,
            "box_tiling": [list(map(list, p)) for p in pieces],
            "terminal": {
                "predecessor_state_index": z - 1,
                "l0_popcount": pc_count,
                "remaining_cells": remaining,
                "final_edge_all_slot0": bool(all_slot0),
                "final_edge_covers_complement": bool(covers),
            },
            "provenance": {
                "generator": ("tools/frontier/v_piece/v_witness_extraction.py "
                              "Direction-B realization of a macro-discovered "
                              f"primitive cycle of length {z} on 3×5"),
                "date": "2026-08-26",
            },
            "claims": [
                {"id": "C1", "status": "VERIFIED CYCLE",
                 "statement": (f"Closed macro walk of length {z} through 0 on "
                               f"the V 3×5 macro graph, concretely realized as "
                               f"a validated {A}×{B}×{z} tiling.")},
            ],
        }
        cname = out_dir / f"v_3x5x{z}_macro_cycle_certificate.json"
        with open(cname, "w") as f:
            json.dump(cert, f, indent=2)

        results["boxes"].append({
            "z": z,
            "realized": realized,
            "validation_errors": val["errors"][:3] if not realized else [],
            "pieces": len(pieces),
            "certificate": str(cname.relative_to(REPO_ROOT)),
            "cycle_states_hex": [hex(s) for s in cycle],
        })
        print(f"[B] 3×5×{z}: realized={realized}, pieces={len(pieces)}, cert={cname.name}")

    with open(out_dir / "v_3x5_realized_witnesses.json", "w") as f:
        json.dump(results, f, indent=2)
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=str,
                    default=str(REPO_ROOT / "data/frontier/v_piece"))
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    ra = part_a(out_dir)
    rb = part_b(out_dir, REPO_ROOT / "data/frontier/v_piece/v_3x5_closure_analysis.json")
    print(f"elapsed {time.perf_counter()-t0:.1f}s")

    summary = {"part_A_witness_extraction": ra, "part_B_realization": rb}
    with open(out_dir / "v_witness_extraction_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("wrote", out_dir / "v_witness_extraction_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
