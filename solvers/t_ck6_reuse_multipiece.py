#!/usr/bin/env python3
"""
Stage 5L: reuse the completed CK6 target corpora (V = 5..45) to search for
CK6-or-higher oddities with EVERY pentacube in common.registry.PENTACUBES,
not only T.

Reuse contract (Stage 5L):
  - The CK6 target spaces are NOT regenerated and the enumeration
    algorithm is NOT modified: targets are streamed from the very same
    functions the completed T searches used
    (t_ck6_oddity_v35_search.build_universe / iter_targets_seeded for the
    sharded volumes, common.oddity.enumerate_connected_ck6_targets for
    V <= 25), over the SAME persisted per-min-id corpus partitions
    (data/ck6_v35/minid_counts.json, data/ck6_v45/minid_counts.json) and
    the SAME shard plans (data/ck6_v{35,45}/shards.json).
  - The funnel + exact-cover + dual-solver audit is the v35 driver's own
    funnel_and_cover, imported unmodified.
  - The TARGET is the CK6-symmetric object; pieces need no symmetry.
  - No correctness check is weakened: per-target volume/connectivity/
    CK6-closure asserts and the dual-solver equality assert all remain.

Resume semantics: one (volume, piece) combination at a time; a combo is
skipped when its workdir already contains final.json; large volumes run
as min-id shards (identical to the historical shard plans) and each
completed shard is persisted, so interrupted runs resume at shard
granularity.  Results stream into data/ck6_reuse/piece_volume_results.jsonl.

Subcommands:
  verify    corpus verification against the known totals
  controls  positive controls (19-T fixture through this driver's path;
            exact-cover SAT regression; T negative anchors)
  combo     run one (volume, piece) combination
  run       orchestrator: loop volumes x pieces with resume
  report    (re)build data/ck6_reuse/report.json from completed combos
  status    print per-combo progress
"""

import json
import os
import resource
import subprocess
import sys
import time
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from t_ck6_oddity_v35_search import (  # noqa: E402  (untouched enumeration)
    build_universe,
    funnel_and_cover,
    iter_targets_seeded,
)
from common.fastfunnel import FastFunnel  # noqa: E402
from common.oddity import (  # noqa: E402
    enumerate_connected_ck6_targets,
    is_face_connected,
    l1_ball,
    max_l1_for_volume,
)
from common.registry import PENTACUBES  # noqa: E402
from common.symmetry import (  # noqa: E402
    ck6_affine_maps,
    canonical_form,
    element_kind,
    full_symmetry,
    order4_lunnon_code,
    symmetry_order,
)

REUSE_DIR = os.path.join(REPO, "data", "ck6_reuse")
JSONL_PATH = os.path.join(REUSE_DIR, "piece_volume_results.jsonl")
REPORT_PATH = os.path.join(REUSE_DIR, "report.json")

# Authoritative corpus totals (Stage 2-4E validated results).
# NOTE (Stage 5L): the stage brief expected V=5 == 1 target, but the
# unmodified reference enumerator yields 2 connected CK6-closed 5-cell
# targets -- the 1x1x5 bar (center + axis orbits t=1, t=2) and the
# planar X cross (center + one generic 4-orbit), both BBC2 (order 16)
# superset-of-CK6 figures.  The enumerator is authoritative; the brief's
# V=5 expectation is corrected here and flagged in the report.
KNOWN_TOTALS = {5: 2, 15: 368, 25: 71539, 35: 15289669, 45: 1469999}

# Historical T funnel counters, for the negative-result controls.
T_ANCHORS = {
    25: {"targets": 71539,
         "reject: <k contained placements": 52541,
         "reject: uncovered cell": 18090,
         "pass coverage": 908,
         "reject: exact cover UNSAT": 908,
         "TILEABLE": 0},
    35: {"targets": 15289669,
         "reject: <k contained placements": 9003562,
         "reject: uncovered cell": 6229218,
         "pass coverage": 56889,
         "reject: exact cover UNSAT": 56889,
         "TILEABLE": 0},
    45: {"targets": 1469999,
         "reject: <k contained placements": 1436064,
         "reject: uncovered cell": 33935,
         "pass coverage": 0,
         "reject: exact cover UNSAT": 0,
         "TILEABLE": 0},
}

