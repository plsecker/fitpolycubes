#!/usr/bin/env python3
"""
Stage 4B: complete exhaustive V=35 (7 T pentacube) CK6 oddity search.

Architecture (per Stage 4A, docs/frontier/ck6_oddity_design.md section 10.5):

  count   one reference orbit-DFS pass over the L1<=17 universe; every leaf
          (connected CK6-closed 35-cell target) is attributed to its minimum
          orbit id, giving the exact shard partition and the grand total.
  plan    balance minimum-orbit-id values into N contiguous shard ranges.
  shard   for each min-id s in the shard range: a *seeded* DFS (bit s preset,
          ids < s forbidden) enumerates exactly the targets whose minimum
          orbit id is s; each target streams through the containment/coverage
          funnel (PlacementIndex) and coverage-passing targets go to exact
          cover (algorithm_x), dual-verified with algorithm_x_fast.  Any
          tileable target is written as a witness immediately and sets the
          global STOP file.
  run     spawn shards in parallel, aggregate, verify totals, and (if the
          result is negative) re-run the DFS in reversed traversal order as
          an independent consistency check.
  status  inspect progress.

Sharding correctness: every connected target contains the center cell and is
face-connected, hence its orbit set intersects the start frontier; seeding
bit s and forbidding ids < s makes shard s enumerate exactly the targets
whose minimum orbit id is s.  Distinct seeds explore disjoint state spaces
(a state's minimum id is intrinsic), so shards partition both targets and
DFS states with zero duplicate work.  Seeded growth starts from
{center, s} which may be disconnected; leaf connectivity is therefore
checked explicitly (the reference single-process enumerator in
common.oddity.enumerate_connected_ck6_targets needs no such check because it
grows from the center alone).

All odd volumes are supported; V=35 is the default.  The reference
single-process implementation remains solvers/t_ck6_oddity_search.py.
"""

import argparse
import json
import os
import resource
import subprocess
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.oddity import PlacementIndex, is_face_connected, l1_ball, \
    max_l1_for_volume
from common.registry import PENTACUBES
from common.symmetry import canonical_form, ck6_affine_maps, full_symmetry, \
    element_kind

PIECE = "T"


def build_universe(volume):
    radius = max_l1_for_volume(volume)
    ball = l1_ball(radius)
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
        return ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                (x, y - 1, z), (x, y, z + 1), (x, y, z - 1))

    adj = [set() for _ in all_orbits]
    for i, o in enumerate(all_orbits):
        for c in o:
            for nb in nbrs(c):
                j = cell2orb.get(nb)
                if j is not None and j != i:
                    adj[i].add(j)
    start_front = frozenset(cell2orb[nb] for nb in nbrs(center)
                            if nb in cell2orb)
    return dict(radius=radius, ball=ball, bset=bset, all_orbits=all_orbits,
                cell2orb=cell2orb, cost=cost, adj=adj, start_front=start_front,
                center=center, nbrs=nbrs)


def iter_targets_seeded(un, min_id, budget):
    """Yield every connected CK6-closed target whose minimum orbit id is
    exactly min_id (seeded DFS; ids < min_id forbidden; leaf connectivity
    checked because the seed need not be center-adjacent)."""
    adj, cost = un["adj"], un["cost"]
    all_orbits = un["all_orbits"]
    center = un["center"]
    s = min_id
    frontier = frozenset(j for j in (un["start_front"] | adj[s]) - {s}
                         if j >= s)
    visited = {(1 << s)}
    stack = [((1 << s), frontier, budget - cost[s])]
    while stack:
        mask, frontier_, rem = stack.pop()
        if rem == 0:
            cells = {center}
            m = mask
            while m:
                b = m & -m
                cells |= set(all_orbits[b.bit_length() - 1])
                m ^= b
            if not is_face_connected(cells):
                continue
            yield cells
            continue
        for j in frontier_:
            c = cost[j]
            if c > rem:
                continue
            nm = mask | (1 << j)
            if nm in visited:
                continue
            visited.add(nm)
            nf = frozenset(x for x in (frontier_ | adj[j]) - {j} if x >= s)
            stack.append((nm, nf, rem - c))


