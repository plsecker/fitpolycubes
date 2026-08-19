#!/usr/bin/env python3
"""
Count low-level placement realizations of every macro edge on the 2048
129-edge macro walks (4x8x130 box), using the existing macro edge
realization machinery (generalized from macro_edge_realizations.py).

For a macro edge a -> b:
    p_target = WORD_MASK | L0(b)<<32 | L1(b)<<64
    count    = number of placement sequences from a that fill layer 0
               and end exactly at p_target (post-shift == b)

The first edge 0 -> M0 (first-generation fill of slice 0) is counted
the same way with start = 0.

Total tilings of the 4x8x130 box:
    R(0->M0) * sum over the 2048 walks of (product over the 129 edges)

If the total is 1, the unique tiling is reconstructed and certified
(832 placements, 4160 cells, exact coverage of 4x8x130).

The mathematical Macro definitions are NOT modified; the enumeration
rules (first-empty-cell, templates, monotone fill, exact end state)
are identical to macro_edge_realizations.py.
"""

from __future__ import annotations

import sys
import time
from collections import Counter
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
ENUM_CAP = 1000  # enumerate sequences for edges with count <= this

ENTRY = 17293822637554016271
TARGET = 0
L = 129
WALKS_FILE = Path("/tmp/opencode/walks_130.txt")
RESULTS_OUT = Path("/tmp/opencode/macro_edge_realizations_130_results.txt")


class LimitError(Exception):
    pass


def load_walks(path: Path):
    walks = []
    for line in path.read_text().splitlines():
        if line.startswith("#"):
            continue
        key, val = line.split("=", 1)
        walks.append([int(x) for x in val.split(",")])
    return walks


def p_target_of(post_shift: int) -> int:
    return (
        WORD_MASK
        | (layer_mask(post_shift, 0) << 32)
        | (layer_mask(post_shift, 1) << 64)
    )


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
    """Count placement sequences from start ending exactly at p_target."""
    memo: dict[int, int] = {}
    visited: set[int] = set()
    calls = 0
    t0 = time.perf_counter()
    limit_hit = False

    sys.setrecursionlimit(10000)

    def rec(u: int) -> int:
        nonlocal calls, limit_hit
        calls += 1

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

    return count, memo, len(visited), limit_hit, time.perf_counter() - t0


def enumerate_sequences(start, p_target, templates, memo, cap=ENUM_CAP):
    """Enumerate all placement sequences (template lists) from start to
    p_target, pruned by memo counts.  Returns up to cap sequences."""
    seqs = []

    def rec(u, seq):
        if len(seqs) >= cap:
            return
        if layer_mask(u, 0) == WORD_MASK:
            if u == p_target:
                seqs.append(list(seq))
            return
        anchor = first_empty(layer_mask(u, 0))
        for t in templates[anchor]:
            if t & (ALL96 ^ p_target):
                continue
            v = apply_template(u, t)
            if v is None:
                continue
            if memo.get(v, 0) > 0:
                seq.append(t)
                rec(v, seq)
                seq.pop()

    rec(start, [])
    return seqs


def unique_sequence(start, p_target, templates, memo):
    """Backtrack the unique sequence (valid only when count == 1)."""
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


