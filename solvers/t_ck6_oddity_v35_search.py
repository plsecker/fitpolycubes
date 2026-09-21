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


def iter_targets_seeded(un, min_id, budget, stats=None, limits=None):
    """Yield every connected CK6-closed target whose minimum orbit id is
    exactly min_id (seeded DFS; ids < min_id forbidden; leaf connectivity
    checked because the seed need not be center-adjacent).

    Visited-set representation: orbit ids are stored SHIFTED DOWN by the
    per-search minimum id s (mask bit i represents orbit id i + s).  This
    is safe because every mask in this search only ever sets bits for ids
    in [s, 3937], so the shifted masks live in [0, 3937 - s] and the
    mapping is a bijection; the visited set is local to one min-id search
    (never shared across shards), so no cross-search identity is needed.
    The shift keeps the Python ints small (<= 348 bits for min-id 3590
    instead of 3938), cutting visited-set memory ~5.5x (106 vs 586
    bytes/entry) with faster hashing; exact-equivalence vs the unshifted
    representation was validated on real min-id-3590 masks."""
    adj, cost = un["adj"], un["cost"]
    all_orbits = un["all_orbits"]
    center = un["center"]
    s = min_id
    frontier = frozenset(j for j in (un["start_front"] | adj[s]) - {s}
                         if j >= s)
    visited = {1}  # shifted seed: orbit id s -> bit 0
    stack = [(1, frontier, budget - cost[s])]
    while stack:
        mask, frontier_, rem = stack.pop()
        if rem == 0:
            cells = {center}
            m = mask
            while m:
                b = m & -m
                cells |= set(all_orbits[(b.bit_length() - 1) + s])
                m ^= b
            if not is_face_connected(cells):
                continue
            yield cells
            continue
        for j in frontier_:
            c = cost[j]
            if c > rem:
                continue
            nm = mask | (1 << (j - s))  # shift orbit id j down by s
            if nm in visited:
                continue
            visited.add(nm)
            nf = frozenset(x for x in (frontier_ | adj[j]) - {j} if x >= s)
            stack.append((nm, nf, rem - c))


def _conn_prune_data(un):
    """Root-level reachability data for the connectivity-pruned seeded
    enumerator, computed once and cached on the universe dict.

    dist_to_center[s]: minimum node-weight path cost from orbit s to the
    centre (Dijkstra over the orbit graph; node weight = orbit cost).
    Any target containing orbit s must contain a path from s to the
    centre, so dist_to_center[s] is a LOWER BOUND on the target's total
    cost; if it exceeds the budget the bucket is provably empty.

    cells_ge[s]: |union of orbits with id >= s|.  A target with min-id s
    has every orbit >= s, so its non-centre cells are a subset of that
    union; if the union has fewer than volume - 1 cells the bucket is
    provably empty.
    """
    if "dist_to_center" in un:
        return un["dist_to_center"], un["cells_ge"]
    import heapq
    adj, cost = un["adj"], un["cost"]
    dist = {f: cost[f] for f in un["start_front"]}
    heap = [(cost[f], f) for f in un["start_front"]]
    heapq.heapify(heap)
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist.get(u, float("inf")):
            continue
        for v in adj[u]:
            nd = d + cost[v]
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    cells_ge = [0] * len(un["all_orbits"])
    acc = set()
    for s in range(len(un["all_orbits"]) - 1, -1, -1):
        acc |= set(un["all_orbits"][s])
        cells_ge[s] = len(acc)
    un["dist_to_center"] = dist
    un["cells_ge"] = cells_ge
    return dist, cells_ge