def count_minids(un, volume):
    """Reference DFS pass: per-leaf minimum orbit id histogram."""
    adj, cost = un["adj"], un["cost"]
    t0 = time.time()
    visited = {0}
    stack = [(0, un["start_front"], (volume - 1) // 2)]
    hist = Counter()
    leaves = 0
    while stack:
        mask, frontier, rem = stack.pop()
        if rem == 0:
            hist[(mask & -mask).bit_length() - 1] += 1
            leaves += 1
            continue
        for j in sorted(frontier):
            c = cost[j]
            if c > rem:
                continue
            nm = mask | (1 << j)
            if nm in visited:
                continue
            visited.add(nm)
            stack.append((nm, (frontier | adj[j]) - {j}, rem - c))
    return (dict(total=leaves,
                 hist={str(k): v for k, v in sorted(hist.items())},
                 elapsed_s=round(time.time() - t0, 2)), leaves)


def funnel_and_cover(t, index, k, shard_state, ff=None):
    """Containment/coverage funnel + exact cover + dual-solver audit.

    ff (optional FastFunnel) runs the hot containment/coverage stages
    as a compiled kernel; its decisions are identical to
    index.contained (validated on complete V=25/V=35 workloads).  The
    reference index is consulted only for survivors, to recover the
    contained rows for exact cover.
    """
    if ff is not None:
        stage0, n_rows, _ = ff.funnel(t, k)
        if stage0 == "reject_k":
            shard_state["funnel"]["reject: <k contained placements"] += 1
            return "reject_k", 0, None
        if stage0 == "reject_cov":
            shard_state["funnel"]["reject: uncovered cell"] += 1
            return "reject_cov", 0, None
    rows, covered, tmask = index.contained(t)
    if len(rows) < k:
        shard_state["funnel"]["reject: <k contained placements"] += 1
        return "reject_k", 0, None
    if covered != tmask:
        shard_state["funnel"]["reject: uncovered cell"] += 1
        return "reject_cov", 0, None
    shard_state["funnel"]["pass coverage"] += 1
    from common.algorithm_x import solve
    y = {i: sorted(p) for i, p in enumerate(rows)}
    x = {c: set() for c in t}
    for i, cs in y.items():
        for c in cs:
            x[c].add(i)
    n = sum(1 for sol in solve(x, y) if len(sol) == k)
    from common.algorithm_x_fast import solve as solve_fast
    # X[c] must be the set of row indices covering cell c (passing all
    # row indices for every column silently disables the solver)
    row_list = list(rows)
    xf = {c: set() for c in t}
    for i, p in enumerate(row_list):
        for c in p:
            xf[c].add(i)
    yf = {i: list(p) for i, p in enumerate(row_list)}
    n_fast = sum(1 for _ in solve_fast(xf, yf, set(t),
                                       [True] * len(row_list)))
    if n != n_fast:
        raise AssertionError(f"dual-solver mismatch on {sorted(t)}: "
                             f"{n} vs {n_fast}")
    if n:
        shard_state["funnel"]["TILEABLE"] += 1
        return "SAT", n, rows
    shard_state["funnel"]["reject: exact cover UNSAT"] += 1
    return "UNSAT", 0, None


def run_shard(volume, shard_idx, min_ids, workdir):
    budget = (volume - 1) // 2
    piece = [tuple(map(int, c)) for c in PENTACUBES[PIECE]]
    un = build_universe(volume)
    from common.fastfunnel import FastFunnel
    ff = FastFunnel(piece, un["ball"])
    index = ff.index
    k = volume // len(piece)
    state = {"volume": volume, "shard": shard_idx, "min_ids": min_ids,
             "funnel": Counter(), "targets": 0, "sat": 0, "unsat": 0,
             "witnesses": [], "status": "running"}
    ckpt = os.path.join(workdir, f"shard_{shard_idx:03d}.checkpoint.json")
    result = os.path.join(workdir, f"shard_{shard_idx:03d}.json")
    stop = os.path.join(workdir, "STOP")
    t0 = time.time()
    last_ckpt = 0.0
    for s in min_ids:
        for t in iter_targets_seeded(un, s, budget):
            state["targets"] += 1
            stage, n, rows = funnel_and_cover(t, index, k, state, ff=ff)
            if stage == "SAT":
                state["sat"] += 1
                syms = full_symmetry(t)
                wit = {
                    "volume": volume, "tiles": k, "piece": PIECE,
                    "canonical_target": canonical_form(t),
                    "placements": sorted(sorted(p) for p in rows),
                    "symmetry_order": len(syms),
                    "symmetry_kinds": dict(Counter(
                        element_kind(m) for m in syms)),
                    "dual_solver_counts": [n, n],
                    "shard": shard_idx,
                }
                wpath = os.path.join(workdir, f"witness_{state['sat']:03d}.json")
                with open(wpath, "w") as f:
                    json.dump(wit, f, indent=1)
                state["witnesses"].append(wpath)
                with open(stop, "w") as f:
                    f.write(f"SAT target found in shard {shard_idx}\n")
            if os.path.exists(stop):
                state["status"] = "stopped-early"
                break
            now = time.time()
            if now - last_ckpt > 120:
                state["elapsed_s"] = round(time.time() - t0, 1)
                state["peak_rss_mb"] = round(
                    resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
                with open(ckpt, "w") as f:
                    json.dump(state, f, default=dict)
                last_ckpt = now
    state["status"] = ("complete" if state["status"] == "running"
                       else state["status"])
    state["elapsed_s"] = round(time.time() - t0, 1)
    state["peak_rss_mb"] = round(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    with open(result, "w") as f:
        json.dump(state, f, default=dict, indent=1)
    if os.path.exists(ckpt):
        os.remove(ckpt)
    print(f"shard {shard_idx}: targets={state['targets']} "
          f"funnel={dict(state['funnel'])} sat={state['sat']} "
          f"elapsed={state['elapsed_s']}s", flush=True)


def cmd_count(args):
    """Reference target count.

    For volumes whose monolithic DFS fits in memory (V <= 35) this is
    the single reference DFS pass.  For larger volumes (V = 45+) the
    monolithic DFS hits the RAM wall (Stage 4C: 41M states / 23.5 GB
    capped at V=45), so the count runs SHARDED: per-min-id seeded DFS
    passes, each memory-bounded, with a checkpoint per completed min-id
    so an interrupted count resumes exactly.
    """
    os.makedirs(args.workdir, exist_ok=True)
    counts_path = os.path.join(args.workdir, "minid_counts.json")
    partial_path = os.path.join(args.workdir, "minid_partial.json")
    if args.volume <= 35:
        un = build_universe(args.volume)
        res, leaves = count_minids(un, args.volume)
        expected = {25: 71539, 35: 15289669}
        if args.volume in expected:
            assert leaves == expected[args.volume], \
                (leaves, expected[args.volume])
        res["volume"] = args.volume
        with open(counts_path, "w") as f:
            json.dump(res, f, indent=1)
        print(f"count: {leaves} targets ({res['elapsed_s']}s); "
              f"{len(res['hist'])} distinct min-ids")
        return
    # sharded count for large volumes
    un = build_universe(args.volume)
    budget = (args.volume - 1) // 2
    # candidate min-ids: every orbit id that can be a minimum, i.e. is
    # in the start frontier or reachable from it via >= ids; cheap
    # validity prefilter: seeded reachability
    start_front = sorted(un["start_front"])
    cands = set(start_front)
    for s0 in start_front:
        stack = [s0]
        seen = {s0}
        while stack:
            v = stack.pop()
            for w in un["adj"][v]:
                if w >= s0 and w not in seen:
                    seen.add(w)
                    cands.add(w)
                    stack.append(w)
    cands = sorted(cands)
    print(f"sharded count: {len(cands)} candidate min-ids")
    done = {}
    if os.path.exists(counts_path):
        with open(counts_path) as f:
            old = json.load(f)
        done = {int(k): v for k, v in old.get("hist", {}).items()}
    t0 = time.time()
    for i, s in enumerate(cands):
        if s in done:
            continue
        cnt = 0
        for _t in iter_targets_seeded(un, s, budget):
            cnt += 1
        done[s] = cnt
        if (i + 1) % 20 == 0:
            with open(counts_path, "w") as f:
                json.dump({"volume": args.volume,
                           "hist": {str(k): v for k, v in sorted(done.items())},
                           "total": sum(done.values()),
                           "elapsed_s": round(time.time() - t0, 1),
                           "cands_total": len(cands)}, f, indent=1)
            print(f"  min-id {s} ({i+1}/{len(cands)}): {cnt:,} "
                  f"cumulative {sum(done.values()):,} "
                  f"({time.time()-t0:.0f}s)", flush=True)
    total = sum(done.values())
    res = {"volume": args.volume, "total": total,
           "hist": {str(k): v for k, v in sorted(done.items())},
           "elapsed_s": round(time.time() - t0, 1), "method": "sharded"}
    with open(counts_path, "w") as f:
        json.dump(res, f, indent=1)
    print(f"count: {total:,} targets ({res['elapsed_s']}s); "
          f"{len(res['hist'])} distinct min-ids")


def cmd_plan(args):
    with open(os.path.join(args.workdir, "minid_counts.json")) as f:
        res = json.load(f)
    items = sorted(((int(k), v) for k, v in res["hist"].items()),
                   key=lambda kv: -kv[1])
    bins = [[] for _ in range(args.shards)]
    loads = [0] * args.shards
    for mid, cnt in items:
        i = min(range(args.shards), key=lambda i: loads[i])
        bins[i].append(mid)
        loads[i] += cnt
    shards = [{"shard": i, "min_ids": sorted(b), "expected": loads[i]}
              for i, b in enumerate(bins)]
    with open(os.path.join(args.workdir, "shards.json"), "w") as f:
        json.dump({"volume": args.volume, "shards": shards,
                   "total": sum(loads)}, f, indent=1)
    print(f"planned {len(shards)} shards, total {sum(loads)}; "
          f"expected load per shard: {sorted(loads, reverse=True)}")


def cmd_shard(args):
    with open(os.path.join(args.workdir, "shards.json")) as f:
        plan = json.load(f)
    sh = next(s for s in plan["shards"] if s["shard"] == args.shard)
    run_shard(args.volume, args.shard, sh["min_ids"], args.workdir)


def cmd_run(args):
    os.makedirs(args.workdir, exist_ok=True)
    if not os.path.exists(os.path.join(args.workdir, "minid_counts.json")):
        cmd_count(args)
    if (args.replan or
            not os.path.exists(os.path.join(args.workdir, "shards.json"))):
        cmd_plan(args)
    with open(os.path.join(args.workdir, "shards.json")) as f:
        plan = json.load(f)
    n = min(args.shards, len(plan["shards"]))
    if len(plan["shards"]) != n:
        # rebalance the planned min-id values into exactly n contiguous ranges
        with open(os.path.join(args.workdir, "minid_counts.json")) as f:
            hist = json.load(f)["hist"]
        flat = sorted((int(mid), hist[mid]) for mid in hist)
        per = -(-sum(c for _, c in flat) // n)
        shards, cur, acc = [], [], 0
        for mid, cnt in flat:
            cur.append(mid)
            acc += cnt
            if acc >= per and len(shards) < n - 1:
                shards.append(cur)
                cur, acc = [], 0
        if cur:
            shards.append(cur)
        plan["shards"] = [{"shard": i, "min_ids": mids}
                          for i, mids in enumerate(shards)]
        with open(os.path.join(args.workdir, "shards.json"), "w") as f:
            json.dump(plan, f, indent=1)
    pending = [s["shard"] for s in plan["shards"]
               if not os.path.exists(os.path.join(
                   args.workdir, f"shard_{s['shard']:03d}.json"))]
    print(f"[run] {len(pending)} shards to run on {args.parallel} workers",
          flush=True)
    queue = list(pending)
    running = {}
    while queue or running:
        while queue and len(running) < args.parallel:
            i = queue.pop(0)
            logf = open(os.path.join(args.workdir, f"shard_{i:03d}.log"), "a")
            p = subprocess.Popen(
                [sys.executable, os.path.abspath(__file__), "shard",
                 "--volume", str(args.volume), "--shard", str(i),
                 "--workdir", args.workdir],
                stdout=logf, stderr=subprocess.STDOUT)
            running[i] = p
            print(f"[run] launched shard {i} (pid {p.pid})", flush=True)
        for i in [i for i, p in running.items() if p.poll() is not None]:
            print(f"[run] shard {i} finished rc={running.pop(i).returncode}",
                  flush=True)
        time.sleep(2)
    aggregate(args)


def aggregate(args):
    workdir = args.workdir
    with open(os.path.join(workdir, "minid_counts.json")) as f:
        counts = json.load(f)
    with open(os.path.join(workdir, "shards.json")) as f:
        plan = json.load(f)
    total = 0
    agg = Counter()
    sat = unsat = 0
    witnesses = []
    elapsed = rss = 0.0
    missing = []
    for s in plan["shards"]:
        path = os.path.join(workdir, f"shard_{s['shard']:03d}.json")
        if not os.path.exists(path):
            missing.append(s["shard"])
            continue
        with open(path) as f:
            r = json.load(f)
        total += r["targets"]
        for k2, v in r["funnel"].items():
            agg[k2] += v
        sat += r["sat"]
        unsat += r["unsat"]
        witnesses.extend(r["witnesses"])
        elapsed = max(elapsed, r.get("elapsed_s", 0))
        rss = max(rss, r.get("peak_rss_mb", 0))
    expected = counts["total"]
    print(f"AGGREGATE: targets {total} / expected {expected} "
          f"match={total == expected}")
    print(f"AGGREGATE: funnel {dict(agg)}")
    print(f"AGGREGATE: sat {sat} unsat {unsat} witnesses {len(witnesses)}")
    if missing:
        print(f"AGGREGATE: INCOMPLETE - missing shards: {missing}")
        return
    if sat == 0:
        print("AGGREGATE: negative result - reversed-order DFS consistency "
              "check...")
        un = build_universe(args.volume)
        t0 = time.time()
        visited = {0}
        stack = [(0, un["start_front"], (args.volume - 1) // 2)]
        leaves = 0
        while stack:
            mask, frontier, rem = stack.pop()
            if rem == 0:
                leaves += 1
                continue
            for j in sorted(frontier, reverse=True):
                c = un["cost"][j]
                if c > rem:
                    continue
                nm = mask | (1 << j)
                if nm in visited:
                    continue
                visited.add(nm)
                stack.append((nm, (frontier | un["adj"][j]) - {j}, rem - c))
        print(f"AGGREGATE: reversed-order leaves {leaves} "
              f"({time.time()-t0:.0f}s) match={leaves == expected}")
        assert leaves == expected
        verdict = (f"V={args.volume} PROVEN NEGATIVE: no CK6-or-higher "
                   f"symmetric {args.volume}-cell polycube is tileable by "
                   f"{args.volume // 5} T pentacubes")
    else:
        verdict = f"V={args.volume} POSITIVE: {sat} tileable target(s) found"
    report = {"volume": args.volume, "status": "COMPLETE",
              "total_targets": total, "expected_targets": expected,
              "funnel": dict(agg), "sat": sat, "unsat": unsat,
              "witnesses": witnesses, "elapsed_shard_max_s": elapsed,
              "peak_rss_mb": rss, "verdict": verdict}
    with open(os.path.join(workdir, "report.json"), "w") as f:
        json.dump(report, f, indent=1)
    print("REPORT:", json.dumps(report, indent=1))


def cmd_status(args):
    workdir = args.workdir
    if not os.path.isdir(workdir):
        print("no workdir")
        return
    for f in sorted(os.listdir(workdir)):
        if f.startswith("shard_") and f.endswith(".json") \
                and "checkpoint" not in f:
            with open(os.path.join(workdir, f)) as fh:
                r = json.load(fh)
            print(f, "targets", r["targets"], "sat", r["sat"],
                  "status", r.get("status"))
    for name in ("report.json", "STOP"):
        p = os.path.join(workdir, name)
        if os.path.exists(p):
            print(name, "exists")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["count", "plan", "shard", "run",
                                    "aggregate", "status"])
    ap.add_argument("--volume", type=int, default=35)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=4)
    ap.add_argument("--parallel", type=int, default=4)
    ap.add_argument("--workdir", default="data/ck6_v35")
    ap.add_argument("--replan", action="store_true")
    args = ap.parse_args()
    dict(count=cmd_count, plan=cmd_plan, shard=cmd_shard, run=cmd_run,
         aggregate=aggregate, status=cmd_status)[args.cmd](args)


if __name__ == "__main__":
    main()