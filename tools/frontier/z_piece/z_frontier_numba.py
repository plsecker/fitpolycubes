#!/usr/bin/env python3
"""Numba port of the validated Z planar-frontier DP (reference:
/tmp/opencode/z_frontier_v4.py, validated in z_frontier_dp_prototype.md).

Same transition system, compiled:
  * boundary state (L0, L1) as two <=63-bit int64 layer masks;
  * explicit-stack DFS over the lowest empty cell, branching over
    precomputed per-bit candidate tables (flat masks; vertical
    (m0,m1,m2) triples per start layer);
  * successors collected in an open-addressing hash table per layer;
  * optional exact mod-5 layer congruence pruning (derived invariant:
    |V_z| = A - 5 f_z  =>  popcount(L0) + va + R == A (mod 5));
  * layer loop + D4 orbit counting in Python/numpy (identical
    canonicalisation to the Python prototype).

The Python prototype (z_frontier_v4.py) remains the reference; this module
must reproduce its measured boundary profiles exactly.
"""
import numpy as np
from numba import njit
import sys, time

sys.path.insert(0, "/tmp/opencode"); sys.path.insert(0, ".")
from z_layer_dp import gen

# ---------------- numba helpers ----------------

@njit
def _popcount(x):
    n = 0
    while x:
        x &= x - 1
        n += 1
    return n

@njit
def _bit_index(e):          # e is a power of two
    n = 0
    while (e & 1) == 0:
        e >>= 1
        n += 1
    return n

@njit
def _mix64(a, b):
    x = (a * np.int64(0x9E3779B97F4A7C15)) & np.int64(0x7FFFFFFFFFFFFFFF)
    y = (b * np.int64(0xC2B2AE3D27D4EB4F)) & np.int64(0x7FFFFFFFFFFFFFFF)
    h = x ^ y
    h ^= h >> np.int64(33)
    h = (h * np.int64(0xFF51AFD7ED558CCD)) & np.int64(0x7FFFFFFFFFFFFFFF)
    h ^= h >> np.int64(29)
    return h

@njit
def _ht_insert(ht_l0, ht_l1, ht_used, ht_mask, a, b):
    h = _mix64(a, b) & ht_mask
    while True:
        if ht_used[h] == 0:
            ht_l0[h] = a; ht_l1[h] = b; ht_used[h] = 1
            return 1                                    # new
        if ht_l0[h] == a and ht_l1[h] == b:
            return 0                                    # duplicate
        h = (h + 1) & ht_mask

# ---------------- per-layer fill kernel ----------------

@njit
def _fill_layer(states_l0, states_l1, nstates, FULL,
                fb_ptr, fb_data,
                v_ptr, v_m0, v_m1, v_m2,
                ht_l0, ht_l1, ht_used, ht_mask,
                st_f, st_l1, st_l2, st_ci, st_fa, st_pop,
                stats, prune_mod5, A_mod5):
    for s in range(nstates):
        L0 = states_l0[s]; L1 = states_l1[s]
        popL0 = _popcount(L0)
        sp = 0
        st_f[sp] = L0; st_l1[sp] = L1; st_l2[sp] = 0
        st_ci[sp] = 0; st_fa[sp] = 0; st_pop[sp] = popL0
        while sp >= 0:
            filled = st_f[sp]; l1 = st_l1[sp]; l2 = st_l2[sp]
            ci = st_ci[sp]; fa = st_fa[sp]; pop = st_pop[sp]
            if filled == FULL:
                # successor boundary state: (L1 | l1, l2)
                h = _mix64(L1 | l1, l2) & ht_mask
                while True:
                    if ht_used[h] == 0:
                        ht_l0[h] = L1 | l1; ht_l1[h] = l2; ht_used[h] = 1
                        stats[0] += 1
                        break
                    if ht_l0[h] == (L1 | l1) and ht_l1[h] == l2:
                        stats[1] += 1
                        break
                    h = (h + 1) & ht_mask
                sp -= 1
                continue
            rem = FULL & ~filled
            R = _popcount(rem)
            va = pop - popL0 - 5 * fa
            if prune_mod5:
                # exact congruence: |V_z| = popcount(L0) + va + R == A (mod 5)
                if (popL0 + va + R) % 5 != A_mod5:
                    sp -= 1
                    stats[2] += 1
                    continue
            e = rem & -rem
            eb = _bit_index(e)
            n_f = fb_ptr[eb + 1] - fb_ptr[eb]
            total = n_f + (v_ptr[eb + 1] - v_ptr[eb])
            if ci < total:
                st_ci[sp] = ci + 1
                if ci < n_f:
                    msk = fb_data[fb_ptr[eb] + ci]
                    if (msk & filled) == 0:
                        sp += 1
                        st_f[sp] = filled | msk; st_l1[sp] = l1; st_l2[sp] = l2
                        st_ci[sp] = 0; st_fa[sp] = fa + 1
                        st_pop[sp] = pop + 5
                else:
                    j = v_ptr[eb] + (ci - n_f)
                    m0 = v_m0[j]; m1 = v_m1[j]; m2 = v_m2[j]
                    if (m0 & filled) == 0 and (m1 & (L1 | l1)) == 0 and (m2 & l2) == 0:
                        sp += 1
                        st_f[sp] = filled | m0; st_l1[sp] = l1 | m1; st_l2[sp] = l2 | m2
                        st_ci[sp] = 0; st_fa[sp] = fa
                        st_pop[sp] = pop + _popcount(m0)
            else:
                sp -= 1
    return 0

# ---------------- template construction (Python, from audited gen) ----------------