def iter_targets_seeded_connected(un, min_id, budget, stats=None, limits=None):
    """Yield every connected CK6-closed target whose minimum orbit id is
    exactly min_id (connectivity-pruned seeded DFS).

    This is the production V45 engine candidate: it is provably complete
    (same target set as iter_targets_seeded) but explores only the
    centre-connected part of the state space, which makes zero-leaf
    buckets either provably empty at the root or cheap.

    CONNECTIVITY PRUNE (complete).  Every connected target T with
    min-id s has a connected orbit graph (a cell path between any two
    cells maps to an orbit walk).  Root a spanning tree of T's orbit
    graph at the centre and order the orbits: s first, then all others
    by non-decreasing tree depth.  Each orbit v != s added in this order
    is adjacent to its tree parent, which has smaller depth and is
    therefore already present and connected to the centre, so v is
    adjacent to the centre's connected component at add time.  The seed
    s may be added disconnected; it joins the centre component when its
    parent is added, and its tree children are then added through
    s-adjacency.  The DFS expands every centre-component-adjacent orbit
    at every state, so every target's orbit set is reached and yielded.

    REACHABILITY PRUNE (root, provably empty buckets).  If
    dist_to_center[s] > budget no target containing s can afford a path
    from s to the centre; if cells_ge[s] < volume - 1 the orbits >= s
    cannot supply enough cells; in both cases the bucket is empty and
    nothing is yielded.

    LEAF CONNECTIVITY CHECK (exact, no BFS).  Every added orbit is
    centre-component-adjacent at add time, so the centre component is
    always connected and is the only component besides possibly the seed
    s.  The cell set is connected iff s is bridged into the centre
    component (s in start_front or some added orbit adjacent to s), so
    the leaf check is `bridged`; is_face_connected is not needed.

    Masks are shifted down by s (bit i = orbit id i + s), as in
    iter_targets_seeded.
    """
    adj, cost = un["adj"], un["cost"]
    all_orbits = un["all_orbits"]
    center = un["center"]
    s = min_id
    dist, cells_ge = _conn_prune_data(un)
    if dist[s] > budget:
        return
    if cells_ge[s] < 2 * budget:  # volume - 1 non-centre cells
        return
    rem0 = budget - cost[s]
    if rem0 < 0:
        return
    bridged = s in un["start_front"]
    if bridged:
        cc_adj = frozenset(j for j in (un["start_front"] | adj[s]) - {s}
                           if j >= s)
    else:
        cc_adj = frozenset(j for j in un["start_front"] if j >= s)
    visited = {1}  # shifted seed: orbit id s -> bit 0
    stack = [(1, rem0, bridged, cc_adj)]
    while stack:
        mask, rem, bridged_, cc_adj_ = stack.pop()
        if stats is not None:
            stats["states"] = stats.get("states", 0) + 1
        if rem == 0:
            if not bridged_:
                continue
            cells = {center}
            m = mask
            while m:
                b = m & -m
                cells |= set(all_orbits[(b.bit_length() - 1) + s])
                m ^= b
            yield cells
            continue
        for j in cc_adj_:
            c = cost[j]
            if c > rem:
                continue
            nm = mask | (1 << (j - s))  # shift orbit id j down by s
            if nm in visited:
                continue
            visited.add(nm)
            n_bridged = bridged_ or (j in adj[s])
            n_cc = frozenset(x for x in (cc_adj_ | adj[j]) - {j} if x >= s)
            if n_bridged and not bridged_:
                # s just joined the centre component: its neighbours
                # become centre-component-adjacent
                n_cc = frozenset(x for x in (n_cc | adj[s]) if x >= s
                                 and x != s)
            stack.append((nm, rem - c, n_bridged, n_cc))


def current_rss_mb():
    """Current process RSS in MiB (0.0 if unreadable)."""
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1024.0
    except OSError:
        pass
    return 0.0


