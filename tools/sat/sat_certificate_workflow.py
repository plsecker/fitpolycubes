#!/usr/bin/env python3
"""Reusable SAT/certificate workflow for hard polycube residual boxes.

Turns the certified Z 6x6x10 / Z 4x11x15 pipeline into a parameterized tool.
The evidence chain implemented here (and required for every closed UNSAT):

    placement generator (repo generator + independent cross-check)
      -> canonical deduplicated CNF (plain ALO+AMO, NO symmetry breaking)
      -> independent semantic audit        (verify_encoding.py, standalone)
      -> native CaDiCaL UNSAT              (binary DRAT proof)
      -> drat-trim VERIFIED                (independent checker)
      -> certificate package + sha256 pins (+ catalogue update, manually)

"Solver returned UNSAT" alone is NOT a result; the chain above is.

Subcommands:
  prepare  generate placements, audit them, build + package the canonical CNF
  solve    native CaDiCaL on the packaged CNF (proof on UNSAT, witness on SAT)
  verify   drat-trim the packaged proof
  audit    run the standalone semantic audit against the package
  witness  validate a SAT witness tiling with the standalone C++ validator
  status   print the package's recorded evidence-chain state

Design invariants (do not weaken without new correctness evidence):
  * Encoding is plain ALO + pairwise AMO exact cover.  NO symmetry-breaking
    predicates (the H 5x5x6 pair-scheme bug destroyed 21.8% of solution
    orbits; symmetry clauses are a proof obligation, not a knob).
  * Clause canonicalization: sorted literals, deduplicated clause set,
    sorted clause sequence (the certified Z 4x11x15 standard).
  * Variable ids follow placements sorted by sorted-cell-list.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, REPO)

TOOLS_SAT = os.path.dirname(os.path.abspath(__file__))
CADICAL_DEFAULT = ("/tmp/opencode/pipdl/python_sat-1.9.dev15/solvers/"
                   "cadical-rel-1.5.3/build/cadical")
DRATTRIM_DEFAULT = "/tmp/opencode/drat-trim-src/drat-trim"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_oris(piece_cells):
    """Distinct normalized orientations under the 24 proper rotations."""
    import itertools
    out = set()
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product([1, -1], repeat=3):
            M = [[0] * 3 for _ in range(3)]
            for i in range(3):
                M[i][perm[i]] = signs[i]
            det = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
                   - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
                   + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
            if det != 1:
                continue
            rot = [tuple(sum(M[i][j] * c[j] for j in range(3)) for i in range(3))
                   for c in piece_cells]
            mn = [min(q[i] for q in rot) for i in range(3)]
            out.add(tuple(sorted((q[0] - mn[0], q[1] - mn[1], q[2] - mn[2])
                                 for q in rot)))
    return out


def regen_placements(oris, dims):
    a, b, c = dims
    pls = set()
    for ori in oris:
        sx = max(q[0] for q in ori)
        sy = max(q[1] for q in ori)
        sz = max(q[2] for q in ori)
        for px in range(a - sx):
            for py in range(b - sy):
                for pz in range(c - sz):
                    pls.add(tuple(sorted((px + q[0], py + q[1], pz + q[2])
                                         for q in ori)))
    return pls


def cmd_prepare(args):
    from common.polycube_utils import generate_placements
    from common.registry import PENTACUBES

    a, b, c = args.box
    dims = tuple(sorted((a, b, c)))
    a, b, c = dims
    piece = PENTACUBES[args.piece]
    piece_cells = [tuple(int(v) for v in row) for row in piece]
    psz = len(piece_cells)
    vol = a * b * c
    if vol % psz:
        sys.exit(f"volume {vol} not divisible by piece size {psz}")

    pkg = args.out
    os.makedirs(pkg, exist_ok=True)

    # ---- placements: repo generator (trusted) ----
    t0 = time.time()
    gen_res = generate_placements(piece, (a, b, c), break_symmetry=False)
    repo_set = set(tuple(sorted((int(x), int(y), int(z)) for x, y, z in p))
                   for p in gen_res[0].values())
    dt_repo = time.time() - t0

    # ---- independent regeneration (audit-grade, own geometry code) ----
    oris = norm_oris(piece_cells)
    indep = regen_placements(oris, dims)
    if indep != repo_set:
        sys.exit(f"PLACEMENT CROSS-CHECK FAILED: repo {len(repo_set)} vs "
                 f"independent {len(indep)} — refuse to build CNF")
    pls_sorted = sorted(indep, key=lambda p: sorted(p))
    n = len(pls_sorted)

    # ---- coverage audit ----
    cover = {}
    for i, p in enumerate(pls_sorted):
        for q in p:
            cover.setdefault(q, []).append(i)
    all_cells = {(x, y, z) for x in range(a) for y in range(b)
                 for z in range(c)}
    if set(cover) != all_cells:
        missing = sorted(all_cells - set(cover))[:5]
        sys.exit(f"coverage incomplete: {len(cover)}/{len(all_cells)} cells, "
                 f"e.g. {missing}")
    for l in cover.values():
        assert len(set(l)) == len(l)

    # ---- canonical deduplicated CNF (plain ALO+AMO, no symmetry breaking)
    naive = 0
    clause_set = set()
    for q, l in cover.items():
        lids = sorted(i + 1 for i in l)
        clause_set.add(tuple(lids))
        naive += 1
        for i in range(len(lids)):
            for j in range(i + 1, len(lids)):
                clause_set.add(tuple(sorted((-lids[i], -lids[j]))))
                naive += 1
    clauses = sorted(clause_set)
    n_amo = sum(1 for cl in clauses if cl[0] < 0)

    stem = f"{args.piece.lower()}_{a}x{b}x{c}".replace("x", "x")
    stem = f"{args.piece.lower()}_{a}x{b}x{c}"
    cnf_path = os.path.join(pkg, f"{stem}.cnf")
    with open(cnf_path, "w") as f:
        f.write(f"c {args.piece} polycube {a}x{b}x{c} exact-cover encoding\n")
        f.write(f"c plain ALO + pairwise AMO, canonical deduplicated form\n")
        f.write(f"c placements: {n}  cells: {vol}  pieces: {vol // psz}\n")
        f.write(f"c generator: repo generate_placements, cross-checked vs "
                f"independent regeneration ({dt_repo:.1f}s)\n")
        f.write(f"p cnf {n} {len(clauses)}\n")
        for cl in clauses:
            f.write(" ".join(map(str, cl)) + " 0\n")
    cnf_sha = sha256_file(cnf_path)

    # ---- package files ----
    with open(os.path.join(pkg, "placement_set.json"), "w") as f:
        json.dump({"box": {"w": a, "h": b, "nz": c},
                   "piece": {"name": args.piece,
                             "cells": [list(q) for q in piece_cells],
                             "provenance": f"common/registry.py "
                                           f"PENTACUBES['{args.piece}']"},
                   "placements": [[list(q) for q in p] for p in pls_sorted]},
                  f)
    with open(os.path.join(pkg, "var_map.json"), "w") as f:
        json.dump({str(i + 1): [list(q) for q in p]
                   for i, p in enumerate(pls_sorted)}, f)
    # self-contained audit: copy the standalone script into the package
    shutil.copy(os.path.join(TOOLS_SAT, "verify_encoding.py"),
                os.path.join(pkg, "verify_encoding.py"))
    if not os.path.exists(os.path.join(pkg, ".gitignore")):
        with open(os.path.join(pkg, ".gitignore"), "w") as f:
            f.write("*.drat\n*.lrat\n")

    if args.expect == "SAT":
        claim = (f"SAT expected: the {a}x{b}x{c} box is tileable by "
                 f"{args.piece} polycubes")
    elif args.expect == "UNSAT":
        claim = (f"UNSAT: the {a}x{b}x{c} box cannot be tiled by "
                 f"{args.piece} polycubes")
    else:
        claim = (f"OPEN QUESTION: decide tileability of the {a}x{b}x{c} "
                 f"box by {args.piece} polycubes")

    meta = {
        "claim": claim,
        "date": time.strftime("%Y-%m-%d"),
        "piece": {"name": args.piece,
                  "cells": [list(q) for q in piece_cells],
                  "size": psz,
                  "provenance": f"common/registry.py "
                                f"PENTACUBES['{args.piece}']"},
        "box": {"w": a, "h": b, "nz": c},
        "box_list": [a, b, c],
        "volume": vol,
        "piece_count": vol // psz,
        "orientation_count": len(oris),
        "placement_count": n,
        "cell_count": vol,
        "variable_count": n,
        "clause_count": len(clauses),
        "clause_families": {"coverage_ge1": vol,
                            "no_overlap_amo_distinct": n_amo},
        "naive_clause_count_before_dedup": naive,
        "encoding": ("plain ALO + pairwise AMO exact cover, canonical "
                     "deduplicated, NO symmetry-breaking predicates"),
        "generator": {"repo": "common.polycube_utils.generate_placements",
                      "repo_seconds": round(dt_repo, 1),
                      "independent_regeneration": "set-identical",
                      "cross_check": "PASS"},
        "cnf_file": os.path.basename(cnf_path),
        "sha256": {"cnf": cnf_sha, "proof": None,
                   "var_map": sha256_file(os.path.join(pkg, "var_map.json")),
                   "placement_set": sha256_file(
                       os.path.join(pkg, "placement_set.json"))},
        "runs": [],
        "chain": {"prepare": "DONE", "solve": None, "verify": None,
                  "audit": None, "witness": None},
    }
    with open(os.path.join(pkg, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print(f"prepared {pkg}: {args.piece} {a}x{b}x{c} placements={n} "
          f"clauses={len(clauses)} ({n_amo} distinct AMO, "
          f"{naive - len(clauses)} dups removed) cnf_sha={cnf_sha[:16]}...")
    return 0


def load_meta(pkg):
    return json.load(open(os.path.join(pkg, "metadata.json")))


def save_meta(pkg, meta):
    with open(os.path.join(pkg, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=1)


def run_record(meta, rec):
    meta.setdefault("runs", []).append(rec)


def cmd_solve(args):
    pkg = args.pkg
    meta = load_meta(pkg)
    cnf = os.path.join(pkg, meta["cnf_file"])
    stem = os.path.basename(cnf)[:-4]
    cadical = args.cadical or CADICAL_DEFAULT
    proof = os.path.join(pkg, f"{stem}.drat")
    log = os.path.join(pkg, f"{stem}_cadical.out")
    t0 = time.time()
    cmd = [cadical]
    if args.time_cap:
        cmd += ["-t", str(args.time_cap)]
    if args.quiet and not args.extract_witness:
        cmd += ["-q"]  # quiet suppresses the witness; never combine them
    cmd += [cnf, proof]
    timed_out = False
    try:
        with open(log, "w") as lf:
            proc = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT,
                                  timeout=(args.time_cap + 120)
                                  if args.time_cap else None)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        timed_out = True
        rc = -1
    dt = time.time() - t0
    out = open(log).read()
    m = re.search(r"^s (UNSATISFIABLE|SATISFIABLE)$", out, re.M)
    verdict = m.group(1) if m else ("TIMEOUT" if timed_out else "NO-VERDICT")

    rec = {"date": time.strftime("%Y-%m-%d"),
           "config": f"native CaDiCaL ({os.path.basename(cadical)}), "
                     f"binary DRAT proof"
                     + (f", time cap {args.time_cap}s" if args.time_cap else ""),
           "wall_seconds": round(dt, 1),
           "result": verdict,
           "exit_code": rc,
           "solver_log": os.path.basename(log)}
    stats = {}
    for key, name in (("conflicts", "conflicts"), ("decisions", "decisions"),
                      ("propagations", "propagations")):
        mm = re.search(rf"^c {name}:\s+(\d+)", out, re.M)
        if mm:
            stats[key] = int(mm.group(1))
    mm = re.search(r"maximum resident set size of process:\s+([\d.]+)\s+MB",
                   out)
    if mm:
        stats["peak_rss_mb"] = float(mm.group(1))
    rec.update(stats)
    run_record(meta, rec)

    if verdict == "SATISFIABLE":
        meta["chain"]["solve"] = "SAT"
        meta["sha256"]["proof"] = None
        if os.path.exists(proof):
            os.remove(proof)
        save_meta(pkg, meta)
        print(f"SAT in {dt:.1f}s — witness lines in {log}")
        if args.extract_witness:
            witness_file = extract_witness(pkg, meta, log)
            if witness_file:
                print(f"witness extracted: {witness_file}")
                rc_v = subprocess.run(
                    [sys.executable, os.path.join(TOOLS_SAT,
                                                  "sat_certificate_workflow.py"),
                     "witness", "--pkg", pkg]).returncode
                if rc_v == 0:
                    meta["chain"]["witness"] = "VALIDATED"
                    save_meta(pkg, meta)
    elif verdict == "UNSATISFIABLE":
        meta["chain"]["solve"] = "UNSAT"
        meta["sha256"]["proof"] = sha256_file(proof)
        with open(proof + ".sha256", "w") as f:
            f.write(f"{meta['sha256']['proof']}  "
                    f"{os.path.basename(proof)}\n")
        save_meta(pkg, meta)
        print(f"UNSAT in {dt:.1f}s — proof {os.path.getsize(proof)/1e9:.2f} GB "
              f"sha256={meta['sha256']['proof'][:16]}...")
    else:
        meta["chain"]["solve"] = verdict
        # a partial proof from a cap abort is never usable — reclaim it
        if os.path.exists(proof):
            os.remove(proof)
        save_meta(pkg, meta)
        limit = "time cap" if "--- [ limit ] ---" in out else \
            ("process timeout" if timed_out else "unknown abort")
        print(f"{verdict} after {dt:.1f}s ({limit}) — no verdict recorded; "
              f"see {log}")
    return 0 if verdict in ("UNSATISFIABLE", "SATISFIABLE") else 3


def extract_witness(pkg, meta, log):
    """Parse the CaDiCaL 'v' witness lines and write witness files."""
    a, b, c = (meta["box"]["w"], meta["box"]["h"], meta["box"]["nz"])
    var_map = json.load(open(os.path.join(pkg, "var_map.json")))
    pos = set()
    for line in open(log):
        if line.startswith("v "):
            for tok in line.split()[1:]:
                try:
                    v = int(tok)
                except ValueError:
                    continue
                if v > 0:
                    pos.add(v)
    chosen = []
    for v in sorted(pos):
        cells = var_map.get(str(v))
        if cells is not None:
            chosen.append([tuple(q) for q in cells])
    if not chosen:
        print("no witness variables parsed")
        return None
    psz = meta["piece"]["size"]
    expected = (a * b * c) // psz
    if len(chosen) != expected:
        print(f"witness parse mismatch: {len(chosen)} pieces vs expected "
              f"{expected}")
        return None
    stem = meta["cnf_file"][:-4]
    wtxt = os.path.join(pkg, f"{stem}_witness.txt")
    with open(wtxt, "w") as f:
        f.write(f"{len(chosen)}\n")
        for p in chosen:
            f.write(" ".join(f"{x} {y} {z}" for x, y, z in sorted(p)) + "\n")
    wjs = os.path.join(pkg, f"{stem}_witness.json")
    with open(wjs, "w") as f:
        json.dump({"box": [a, b, c], "piece": meta["piece"]["name"],
                   "source": "native CaDiCaL witness (this package)",
                   "tiling": [sorted([list(q) for q in p]) for p in chosen]},
                  f)
    return wjs


def cmd_witness(args):
    """Independent C++ validation of the packaged witness tiling."""
    pkg = args.pkg
    meta = load_meta(pkg)
    stem = meta["cnf_file"][:-4]
    wtxt = os.path.join(pkg, f"{stem}_witness.txt")
    if not os.path.exists(wtxt):
        print(f"no witness file {wtxt}")
        return 1
    binary = os.path.join(TOOLS_SAT, "tiling_validator")
    if not os.path.exists(binary):
        subprocess.run(["/tmp/opencode/zxx", "-O2", "-std=c++17", "-o",
                        binary,
                        os.path.join(TOOLS_SAT, "tiling_validator.cpp")],
                       check=True)
    cells = ";".join(",".join(map(str, q)) for q in meta["piece"]["cells"])
    r = subprocess.run([binary, str(meta["box"]["w"]), str(meta["box"]["h"]),
                        str(meta["box"]["nz"]), cells, wtxt],
                       capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    ok = r.returncode == 0 and r.stdout.startswith("VALID")
    meta = load_meta(pkg)
    meta["chain"]["witness"] = "VALIDATED" if ok else "REJECTED"
    save_meta(pkg, meta)
    return 0 if ok else 1


def cmd_verify(args):
    pkg = args.pkg
    meta = load_meta(pkg)
    cnf = os.path.join(pkg, meta["cnf_file"])
    stem = os.path.basename(cnf)[:-4]
    proof = os.path.join(pkg, f"{stem}.drat")
    if not os.path.exists(proof):
        print(f"no proof file {proof}")
        return 1
    checker = args.drattrim or DRATTRIM_DEFAULT
    log = os.path.join(pkg, f"{stem}_drattrim.out")
    t0 = time.time()
    with open(log, "w") as lf:
        proc = subprocess.run([checker, cnf, proof], stdout=lf,
                              stderr=subprocess.STDOUT,
                              timeout=args.time_cap or None)
    dt = time.time() - t0
    out = open(log).read()
    verified = "s VERIFIED" in out
    rec = {"date": time.strftime("%Y-%m-%d"),
           "config": f"drat-trim verification of {os.path.basename(proof)}",
           "checker": checker,
           "result": "s VERIFIED" if verified else
                     ("s NOT VERIFIED" if "s NOT " in out else
                      "NO-VERDICT/TIMEOUT"),
           "wall_seconds": round(dt, 1),
           "checker_log": os.path.basename(log)}
    mm = re.search(r"c (\d+) of (\d+) clauses in core", out)
    if mm:
        rec["core_clauses"] = f"{mm.group(1)}/{mm.group(2)}"
    mm = re.search(r"c (\d+) of (\d+) lemmas in core", out)
    if mm:
        rec["core_lemmas"] = f"{mm.group(1)}/{mm.group(2)}"
    mm = re.search(r"c (\d+) RAT lemmas in core", out)
    if mm:
        rec["rat_lemmas"] = int(mm.group(1))
    mm = re.search(r"c verification time: ([\d.]+) seconds", out)
    if mm:
        rec["checker_seconds"] = float(mm.group(1))
    run_record(meta, rec)
    meta["chain"]["verify"] = "VERIFIED" if verified else "FAILED"
    save_meta(pkg, meta)
    print(f"drat-trim: {'s VERIFIED' if verified else rec['result']} "
          f"in {dt:.1f}s")
    return 0 if verified else 1


def cmd_audit(args):
    pkg = args.pkg
    meta = load_meta(pkg)
    script = os.path.join(pkg, "verify_encoding.py")
    if not os.path.exists(script):
        script = os.path.join(TOOLS_SAT, "verify_encoding.py")
    r = subprocess.run([sys.executable, script, pkg,
                        "--standard", args.standard] +
                       (["--piece-cells", args.piece_cells]
                        if args.piece_cells else []),
                       )
    meta = load_meta(pkg)
    meta["chain"]["audit"] = "PASS" if r.returncode == 0 else "FAIL"
    save_meta(pkg, meta)
    return r.returncode


def cmd_status(args):
    pkg = args.pkg
    meta = load_meta(pkg)
    stem = meta["cnf_file"][:-4]
    proof = os.path.join(pkg, f"{stem}.drat")
    print(f"package: {pkg}")
    print(f"  piece={meta['piece']['name']} box="
          f"{meta['box']['w']}x{meta['box']['h']}x{meta['box']['nz']} "
          f"placements={meta['placement_count']} "
          f"clauses={meta['clause_count']}")
    for r in meta.get("runs", []):
        extra = {k: v for k, v in r.items() if k not in
                 ("date", "config", "result", "wall_seconds")}
        print(f"  run {r.get('date')}: {r.get('result')} "
              f"({r.get('wall_seconds')}s) {r.get('config')}")
        if extra:
            print(f"        {extra}")
    print(f"  chain: {meta.get('chain')}")
    if os.path.exists(proof):
        print(f"  proof: {os.path.getsize(proof)/1e9:.2f} GB")
    return 0


def cmd_readme(args):
    """Write/refresh the package README from metadata + chain state."""
    pkg = args.pkg
    meta = load_meta(pkg)
    a, b, c = meta["box"]["w"], meta["box"]["h"], meta["box"]["nz"]
    piece = meta["piece"]["name"]
    chain = meta.get("chain", {})
    stem = meta["cnf_file"][:-4]
    solve_rec = meta["runs"][0] if meta.get("runs") else None
    verdicts = {"prepare": "canonical deduplicated CNF, plain ALO+AMO, "
                           "no symmetry breaking"}
    lines = [
        f"# {piece} {a}x{b}x{c} Certificate Package",
        "",
        f"**Claim:** {meta['claim']}",
        "",
        "**Encoding:** " + meta["encoding"],
        "",
        "| fact | value |",
        "|---|---|",
        f"| placements / variables | {meta['placement_count']} |",
        f"| clauses (deduplicated) | {meta['clause_count']} |",
        f"| box cells / pieces | {meta['cell_count']} / "
        f"{meta['piece_count']} |",
        f"| generator cross-check | "
        f"{meta['generator']['cross_check']} (repo vs independent "
        f"regeneration) |",
        f"| CNF sha256 | {meta['sha256']['cnf'][:16]}... |",
        "",
        "## Evidence chain",
        "",
    ]
    labels = {"prepare": "prepare (CNF build + cross-check)",
              "audit": "semantic audit (verify_encoding.py)",
              "solve": "native CaDiCaL solve",
              "verify": "drat-trim verification",
              "witness": "C++ witness validation"}
    for k, label in labels.items():
        v = chain.get(k)
        lines.append(f"- {label}: **{v if v else 'NOT RUN'}**")
    if solve_rec:
        lines += ["",
                  f"Solve record: {solve_rec.get('result')} in "
                  f"{solve_rec.get('wall_seconds')} s "
                  f"({solve_rec.get('conflicts', '?')} conflicts). "
                  f"See metadata.json for all runs."]
    lines += ["",
              "## Contents",
              "",
              f"- `{meta['cnf_file']}` — the canonical encoding",
              "- `placement_set.json`, `var_map.json` — encoding provenance",
              "- `metadata.json` — full run history + sha256 pins",
              "- `verify_encoding.py` — standalone semantic audit "
              "(no repo imports)",
              "- `hashes.txt` — integrity pins (write after runs conclude)",
              "",
              "## Status",
              ""]
    if chain.get("solve") == "UNSAT" and chain.get("verify") == "VERIFIED":
        lines.append("**VERIFIED UNSAT** — do not close the catalogue entry "
                     "before this line says so.")
    elif chain.get("solve") == "SAT":
        lines.append("**SAT** — witness tiling in "
                     f"`{stem}_witness.json` (C++-validated: "
                     f"{chain.get('witness')}).")
    elif chain.get("solve") == "TIMEOUT":
        lines.append("**UNKNOWN — solver time cap reached without a "
                     "verdict.** The encoding is audited; the instance "
                     "exceeds the budget. This package documents the "
                     "attempt; it is NOT a decision.")
    else:
        lines.append(f"Chain state: {chain}.")
    with open(os.path.join(pkg, "README.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"README written: {os.path.join(pkg, 'README.md')}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("prepare")
    p.add_argument("--piece", required=True)
    p.add_argument("--box", nargs=3, type=int, required=True, metavar="A B C")
    p.add_argument("--out", required=True)
    p.add_argument("--expect", choices=("UNSAT", "SAT", "UNKNOWN"),
                   default="UNKNOWN")
    p.set_defaults(func=cmd_prepare)

    p = sub.add_parser("solve")
    p.add_argument("--pkg", required=True)
    p.add_argument("--cadical", default=None)
    p.add_argument("--time-cap", type=int, default=None)
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--no-witness", dest="extract_witness",
                   action="store_false", default=True)
    p.set_defaults(func=cmd_solve)

    p = sub.add_parser("verify")
    p.add_argument("--pkg", required=True)
    p.add_argument("--drattrim", default=None)
    p.add_argument("--time-cap", type=int, default=None)
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("audit")
    p.add_argument("--pkg", required=True)
    p.add_argument("--standard", choices=("canonical", "legacy"),
                   default="canonical")
    p.add_argument("--piece-cells", default=None)
    p.set_defaults(func=cmd_audit)

    p = sub.add_parser("witness")
    p.add_argument("--pkg", required=True)
    p.set_defaults(func=cmd_witness)

    p = sub.add_parser("status")
    p.add_argument("--pkg", required=True)
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("readme")
    p.add_argument("--pkg", required=True)
    p.set_defaults(func=cmd_readme)

    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
