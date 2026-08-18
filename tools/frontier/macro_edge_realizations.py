#!/usr/bin/env python3
"""
Exhaustive placement-level realization enumeration for each of the 20
macro edges of the verified 4x8x20 frontier cycle.

For edge k (k = 1..20), with fixed start state S_k and fixed target
pre-shift state p_k (whose post-shift is the recorded post-shift state
T_k of the cycle):

  S_k = 0                              (k = 1)
  S_k = PATH[k-2]                      (k = 2..20, post-shift state)
  p_k = WORD_MASK | L0(T_k)<<32 | L1(T_k)<<64
  T_k = PATH[k-1]

Enumerate ALL placement sequences such that:
  1. start at S_k
  2. first-empty-cell rule exactly as the solver (first_empty(layer0))
  3. templates exactly as build_templates() of solvers/s_z_frontier_packed.py
  4. continue until layer 0 becomes full
  5. the final pre-shift state is EXACTLY p_k (post-shift == T_k)
  6. count distinct placement sequences (paths in the placement DAG)
  7. exhaustive: no early exit

Pruning: a template whose cells are not all within p_k can never appear
on a sequence ending at p_k (the fill is monotone; cells are permanent),
so such templates are skipped.  This is exact and complete, not a
heuristic: every state ever explored is a subset of p_k.

Counting: memoized recursion over the placement DAG (acyclic: each
placement adds exactly 5 previously-empty cells).  memo[u] = number of
valid sequences from state u; the answer for the edge is memo[S_k].
Distinct sequences = distinct paths in the DAG (each edge corresponds to
one template choice; two choice sequences with the same state sequence
would require identical templates).

The solver is NOT modified.  This enumerates placement-level realizations
of the UNIQUE macro path only; no other macro paths, boxes, or tilings
are searched.

Safety limits (recorded if hit; expected never): MAX_VISITED_PER_EDGE.
"""

from __future__ import annotations

import re
import sys
import time
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
)

ALL96 = (1 << 96) - 1
MAX_VISITED_PER_EDGE = 200_000_000
PROGRESS_EVERY = 10.0  # seconds