def iter_targets_seeded_connected_sqlite(un, min_id, budget, db_path,
                                         ckpt_every=2_000_000, run_id=None,
                                         state=None, info=None, stats=None,
                                         limits=None, stop_check=None):
    """Yield every connected CK6-closed target whose minimum orbit id is
    exactly min_id, with the visited set stored in a SQLite database at
    db_path (bounded memory; identical target set and traversal to
    iter_targets_seeded_connected -- the visited set is only a
    membership test, so traversal order and yielded targets are
    unchanged).

    Crash-safe resume: the DFS stack, counters and (optionally) the
    caller's processing state are checkpointed into the same database in
    the same transaction as the visited-set inserts, so the database is
    always internally consistent (visited set == every state ever
    pushed, stack == pushed-but-unpopped).  If db_path holds a
    checkpoint for this min_id the search resumes exactly; otherwise it
    starts fresh (a stale database -- wrong bucket, or a run_id
    mismatch -- is removed).

    run_id: optional identity token.  When given, a database whose
    stored run_id differs is treated as stale and discarded; the
    production driver passes a stable run_id (persisted in its shard
    checkpoint) so a killed shard resumes its own databases and never
    reuses another run's.

    state: optional mutable dict owned by the caller (e.g. the driver's
    funnel/sat/unsat/witness state).  At every checkpoint the current
    state is pickled into the meta table; on resume the state dict is
    restored in place (cleared and re-filled) so a killed bucket resumes
    without losing or duplicating processed targets.

    info: optional BucketRunInfo filled with run metadata (db_path,
    run_id, resumed, completed, targets, states).

    limits: optional dict (max_states / max_seconds / t0 / max_rss_mb,
    same convention as iter_targets_seeded_seeds).  Bounds are checked
    at checkpoint boundaries; on a hit the checkpoint is committed and
    SearchLimit is raised with limits['reason'] set.

    stop_check: optional zero-arg callable checked at checkpoint
    boundaries; when it returns True the checkpoint is committed and
    BucketStopped is raised (the bucket is resumable).

    On resume of an already-complete bucket (meta 'complete' == '1')
    nothing is yielded; info.completed is set, info.targets holds the
    recorded total, and the caller's state is restored from the final
    checkpoint.  The caller should record the bucket as done without
    re-enumerating.

    The database is NEVER deleted by this function: completed buckets
    keep their database (marked complete) for audit/reproducibility;
    explicit cleanup is the caller's decision.
    """
    import pickle
    import sqlite3
    adj, cost = un["adj"], un["cost"]
    all_orbits = un["all_orbits"]
    center = un["center"]
    s = min_id
    dist, cells_ge = _conn_prune_data(un)
    if dist[s] > budget:
        return
    if cells_ge[s] < 2 * budget:  # volume - 1 non-centre cells
        return
    rem0 = budget - cost[s]
    if rem0 < 0:
        return
    bridged = s in un["start_front"]
    if bridged:
        cc_adj = frozenset(j for j in (un["start_front"] | adj[s]) - {s}
                           if j >= s)
    else:
        cc_adj = frozenset(j for j in un["start_front"] if j >= s)
    nbytes = ((len(all_orbits) - 1 - s) + 8) // 8
    t0 = time.time()

    def open_db():
        con = sqlite3.connect(db_path)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=NORMAL")
        con.execute("PRAGMA cache_size=-1000000")  # 1 GiB page cache
        con.execute("CREATE TABLE IF NOT EXISTS visited "
                    "(mask BLOB PRIMARY KEY) WITHOUT ROWID")
        con.execute("CREATE TABLE IF NOT EXISTS meta "
                    "(key TEXT PRIMARY KEY, value BLOB) WITHOUT ROWID")
        return con

    def write_meta(con, stack, targets, states):
        con.execute("INSERT OR REPLACE INTO meta(key, value) VALUES "
                    "('bucket', ?)", (str(s).encode(),))
        if run_id is not None:
            con.execute("INSERT OR REPLACE INTO meta(key, value) VALUES "
                        "('run_id', ?)", (run_id.encode(),))
        con.execute("INSERT OR REPLACE INTO meta(key, value) VALUES "
                    "('stack', ?)", (pickle.dumps(stack),))
        con.execute("INSERT OR REPLACE INTO meta(key, value) VALUES "
                    "('targets', ?)", (str(targets).encode(),))
        con.execute("INSERT OR REPLACE INTO meta(key, value) VALUES "
                    "('states', ?)", (str(states).encode(),))
        if state is not None:
            con.execute("INSERT OR REPLACE INTO meta(key, value) VALUES "
                        "('state', ?)", (pickle.dumps(state),))

    def restore_state():
        if state is None:
            return
        saved = pickle.loads(con.execute(
            "SELECT value FROM meta WHERE key='state'").fetchone()[0])
        state.clear()
        state.update(saved)

    def limit_reason():
        if limits is None:
            return None
        if limits.get("max_states") is not None and \
                states >= limits["max_states"]:
            return "max_states %d" % limits["max_states"]
        if limits.get("max_seconds") is not None and \
                time.time() - limits.get("t0", t0) > limits["max_seconds"]:
            return "max_seconds %g" % limits["max_seconds"]
        if limits.get("max_rss_mb") is not None and \
                current_rss_mb() > limits["max_rss_mb"]:
            return "max_rss_mb %g" % limits["max_rss_mb"]
        return None

    con = open_db()
    row = con.execute("SELECT value FROM meta WHERE key='bucket'").fetchone()
    resume = False
    if row is not None and int(row[0]) == s:
        rid_row = con.execute(
            "SELECT value FROM meta WHERE key='run_id'").fetchone()
        rid = None if rid_row is None else rid_row[0].decode()
        if run_id is None or rid == run_id:
            stack = pickle.loads(con.execute(
                "SELECT value FROM meta WHERE key='stack'").fetchone()[0])
            targets = int(con.execute(
                "SELECT value FROM meta WHERE key='targets'").fetchone()[0])
            states = int(con.execute(
                "SELECT value FROM meta WHERE key='states'").fetchone()[0])
            complete = con.execute(
                "SELECT value FROM meta WHERE key='complete'").fetchone()
            if complete is not None and complete[0] == b"1":
                restore_state()
                if info is not None:
                    info.db_path = db_path
                    info.run_id = rid
                    info.completed = True
                    info.targets = targets
                    info.states = states
                print(f"bucket {s}: already complete ({targets:,} targets, "
                      f"{states:,} states); state restored", flush=True)
                con.close()
                return
            restore_state()
            resume = True
    if not resume:
        con.close()
        if os.path.exists(db_path):
            os.remove(db_path)
        con = open_db()
        stack = [(1, rem0, bridged, cc_adj)]
        targets = 0
        states = 0
        con.execute("INSERT OR IGNORE INTO visited(mask) VALUES (?)",
                    (b"\x00" * (nbytes - 1) + b"\x01",))
        write_meta(con, stack, targets, states)
        con.commit()
        print(f"bucket {s}: fresh start (rem {rem0}, bridged {bridged}, "
              f"cc_adj {len(cc_adj)}, nbytes {nbytes}, db {db_path})",
              flush=True)
    else:
        print(f"bucket {s}: resumed from checkpoint ({states:,} states, "
              f"{targets:,} targets, db {db_path})", flush=True)
    if info is not None:
        info.db_path = db_path
        info.run_id = run_id
        info.resumed = resume
    con.execute("BEGIN")
    while stack:
        mask, rem, bridged_, cc_adj_ = stack.pop()
        states += 1
        if stats is not None:
            stats["states"] = stats.get("states", 0) + 1
        if states % 100_000 == 0:
            db_mb = (os.path.getsize(db_path) / 1e6
                     if os.path.exists(db_path) else 0)
            print(f"  bucket {s}: {states:,} states, {targets:,} targets, "
                  f"rss {current_rss_mb():.0f} MiB, stack {len(stack)}, "
                  f"db {db_mb:.0f} MB, {time.time()-t0:.0f}s", flush=True)
        if rem == 0:
            if not bridged_:
                continue
            cells = {center}
            m = mask
            while m:
                b = m & -m
                cells |= set(all_orbits[(b.bit_length() - 1) + s])
                m ^= b
            targets += 1
            yield cells
            continue
        for j in cc_adj_:
            c = cost[j]
            if c > rem:
                continue
            nm = mask | (1 << (j - s))
            nb = nm.to_bytes(nbytes, "big")
            if con.execute("SELECT 1 FROM visited WHERE mask=?",
                           (nb,)).fetchone() is not None:
                continue
            con.execute("INSERT OR IGNORE INTO visited(mask) VALUES (?)",
                        (nb,))
            n_bridged = bridged_ or (j in adj[s])
            n_cc = frozenset(x for x in (cc_adj_ | adj[j]) - {j} if x >= s)
            if n_bridged and not bridged_:
                # s just joined the centre component: its neighbours
                # become centre-component-adjacent
                n_cc = frozenset(x for x in (n_cc | adj[s]) if x >= s
                                 and x != s)
            stack.append((nm, rem - c, n_bridged, n_cc))
        # checkpoint after every state is fully processed (leaf counted or
        # children pushed), so the saved stack is always consistent with
        # the committed visited set
        if states % ckpt_every == 0:
            write_meta(con, stack, targets, states)
            con.commit()
            con.execute("BEGIN")
            print(f"  bucket {s}: checkpoint at {states:,} states "
                  f"(stack {len(stack)}, {time.time()-t0:.0f}s)",
                  flush=True)
            reason = limit_reason()
            if reason is not None:
                limits["reason"] = reason
                print(f"bucket {s}: {reason}; exiting (resumable)",
                      flush=True)
                con.close()
                raise SearchLimit(reason)
            if stop_check is not None and stop_check():
                print(f"bucket {s}: STOP requested; exiting (resumable)",
                      flush=True)
                con.close()
                raise BucketStopped()
    write_meta(con, stack, targets, states)
    con.execute("INSERT OR REPLACE INTO meta(key, value) VALUES "
                "('complete', ?)", (b"1",))
    con.commit()
    con.close()
    if info is not None:
        info.completed = True
        info.targets = targets
        info.states = states
    db_mb = os.path.getsize(db_path) / 1e6
    print(f"bucket {s}: COMPLETE {states:,} states, {targets:,} targets, "
          f"{time.time()-t0:.0f}s, db {db_mb:.0f} MB, "
          f"rss {current_rss_mb():.0f} MiB", flush=True)


