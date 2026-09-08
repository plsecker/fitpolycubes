#!/usr/bin/env python3
"""
Stage 5F-B: V=55 / 11-T unrestricted CK6 oddity search driver.

Architecture:
  fixed min-id shard ranges (no count phase required)
  + per-min-id visited sets (memory-bounded per min-id)
  + packed NumPy/Numba funnel
  + conservative parallelism (2 workers)

Target ownership: each connected target's minimum orbit id determines
its unique shard.  Shards partition the target space exactly.

The no-visited-set experiment was REJECTED: it causes exponential node
blowup (V=25 smoke test: >15 min vs <1 s with visited set).  Per-min-id
visited sets are retained for correct deduplication.
"""
import sys, os, time, json, resource, subprocess, argparse
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.oddity import l1_ball, is_face_connected, unique_orientations
from common.symmetry import ck6_affine_maps, canonical_form, full_symmetry, \
    element_kind
from common.registry import PENTACUBES
from common.packed_funnel import PackedFunnel
from common.algorithm_x import solve
from common.algorithm_x_fast import solve as solve_fast

PIECE = "T"


# ---------------------------------------------------------------------------
# universe
# ---------------------------------------------------------------------------

def build_universe(volume):
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


# ---------------------------------------------------------------------------
# seeded DFS (per-min-id visited set)
# ---------------------------------------------------------------------------

def iter_targets_seeded(un, min_id, budget):
    """Yield every connected CK6-closed target whose minimum orbit id is
    exactly min_id.  The visited set is LOCAL to this min-id and is
    discarded when the DFS completes (memory is bounded by one active
    min-id's state space, not by the entire V=55 search)."""
    adj, cost = un["adj"], un["cost"]
    all_orbits = un["all_orbits"]
    center = un["center"]
    s = min_id
    frontier = frozenset(j for j in (un["start_front"] | adj[s]) - {s}
                         if j >= s)
    visited = {(1 << s)}
    stack = [((1 << s), frontier, budget - cost[s])]
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
                yield cells
            continue
        for j in fr:
            c = cost[j]
            if c > rem:
                continue
            nm = mask | (1 << j)
            if nm in visited:
                continue
            visited.add(nm)
            stack.append((nm,
                          frozenset(x for x in (fr | adj[j]) - {j}
                                    if x >= s), rem - c))


# ---------------------------------------------------------------------------
# shard definition
# ---------------------------------------------------------------------------