def main() -> int:
    t0 = time.perf_counter()

    print("Building templates...", flush=True)
    templates, concrete_count = build_templates()
    total_templates = sum(len(v) for v in templates.values())
    print(
        f"  concrete placements={concrete_count} "
        f"target templates={total_templates}",
        flush=True,
    )

    print("Loading walks...", flush=True)
    walks = load_walks(WALKS_FILE)
    print(f"  walks: {len(walks)}", flush=True)
    assert all(len(w) == L + 1 for w in walks)

    # distinct edges across all walks, plus the first edge 0 -> ENTRY
    edges = set()
    for w in walks:
        for a, b in zip(w, w[1:]):
            edges.add((a, b))
    first_edge = (0, ENTRY)
    print(f"  distinct walk edges: {len(edges)}", flush=True)
    print(f"  first edge 0 -> {ENTRY} included", flush=True)

    # ---- count realizations per distinct edge ----
    print("Counting realizations per edge...", flush=True)
    counts = {}
    memos = {}
    seqs = {}
    edge_results = {}

    all_edges = sorted(edges) + [first_edge]
    for ei, (a, b) in enumerate(all_edges):
        p_target = p_target_of(b)
        count, memo, visited_count, limit_hit, elapsed = enumerate_edge(
            ei, a, p_target, templates
        )
        counts[(a, b)] = count
        memos[(a, b)] = memo

        if count <= ENUM_CAP:
            seqs[(a, b)] = enumerate_sequences(a, p_target, templates, memo)
            n_seq = len(seqs[(a, b)])
        else:
            seqs[(a, b)] = None
            n_seq = -1

        edge_results[(a, b)] = {
            "a": a,
            "b": b,
            "count": count,
            "visited": visited_count,
            "exhaustive": not limit_hit,
            "elapsed": elapsed,
            "n_seq": n_seq,
        }

        print(
            f"  edge {ei:3d}: {a} -> {b}  count={count}  "
            f"visited={visited_count:,}  exhaustive={not limit_hit}  "
            f"seqs={n_seq}  {elapsed:.2f}s",
            flush=True,
        )

    # ---- total tiling count ----
    print("Computing total tiling count...", flush=True)
    r_first = counts[first_edge]
    print(f"  R(0 -> ENTRY) = {r_first}", flush=True)

    walk_products = []
    for wi, w in enumerate(walks):
        prod = 1
        for a, b in zip(w, w[1:]):
            prod *= counts[(a, b)]
        walk_products.append(prod)

    sum_products = sum(walk_products)
    total = r_first * sum_products
    print(f"  sum over walks of edge products: {sum_products}", flush=True)
    print(f"  TOTAL tilings of 4x8x130: {total}", flush=True)

    # distribution of walk products
    prod_counter = Counter(walk_products)
    print(f"  walk product distribution: {dict(sorted(prod_counter.items()))}", flush=True)

    # ---- certificate if unique ----
    certificate = None
    if total == 1:
        print("\n=== TOTAL == 1: RECONSTRUCTING THE UNIQUE TILING ===", flush=True)
        placements_abs = []  # (slice_no, cells in absolute coords)
        all_cells = set()

        # first edge: slice 0
        p0 = p_target_of(ENTRY)
        seq0 = unique_sequence(0, p0, templates, memos[first_edge])
        for t in seq0:
            abs_cells = tuple(
                (x, y, z) for (x, y, z) in template_cells(t)
            )
            placements_abs.append((0, abs_cells))
            all_cells |= set(abs_cells)

        # walk edges: slice i+1 for edge i
        w = walks[0]
        for i, (a, b) in enumerate(zip(w, w[1:])):
            p_target = p_target_of(b)
            seq = unique_sequence(a, p_target, templates, memos[(a, b)])
            offset = i + 1
            for t in seq:
                abs_cells = tuple(
                    (x, y, z + offset) for (x, y, z) in template_cells(t)
                )
                placements_abs.append((offset, abs_cells))
                all_cells |= set(abs_cells)

        n_placements = len(placements_abs)
        box = {
            (x, y, z)
            for x in range(4)
            for y in range(8)
            for z in range(130)
        }

        print(f"  total placements: {n_placements}", flush=True)
        print(f"  distinct occupied cubes: {len(all_cells)}", flush=True)
        print(f"  all cells in 4x8x130: {all(c in box for c in all_cells)}", flush=True)
        print(
            f"  every cube covered exactly once: {all_cells == box}",
            flush=True,
        )
        ok = (
            n_placements == 832
            and len(all_cells) == 4160
            and all(c in box for c in all_cells)
            and all_cells == box
        )
        print(f"  CERTIFICATE: {'PASS' if ok else 'FAIL'}", flush=True)
        certificate = ok

    # ---- save per-edge placement sequences (task E) ----
    seq_out = Path("/tmp/opencode/edge_realizations_130.txt")
    with open(seq_out, "w") as f:
        f.write(f"# unique placement sequence per macro edge (all counts == 1)\n")
        f.write(f"# first edge 0 -> {ENTRY} fills slice 0; walk edge i fills slice i+1\n")
        for (a, b) in sorted(edges) + [first_edge]:
            p_target = p_target_of(b)
            seq = unique_sequence(a, p_target, templates, memos[(a, b)])
            f.write(f"edge_{a}_{b}=" + ";".join(
                ",".join(f"{x},{y},{z}" for x, y, z in template_cells(t))
                for t in seq
            ) + "\n")

    # ---- reconstruct + certify the full tiling for walk 0 ----
    print("\n=== RECONSTRUCTING FULL TILING FOR WALK 0 ===", flush=True)
    placements_abs = []
    all_cells = set()

    p0 = p_target_of(ENTRY)
    seq0 = unique_sequence(0, p0, templates, memos[first_edge])
    for t in seq0:
        abs_cells = tuple((x, y, z) for (x, y, z) in template_cells(t))
        placements_abs.append((0, abs_cells))
        all_cells |= set(abs_cells)

    w = walks[0]
    for i, (a, b) in enumerate(zip(w, w[1:])):
        p_target = p_target_of(b)
        seq = unique_sequence(a, p_target, templates, memos[(a, b)])
        offset = i + 1
        for t in seq:
            abs_cells = tuple(
                (x, y, z + offset) for (x, y, z) in template_cells(t)
            )
            placements_abs.append((offset, abs_cells))
            all_cells |= set(abs_cells)

    n_placements = len(placements_abs)
    box = {
        (x, y, z)
        for x in range(4)
        for y in range(8)
        for z in range(130)
    }
    ok = (
        n_placements == 832
        and len(all_cells) == 4160
        and all(c in box for c in all_cells)
        and all_cells == box
    )
    print(f"  total placements: {n_placements}", flush=True)
    print(f"  distinct occupied cubes: {len(all_cells)}", flush=True)
    print(f"  all cells in 4x8x130: {all(c in box for c in all_cells)}", flush=True)
    print(f"  every cube covered exactly once: {all_cells == box}", flush=True)
    print(f"  CERTIFICATE: {'PASS' if ok else 'FAIL'}", flush=True)
    certificate_walk0 = ok

    # ---- dump ----
    lines = [
        f"num_walks={len(walks)}",
        f"distinct_edges={len(edges)}",
        f"r_first_edge_0_to_entry={r_first}",
        f"sum_walk_products={sum_products}",
        f"total_tilings_4x8x130={total}",
        f"walk_product_distribution={dict(sorted(prod_counter.items()))}",
        f"edges_with_count_gt_1={sum(1 for r in edge_results.values() if r['count'] > 1)}",
        f"certificate_walk0_tiling={certificate_walk0}",
    ]
    for (a, b), r in sorted(edge_results.items()):
        lines.append(
            f"edge_{a}_{b}_count={r['count']} "
            f"edge_{a}_{b}_visited={r['visited']} "
            f"edge_{a}_{b}_exhaustive={r['exhaustive']} "
            f"edge_{a}_{b}_elapsed={r['elapsed']:.2f} "
            f"edge_{a}_{b}_seqs={r['n_seq']}"
        )
    if certificate is not None:
        lines.append(f"certificate_unique_tiling={certificate}")

    RESULTS_OUT.write_text("\n".join(lines) + "\n")

    print()
    print("=== SUMMARY ===", flush=True)
    print(f"  distinct edges counted: {len(edge_results)}", flush=True)
    print(f"  all exhaustive: {all(r['exhaustive'] for r in edge_results.values())}", flush=True)
    print(f"  edges with count > 1: {sum(1 for r in edge_results.values() if r['count'] > 1)}", flush=True)
    print(f"  R(0 -> ENTRY) = {r_first}", flush=True)
    print(f"  sum over walks of edge products = {sum_products}", flush=True)
    print(f"  TOTAL tilings of 4x8x130 = {total}", flush=True)
    print(f"  results written to {RESULTS_OUT}", flush=True)
    print(f"  elapsed: {time.perf_counter() - t0:.1f}s", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())