def build_templates(w, h, nz):
    FULL, flat, vert, fam = gen(w, h, nz)
    nbits = w * h
    flat_arr = np.array(sorted(flat), dtype=np.int64)

    # flat candidates indexed by covered cell bit
    buckets_f = [[] for _ in range(nbits)]
    for m in sorted(flat):
        for b in range(nbits):
            if (m >> b) & 1:
                buckets_f[b].append(m)
    fb_ptr = np.zeros(nbits + 1, dtype=np.int64)
    fb_data = []
    for b in range(nbits):
        fb_ptr[b] = len(fb_data)
        fb_data.extend(buckets_f[b])
    fb_ptr[nbits] = len(fb_data)
    fb_data = np.array(fb_data, dtype=np.int64)

    # vertical candidates per start layer, indexed by covered cell bit of m0
    vb_ptr = np.zeros((nz, nbits + 1), dtype=np.int64)
    vb_m0, vb_m1, vb_m2 = [], [], []
    for z in range(nz):
        buckets = [[] for _ in range(nbits)]
        for (m0, m1, m2) in vert[z]:
            for b in range(nbits):
                if (m0 >> b) & 1:
                    buckets[b].append((m0, m1, m2))
        for b in range(nbits):
            vb_ptr[z, b + 1] = vb_ptr[z, b] + len(buckets[b])
            for (m0, m1, m2) in buckets[b]:
                vb_m0.append(m0); vb_m1.append(m1); vb_m2.append(m2)
    vb_m0 = np.array(vb_m0, dtype=np.int64)
    vb_m1 = np.array(vb_m1, dtype=np.int64)
    vb_m2 = np.array(vb_m2, dtype=np.int64)
    return FULL, fb_ptr, fb_data, vb_ptr, vb_m0, vb_m1, vb_m2, fam

# ---------------- layer loop ----------------

def run(w, h, nz, prune_mod5=False, ht_cap_log=22, verbose=True):
    FULL = (1 << (w * h)) - 1
    A_mod5 = (w * h) % 5
    FULL, fb_ptr, fb_data, vb_ptr, vb_m0, vb_m1, vb_m2, fam = \
        build_templates(w, h, nz)
    nbits = w * h
    stats = np.zeros(4, dtype=np.int64)   # [new, dup, prunes, unused]
    ht_cap = 1 << ht_cap_log
    ht_l0 = np.zeros(ht_cap, dtype=np.int64)
    ht_l1 = np.zeros(ht_cap, dtype=np.int64)
    ht_used = np.zeros(ht_cap, dtype=np.int8)
    ht_mask = ht_cap - 1
    st_f = np.zeros(512, dtype=np.int64)
    st_l1 = np.zeros(512, dtype=np.int64)
    st_l2 = np.zeros(512, dtype=np.int64)
    st_ci = np.zeros(512, dtype=np.int64)
    st_fa = np.zeros(512, dtype=np.int64)
    st_pop = np.zeros(512, dtype=np.int64)

    cur_l0 = np.zeros(1, dtype=np.int64)
    cur_l1 = np.zeros(1, dtype=np.int64)
    per_layer = []
    verdict = None
    t0 = time.time()

    for z in range(nz):
        ht_used[:] = 0
        ptr = vb_ptr[z]
        v_ptr = ptr - ptr[0]                      # per-bit indptr for layer z
        v_m0 = vb_m0[ptr[0]:ptr[nbits]]
        v_m1 = vb_m1[ptr[0]:ptr[nbits]]
        v_m2 = vb_m2[ptr[0]:ptr[nbits]]
        _fill_layer(cur_l0, cur_l1, len(cur_l0), FULL,
                    fb_ptr, fb_data,
                    v_ptr, v_m0, v_m1, v_m2,
                    ht_l0, ht_l1, ht_used, ht_cap - 1,
                    st_f, st_l1, st_l2, st_ci, st_fa, st_pop,
                    stats, prune_mod5, A_mod5)
        used = int(ht_used.sum())
        idx = np.nonzero(ht_used)[0]
        nxt_l0 = ht_l0[idx]; nxt_l1 = ht_l1[idx]
        order = np.lexsort((nxt_l1, nxt_l0))
        cur_l0 = nxt_l0[order]; cur_l1 = nxt_l1[order]
        per_layer.append(len(cur_l0))
        if verbose:
            print(f"  boundary {z+1}: {len(cur_l0)} states "
                  f"(new inserts {stats[0]}, dup hits {stats[1]}, "
                  f"prunes {stats[2]})", flush=True)
        stats[0] = 0; stats[1] = 0; stats[2] = 0
        if len(cur_l0) == 0:
            verdict = f"UNSAT (frontier empty at boundary {z+1})"
            break
    if verdict is None:
        acc = np.nonzero((cur_l0 == 0) & (cur_l1 == 0))[0]
        verdict = ("SAT (tiling exists)" if len(acc)
                   else "UNSAT (boundary reached, no accepting state)")
    return {"verdict": verdict, "per_layer": per_layer,
            "secs": round(time.time() - t0, 1), "families": fam}

# ---------------- D4 orbit counting (matches Python prototype) ----------------

def d4_orbits(state_pairs, w, h):
    """state_pairs: iterable of (L0, L1). Returns the number of distinct
    canonical pairs under the 8 D4 transforms + (min,max) L0/L1 swap,
    exactly as the Python prototype's sym_reduce."""
    def ap(m, k):
        out = 0
        for i in range(w * h):
            if (m >> i) & 1:
                x, y = i % w, i // w
                if k >= 4:
                    x = w - 1 - x
                for _ in range(k % 4):
                    x, y = y, w - 1 - x
                out |= 1 << (y * w + x)
        return out
    uniq = set()
    for (a, b) in state_pairs:
        best = None
        for k in range(8):
            pair = tuple(sorted((ap(a, k), ap(b, k))))
            if best is None or pair < best:
                best = pair
        uniq.add(best)
    return len(uniq)