def shard_range(shard_idx, n_shards, max_orbit_id):
    total = max_orbit_id + 1
    per = -(-total // n_shards)
    lo = shard_idx * per
    hi = min((shard_idx + 1) * per, total)
    return list(range(lo, hi))


# ---------------------------------------------------------------------------
# shard runner
# ---------------------------------------------------------------------------

def run_shard(volume, shard_idx, n_shards, workdir):
    piece = [tuple(map(int, c)) for c in PENTACUBES[PIECE]]
    un = build_universe(volume)
    budget = (volume - 1) // 2
    k = volume // len(piece)
    max_oid = len(un["all_orbits"]) - 1
    min_ids = shard_range(shard_idx, n_shards, max_oid)
    ff = PackedFunnel(piece, un["ball"])
    state = {
        "volume": volume, "shard": shard_idx, "n_shards": n_shards,
        "min_id_range": [min_ids[0], min_ids[-1]] if min_ids else None,
        "funnel": Counter(), "target_occurrences": 0,
        "sat": 0, "witnesses": [], "status": "running",
    }
    ckpt = os.path.join(workdir, f"shard_{shard_idx:03d}.checkpoint.json")
    result = os.path.join(workdir, f"shard_{shard_idx:03d}.json")
    stop = os.path.join(workdir, "STOP")
    t0 = time.time()
    last_ckpt = 0.0
    for s in min_ids:
        for t in iter_targets_seeded(un, s, budget):
            state["target_occurrences"] += 1
            stage, n_rows, cov = ff.funnel(t, k)
            if stage == "reject_k":
                state["funnel"]["reject: <k contained placements"] += 1
            elif stage == "reject_cov":
                state["funnel"]["reject: uncovered cell"] += 1
            else:
                state["funnel"]["pass coverage"] += 1
                # exact cover: reconstruct rows from the packed placement list
                tset = set(t)
                rows = [frozenset(pl) for pl in ff.idx.placements_list
                        if set(pl) <= tset]
                y = {i: sorted(p) for i, p in enumerate(rows)}
                x = {c: set() for c in t}
                for i, cs in y.items():
                    for c in cs:
                        x[c].add(i)
                n = sum(1 for sol in solve(x, y) if len(sol) == k)
                xf = {c: set() for c in t}
                for i, p in enumerate(rows):
                    for c in p:
                        xf[c].add(i)
                yf = {i: list(p) for i, p in enumerate(rows)}
                n_fast = sum(1 for _ in solve_fast(xf, yf, set(t),
                                                   [True] * len(rows)))
                assert n == n_fast, (sorted(t), n, n_fast)
                if n:
                    state["sat"] += 1
                    state["funnel"]["TILEABLE"] += 1
                    syms = full_symmetry(t)
                    wit = {
                        "volume": volume, "tiles": k, "piece": PIECE,
                        "canonical_target": canonical_form(t),
                        "placements": sorted(sorted(p) for p in rows),
                        "symmetry_order": len(syms),
                        "symmetry_kinds": dict(Counter(
                            element_kind(m) for m in syms)),
                        "shard": shard_idx,
                    }
                    wpath = os.path.join(workdir,
                                         f"witness_{state['sat']:03d}.json")
                    with open(wpath, "w") as f:
                        json.dump(wit, f, indent=1)
                    state["witnesses"].append(wpath)
                    with open(stop, "w") as f:
                        f.write(f"SAT in shard {shard_idx}\n")
            if os.path.exists(stop):
                state["status"] = "stopped-early"
                break
            now = time.time()
            if now - last_ckpt > 120:
                state["elapsed_s"] = round(time.time() - t0, 1)
                state["peak_rss_mb"] = round(
                    resource.getrusage(
                        resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
                atomic_write(ckpt, state)
                last_ckpt = now
    state["status"] = ("complete" if state["status"] == "running"
                       else state["status"])
    state["elapsed_s"] = round(time.time() - t0, 1)
    state["peak_rss_mb"] = round(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    atomic_write(result, state)
    if os.path.exists(ckpt):
        os.remove(ckpt)
    print(f"shard {shard_idx}: occ={state['target_occurrences']} "
          f"funnel={dict(state['funnel'])} sat={state['sat']} "
          f"elapsed={state['elapsed_s']}s", flush=True)


def atomic_write(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=1, default=str)
    os.rename(tmp, path)


def canonical_form(cells):
    from common.symmetry import canonical_form as cf
    return cf(cells)


def full_symmetry(cells):
    from common.symmetry import full_symmetry as fs
    return fs(cells)


# ---------------------------------------------------------------------------
# aggregate
# ---------------------------------------------------------------------------

def aggregate(volume, n_shards, workdir):
    agg = Counter()
    sat = 0
    total = 0
    missing = []
    for i in range(n_shards):
        path = os.path.join(workdir, f"shard_{i:03d}.json")
        if not os.path.exists(path):
            missing.append(i)
            continue
        with open(path) as f:
            r = json.load(f)
        total += r["target_occurrences"]
        for k2, v in r["funnel"].items():
            agg[k2] += v
        sat += r["sat"]
    print(f"AGGREGATE: target occurrences {total:,}")
    print(f"AGGREGATE: funnel {dict(agg)}")
    print(f"AGGREGATE: SAT {sat}")
    if missing:
        print(f"AGGREGATE: INCOMPLETE - missing shards: {missing}")
    elif sat == 0:
        print(f"VERDICT: V={volume} PROVEN NEGATIVE (occurrence-based)")
    else:
        print(f"VERDICT: V={volume} POSITIVE — {sat} tileable occurrence(s)")


# ---------------------------------------------------------------------------
# shard plan
# ---------------------------------------------------------------------------

def write_shard_plan(volume, n_shards, workdir):
    un = build_universe(volume)
    max_oid = len(un["all_orbits"]) - 1
    shards = []
    for i in range(n_shards):
        lo, hi = i, i
        r = shard_range(i, n_shards, max_oid)
        shards.append({"shard": i, "min_ids": r,
                       "range": [r[0], r[-1]] if r else None})
    plan = {"volume": volume, "n_shards": n_shards,
            "max_orbit_id": max_oid, "shards": shards,
            "method": "fixed contiguous min-id ranges (no count phase)",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
    path = os.path.join(workdir, "shard_plan.json")
    with open(path, "w") as f:
        json.dump(plan, f, indent=1)
    print(f"shard plan written: {path}")
    return plan


# ---------------------------------------------------------------------------
# main dispatch
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["shard", "run", "aggregate",
                                    "plan", "status"])
    ap.add_argument("--volume", type=int, default=55)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=8)
    ap.add_argument("--parallel", type=int, default=2)
    ap.add_argument("--workdir", default=None)
    args = ap.parse_args()
    workdir = args.workdir or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", f"ck6_v{args.volume}")
    os.makedirs(workdir, exist_ok=True)

    if args.cmd == "plan":
        write_shard_plan(args.volume, args.shards, workdir)
    elif args.cmd == "shard":
        run_shard(args.volume, args.shard, args.shards, workdir)
    elif args.cmd == "run":
        n_shards = args.shards
        print(f"[run] V={args.volume}, {n_shards} fixed min-id shards, "
              f"{args.parallel} workers", flush=True)
        write_shard_plan(args.volume, n_shards, workdir)
        pending = list(range(n_shards))
        queue = list(pending)
        running = {}
        t0 = time.time()
        while queue or running:
            while queue and len(running) < args.parallel:
                i = queue.pop(0)
                logf = open(os.path.join(workdir, f"shard_{i:03d}.log"), "a")
                p = subprocess.Popen(
                    [sys.executable, os.path.abspath(__file__), "shard",
                     "--volume", str(args.volume), "--shard", str(i),
                     "--shards", str(n_shards), "--workdir", workdir],
                    stdout=logf, stderr=subprocess.STDOUT)
                running[i] = p
                print(f"[run] launched shard {i} (pid {p.pid})", flush=True)
            for i in [i for i, p in running.items() if p.poll() is not None]:
                print(f"[run] shard {i} finished "
                      f"rc={running.pop(i).returncode}", flush=True)
            stop = os.path.join(workdir, "STOP")
            if os.path.exists(stop):
                print("[run] STOP marker found", flush=True)
                break
            time.sleep(2)
        for p in running.values():
            p.wait()
        el = time.time() - t0
        print(f"[run] all done in {el:.0f}s", flush=True)
        aggregate(args.volume, n_shards, workdir)
    elif args.cmd == "aggregate":
        aggregate(args.volume, args.shards, workdir)
    elif args.cmd == "status":
        for f in sorted(os.listdir(workdir)):
            if f.startswith("shard_") and f.endswith(".json") \
                    and "checkpoint" not in f:
                with open(os.path.join(workdir, f)) as fh:
                    r = json.load(fh)
                print(f, "occ", r.get("target_occurrences", "?"),
                      "sat", r.get("sat", "?"), "status", r.get("status"))
        stop = os.path.join(workdir, "STOP")
        if os.path.exists(stop):
            print("STOP exists")


if __name__ == "__main__":
    main()