PIECES = sorted(PENTACUBES)  # canonical registry catalogue, 23 pieces


def combo_workdir(volume, piece):
    return os.path.join(REUSE_DIR, "run", f"v{volume}_{piece}")


def classify(cells):
    syms = full_symmetry(cells)
    code = order4_lunnon_code(syms)
    return (code if code is not None else f"order{symmetry_order(syms)}"), syms


# ---------------------------------------------------------------------------
# corpus verification (Stage 5L item 1)
# ---------------------------------------------------------------------------

def cmd_verify(_args):
    print("Verifying persisted CK6 target corpora against known totals...")
    for volume, known in sorted(KNOWN_TOTALS.items()):
        t0 = time.time()
        if volume <= 25:
            n = sum(1 for _ in enumerate_connected_ck6_targets(volume))
            how = "re-enumerated (reference enumerator)"
        else:
            with open(os.path.join(REPO, "data", f"ck6_v{volume}",
                                   "minid_counts.json")) as f:
                mc = json.load(f)
            total = mc["total"]
            assert sum(mc["hist"].values()) == total, (volume, total)
            with open(os.path.join(REPO, "data", f"ck6_v{volume}",
                                   "report.json")) as f:
                rep = json.load(f)
            assert rep["status"] == "COMPLETE", (volume, rep["status"])
            assert rep["total_targets"] == rep["expected_targets"] == total, \
                (volume, rep["total_targets"], rep["expected_targets"], total)
            n, how = total, "persisted min-id partition + validated report"
        assert n == known, (volume, n, known)
        print(f"  V={volume}: {n:,} targets == known total  "
              f"[{how}, {time.time()-t0:.1f}s]")
    print("CORPUS VERIFIED")


# ---------------------------------------------------------------------------
# positive controls (Stage 5L item 5)
# ---------------------------------------------------------------------------

def control_19T():
    """George's 19-T construction through THIS driver's funnel+cover path."""
    path = os.path.join(REPO, "tools", "frontier",
                        "_ck6_19T_sicherman_fixture.json")
    with open(path) as f:
        fx = json.load(f)
    target = frozenset(tuple(c) for c in fx["cells"])
    assert len(target) == 95
    maps = ck6_affine_maps((0, 0)).values()
    # the fixture's CK6 subgroup is conjugate; verify closure under the
    # canonical center-type maps after translating the fixed point to 0
    f0 = (1, 1, 8)
    shifted = frozenset((x - f0[0], y - f0[1], z - f0[2])
                        for (x, y, z) in target)
    assert all(frozenset(m(c) for c in shifted) == shifted for m in maps), \
        "19-T fixture not CK6-closed about its fixed point"
    # funnel + exact cover over a containing domain (the target bbox)
    xs = sorted({c[0] for c in shifted})
    ys = sorted({c[1] for c in shifted})
    zs = sorted({c[2] for c in shifted})
    domain = [(x, y, z) for x in range(xs[0], xs[-1] + 1)
              for y in range(ys[0], ys[-1] + 1)
              for z in range(zs[0], zs[-1] + 1)]
    piece = [tuple(map(int, c)) for c in PENTACUBES["T"]]
    index = FastFunnel(piece, domain).index
    state = {"funnel": Counter()}
    stage, n, _rows = funnel_and_cover(shifted, index, 19, state)
    assert stage == "SAT" and n == 16, (stage, n)
    print(f"  PASS: 19-T fixture: CK6-closed, funnel+cover finds exactly "
          f"{n} tilings by 19 T pentacubes")
    code, syms = classify(shifted)
    kinds = sorted(element_kind(m) for m in syms)
    # D4h (BBC2, order 16): the Lunnon label above order 4 is structural
    assert len(syms) == 16 and code == "order16", (code, len(syms))
    assert kinds == ["c2_diag"] * 2 + ["c2_ortho"] * 3 + ["c4"] * 2 + \
        ["identity"] + ["inversion"] + ["mirror_diag"] * 2 + \
        ["mirror_ortho"] * 3 + ["s4"] * 2, kinds
    print(f"  PASS: 19-T fixture class {code} (D4h = BBC2), |Sym| = "
          f"{len(syms)} (superset of CK6)")