class BucketRunInfo:
    """Per-bucket SQLite run metadata, filled by
    iter_targets_seeded_connected_sqlite for the caller (the production
    driver) to log and to detect completed-bucket re-entry."""

    def __init__(self):
        self.db_path = None      # SQLite database used for this bucket
        self.run_id = None       # run identity token (None standalone)
        self.resumed = False     # True if the bucket resumed from a ckpt
        self.completed = False   # True if the bucket was already complete
        self.targets = 0         # total targets (from the DB if completed)
        self.states = 0          # total states (from the DB if completed)


class BucketStopped(Exception):
    """Raised by iter_targets_seeded_connected_sqlite when stop_check()
    returns True at a checkpoint boundary.  The bucket's progress is
    checkpointed and resumable; the caller must NOT record the bucket as
    done (recording it would silently truncate the bucket on resume)."""


class SearchLimit(Exception):
    """Raised by the seeded generators when a caller-supplied bound is
    hit (max_states / max_seconds / max_rss_mb); the reason is recorded
    in the limits dict before raising."""


def iter_targets_seeded_seeds(un, seeds, budget, stats=None, limits=None):
    """Exact partition of a min-id search by a mandatory seed set.

    seeds: sorted tuple of mandatory orbit ids (s, q1, ..., qk), k >= 2.
    Yields every connected CK6-closed target whose orbit set is
    {seeds} | R with R a subset of {j > seeds[-1]}; the target's minimum
    orbit id is seeds[0] and its second-minimum is seeds[1].  Masks are
    shifted down by seeds[-1] (bit i represents orbit id i + seeds[-1]),
    the same memory optimization as iter_targets_seeded.

    stats (optional dict) counts DFS pops and samples peak RSS / mask
    sizes; limits (optional dict: max_states / max_seconds / max_rss_mb /
    t0) raises SearchLimit when a bound is hit, recording the reason in
    limits['reason'].
    """
    adj, cost = un["adj"], un["cost"]
    all_orbits = un["all_orbits"]
    center = un["center"]
    base = seeds[-1]
    rem0 = budget - sum(cost[x] for x in seeds)
    if rem0 < 0:
        return
    seed_set = set(seeds)
    adj_union = set().union(*(adj[x] for x in seeds))
    frontier = frozenset(j for j in (un["start_front"] | adj_union)
                         - seed_set if j > base)
    visited = {0}  # shifted by base: bit i = orbit id i + base
    stack = [(0, frontier, rem0)]
    while stack:
        mask, frontier_, rem = stack.pop()
        if stats is not None:
            stats["states"] += 1
            if stats["states"] % 50000 == 0:
                rss = current_rss_mb()
                if rss > stats.get("peak_rss", 0):
                    stats["peak_rss"] = rss
                mb = stats.setdefault("mask_bytes_sum", 0)
                stats["mask_bytes_sum"] = mb + sys.getsizeof(mask)
                stats["mask_bytes_n"] = stats.get("mask_bytes_n", 0) + 1
                if limits is not None:
                    if stats["states"] >= limits["max_states"]:
                        limits["reason"] = "max_states %d" % limits["max_states"]
                        raise SearchLimit
                    if time.time() - limits["t0"] > limits["max_seconds"]:
                        limits["reason"] = "max_seconds %g" % limits["max_seconds"]
                        raise SearchLimit
                    if rss > limits["max_rss_mb"]:
                        limits["reason"] = ("max_rss_mb %g (rss %.0f MiB)"
                                            % (limits["max_rss_mb"], rss))
                        raise SearchLimit
        if rem == 0:
            cells = {center}
            for x in seeds:
                cells |= set(all_orbits[x])
            m = mask
            while m:
                b = m & -m
                cells |= set(all_orbits[(b.bit_length() - 1) + base])
                m ^= b
            if not is_face_connected(cells):
                continue
            yield cells
            continue
        for j in frontier_:
            c = cost[j]
            if c > rem:
                continue
            nm = mask | (1 << (j - base))
            if nm in visited:
                continue
            visited.add(nm)
            nf = frozenset(x for x in (frontier_ | adj[j]) - {j} if x > base)
            stack.append((nm, nf, rem - c))
    if stats is not None:
        stats["visited"] = len(visited)
        stats["stack"] = len(stack)