# Verified N=20 macro path (post-shift states), from
# /tmp/opencode/macro_length_analysis_results.txt (n20_path).
PATH = [
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
assert len(PATH) == 20
assert PATH[18] == WORD_MASK and PATH[19] == 0

CYCLE_FILE = Path("/tmp/opencode/s_4x8x20_frontier_cycle_full.txt")


class LimitError(Exception):
    pass


def parse_cycle_file(path: Path):
    """Return {layer_no: (p_target, recorded_placements)} where recorded
    placements is a list of (anchor_cell_id, cells) in order."""
    text = path.read_text()
    sections = re.split(r"=== (LAYER \d+[^(]*)", text)
    layers = {}

    for i in range(1, len(sections), 2):
        name = sections[i].strip()
        body = sections[i + 1]
        layer_no = int(name.split()[1])

        m = re.search(r"p0 = (0x[0-9a-f]+)", body)
        if m:
            p = int(m.group(1), 16)
        else:
            m2 = re.search(r"pre-shift p = (0x[0-9a-f]+)", body)
            p = int(m2.group(1), 16)

        rows = re.findall(
            r"^\s+\d+\. anchor=\((\d+),(\d+)\) cells=(.*)$", body, re.M
        )
        placements = []

        for a, b, c in rows:
            cells = tuple(
                tuple(map(int, t))
                for t in re.findall(r"\((\d+),(\d+),(\d+)\)", c)
            )
            anchor = int(a) + 4 * int(b)
            placements.append((anchor, cells))

        layers[layer_no] = (p, placements)

    return layers


def build_edges(layers):
    """Return list of (edge_no, start, target_postshift, p_target,
    recorded_placements) for edges 1..20, with cross-checks against the
    cycle file."""
    edges = []

    for k in range(1, 21):
        if k == 1:
            start, target = 0, PATH[0]
        else:
            start, target = PATH[k - 2], PATH[k - 1]

        p_target = (
            WORD_MASK
            | (layer_mask(target, 0) << 32)
            | (layer_mask(target, 1) << 64)
        )

        recorded_p, recorded_pl = layers[k]
        assert p_target == recorded_p, (
            f"edge {k}: computed p_target {p_target:#x} != recorded "
            f"{recorded_p:#x}"
        )

        edges.append((k, start, target, p_target, recorded_pl))

    return edges


def template_cells(t: int):
    cells = []
    for layer in range(3):
        m = (t >> (32 * layer)) & WORD_MASK
        while m:
            b = m & -m
            cell = b.bit_length() - 1
            cells.append((cell % 4, cell // 4, layer))
            m ^= b
    return tuple(cells)


def enumerate_edge(edge_no, start, p_target, templates):
    """Exhaustively count placement sequences from start ending exactly at
    p_target.  Returns (count, memo, visited_count, limit_hit)."""
    memo: dict[int, int] = {}
    visited: set[int] = set()
    calls = 0
    t0 = time.perf_counter()
    last_report = t0
    limit_hit = False

    sys.setrecursionlimit(10000)

    def rec(u: int) -> int:
        nonlocal calls, last_report, limit_hit
        calls += 1

        if calls % 5000 == 0:
            now = time.perf_counter()
            if now - last_report >= PROGRESS_EVERY:
                last_report = now
                print(
                    f"    [edge {edge_no} progress] visited={len(visited):,} "
                    f"calls={calls:,} elapsed={now - t0:.1f}s",
                    flush=True,
                )

        if u in memo:
            return memo[u]

        if u in visited:
            raise RuntimeError("cycle in placement DAG (impossible)")

        visited.add(u)

        if len(visited) >= MAX_VISITED_PER_EDGE:
            raise LimitError(edge_no)

        if layer_mask(u, 0) == WORD_MASK:
            memo[u] = 1 if u == p_target else 0
            return memo[u]

        anchor = first_empty(layer_mask(u, 0))
        total = 0

        for t in templates[anchor]:
            if t & (ALL96 ^ p_target):
                continue  # exact pruning: cells must lie within p_target

            v = apply_template(u, t)

            if v is None:
                continue

            total += rec(v)

        memo[u] = total
        return total

    try:
        count = rec(start)
    except LimitError:
        limit_hit = True
        count = memo.get(start, 0)

    return count, memo, len(visited), limit_hit


def unique_sequence(start, p_target, templates, memo):
    """Backtrack the unique sequence (used only when count == 1)."""
    seq = []
    u = start

    while layer_mask(u, 0) != WORD_MASK:
        anchor = first_empty(layer_mask(u, 0))
        chosen = None

        for t in templates[anchor]:
            if t & (ALL96 ^ p_target):
                continue

            v = apply_template(u, t)

            if v is None:
                continue

            if memo.get(v, 0) == 1:
                chosen = (t, v)
                break

        if chosen is None:
            raise RuntimeError("backtrack failed")

        t, v = chosen
        seq.append(t)
        u = v

    assert u == p_target
    return seq


def verify_recorded_sequence(start, p_target, templates, recorded):
    """Simulate the recorded placement list; must end exactly at p_target."""
    u = start

    for anchor, cells in recorded:
        assert layer_mask(u, 0) != WORD_MASK, "recorded sequence too long"
        assert first_empty(layer_mask(u, 0)) == anchor, (
            "recorded anchor mismatch"
        )

        # find the template at this anchor with exactly these cells
        chosen = None
        for t in templates[anchor]:
            if set(template_cells(t)) == set(cells):
                chosen = t
                break

        assert chosen is not None, "recorded cells not a template at anchor"
        v = apply_template(u, chosen)
        assert v is not None, "recorded sequence overlaps"
        u = v

    assert layer_mask(u, 0) == WORD_MASK, "recorded sequence did not fill L0"
    assert u == p_target, "recorded sequence ended at wrong pre-shift state"
    return True


def main() -> int:
    print("Building templates...", flush=True)
    templates, concrete_count = build_templates()
    total_templates = sum(len(v) for v in templates.values())
    print(
        f"  concrete placements={concrete_count} "
        f"target templates={total_templates}",
        flush=True,
    )

    print(f"Parsing cycle file {CYCLE_FILE}...", flush=True)
    layers = parse_cycle_file(CYCLE_FILE)
    assert len(layers) == 20

    edges = build_edges(layers)
    print(f"Edges built: {len(edges)} (all pre-shift targets match recorded)", flush=True)

    edge_counts = {}
    unique_seqs = {}  # edge_no -> list of templates (only when count == 1)
    results = {}

    for k, start, target, p_target, recorded in edges:
        print(f"\n=== EDGE {k}: {start} -> [placements] -> {p_target:#x} -> {target} ===", flush=True)
        t0 = time.perf_counter()
        count, memo, visited_count, limit_hit = enumerate_edge(
            k, start, p_target, templates
        )
        elapsed = time.perf_counter() - t0

        live = sum(1 for v in memo.values() if v > 0)

        # the recorded sequence must be a valid realization (sanity)
        try:
            verify_recorded_sequence(start, p_target, templates, recorded)
            recorded_ok = True
        except AssertionError as e:
            recorded_ok = False
            print(f"    WARNING: recorded sequence invalid: {e}", flush=True)

        seq = None
        if count == 1:
            seq = unique_sequence(start, p_target, templates, memo)

            # cross-check the unique sequence against the recorded one
            uniq_cells = [set(template_cells(t)) for t in seq]
            rec_cells = [set(c) for _, c in recorded]
            seq_matches = uniq_cells == rec_cells
        else:
            seq_matches = None

        edge_counts[k] = count
        if count == 1:
            unique_seqs[k] = seq

        print(
            f"  start={start} ({start:#x})  target={target} ({target:#x})",
            flush=True,
        )
        print(f"  target pre-shift: {p_target:#x}", flush=True)
        print(f"  placement sequences: {count}", flush=True)
        print(
            f"  distinct states visited (incl. start): {visited_count:,}  "
            f"intermediate (excl. start): {visited_count - 1:,}  "
            f"states on valid sequences: {live:,}",
            flush=True,
        )
        print(
            f"  elapsed: {elapsed:.2f}s  exhaustive: {not limit_hit}  "
            f"limit hit: {limit_hit}",
            flush=True,
        )
        print(f"  recorded sequence valid: {recorded_ok}", flush=True)
        if count == 1:
            print(f"  unique sequence == recorded sequence: {seq_matches}", flush=True)

        results[k] = {
            "start": start,
            "target": target,
            "p_target": p_target,
            "count": count,
            "visited": visited_count,
            "live": live,
            "elapsed": elapsed,
            "exhaustive": not limit_hit,
            "limit_hit": limit_hit,
            "recorded_ok": recorded_ok,
            "seq_matches": seq_matches,
        }

    # ---- product ----
    product = 1
    for k in range(1, 21):
        product *= edge_counts[k]

    print()
    print("=== SUMMARY ===", flush=True)
    for k in range(1, 21):
        r = results[k]
        print(
            f"  edge {k:2d}: count={r['count']}  visited={r['visited']:,}  "
            f"exhaustive={r['exhaustive']}  {r['elapsed']:.2f}s",
            flush=True,
        )
    print(f"PRODUCT of 20 edge counts: {product}", flush=True)

    all_exhaustive = all(r["exhaustive"] for r in results.values())
    print(f"all edges exhaustive: {all_exhaustive}", flush=True)

    # ---- if product == 1: reconstruct the 128 placements and certify ----
    if product == 1 and all_exhaustive:
        print("\n=== PRODUCT == 1: RECONSTRUCTING THE 128 PLACEMENTS ===", flush=True)
        placements_abs = []  # (layer_no, cells in absolute coords)
        all_cells = set()

        for k in range(1, 21):
            if k not in unique_seqs:
                print(f"  edge {k}: no unique sequence recorded!", flush=True)
                return 2

            offset = k - 1

            for t in unique_seqs[k]:
                abs_cells = tuple(
                    (x, y, z + offset) for (x, y, z) in template_cells(t)
                )
                placements_abs.append((k, abs_cells))
                all_cells |= set(abs_cells)

        n_placements = len(placements_abs)
        box = {
            (x, y, z)
            for x in range(4)
            for y in range(8)
            for z in range(20)
        }

        print(f"  total placements: {n_placements}", flush=True)
        print(f"  distinct occupied cubes: {len(all_cells)}", flush=True)
        print(f"  all cells in 4x8x20: {all(c in box for c in all_cells)}", flush=True)
        print(
            f"  every cube covered exactly once: {all_cells == box}",
            flush=True,
        )
        ok = (
            n_placements == 128
            and len(all_cells) == 640
            and all(c in box for c in all_cells)
            and all_cells == box
        )
        print(f"  CERTIFICATE: {'PASS' if ok else 'FAIL'}", flush=True)

        # cross-check against the certificate doc's placement list
        cert_doc = Path(REPO_ROOT / "docs" / "s_4x8x20_tiling_certificate.md")
        if cert_doc.exists():
            body = cert_doc.read_text().split("## The 128 placements")[1]
            body = body.split("## Coverage and overlap checks")[0]
            rows = re.findall(
                r"^\d+\. ((?:\(\d+,\d+,\d+\) ?)+)$", body, re.M
            )
            cert_sets = [
                frozenset(
                    tuple(map(int, t))
                    for t in re.findall(r"\((\d+),(\d+),(\d+)\)", r)
                )
                for r in rows
            ]
            mine_sets = [frozenset(c) for _, c in placements_abs]
            match = sorted(cert_sets) == sorted(mine_sets)
            print(f"  matches certificate doc placement sets: {match}", flush=True)
        else:
            match = None
            print("  (certificate doc not found, skipped cross-check)", flush=True)
    else:
        match = None

    # ---- dump ----
    out = Path("/tmp/opencode/macro_edge_realizations_results.txt")
    lines = [
        "product=" + str(product),
        "all_edges_exhaustive=" + str(all_exhaustive),
    ]

    for k in range(1, 21):
        r = results[k]
        lines.append(
            f"edge{k}_start={r['start']} "
            f"edge{k}_target={r['target']} "
            f"edge{k}_count={r['count']} "
            f"edge{k}_visited={r['visited']} "
            f"edge{k}_live={r['live']} "
            f"edge{k}_elapsed={r['elapsed']:.2f} "
            f"edge{k}_exhaustive={r['exhaustive']} "
            f"edge{k}_limit_hit={r['limit_hit']} "
            f"edge{k}_recorded_ok={r['recorded_ok']} "
            f"edge{k}_seq_matches={r['seq_matches']}"
        )

    if product == 1 and all_exhaustive and match is not None:
        lines.append("certificate_128_placements=PASS")
        lines.append("certificate_640_distinct=PASS")
        lines.append(f"certificate_matches_doc={match}")

    out.write_text("\n".join(lines) + "\n")
    print(f"\nResults written to {out}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
