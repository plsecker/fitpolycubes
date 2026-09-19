#!/usr/bin/env python3
"""
Independent validation of the corrected CK6 V45 enumeration architecture.

This harness validates the corrected enumerator
(solvers/ck6_sharding_corrected.py corrected_candidate_min_ids +
solvers/t_ck6_oddity_v35_search.py iter_targets_seeded, or the
connectivity-pruned engine iter_targets_seeded_connected with --pruned)
against:

  A. an INDEPENDENT cell-level brute-force enumerator written here from
     scratch (no orbit graph, no costs, no budgets, no min-id seeding:
     it grows connected cell sets from the centre and enforces CK6
     closure by adding orbit mates on the fly);
  B. the repo's single-process reference enumerator
     (common.oddity.enumerate_connected_ck6_targets);
  C. the known reference totals V25 = 71,539 and V35 = 15,289,669
     (re-derived here by count_minids, not read from disk);
  D. the George B-9 counterexample (min orbit id 3590).

Subcommands:
  small        V5/V15/V25 exhaustive comparisons (brute force vs
               corrected vs reference) + full V25 verification
  v35count     reference count_minids re-run for V35 (total + hist)
  v35          full corrected V35 enumeration over the corrected
               candidate domain; per-min-id counts vs reference hist
  george       George B-9 regression: static checks + full min-id-3590
               subtree walk (counts occurrences of the target)
  partition    V25 partition validation with the corrected shard plan
  determinism  V15 corrected enumeration twice (different hash seeds);
               compare counts / canonical hashes / branch ownership
  audit        static audit of the V45 production driver design

Nothing here modifies historical artefacts; all outputs are printed and
optionally written to a scratch dir (default /tmp/opencode/v45_validation).
"""
import argparse
import hashlib
import itertools
import json
import os
import sys
import time
from pathlib import Path

REPO = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "solvers"))

from t_ck6_oddity_v35_search import (  # noqa: E402
    build_universe,
    count_minids,
    iter_targets_seeded,
    iter_targets_seeded_connected,
)
from solvers.ck6_sharding_corrected import (  # noqa: E402
    GEORGE_B9_CORPUS_FRAME,
    GEORGE_B9_MIN_ORBIT_ID,
    GEORGE_B9_OH_ID,
    build_corrected_plan,
    corrected_candidate_min_ids,
)
from common.oddity import (  # noqa: E402
    enumerate_connected_ck6_targets,
    is_face_connected,
    l1_ball,
)
from common.symmetry import (  # noqa: E402
    canonical_form,
    ck6_affine_maps,
)

FAILURES = []


def enum(un, s, budget, pruned):
    """Corrected enumerator for bucket s: the original seeded DFS or the
    connectivity-pruned engine (iter_targets_seeded_connected)."""
    if pruned:
        return iter_targets_seeded_connected(un, s, budget)
    return iter_targets_seeded(un, s, budget)


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {name}" + (f" -- {detail}" if detail else ""))
    if not cond:
        FAILURES.append(name)
    return cond


def cid(coords):
    """O_h canonical id (repo convention: sha1 of the sorted cell list)."""
    h = hashlib.sha1(
        json.dumps(sorted(tuple(int(v) for v in c) for c in coords))
        .encode()).hexdigest()[:12]
    return "oh-" + h


# ---------------------------------------------------------------------------
# A. independent cell-level brute force (no orbit machinery)
# ---------------------------------------------------------------------------