def iter_targets_seeded_pair(un, s, q, budget, stats=None, limits=None):
    """Exact partition of the min-id-s search by second-minimum orbit q.

    Yields exactly the connected CK6-closed targets whose orbit set has
    minimum id s and second-minimum id q.  The (s, q) searches are
    pairwise disjoint and their union (plus the single-orbit degenerate
    case, iter_targets_seeded_single) equals the full min-id-s search.
    """
    return iter_targets_seeded_seeds(un, (s, q), budget, stats=stats,
                                     limits=limits)


def iter_targets_seeded_single(un, s, budget):
    """Degenerate case: {center} | orbit[s] alone is a complete connected
    target (no second orbit).  Only possible when budget - cost[s] == 0."""
    if budget - un["cost"][s] != 0:
        return
    cells = {un["center"]} | set(un["all_orbits"][s])
    if is_face_connected(cells):
        yield cells


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


def count_minids_sqlite(un, volume, db_path, ckpt_every=2_000_000):
    """Monolithic DFS with a SQLite-backed visited set (bounded memory).

    Identical traversal to count_minids (sorted-frontier expansion, same
    leaf attribution), so the histogram is exactly the same; only the
    visited-set storage differs: masks are stored as fixed-size BLOBs in
    a WITHOUT ROWID table instead of an in-memory Python set.  Memory
    stays bounded (~150 MiB + DFS stack) for V=45's ~41M states, which
    the in-memory set cannot hold (23.5 GB, Stage 4C).

    Crash-safe resume: the DFS stack, histogram and counters are
    checkpointed into the same database (meta table) in the same
    transaction as the visited-set inserts, so the database is always
    internally consistent (visited set == every state ever pushed, stack
    == pushed-but-unpopped).  If db_path holds a checkpoint for this
    volume the search resumes exactly; otherwise it starts fresh (a
    stale database without a matching checkpoint is removed).  On
    completion the caller should delete db_path (it is only needed for
    resume).
    """
    import pickle
    import sqlite3
    adj, cost = un["adj"], un["cost"]
    nbytes = (len(un["all_orbits"]) + 7) // 8
    t0 = time.time()

    def open_db():
        con = sqlite3.connect(db_path)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=NORMAL")
        con.execute("PRAGMA cache_size=-1000000")  # 1 GiB page cache
        con.execute("CREATE TABLE IF NOT EXISTS visited "
                    "(mask BLOB PRIMARY KEY) WITHOUT ROWID")
        con.execute("CREATE TABLE IF NOT EXISTS meta "
                    "(key TEXT PRIMARY KEY, value BLOB) WITHOUT ROWID")
        return con

    def write_meta(con, stack, hist, leaves, states):
        con.execute("INSERT OR REPLACE INTO meta(key, value) VALUES "
                    "('volume', ?)", (str(volume).encode(),))
        con.execute("INSERT OR REPLACE INTO meta(key, value) VALUES "
                    "('stack', ?)", (pickle.dumps(stack),))
        con.execute("INSERT OR REPLACE INTO meta(key, value) VALUES "
                    "('hist', ?)", (pickle.dumps(hist),))
        con.execute("INSERT OR REPLACE INTO meta(key, value) VALUES "
                    "('leaves', ?)", (str(leaves).encode(),))
        con.execute("INSERT OR REPLACE INTO meta(key, value) VALUES "
                    "('states', ?)", (str(states).encode(),))

    con = open_db()
    row = con.execute("SELECT value FROM meta WHERE key='volume'").fetchone()
    if row is not None and int(row[0]) == volume:
        stack = pickle.loads(con.execute(
            "SELECT value FROM meta WHERE key='stack'").fetchone()[0])
        hist = pickle.loads(con.execute(
            "SELECT value FROM meta WHERE key='hist'").fetchone()[0])
        leaves = int(con.execute(
            "SELECT value FROM meta WHERE key='leaves'").fetchone()[0])
        states = int(con.execute(
            "SELECT value FROM meta WHERE key='states'").fetchone()[0])
        print(f"count: resumed from checkpoint ({states:,} states, "
              f"{leaves:,} leaves)", flush=True)
    else:
        con.close()
        if os.path.exists(db_path):
            os.remove(db_path)
        con = open_db()
        stack = [(0, un["start_front"], (volume - 1) // 2)]
        hist = Counter()
        leaves = 0
        states = 0
        con.execute("INSERT OR IGNORE INTO visited(mask) VALUES (?)",
                    (b"\x00" * nbytes,))
        write_meta(con, stack, hist, leaves, states)
        con.commit()
    con.execute("BEGIN")
    while stack:
        mask, frontier, rem = stack.pop()
        states += 1
        if states % 100000 == 0:
            print(f"  count: {states:,} states, {leaves:,} leaves, "
                  f"rss {current_rss_mb():.0f} MiB, "
                  f"elapsed {time.time()-t0:.0f}s", flush=True)
        if rem == 0:
            hist[(mask & -mask).bit_length() - 1] += 1
            leaves += 1
        else:
            for j in sorted(frontier):
                c = cost[j]
                if c > rem:
                    continue
                nm = mask | (1 << j)
                nb = nm.to_bytes(nbytes, "big")
                if con.execute("SELECT 1 FROM visited WHERE mask=?",
                               (nb,)).fetchone() is not None:
                    continue
                con.execute("INSERT OR IGNORE INTO visited(mask) VALUES (?)",
                            (nb,))
                stack.append((nm, (frontier | adj[j]) - {j}, rem - c))
        # checkpoint after every state is fully processed (leaf counted or
        # children pushed), so the saved stack is always consistent with
        # the committed visited set
        if states % ckpt_every == 0:
            write_meta(con, stack, hist, leaves, states)
            con.commit()
            con.execute("BEGIN")
            print(f"  count: checkpoint at {states:,} states "
                  f"(stack {len(stack):,}, {time.time()-t0:.0f}s)",
                  flush=True)
    con.commit()
    con.close()
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
    limits = {"max_states": 40_000_000, "max_seconds": 3600, "t0": time.time(), "max_rss_mb": 10838}
    for s in min_ids:
        for t in iter_targets_seeded(un, s, budget, stats=None, limits=limits):
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
    monolithic DFS's in-memory visited set hits the RAM wall (Stage 4C:
    41M states / 23.5 GB capped at V=45), so the same DFS runs with a
    SQLite-backed visited set (count_minids_sqlite): identical traversal
    and histogram, bounded memory, crash-safe checkpoint/resume.
    """
    os.makedirs(args.workdir, exist_ok=True)
    counts_path = os.path.join(args.workdir, "minid_counts.json")
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
    # monolithic SQLite-backed count for large volumes
    un = build_universe(args.volume)
    db_path = os.path.join(args.workdir, f"visited_v{args.volume}.db")
    res, leaves = count_minids_sqlite(un, args.volume, db_path)
    res["volume"] = args.volume
    res["method"] = "monolithic-sqlite"
    with open(counts_path, "w") as f:
        json.dump(res, f, indent=1)
    # resume artifacts are only needed for an interrupted run
    for p in (db_path, db_path + "-wal", db_path + "-shm"):
        if os.path.exists(p):
            os.remove(p)
    print(f"count: {leaves:,} targets ({res['elapsed_s']}s); "
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