#!/usr/bin/env python3
"""
Direction-A faithfulness replay for V on the exhaustively verified 5×5×6 box.

For every one of the 144 raw Algorithm X solutions
(data/v_5x5x6_complete_solutions.json):

  1. Independently validate the tiling (bounds, congruence, disjointness,
     exact coverage) against V's proper-rotation orientation set.
  2. Compute the induced frontier-window sequence F(0..z).
  3. CONSTRUCTIVE check: greedily realize each transition F(k)->F(k+1) by
     placing the tiling's own pieces under the first-empty-cell discipline.
  4. GRAPH-MEMBERSHIP check: independently confirm F(k+1) is a successor of
     F(k) in the true macro graph (bounded BFS with the real template set).
  5. Collect distinct induced walks to quantify the tiling->walk collapse
     (explains the historical 80-vs-144 calibration discrepancy).

Outputs JSON summary used by docs/frontier/v_piece/v_macro_faithfulness.md.

Usage: python3 tools/frontier/v_piece/v_faithfulness_replay_5x5x6.py [--out PATH]
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

A, B, Z = 5, 5, 6


def load_solutions():
    path = REPO_ROOT / "data/v_5x5x6_complete_solutions.json"
    data = json.loads(path.read_text())
    out = []
    for sol in data:
        placements = tuple(
            tuple(tuple(cell) for cell in piece) for piece in sol["canonical"]
        )
        out.append(placements)
    return out


def window_state(cells_by_layer_old_pieces, k, NCELLS):
    """Frontier state just before filling layer k: occupancy of layers k..k+2
    restricted to pieces whose bottom lies strictly below k."""
    s = 0
    for z in range(k, min(k + 3, Z + 2)):
        mask = 0
        for (x, y) in cells_by_layer_old_pieces.get(z, ()):
            mask |= 1 << (x + A * y)
        s |= mask << ((z - k) * NCELLS)
    return s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()

    V = PENTACUBES["V"]
    oset = get_orientation_set(V)
    templates, NCELLS, WM, _, _ = build_templates(V, A, B)
    assert NCELLS == A * B

    solutions = load_solutions()
    print(f"loaded {len(solutions)} solutions")

    # Template lookup by slot-0 cell for the membership BFS.
    tmpl_by_cell = templates  # dict cell_id -> list of packed templates

    n_valid = 0
    n_walk_ok_constructive = 0
    n_walk_ok_membership = 0
    walk_signatures = {}
    failures = []

    t0 = time.perf_counter()
    for idx, placements in enumerate(solutions):
        # --- 1. independent tiling validation ---
        res = validate_placement_list([list(p) for p in placements], oset, A, B, Z)
        if not res["valid"]:
            failures.append((idx, "invalid tiling", res["errors"][:3]))
            continue
        n_valid += 1

        # Frontier state s_k (just before filling layer k) = occupancy of
        # layers k..k+2 restricted to pieces whose bottom lies strictly below k.
        def old_piece_cells(k):
            m = {}
            for p in placements:
                if min(z for (_, _, z) in p) < k:
                    for (x, y, z) in p:
                        m.setdefault(z, []).append((x, y))
            return m

        all_cells = [c for p in placements for c in p]
        assert len(all_cells) == A * B * Z

        walk = [window_state(old_piece_cells(k), k, NCELLS) for k in range(Z + 1)]
        assert walk[0] == 0 and walk[Z] == 0

        # --- 3. constructive replay ---
        ok_c = True
        for k in range(Z):
            src = walk[k]
            pieces_here = [
                sorted((x + A * y, z - k) for (x, y, z) in p) for p in placements
                if min(z for (_, _, z) in p) == k
            ]
            # normalize piece footprints relative to window
            piece_masks = []
            for cells in pieces_here:
                m = [0, 0, 0]
                for cid, dz in cells:
                    m[dz] |= 1 << cid
                piece_masks.append(m)
            occ_layers = [layer_mask(src, i, NCELLS) for i in range(3)]
            remaining = list(range(len(piece_masks)))
            steps = 0
            while occ_layers[0] != WM:
                c = first_empty(occ_layers[0], NCELLS)
                chosen = None
                for pi in remaining:
                    m = piece_masks[pi]
                    if not (m[0] & (1 << c)):
                        continue
                    if (m[0] & occ_layers[0]) or (m[1] & occ_layers[1]) or (m[2] & occ_layers[2]):
                        continue
                    chosen = pi
                    break
                if chosen is None:
                    ok_c = False
                    break
                m = piece_masks[chosen]
                occ_layers[0] |= m[0]
                occ_layers[1] |= m[1]
                occ_layers[2] |= m[2]
                remaining.remove(chosen)
                steps += 1
            if not ok_c or remaining:
                ok_c = False
                break
            shifted = (occ_layers[1]) | (occ_layers[2] << NCELLS)
            if shifted != walk[k + 1]:
                ok_c = False
                break
        if ok_c:
            n_walk_ok_constructive += 1
        else:
            failures.append((idx, "constructive replay failed", ""))

        # --- 4. graph-membership check (independent mini-BFS per edge) ---
        ok_m = True
        for k in range(Z):
            src = walk[k]
            found = False
            seen = {src}
            q = deque([src])
            while q and not found:
                st = q.popleft()
                if layer_mask(st, 0, NCELLS) == WM:
                    if shift_state(st, NCELLS) == walk[k + 1]:
                        found = True
                    continue
                c = first_empty(layer_mask(st, 0, NCELLS), NCELLS)
                for tp in tmpl_by_cell[c]:
                    nxt = apply_template(st, tp)
                    if nxt is None or nxt in seen:
                        continue
                    if layer_mask(nxt, 0, NCELLS) == WM and \
                       shift_state(nxt, NCELLS) == walk[k + 1]:
                        found = True
                        break
                    seen.add(nxt)
                    q.append(nxt)
            if not found:
                ok_m = False
                failures.append((idx, f"edge {k} not in macro graph", ""))
                break
        if ok_m:
            n_walk_ok_membership += 1

        sig = tuple(walk)
        walk_signatures.setdefault(sig, []).append(idx)

    elapsed = time.perf_counter() - t0
    distinct_walks = len(walk_signatures)
    group_sizes = sorted((len(v) for v in walk_signatures.values()), reverse=True)

    result = {
        "piece": "V",
        "box": {"a": A, "b": B, "z": Z},
        "solutions_file": "data/v_5x5x6_complete_solutions.json",
        "raw_solutions": len(solutions),
        "valid_tilings_independently_revalidated": n_valid,
        "direction_A_constructive_replay_ok": n_walk_ok_constructive,
        "direction_A_graph_membership_ok": n_walk_ok_membership,
        "distinct_induced_macro_walks": distinct_walks,
        "tilings_per_walk_distribution_top10": group_sizes[:10],
        "walk_length": Z,
        "elapsed_seconds": round(elapsed, 2),
        "failures_first5": failures[:5],
        "interpretation": (
            "Tiling->walk is many-to-one: distinct raw tilings sharing one "
            "state-sequence differ only in HOW layers are filled, which the "
            "macro graph intentionally abstracts away."
        ),
    }
    print(json.dumps({k: v for k, v in result.items()
                      if k != "failures_first5"}, indent=2))
    if failures:
        print("FAILURES:", failures[:5])

    out = args.out or str(REPO_ROOT / "data/frontier/v_piece/v_faithfulness_replay_5x5x6.json")
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    print("wrote", out)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