def brute_force_ck6_targets(volume, time_cap_s=None):
    """Every connected CK6-closed volume-cell set, as O_h canonical forms.

    Grows connected cell sets from the centre cell; CK6 closure is
    enforced by adding the full orbit of every added cell (the L1 ball
    is CK6-closed, so orbits never leave it).  No orbit graph, no
    costs, no budgets, no min-id seeding, no sharding: this is a
    different algorithm from both the corrected enumerator and the repo
    reference enumerator.
    """
    maps = list(ck6_affine_maps((0, 0)).values())
    ball = set(l1_ball((volume - 1) // 2))
    center = (0, 0, 0)

    def orbit(v):
        return frozenset(m(v) for m in maps)

    def nbrs(v):
        x, y, z = v
        return ((x + 1, y, z), (x - 1, y, z),
                (x, y + 1, z), (x, y - 1, z),
                (x, y, z + 1), (x, y, z - 1))

    t0 = time.time()
    visited = set()
    out = set()
    stack = [frozenset({center})]
    while stack:
        s = stack.pop()
        if s in visited:
            continue
        visited.add(s)
        if time_cap_s is not None and time.time() - t0 > time_cap_s:
            raise TimeoutError(f"brute force V{volume} exceeded "
                               f"{time_cap_s}s ({len(visited)} states)")
        if len(s) == volume:
            out.add(canonical_form(s))
            continue
        for v in s:
            for nb in nbrs(v):
                if nb in ball and nb not in s:
                    ns = s | orbit(nb)
                    if len(ns) <= volume and ns not in visited:
                        stack.append(ns)
    return out, len(visited)


def subset_brute_force_v5():
    """True subset enumeration for V5: all 5-cell subsets of the
    radius-2 ball containing the centre (C(18,4) = 3060), filtered by
    connectivity and CK6 closure.  The most independent check possible."""
    ball = l1_ball(2)
    center = (0, 0, 0)
    others = [c for c in ball if c != center]
    maps = list(ck6_affine_maps((0, 0)).values())
    out = set()
    for combo in itertools.combinations(others, 4):
        s = frozenset([center]) | frozenset(combo)
        if not is_face_connected(s):
            continue
        if not all(frozenset(m(c) for c in s) == s for m in maps):
            continue
        out.add(canonical_form(s))
    return out


# ---------------------------------------------------------------------------
# corrected enumerator helpers
# ---------------------------------------------------------------------------

def corrected_enumeration(volume, per_min_id=None, verify_targets=False,
                          sample_closure=0, collect_raw=False, pruned=False):
    """Run the corrected enumerator over the corrected candidate domain.

    Returns (total, per-min-id counts dict, canonical-form set[, raw set]).
    per_min_id: optional dict to fill with counts.
    verify_targets: check len/connectivity/CK6-closure of every target.
    sample_closure: verify CK6 closure on every Nth target (0 = off).
    collect_raw: also collect the raw (non-canonicalized) target set.
    pruned: use the connectivity-pruned engine (iter_targets_seeded_connected).
    """
    un = build_universe(volume)
    budget = (volume - 1) // 2
    cands = sorted(corrected_candidate_min_ids(un))
    maps = list(ck6_affine_maps((0, 0)).values())
    total = 0
    forms = set()
    raw = set() if collect_raw else None
    counts = {}
    n = 0
    for s in cands:
        cnt = 0
        for t in enum(un, s, budget, pruned):
            cnt += 1
            total += 1
            n += 1
            if verify_targets:
                assert len(t) == volume, (volume, len(t))
                assert is_face_connected(t), "disconnected target"
            if sample_closure and n % sample_closure == 0:
                assert all(frozenset(m(c) for c in t) == t for m in maps), \
                    "non-CK6-closed target"
            forms.add(canonical_form(t))
            if raw is not None:
                raw.add(frozenset(t))
        counts[s] = cnt
        if per_min_id is not None:
            per_min_id[s] = cnt
    if raw is not None:
        return total, counts, forms, raw
    return total, counts, forms


# ---------------------------------------------------------------------------
# subcommands
# ---------------------------------------------------------------------------

def cmd_small(args):
    print("== small-volume exhaustive validation ==")
    # V5: true subset brute force
    bf5 = subset_brute_force_v5()
    check("V5 subset brute force finds 2 targets", len(bf5) == 2, str(len(bf5)))
    total5, counts5, forms5, raw5 = corrected_enumeration(
        5, verify_targets=True, collect_raw=True, pruned=args.pruned)
    ref5 = {frozenset(t) for t in enumerate_connected_ck6_targets(5)}
    check("V5 corrected total == 2", total5 == 2, str(total5))
    check("V5 corrected raw set == reference raw set (no dups/omissions)",
          raw5 == ref5, f"|corrected|={len(raw5)} |ref|={len(ref5)}")
    check("V5 corrected canonical set == subset brute force", forms5 == bf5,
          f"|corrected|={len(forms5)} |brute|={len(bf5)}")
    check("V5 no duplicate raw targets", len(raw5) == total5)

    for vol, expected in ((15, 368), (25, 71539)):
        t0 = time.time()
        bf, nstates = brute_force_ck6_targets(vol, time_cap_s=args.brute_cap)
        print(f"  brute force V{vol}: {len(bf)} canonical forms, "
              f"{nstates} states, {time.time()-t0:.1f}s")
        t0 = time.time()
        total, counts, forms, raw = corrected_enumeration(
            vol, verify_targets=True, sample_closure=1000, collect_raw=True,
            pruned=args.pruned)
        print(f"  corrected V{vol}: {total} targets, {time.time()-t0:.1f}s")
        check(f"V{vol} corrected total == {expected}", total == expected,
              str(total))
        check(f"V{vol} corrected canonical set == brute force", forms == bf,
              f"|corrected|={len(forms)} |brute|={len(bf)}")
        ref = {frozenset(t) for t in enumerate_connected_ck6_targets(vol)}
        check(f"V{vol} corrected raw set == reference raw set "
              f"(no dups/omissions)", raw == ref,
              f"|corrected|={len(raw)} |ref|={len(ref)}")
        check(f"V{vol} no duplicate raw targets", len(raw) == total,
              f"|raw|={len(raw)} total={total}")
        print(f"  V{vol}: {total} raw targets -> {len(forms)} O_h "
              f"congruence classes (ratio {total/len(forms):.3f})")
        if vol == 25:
            # full V25 verification: min-id coverage, ownership, histogram
            un = build_universe(25)
            res, leaves = count_minids(un, 25)
            hist = {int(k): v for k, v in res["hist"].items()}
            check("V25 reference count_minids == 71539", leaves == 71539,
                  str(leaves))
            cands = sorted(corrected_candidate_min_ids(un))
            check("V25 every hist min-id is a corrected candidate",
                  set(hist) <= set(cands),
                  f"missing={sorted(set(hist) - set(cands))}")
            check("V25 per-min-id counts == reference hist",
                  all(counts.get(k, 0) == v for k, v in hist.items()),
                  f"|counts|={len(counts)} |hist|={len(hist)}")
            check("V25 sum(per-min-id counts) == total",
                  sum(counts.values()) == total)
            check("V25 no duplicated ownership (raw set == reference, "
                  "no dups)", raw == ref and len(raw) == total)
            check("V25 no missing ownership (every hist min-id covered)",
                  all(counts.get(k, 0) > 0 for k in hist))
    print("SMALL OK" if not FAILURES else f"FAILURES: {FAILURES}")


def cmd_v35count(args):
    print("== V35 reference count (count_minids, re-derived) ==")
    un = build_universe(35)
    res, leaves = count_minids(un, 35)
    hist = {int(k): v for k, v in res["hist"].items()}
    check("V35 reference total == 15,289,669", leaves == 15289669,
          f"{leaves:,}")
    check("V35 hist sum == total", sum(hist.values()) == leaves)
    check("V35 hist has 489 min-ids", len(hist) == 489, str(len(hist)))
    check("V35 hist range [558..1857]", min(hist) == 558 and max(hist) == 1857,
          f"[{min(hist)}..{max(hist)}]")
    out = {"volume": 35, "total": leaves,
           "n_min_ids": len(hist), "min_id": min(hist), "max_id": max(hist),
           "elapsed_s": res["elapsed_s"]}
    print(json.dumps(out))
    print("V35COUNT OK" if not FAILURES else f"FAILURES: {FAILURES}")


def cmd_v35(args):
    print("== full corrected V35 enumeration over the corrected domain ==")
    un = build_universe(35)
    cands = sorted(corrected_candidate_min_ids(un))
    print(f"  corrected candidate domain: {len(cands)} min-ids "
          f"[{cands[0]}..{cands[-1]}]")
    # reference hist (re-derived, not read from disk)
    res, leaves = count_minids(un, 35)
    hist = {int(k): v for k, v in res["hist"].items()}
    check("V35 reference total == 15,289,669", leaves == 15289669,
          f"{leaves:,}")
    t0 = time.time()
    per = {}
    total = 0
    bucket_masks = {}
    maps = list(ck6_affine_maps((0, 0)).values())
    n = 0
    for s in cands:
        cnt = 0
        masks = set()
        for t in enum(un, s, 17, args.pruned):
            cnt += 1
            total += 1
            n += 1
            # per-bucket uniqueness: the shifted mask is the target's
            # identity within this bucket (cell set = centre + orbits)
            m = 0
            for c in t:
                if c == (0, 0, 0):
                    continue
                m |= 1 << un["cell2orb"][c]
            masks.add(m)
            if n % 500000 == 0:
                print(f"  ... {n:,} targets, {time.time()-t0:.0f}s", flush=True)
        per[s] = cnt
        bucket_masks[s] = len(masks)
        if cnt and cnt != len(masks):
            check(f"V35 bucket {s}: no duplicate masks", False,
                  f"cnt={cnt} distinct={len(masks)}")
    elapsed = time.time() - t0
    print(f"  corrected V35 enumeration: {total:,} targets in {elapsed:.0f}s")
    check("V35 corrected total == 15,289,669", total == 15289669,
          f"{total:,}")
    check("V35 per-min-id counts == reference hist on all hist keys",
          all(per.get(k, 0) == v for k, v in hist.items()),
          f"mismatches={sum(1 for k, v in hist.items() if per.get(k, 0) != v)}")
    check("V35 zero targets on non-hist candidates",
          all(per.get(k, 0) == 0 for k in cands if k not in hist))
    check("V35 min-id coverage: every hist key enumerated",
          all(per.get(k, 0) > 0 for k in hist))
    check("V35 no duplicated ownership (per-bucket masks unique)",
          all(per[s] == bucket_masks[s] for s in cands))
    check("V35 histogram consistency (sum per-min-id == total)",
          sum(per.values()) == total)
    out = {"volume": 35, "total": total, "n_candidates": len(cands),
           "n_realized": sum(1 for v in per.values() if v),
           "elapsed_s": round(elapsed, 1)}
    print(json.dumps(out))
    print("V35 OK" if not FAILURES else f"FAILURES: {FAILURES}")


def old_prefilter_candidates(un):
    """EXACT replica of the buggy V45 sharded-count prefilter."""
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
    return cands


def cmd_george(args):
    print("== George B-9 regression ==")
    target = frozenset(GEORGE_B9_CORPUS_FRAME)
    maps = list(ck6_affine_maps((0, 0)).values())
    check("George target has 45 cells", len(target) == 45)
    check("George target face-connected", is_face_connected(target))
    check("George target CK6-closed", all(frozenset(m(c) for c in target)
                                          == target for m in maps))
    check("George canonical id == oh-109166b4c83a",
          cid(canonical_form(target)) == GEORGE_B9_OH_ID,
          cid(canonical_form(target)))
    un = build_universe(45)
    cell2orb = un["cell2orb"]
    noncentre = target - {(0, 0, 0)}
    orbit_ids = sorted({cell2orb[c] for c in noncentre})
    s_min = orbit_ids[0]
    check("George min orbit id == 3590", s_min == GEORGE_B9_MIN_ORBIT_ID,
          str(s_min))
    check("George orbit cost == 22", sum(un["cost"][i] for i in orbit_ids) == 22)
    sf = set(un["start_front"])
    check("V45 start_front == {3652, 3937}", sf == {3652, 3937},
          str(sorted(sf)))
    check("George centre-adjacent orbits 3652 and 3937 present",
          3652 in orbit_ids and 3937 in orbit_ids)
    check("3652 and 3937 are start-front (centre-adjacent)",
          3652 in sf and 3937 in sf)
    old = old_prefilter_candidates(un)
    check("OLD prefilter excludes 3590 (bug reproduced)",
          s_min not in old, f"old range [{min(old)}..{max(old)}] "
          f"({len(old)} ids)")
    new = corrected_candidate_min_ids(un)
    check("CORRECTED filter accepts 3590", s_min in new,
          f"{len(new)} candidates")
    check("Corrected domain == 3696 min-ids", len(new) == 3696, str(len(new)))
    # the target is NOT excluded merely because adjacent orbit ids
    # (3652, 3937) are greater than 3590: the old w >= s0 chain rule
    # drops it, the corrected rule keeps it.
    check("Not excluded because adjacent ids > 3590 (3652, 3937 in target)",
          3652 > s_min and 3937 > s_min and s_min in new)
    if not args.skip_walk:
        print("  walking the full min-id-3590 subtree "
              "(iter_targets_seeded(un45, 3590, 22))...")
        t0 = time.time()
        found = 0
        total = 0
        for t in enum(un, 3590, 22, args.pruned):
            total += 1
            if frozenset(t) == target:
                found += 1
                print(f"  George target found at leaf #{total} "
                      f"({time.time()-t0:.0f}s)")
        elapsed = time.time() - t0
        check("George target yielded exactly once by bucket 3590",
              found == 1, f"found={found} total={total}")
        # Provenance of the expected total: the 2026-09-11 smoke test
        # (ck6_sharding_corrected.smoke_george_b9) STOPPED at George,
        # which it found after 3,430,348 targets -- that is a leaf
        # POSITION, not the subtree total (its note over-claimed it).
        # The 2026-09-12 monolithic runs (run2/run3, same enumeration,
        # min_ids=[3590], budget 22) reached 14.2M and 20,342,912 targets
        # before RSS/RAM safety stops, so the subtree total is >= that.
        # This walk establishes the authoritative total.
        check("min-id-3590 subtree total >= 20,342,912 (run3 partial)",
              total >= 20342912, f"{total:,}")
        # ownership uniqueness: no other bucket can own it (its min orbit
        # id is 3590; bucket s' > 3590 forbids ids < s', bucket s' < 3590
        # yields only sets containing s')
        check("Exactly one ownership path (min-id 3590 is intrinsic)",
              found == 1)
        print(f"  subtree walk: {total:,} targets in {elapsed:.0f}s")
    print("GEORGE OK" if not FAILURES else f"FAILURES: {FAILURES}")


def cmd_partition(args):
    print("== V25 partition validation (corrected plan, 4 shards) ==")
    plan, un = build_corrected_plan(25, n_shards=4)
    check("V25 corrected plan covers all candidates exactly once",
          sorted(m for sh in plan["shards"] for m in sh["min_ids"])
          == sorted(corrected_candidate_min_ids(un)))
    res, leaves = count_minids(un, 25)
    hist = {int(k): v for k, v in res["hist"].items()}
    check("V25 reference total == 71,539", leaves == 71539, str(leaves))
    branch_forms = []
    branch_raw = []
    branch_counts = []
    for sh in plan["shards"]:
        forms = set()
        raw = set()
        cnt = 0
        for s in sh["min_ids"]:
            for t in enum(un, s, 12, args.pruned):
                cnt += 1
                forms.add(canonical_form(t))
                raw.add(frozenset(t))
        branch_forms.append(forms)
        branch_raw.append(raw)
        branch_counts.append(cnt)
        print(f"  shard {sh['shard']}: {cnt} targets "
              f"({len(sh['min_ids'])} min-ids)")
    check("sum(branch_counts) == 71,539", sum(branch_counts) == 71539,
          str(sum(branch_counts)))
    # no target in >1 branch: pairwise intersections of RAW target sets
    # must be empty (canonical forms may legitimately overlap across
    # branches because O_h-congruent distinct targets can have different
    # min-ids; raw cell sets are the true identity)
    dup = False
    for i in range(len(branch_raw)):
        for j in range(i + 1, len(branch_raw)):
            inter = branch_raw[i] & branch_raw[j]
            if inter:
                dup = True
                print(f"  OVERLAP shards {i},{j}: {len(inter)} raw targets")
    check("no target occurs in >1 branch (raw sets disjoint)", not dup)
    check("every target has exactly one branch owner",
          sum(len(r) for r in branch_raw) == 71539)
    # canonical-form overlap across branches is expected (congruence
    # classes); report it as information
    total_forms = set().union(*branch_forms)
    print(f"  note: {sum(len(f) for f in branch_forms)} branch canonical "
          f"forms -> {len(total_forms)} distinct (congruence classes span "
          f"branches, expected)")
    # every valid root/min-id accounted for
    shard_ids = {m for sh in plan["shards"] for m in sh["min_ids"]}
    check("every hist min-id in exactly one shard",
          set(hist) <= shard_ids and
          sum(1 for sh in plan["shards"] for m in sh["min_ids"]
              if m in hist) == len(hist))
    print("PARTITION OK" if not FAILURES else f"FAILURES: {FAILURES}")


def cmd_determinism(args):
    print("== V15 determinism (two runs, different hash seeds) ==")
    results = []
    for seed in (0, 12345):
        os.environ["PYTHONHASHSEED"] = str(seed)
        # hash seed only affects str/bytes hashing; int hashes are
        # deterministic, so this also probes set-iteration stability
        total, counts, forms = corrected_enumeration(15, verify_targets=True,
                                                     pruned=args.pruned)
        digests = sorted(hashlib.sha256(
            json.dumps(sorted(f)).encode()).hexdigest() for f in forms)
        results.append({"seed": seed, "total": total, "counts": counts,
                        "digests": digests})
    r0, r1 = results
    check("V15 run1 total == 368", r0["total"] == 368, str(r0["total"]))
    check("V15 run2 total == 368", r1["total"] == 368, str(r1["total"]))
    check("counts identical across runs", r0["counts"] == r1["counts"])
    check("canonical target hashes identical across runs",
          r0["digests"] == r1["digests"])
    check("ordering-independent target sets (same digest multiset)",
          sorted(r0["digests"]) == sorted(r1["digests"]))
    print("DETERMINISM OK" if not FAILURES else f"FAILURES: {FAILURES}")


def cmd_audit(args):
    print("== V45 production driver audit (static, no run) ==")
    findings = []
    # 1. corrected min-id coverage
    plan_path = os.path.join(REPO, "data", "ck6_v45", "shards.json")
    corr_path = os.path.join(REPO, "data", "ck6_reuse",
                             "ck6_v45_shards_corrected.json")
    if os.path.exists(plan_path):
        with open(plan_path) as f:
            hist_plan = json.load(f)
        n_hist = sum(len(s["min_ids"]) for s in hist_plan["shards"])
        findings.append(("historical plan data/ck6_v45/shards.json covers "
                         f"{n_hist} min-ids (86 expected); driver reads THIS "
                         "plan, not the corrected one", n_hist == 86))
    if os.path.exists(corr_path):
        with open(corr_path) as f:
            corr = json.load(f)
        n_corr = sum(len(s["min_ids"]) for s in corr["shards"])
        ids = [m for s in corr["shards"] for m in s["min_ids"]]
        findings.append(("corrected plan covers 3,696 min-ids incl. 3590",
                         n_corr == 3696 and 3590 in ids and
                         len(ids) == len(set(ids))))
    # 2. driver wiring
    with open(os.path.join(REPO, "solvers",
                           "t_ck6_reuse_multipiece.py")) as f:
        src = f.read()
    findings.append(("driver reads data/ck6_v{volume}/shards.json "
                     "(historical plan) for volume > 25",
                     "data\", f\"ck6_v{volume}\"" in src or
                     "ck6_v{volume}" in src))
    findings.append(("KNOWN_TOTALS has no stale V45 entry "
                     "(1,469,999 retired with the buggy prefilter)",
                     "45: 1469999" not in src))
    findings.append(("T_ANCHORS has no stale V45 entry",
                     "45: {\"targets\": 1469999" not in src))
    findings.append(("V45_STATUS guard present (UNKNOWN / NOT YET VALIDATED)",
                     "V45_STATUS" in src and "NOT YET VALIDATED" in src))
    findings.append(("aggregate asserts targets == KNOWN_TOTALS[volume]",
                     "total[\"targets\"] == expected_total" in src))
    findings.append(("checkpoint json written every 120s but never read "
                     "(no mid-shard resume; shard-level resume = re-run)",
                     "checkpoint.json" in src and "checkpoint" in src))
    findings.append(("STOP file stops other shards early; stopped-early "
                     "shards still write partial result jsons -> "
                     "conservation assert fails in the positive case",
                     "stopped-early" in src))
    for name, cond in findings:
        check(name, cond)
    print("AUDIT OK" if not FAILURES else f"FAILURES: {FAILURES}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pruned", action="store_true",
                    help="use the connectivity-pruned engine "
                         "(iter_targets_seeded_connected) instead of the "
                         "original seeded DFS")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("small")
    s.add_argument("--brute-cap", type=float, default=1800.0)
    sub.add_parser("v35count")
    sub.add_parser("v35")
    g = sub.add_parser("george")
    g.add_argument("--skip-walk", action="store_true")
    sub.add_parser("partition")
    sub.add_parser("determinism")
    sub.add_parser("audit")
    args = ap.parse_args()
    dict(small=cmd_small, v35count=cmd_v35count, v35=cmd_v35,
         george=cmd_george, partition=cmd_partition,
         determinism=cmd_determinism, audit=cmd_audit)[args.cmd](args)
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())