#!/usr/bin/env python3
"""
Stage 5D: V=55 feasibility benchmark harness.

Detached, checkpointed, bounded-memory probes + FastFunnel benchmark.
Writes one JSON result per min-id probe and per funnel benchmark batch.
Never launches the full V=55 search.
"""
import sys, os, time, json, resource, argparse
from collections import Counter
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.symmetry import ck6_affine_maps
from common.oddity import l1_ball, is_face_connected, placements_in_region, \
    unique_orientations, count_exact_covers
from common.registry import PENTACUBES
from common.fastfunnel import FastFunnel

WORKDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "data", "ck6_v55_feas")


def build_universe(volume=55):
    R = (volume - 1) // 2
    ball = l1_ball(R)
    bset = set(ball)
    maps = list(ck6_affine_maps((0, 0)).values())
    center = (0, 0, 0)
    four, two, seen = [], [], set()
    for v in ball:
        if v in seen:
            continue
        o = frozenset(m(v) for m in maps)
        seen |= o
        if not o <= bset or v == center:
            continue
        (four if len(o) == 4 else two).append(o)
    all_orbits = four + two
    cell2orb = {}
    for i, o in enumerate(all_orbits):
        for c in o:
            cell2orb[c] = i
    cost = [2] * len(four) + [1] * len(two)

    def nbrs(v):
        x, y, z = v
        return ((x+1, y, z), (x-1, y, z), (x, y+1, z),
                (x, y-1, z), (x, y, z+1), (x, y, z-1))

    adj = [set() for _ in all_orbits]
    for i, o in enumerate(all_orbits):
        for c in o:
            for nb in nbrs(c):
                j = cell2orb.get(nb)
                if j is not None and j != i:
                    adj[i].add(j)
    start_front = frozenset(cell2orb[nb] for nb in nbrs(center)
                            if nb in cell2orb)
    return dict(radius=R, ball=ball, bset=bset, all_orbits=all_orbits,
                cell2orb=cell2orb, cost=cost, adj=adj,
                start_front=start_front, center=center, nbrs=nbrs)


def atomic_write_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=1, default=str)
    os.rename(tmp, path)


def seeded_probe(un, min_id, node_cap, time_cap):
    """Capped seeded DFS; returns dict with nodes/states/leaves/RSS."""
    adj, cost = un["adj"], un["cost"]
    all_orbits = un["all_orbits"]
    center = un["center"]
    s = min_id
    frontier = frozenset(j for j in (un["start_front"] | adj[s]) - {s}
                         if j >= s)
    visited = {(1 << s)}
    stack = [((1 << s), frontier, 27 - cost[s])]
    leaves = nodes = 0
    t0 = time.time()
    while stack:
        mask, fr, rem = stack.pop()
        if rem == 0:
            cells = {center}
            m = mask
            while m:
                b = m & -m
                cells |= set(all_orbits[b.bit_length() - 1])
                m ^= b
            if is_face_connected(cells):
                leaves += 1
            continue
        nodes += 1
        if nodes % 100_000 == 0:
            now = time.time()
            if now - t0 > time_cap or len(visited) > 40_000_000:
                rss = resource.getrusage(
                    resource.RUSAGE_SELF).ru_maxrss / 1024
                return dict(status="CAPPED_TIME" if now - t0 > time_cap
                            else "CAPPED_NODES",
                            nodes=nodes, visited=len(visited),
                            leaves=leaves, elapsed_s=round(now - t0, 1),
                            peak_rss_mb=round(rss, 0))
        for j in fr:
            c = cost[j]
            if c > rem:
                continue
            nm = mask | (1 << j)
            if nm in visited:
                continue
            visited.add(nm)
            stack.append((nm, (fr | adj[j]) - {j}, rem - c))
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    return dict(status="DONE", nodes=nodes, visited=len(visited),
                leaves=leaves, elapsed_s=round(time.time() - t0, 1),
                peak_rss_mb=round(rss, 0))


def probe_min_ids(volume, min_ids, node_cap, time_cap, workdir):
    un = build_universe(volume)
    for s in min_ids:
        path = os.path.join(workdir, f"probe_{s}.json")
        if os.path.exists(path):
            continue
        r = seeded_probe(un, s, node_cap, time_cap)
        r["min_id"] = s
        atomic_write_json(path, r)
        print(f"probe {s}: {r['status']} nodes={r['nodes']:,} "
              f"leaves={r['leaves']:,} ({r['elapsed_s']}s)", flush=True)


def funnel_bench(volume, min_ids, target_cap, workdir):
    """FastFunnel benchmark on real V=55 targets from the given min-ids."""
    piece = [tuple(map(int, c)) for c in PENTACUBES["T"]]
    un = build_universe(volume)
    ff = FastFunnel(piece, un["ball"])
    adj, cost = un["adj"], un["cost"]
    all_orbits = un["all_orbits"]
    center = un["center"]
    funnel = Counter()
    t0 = time.time()
    for s in min_ids:
        path = os.path.join(workdir, f"funnel_{s}.json")
        if os.path.exists(path):
            continue
        # generate targets (seeded DFS, no connectivity filter — funnel handles all)
        frontier = frozenset(j for j in (un["start_front"] | adj[s]) - {s}
                             if j >= s)
        visited = {(1 << s)}
        stack = [((1 << s), frontier, 27 - cost[s])]
        n_gen = 0
        for t in _targets(visited, stack, all_orbits, center, s, target_cap):
            funnel["targets"] += 1
            rows, cov, tm = ff.index.contained(t)
            if len(rows) < 11:
                funnel["reject: <11 contained placements"] += 1
                continue
            if cov != tm:
                funnel["reject: uncovered cell"] += 1
                continue
            funnel["pass coverage"] += 1
            survivors.append((t, rows))
            n_gen += 1
            if n_gen >= target_cap:
                break
        el = time.time() - t0
        rate = funnel["targets"] / el
        atomic_write_json(path, dict(funnel=dict(funnel), elapsed=round(el, 1),
                                     rate=round(rate, 0)))
        print(f"funnel min-id {s}: cumulative {dict(funnel)} rate {rate:.0f}/s",
              flush=True)
    return funnel, survivors


def _targets(visited, stack, all_orbits, center, s, cap):
    """Rebuild generator from stack state for funnel_bench."""
    yield from []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["probe", "funnel", "status", "count"])
    ap.add_argument("--volume", type=int, default=55)
    ap.add_argument("--min-ids", type=str, default="",
                    help="comma-separated min-id values to probe")
    ap.add_argument("--node-cap", type=int, default=1_000_000)
    ap.add_argument("--time-cap", type=int, default=150)
    ap.add_argument("--target-cap", type=int, default=100_000)
    ap.add_argument("--workdir", default=WORKDIR)
    args = ap.parse_args()
    os.makedirs(args.workdir, exist_ok=True)

    if args.cmd == "probe":
        ids = [int(x) for x in args.min_ids.split(",") if x.strip()]
        probe_min_ids(args.volume, ids, args.node_cap, args.time_cap,
                      args.workdir)
    elif args.cmd == "status":
        for f in sorted(os.listdir(args.workdir)):
            if f.endswith(".json"):
                path = os.path.join(args.workdir, f)
                with open(path) as fh:
                    r = json.load(fh)
                print(f, json.dumps(r, default=str)[:200])
    elif args.cmd == "count":
        un = build_universe(args.volume)
        min_ids = sorted(un["start_front"])
        probe_min_ids(args.volume, min_ids, 2_000_000, 300, args.workdir)


if __name__ == "__main__":
    main()