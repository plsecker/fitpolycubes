#!/usr/bin/env python3
"""Prototype: planar-layer frontier DP for the flat Z pentacube.

Geometric facts used:
  * Z pentacube cells (0,0,0),(1,0,0),(1,1,0),(1,2,0),(2,2,0) -- flat,
    z-span 1 in EVERY orientation (12 orientations = 4 planar x 3 planes).
  * Every placement lies in a single axis-parallel plane:
      xy (flat, one z-layer), xz (fixed y, spans 3 z-layers),
      yz (fixed x, spans 3 z-layers).
  * Vertical (xz/yz) pieces contribute per-layer cell counts (2,1,2)
    or (1,3,1) along z.

DP: fill z-layers in order. Boundary state (L0, L1) = cells of layers z, z+1
already filled by verticals started earlier (L2 == 0 at every boundary,
since no piece reaches 3 layers past its start). Inside a layer, DFS on the
lowest empty cell branches over flat pieces (in-layer) and vertical pieces
starting at this layer. Memoize failed boundary states (z, L0, L1).
"""
import sys, time
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from common.rotmatrix import RM

PIECE = [(0,0,0),(1,0,0),(1,1,0),(1,2,0),(2,2,0)]

def orientations():
    out = {}
    for m in RM:
        # cast to pure Python ints: np.int64 shifts overflow at bit 63
        rot = [tuple(sum(int(m[i][j])*int(c[j]) for j in range(3)) for i in range(3))
               for c in PIECE]
        mins = [min(c[i] for c in rot) for i in range(3)]
        rot = tuple(sorted((c[0]-mins[0], c[1]-mins[1], c[2]-mins[2]) for c in rot))
        out[rot] = True
    return list(out.keys())

def gen(w, h, nz):
    """returns FULL, flat(list per layer), vert(list per start layer)"""
    bit = lambda x, y: 1 << (y*w + x)
    FULL = (1 << (w*h)) - 1
    flat_masks = set()
    vert = [[] for _ in range(nz)]
    n_oris = Counter()
    for ori in orientations():
        sx = max(c[0] for c in ori); sy = max(c[1] for c in ori); sz = max(c[2] for c in ori)
        spans = (sx, sy, sz)
        if sz == 0:      # xy-plane
            n_oris['xy'] += 1
            for px in range(w - sx):
                for py in range(h - sy):
                    m = 0
                    for (cx, cy, cz) in ori:
                        m |= bit(px+cx, py+cy)
                    flat_masks.add(m)
        elif sy == 0:    # xz-plane (fixed y0)
            n_oris['xz'] += 1
            for y0 in range(h):
                for px in range(w - sx):
                    for pz in range(nz - 2):
                        m = [0,0,0]
                        for (cx, cy, cz) in ori:
                            m[cz] |= bit(px+cx, y0)
                        vert[pz].append((m[0], m[1], m[2]))
        elif sx == 0:    # yz-plane (fixed x0)
            n_oris['yz'] += 1
            for x0 in range(w):
                for py in range(h - sy):
                    for pz in range(nz - 2):
                        m = [0,0,0]
                        for (cx, cy, cz) in ori:
                            m[cz] |= bit(x0, py+cy)
                        vert[pz].append((m[0], m[1], m[2]))
        else:
            raise AssertionError("non-planar orientation")
    return FULL, sorted(flat_masks), vert, dict(n_oris)

def solve(w, h, nz, time_cap=600.0, verbose=True):
    FULL, flat, vert, oris = gen(w, h, nz)
    t0 = time.time()
    fail = set()
    stats = Counter()
    path = []
    LIMIT = (1 << 62)

    def dfs_layer(z, L0, L1):
        """complete layer z; returns success; L2 accumulated locally"""
        key = (z, L0, L1)
        if key in fail:
            stats['failcache_hits'] += 1
            return False
        filled = L0
        L2 = 0
        # iterative-ish recursive fill
        def fill(filled, L1, L2):
            stats['nodes'] += 1
            if time.time() - t0 > time_cap:
                raise TimeoutError
            if filled == FULL:
                if z + 1 == nz:
                    return True if L1 == 0 and L2 == 0 else False
                return dfs_layer(z+1, L1, L2)
            rem = FULL & ~filled
            e = rem & -rem
            # flat pieces covering e
            for m in flat:
                if m & e and (m & filled) == 0:
                    if fill(filled | m, L1, L2):
                        path.append(('F', z, m))
                        return True
            # vertical pieces starting at z covering e
            for (m0, m1, m2) in vert[z]:
                if (m0 & e) and (m0 & filled) == 0 and (m1 & L1) == 0 and (m2 & L2) == 0:
                    if fill(filled | m0, L1 | m1, L2 | m2):
                        path.append(('V', z, (m0, m1, m2)))
                        return True
            return False

        ok = fill(L0, L1, 0)
        if not ok:
            fail.add(key)
            stats['fail_states'] += 1
        else:
            stats['ok_states'] += 1
        return ok

    sys.setrecursionlimit(50000)
    try:
        ok = dfs_layer(0, 0, 0)
        err = None
    except TimeoutError:
        ok, err = False, "time cap"
    except RecursionError:
        ok, err = False, "recursion cap"
    dt = time.time() - t0
    return {"sat": ok, "err": err, "secs": round(dt, 1),
            "nodes": stats['nodes'], "fail_states": len(fail),
            "failcache_hits": stats['failcache_hits'],
            "path": list(reversed(path)) if ok else None}

if __name__ == "__main__":
    print("== known-answer validations (task 8) ==")
    for (w,h,nz,expect) in [(5,5,5,"UNSAT-rule 5x{5,6,7}"),
                            (6,6,5,"UNSAT-rule 5x{5,6,7}"),
                            (6,10,10,"SAT-rule 6x10x10 prime")]:
        r = solve(w,h,nz, time_cap=300.0)
        print(f"Z {w}x{h}x{nz} [{expect}]: sat={r['sat']} err={r['err']} "
              f"secs={r['secs']} nodes={r['nodes']} fail_states={r['fail_states']} "
              f"fail_hits={r['failcache_hits']}")
        if r['sat']:
            print("   tiling pieces:", len(r['path']))