def control_sat_regression():
    """The existing exact-cover SAT regression must keep passing."""
    sys.path.insert(0, os.path.join(REPO, "tools", "frontier"))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "test_ck6_oddity", os.path.join(REPO, "tools", "frontier",
                                        "test_ck6_oddity.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.test_exact_cover_solvers_agree_on_sat_instances()
    print("  PASS: exact-cover SAT regression "
          "(9-cell fixture = 2 covers, 19-T tower = 16 covers)")


def cmd_controls(_args):
    print("Stage 5L positive controls...")
    control_19T()
    control_sat_regression()
    print("CONTROLS OK")


# ---------------------------------------------------------------------------
# one (volume, piece) combination
# ---------------------------------------------------------------------------

def _new_state(volume, piece, shard=None):
    return {"volume": volume, "piece": piece, "shard": shard,
            "funnel": Counter(), "targets": 0, "sat": 0, "unsat": 0,
            "covers_total": 0, "covers_max": 0, "witnesses": [],
            "status": "running"}


def _record_witness(state, t, n):
    code, syms = classify(t)
    wit = {"volume": state["volume"], "piece": state["piece"],
           "tiles": state["volume"] // 5,
           # full-O_h canonical form (historical comparability); for the
           # chiral pieces (G, H, R) this can be the mirror image, which
           # is NOT tileable by proper-only placements:
           "canonical_target": canonical_form(t),
           # proper-rotation canonical form: congruent to the enumerated
           # target by a proper rotation, hence tileable -- use this as
           # the geometric identifier of a positive construction
           "canonical_target_proper": canonical_form(t, proper_only=True),
           "number_of_covers": n,
           "symmetry_order": len(syms),
           "symmetry_kinds": dict(Counter(element_kind(m) for m in syms)),
           "symmetry_class": code}
    state["witnesses"].append(wit)
    if state["shard"] is not None:
        wpath = os.path.join(
            _shard_dir(state), f"witness_{state['shard']:02d}_"
            f"{len(state['witnesses']):03d}.json")
        with open(wpath, "w") as f:
            json.dump(wit, f, indent=1)


def _shard_dir(state):
    return state.setdefault("workdir", combo_workdir(state["volume"],
                                                     state["piece"]))


def _process_target(t, state, index, ff, k):
    state["targets"] += 1
    assert len(t) == state["volume"]
    assert is_face_connected(t)
    stage, n, _rows = funnel_and_cover(t, index, k, state, ff=ff)
    if stage == "SAT":
        state["sat"] += 1
        state["covers_total"] += n
        state["covers_max"] = max(state["covers_max"], n)
        _record_witness(state, t, n)
    return stage


def run_combo_small(volume, piece, workdir):
    """V <= 25: stream the reference enumerator in one process."""
    k = volume // 5
    piece_cells = [tuple(map(int, c)) for c in PENTACUBES[piece]]
    ball = l1_ball(max_l1_for_volume(volume))
    ff = FastFunnel(piece_cells, ball)
    index = ff.index
    maps = list(ck6_affine_maps((0, 0)).values())
    state = _new_state(volume, piece)
    state["workdir"] = workdir
    t0 = time.time()
    for t in enumerate_connected_ck6_targets(volume):
        assert all(frozenset(m(c) for c in t) == t for m in maps), \
            "enumerator produced a non-CK6-closed target"
        _process_target(t, state, index, ff, k)
    return state, time.time() - t0


def run_shard_piece(volume, piece, min_ids, workdir, shard_idx):
    """One min-id shard; identical iteration to the historical run_shard."""
    k = volume // 5
    piece_cells = [tuple(map(int, c)) for c in PENTACUBES[piece]]
    un = build_universe(volume)
    ff = FastFunnel(piece_cells, un["ball"])
    index = ff.index
    state = _new_state(volume, piece, shard=shard_idx)
    state["workdir"] = workdir
    ckpt = os.path.join(workdir, f"shard_{shard_idx:03d}.checkpoint.json")
    result = os.path.join(workdir, f"shard_{shard_idx:03d}.json")
    stop = os.path.join(workdir, "STOP")
    t0 = time.time()
    last_ckpt = 0.0
    for s in min_ids:
        for t in iter_targets_seeded(un, s, (volume - 1) // 2):
            _process_target(t, state, index, ff, k)
            if os.path.exists(stop):
                state["status"] = "stopped-early"
                break
            now = time.time()
            if now - last_ckpt > 120:
                state["elapsed_s"] = round(time.time() - t0, 1)
                state["peak_rss_mb"] = round(
                    resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
                    1)
                with open(ckpt, "w") as f:
                    json.dump(state, f, default=dict)
                last_ckpt = now
        if state["status"] != "running":
            break
    state["status"] = ("complete" if state["status"] == "running"
                       else state["status"])
    state["elapsed_s"] = round(time.time() - t0, 1)
    state["peak_rss_mb"] = round(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    with open(result, "w") as f:
        json.dump(state, f, default=dict, indent=1)
    if os.path.exists(ckpt):
        os.remove(ckpt)
    print(f"shard {shard_idx} [{piece} V={volume}]: targets="
          f"{state['targets']} sat={state['sat']} "
          f"elapsed={state['elapsed_s']}s", flush=True)


def aggregate_combo(volume, piece, workdir, expected_total):
    """Aggregate shard states into final.json (combo-level resume unit)."""
    plan_path = os.path.join(REPO, "data", f"ck6_v{volume}", "shards.json")
    with open(plan_path) as f:
        plan = json.load(f)
    total = _new_state(volume, piece)
    total["workdir"] = workdir
    missing = []
    for sh in plan["shards"]:
        path = os.path.join(workdir, f"shard_{sh['shard']:03d}.json")
        if not os.path.exists(path):
            missing.append(sh["shard"])
            continue
        with open(path) as f:
            r = json.load(f)
        total["targets"] += r["targets"]
        for key, v in r["funnel"].items():
            total["funnel"][key] += v
        total["sat"] += r["sat"]
        total["unsat"] += r["unsat"]
        total["covers_total"] += r.get("covers_total", 0)
        total["covers_max"] = max(total["covers_max"],
                                  r.get("covers_max", 0))
        total["witnesses"].extend(r["witnesses"])
        total["elapsed_s"] = max(total.get("elapsed_s", 0),
                                 r.get("elapsed_s", 0))
        total["peak_rss_mb"] = max(total.get("peak_rss_mb", 0),
                                   r.get("peak_rss_mb", 0))
    if missing:
        return None, missing
    assert total["targets"] == expected_total, \
        (volume, piece, total["targets"], expected_total)
    _check_t_anchor(volume, piece, total)
    final = _finalize(volume, piece, total, "COMPLETE")
    with open(os.path.join(workdir, "final.json"), "w") as f:
        json.dump(final, f, default=dict, indent=1)
    _append_jsonl(final)
    return final, []


def _check_t_anchor(volume, piece, state):
    """Hard control: the T rerun must reproduce the historical counters."""
    if piece != "T" or volume not in T_ANCHORS:
        return
    anchor = T_ANCHORS[volume]
    f = dict(state["funnel"])
    got = {"targets": state["targets"],
           "reject: <k contained placements":
               f.get("reject: <k contained placements", 0),
           "reject: uncovered cell": f.get("reject: uncovered cell", 0),
           "pass coverage": f.get("pass coverage", 0),
           "reject: exact cover UNSAT":
               f.get("reject: exact cover UNSAT", 0),
           "TILEABLE": f.get("TILEABLE", 0)}
    assert got == anchor, f"T anchor drift at V={volume}:\n{got}\n{anchor}"
    print(f"  T anchor V={volume}: funnel counters match the historical "
          f"result exactly", flush=True)


def _finalize(volume, piece, state, status):
    funnel = dict(state["funnel"])
    wit = state["witnesses"]
    first = None
    if wit:
        w = wit[0]
        first = {"canonical_target": w.get("canonical_target_proper",
                                           w["canonical_target"]),
                 "number_of_covers": w["number_of_covers"],
                 "symmetry_order": w["symmetry_order"],
                 "symmetry_class": w["symmetry_class"]}
    return {
        "piece": piece,
        "volume": volume,
        "tiles": volume // 5,
        "number_of_targets": state["targets"],
        "targets_rejected_few_placements":
            funnel.get("reject: <k contained placements", 0),
        "targets_rejected_uncovered":
            funnel.get("reject: uncovered cell", 0),
        "exact_cover_candidates": funnel.get("pass coverage", 0),
        "reject_exact_cover_unsat":
            funnel.get("reject: exact cover UNSAT", 0),
        "sat_count": state["sat"],
        "number_of_solutions": state["covers_total"],
        "max_solutions_single_target": state["covers_max"],
        "first_solution_target": first,
        "witnesses": wit,
        "symmetry_order": first["symmetry_order"] if first else None,
        "symmetry_class": first["symmetry_class"] if first else None,
        "elapsed_shard_max_s": state.get("elapsed_s", 0),
        "peak_rss_mb": state.get("peak_rss_mb", 0),
        "status": status,
    }


def _append_jsonl(final):
    os.makedirs(REUSE_DIR, exist_ok=True)
    with open(JSONL_PATH, "a") as f:
        f.write(json.dumps(final, default=dict, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def run_combo(volume, piece, parallel=None):
    if parallel is None:
        # V=45: 4 workers x ~3.2 GB peak fits RAM; V=35: the DFS visited
        # set dominates (~7-8 GB/shard, piece-independent), so 2 workers.
        parallel = 4 if volume >= 45 else 2
    workdir = combo_workdir(volume, piece)
    final_path = os.path.join(workdir, "final.json")
    if os.path.exists(final_path):
        with open(final_path) as f:
            print(f"[combo] V={volume} {piece}: already complete (resume)")
        return
    os.makedirs(workdir, exist_ok=True)
    t0 = time.time()
    if volume <= 25:
        state, elapsed = run_combo_small(volume, piece, workdir)
        _check_t_anchor(volume, piece, state)
        final = _finalize(volume, piece, state, "COMPLETE")
        final["elapsed_shard_max_s"] = round(elapsed, 1)
        with open(final_path, "w") as f:
            json.dump(final, f, default=dict, indent=1)
        _append_jsonl(final)
        print(f"[combo] V={volume} {piece}: targets={final['number_of_targets']}"
              f" candidates={final['exact_cover_candidates']}"
              f" SAT={final['sat_count']}"
              f" ({time.time()-t0:.0f}s)", flush=True)
    else:
        with open(os.path.join(REPO, "data", f"ck6_v{volume}",
                               "shards.json")) as f:
            plan = json.load(f)
        pending = [s["shard"] for s in plan["shards"]
                   if not os.path.exists(os.path.join(
                       workdir, f"shard_{s['shard']:03d}.json"))]
        print(f"[combo] V={volume} {piece}: {len(pending)} shards to run on "
              f"{parallel} workers", flush=True)
        queue = list(pending)
        running = {}
        while queue or running:
            while queue and len(running) < parallel:
                i = queue.pop(0)
                logf = open(os.path.join(
                    workdir, f"shard_{i:03d}.log"), "a")
                p = subprocess.Popen(
                    [sys.executable, os.path.abspath(__file__), "combo",
                     "--volume", str(volume), "--piece", piece,
                     "--shard", str(i)],
                    stdout=logf, stderr=subprocess.STDOUT)
                running[i] = p
                print(f"[combo] launched shard {i} (pid {p.pid})", flush=True)
            for i in [i for i, p in running.items() if p.poll() is not None]:
                print(f"[combo] shard {i} finished "
                      f"rc={running.pop(i).returncode}", flush=True)
            time.sleep(2)
        final, missing = aggregate_combo(volume, piece, workdir,
                                         KNOWN_TOTALS[volume])
        if final is None:
            raise RuntimeError(f"missing shards after run: {missing}")
        print(f"[combo] V={volume} {piece}: targets={final['number_of_targets']}"
              f" candidates={final['exact_cover_candidates']}"
              f" SAT={final['sat_count']}"
              f" (shard max {final['elapsed_shard_max_s']:.0f}s)",
              flush=True)


def cmd_combo(args):
    if args.shard is None:
        parallel = args.parallel or (4 if args.volume >= 45 else 2)
        run_combo(args.volume, args.piece, parallel)
    else:
        with open(os.path.join(REPO, "data", f"ck6_v{args.volume}",
                               "shards.json")) as f:
            plan = json.load(f)
        sh = next(s for s in plan["shards"] if s["shard"] == args.shard)
        workdir = combo_workdir(args.volume, args.piece)
        os.makedirs(workdir, exist_ok=True)
        run_shard_piece(args.volume, args.piece, sh["min_ids"], workdir,
                        args.shard)


# ---------------------------------------------------------------------------
# orchestrator + report
# ---------------------------------------------------------------------------

def cmd_run(args):
    volumes = [int(v) for v in args.volumes.split(",")]
    for volume in volumes:
        assert volume in KNOWN_TOTALS, volume
        for piece in PIECES:
            if piece == "T" and args.skip_t:
                continue
            run_combo(volume, piece, args.parallel)
    print("RUN LOOP COMPLETE for volumes", volumes)


def cmd_report(_args):
    rows = []
    if os.path.exists(JSONL_PATH):
        with open(JSONL_PATH) as f:
            rows = [json.loads(line) for line in f if line.strip()]
    # keep the last record per (volume, piece)
    best = {}
    for r in rows:
        best[(r["volume"], r["piece"])] = r
    matrix = {}
    positives = []
    for piece in PIECES:
        matrix[piece] = {}
        for volume in sorted(KNOWN_TOTALS):
            r = best.get((volume, piece))
            if r is None:
                matrix[piece][f"V={volume}"] = None
                continue
            matrix[piece][f"V={volume}"] = {
                "targets": r["number_of_targets"],
                "candidates": r["exact_cover_candidates"],
                "sat": r["sat_count"],
                "status": r["status"],
            }
            if r["sat_count"]:
                positives.append({
                    "piece": piece,
                    "volume": volume,
                    "target_identifier": r["first_solution_target"][
                        "canonical_target"] if r["first_solution_target"]
                    else None,
                    "number_of_copies": r["tiles"],
                    "sat_count": r["sat_count"],
                    "number_of_exact_covers": r["number_of_solutions"],
                    "symmetry_class": r["symmetry_class"],
                    "symmetry_order": r["symmetry_order"],
                    "witnesses": r["witnesses"],
                })
    report = {
        "stage": "5L",
        "description": "CK6 target-corpora reuse: all registry pentacubes "
                       "against the completed V=5..45 CK6 target corpora",
        "corpus_totals": {f"V={v}": n for v, n in sorted(KNOWN_TOTALS.items())},
        "pieces": PIECES,
        "matrix": matrix,
        "positives": positives,
        "jsonl": os.path.relpath(JSONL_PATH, REPO),
    }
    os.makedirs(REUSE_DIR, exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=1, default=dict)
    print(f"report written to {REPORT_PATH} "
          f"({len(best)} combos recorded, {len(positives)} positive)")


def cmd_status(_args):
    for volume in sorted(KNOWN_TOTALS):
        for piece in PIECES:
            wd = combo_workdir(volume, piece)
            final = os.path.join(wd, "final.json")
            if os.path.exists(final):
                with open(final) as f:
                    r = json.load(f)
                print(f"V={volume} {piece}: DONE targets="
                      f"{r['number_of_targets']} SAT={r['sat_count']}")
            else:
                ckpts = [f for f in sorted(os.listdir(wd))
                         if f.startswith("shard_") and f.endswith(".json")
                         and "checkpoint" not in f] if os.path.isdir(wd) else []
                if ckpts:
                    print(f"V={volume} {piece}: partial ({len(ckpts)} shards)")
    if os.path.exists(REPORT_PATH):
        print("report:", REPORT_PATH)


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["verify", "controls", "combo", "run",
                                    "report", "status"])
    ap.add_argument("--volume", type=int, default=25)
    ap.add_argument("--piece", default="T")
    ap.add_argument("--shard", type=int, default=None)
    ap.add_argument("--parallel", type=int, default=None)
    ap.add_argument("--volumes", default="5,15,25,45,35")
    ap.add_argument("--skip-t", action="store_true",
                    help="skip T (already covered by the completed searches)")
    args = ap.parse_args()
    dict(verify=cmd_verify, controls=cmd_controls, combo=cmd_combo,
         run=cmd_run, report=cmd_report, status=cmd_status)[args.cmd](args)


if __name__ == "__main__":
    main()
