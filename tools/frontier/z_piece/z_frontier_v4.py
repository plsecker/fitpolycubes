#!/usr/bin/env python3
"""Z planar-frontier DP prototype (v4).

Formal model (derived from Z geometry, not from any solver):

  Box: cross-section W x H (x = columns, y = rows), NZ layers.
  Every Z placement is planar:
    * xy-flat: 5 cells inside one z-layer (4 in-plane orientations);
    * vertical xz (fixed y) or yz (fixed x): spans exactly 3 consecutive
      z-layers with per-layer profiles (2,1,2) or (1,3,1).

  Boundary state at layer z: the pair (L0, L1) of w*h-bit masks,
    L0 = cells of layer z already filled by vertical pieces started at
         z-2 or z-1,
    L1 = cells of layer z+1 already filled by vertical pieces started at
         z-1.
  L2 (layer z+2) is identically empty at every boundary because no piece
  reaches 3 layers past its start (start <= NZ-3).

  Transition (complete layer z):
    fill the free cells of L0 by
      (a) flat pieces entirely inside layer z, and
      (b) vertical pieces starting at z, whose m0 fills free cells of
          layer z, m1 disjoint from L1, m2 disjoint from the L2
          accumulated during this transition;
    on completion the successor boundary state at z+1 is
      (L1 | d1, d2),  d1/d2 = cells this layer's verticals put into
      layers z+1 / z+2.
  Accepting: boundary NZ == (0, 0).  (Automatic: no vertical may start
  at NZ-2 or NZ-1, so no overhang is possible.)

Correctness: by induction on z, a boundary state (L0, L1) is reachable at
layer z iff there is a set of pieces, each inside layers 0..z+1, covering
exactly the cells of layers 0..z-1 plus (L0 in layer z) and (L1 in layer
z+1).  Hence a chain of transitions from boundary 0 to boundary NZ ending
in (0,0) is exactly a tiling, and exhaustive forward closure with an empty
final frontier proves UNSAT.  (Full argument in the companion doc.)
"""
import sys, time, json
from collections import Counter, deque

sys.path.insert(0, "/tmp/opencode"); sys.path.insert(0, ".")
from z_layer_dp import gen   # audited placement generator (int-cast fixed)

def frontier_bfs(w, h, nz, time_cap=600.0, max_states=8_000_000,
                 store_paths=False, sym_reduce=False):
    FULL, flat, vert, fam = gen(w, h, nz)
    bit_it = iter  # noqa
    t0 = time.time()
    FULLMASK = FULL

    # D4 symmetries of the w x h cross-section (only for w == h)
    syms = None
    if sym_reduce and w == h:
        def apply_sym(m, kind):
            out = 0
            for i in range(w*h):
                if (m >> i) & 1:
                    x, y = i % w, i // w
                    if kind >= 4:  # mirror
                        x = w - 1 - x
                    k = kind % 4
                    for _ in range(k):
                        x, y = y, w - 1 - x
                    out |= 1 << (y*w + x)
            return out
        syms = []
        seen = set()
        for k in range(8):
            if k not in seen:
                seen.add(k)
    # -- simple correct D4 canonicalisation --
    def sym_canon(state):
        if not sym_reduce or w != h:
            return state
        L0, L1 = state
        best = None
        for k in range(8):
            def ap(m):
                out = 0
                for i in range(w*h):
                    if (m >> i) & 1:
                        x, y = i % w, i // w
                        if k >= 4:
                            x = w - 1 - x
                        r = k % 4
                        for _ in range(r):
                            x, y = y, w - 1 - x
                        out |= 1 << (y*w + x)
                return out
            pair = (ap(L0), ap(L1))
            cand = (min(pair[0], pair[1]), max(pair[0], pair[1]))
            if best is None or cand < best:
                best = cand
        return best

    states = [dict() for _ in range(nz + 1)]
    states[0][(0, 0)] = None
    per_layer = [0]*nz
    transitions_total = 0
    max_width = 1
    timeout = False

    for z in range(nz):
        nxt = {}
        for (L0, L1) in states[z]:
            # enumerate completions of layer z from (L0, L1)
            found = set()
            def fill(filled, l1acc, l2acc):
                if time.time() - t0 > time_cap or len(nxt) > max_states:
                    raise TimeoutError
                if filled == FULLMASK:
                    key = (L1 | l1acc, l2acc)
                    nxt.setdefault(key, None)
                    return
                rem = FULLMASK & ~filled
                e = rem & -rem
                for m in flat:
                    if (m & e) and (m & filled) == 0:
                        fill(filled | m, l1acc, l2acc)
                for (m0, m1, m2) in vert[z]:
                    if (m0 & e) and (m0 & filled) == 0 \
                       and (m1 & (L1 | l1acc)) == 0 and (m2 & l2acc) == 0:
                        fill(filled | m0, l1acc | m1, l2acc | m2)
            fill(L0, L1, 0)
            transitions_total += len(nxt)
        # sym-reduce counting if requested (only affects reported widths)
        if sym_reduce and w == h:
            uniq = set()
            for (a, b) in nxt:
                best = None
                for k in range(8):
                    def ap(m):
                        out = 0
                        for i in range(w*h):
                            if (m >> i) & 1:
                                x, y = i % w, i // w
                                if k >= 4: x = w - 1 - x
                                for _ in range(k % 4):
                                    x, y = y, w - 1 - x
                                out |= 1 << (y*w + x)
                        return out
                    pair = tuple(sorted((ap(a), ap(b))))
                    if best is None or pair < best:
                        best = pair
                uniq.add(best)
            per_layer[z] = len(uniq)
            max_width = max(max_width, len(uniq))
        else:
            per_layer[z] = len(nxt)
            max_width = max(max_width, len(nxt))
        states[z+1] = nxt
        if not nxt:
            print(f"frontier empty at boundary z={z+1}: no tiling", flush=True)
            break
        if time.time() - t0 > time_cap or len(nxt) > max_states:
            timeout = True
            print(f"cap hit at boundary z={z+1}", flush=True)
            break

    reached_end = (z == nz - 1 and states[nz].get((0, 0)) is not None) \
        if not timeout else None
    return {
        "sat_like": (not timeout) and any(k == (0, 0) for k in states[nz]) \
            if len(states) > nz else False,
        "reached_final": len(states) > nz,
        "timeout_or_cap": timeout,
        "per_layer_states": per_layer[:nz+1],
        "max_width": max_width,
        "transitions": transitions_total,
        "secs": round(time.time() - t0, 1),
        "families": fam,
    }

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("w", type=int); ap.add_argument("h", type=int)
    ap.add_argument("nz", type=int)
    ap.add_argument("--time", type=float, default=600.0)
    ap.add_argument("--max-states", type=int, default=4_000_000)
    ap.add_argument("--sym", action="store_true")
    a = ap.parse_args()
    r = frontier_bfs(a.w, a.h, a.nz, time_cap=a.time,
                     max_states=a.max_states, sym_reduce=a.sym)
    print(f"Z {a.w}x{a.h}x{a.nz}: reached_final={r['reached_final']} "
          f"sat={r['sat_like']} cap={r['timeout_or_cap']} secs={r['secs']} "
          f"max_width={r['max_width']} transitions={r['transitions_total'] if 'transitions_total' in r else '?'}")
    print("states per boundary:", r["per_layer_states"])
