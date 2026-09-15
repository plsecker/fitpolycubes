#!/usr/bin/env python3
"""Shirakawa corpus gap audit.

Non-destructive, read-only analysis that compares the repository's existing
concrete solution files (data/solutions_*.dat) against the Shirakawa corpus
(shirakawa/*.md) and classifies every (piece, box) pair that has a local
tiling witness.

Outputs:
  - a JSON report (stdout or --out file) with per-file classifications
  - a compact human-readable table

This script never modifies catalogue files, solution files, or the corpus.
It does not launch any solver.

Usage:
  python3 tools/frontier/shirakawa_gap_audit.py [--out report.json] [--verbose]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SHIRAKAWA = ROOT / "shirakawa"
DATA = ROOT / "data"

BOX_RE = re.compile(r"^\d+x\d+x\d+$")
# A pattern position is one of: a plain number, a [lo-hi] range, or M/N wildcard.
POS_RE = re.compile(r"^(\d+)|\[(\d+)-(\d+)\]|([MN])$")


def parse_range_token(token: str):
    """Return a matcher for one pattern position: (kind, lo, hi)."""
    m = POS_RE.match(token.strip())
    if not m:
        return None
    if m.group(1) is not None:
        n = int(m.group(1))
        return ("num", n, n)
    if m.group(2) is not None:
        return ("range", int(m.group(2)), int(m.group(3)))
    return ("any", 0, 0)


def pattern_covers(pattern: str, box: tuple[int, int, int]) -> bool:
    """Does a family pattern like '2x[2-20]xN' cover canonical box (a,b,c)?

    The box is unordered, so we try every permutation of the box dimensions
    against the three pattern positions.
    """
    parts = pattern.split("x")
    if len(parts) != 3:
        return False
    matchers = [parse_range_token(p) for p in parts]
    if any(m is None for m in matchers):
        return False
    import itertools

    for perm in itertools.permutations(box):
        ok = True
        for dim, (kind, lo, hi) in zip(perm, matchers):
            if kind == "num" and dim != lo:
                ok = False
                break
            if kind == "range" and not (lo <= dim <= hi):
                ok = False
                break
        if ok:
            return True
    return False


def parse_shirakawa():
    """Parse the corpus into concrete records and family statements.

    Two row formats occur:
      A (S.md style, 8 fields):  nump  size  [size: markers]  sols  [sols href]  [remark]  date  who
      B (R.md style, 6 fields):  nump  size  sols  remark  date  who
    Format B is detected when field 2 does not start with '[size'.
    """
    concrete = {}   # (piece, box) -> list of record dicts
    families = {}   # piece -> list of (pattern, status, source, year)

    for path in sorted(SHIRAKAWA.glob("*.md")):
        piece = path.stem
        section = None
        for line in path.read_text(errors="replace").splitlines():
            s = line.strip()
            if s == "3D":
                section = "3D"
                continue
            if s in {"4D", "5D", "*D", "3D 2-sided"}:
                section = None
                continue
            if section != "3D":
                continue
            fields = line.split("\t")
            if len(fields) < 4:
                continue
            size = fields[1].strip()
            if not size:
                continue
            if fields[2].strip().startswith("[size"):
                # format A
                status = fields[3].strip()
                source = fields[7].strip() if len(fields) > 7 else ""
                year = fields[6].strip() if len(fields) > 6 else ""
            else:
                # format B (R.md)
                status = fields[2].strip()
                source = fields[5].strip() if len(fields) > 5 else ""
                year = fields[4].strip() if len(fields) > 4 else ""
            if BOX_RE.fullmatch(size):
                dims = tuple(sorted(map(int, size.split("x"))))
                concrete.setdefault((piece, dims), []).append(
                    {"status": status, "source": source, "year": year,
                     "size_str": size}
                )
            else:
                families.setdefault(piece, []).append(
                    {"pattern": size, "status": status, "source": source,
                     "year": year}
                )
    return concrete, families


def parse_solution_files():
    """Parse data/solutions_*.dat into (piece, box, witness) entries.

    The box is taken from the filename (canonicalised); the header is used as
    a cross-check when present.  A file counts as a witness only if it
    contains at least one solution line (non-empty content beyond the header).
    """
    entries = []
    for path in sorted(DATA.glob("solutions_*.dat")):
        name = path.name
        # strip solver prefix and trailing qualifiers
        stem = name[len("solutions_"):]
        # e.g. fast_v_5x5x9_282_baseline / hybrid_s_4x8x130 / s_4x9x60_shirakawa
        m = re.match(r"^(?:[a-z0-9]+_)?([A-Za-z])_(\d+)x(\d+)x(\d+)(?:_|\.)", stem)
        if not m:
            # mp_n_5x5x5 has no solver prefix
            m = re.match(r"^([A-Za-z])_(\d+)x(\d+)x(\d+)(?:_|\.)", stem)
        if not m:
            print(f"WARN: cannot parse filename {name}", file=sys.stderr)
            continue
        piece = m.group(1).upper()
        box = tuple(sorted((int(m.group(2)), int(m.group(3)), int(m.group(4)))))
        text = path.read_text(errors="replace")
        lines = [ln for ln in text.splitlines() if ln.strip()]
        # header lines start with '#'
        body = [ln for ln in lines if not ln.startswith("#")]
        # a witness needs at least one solution line; a bare count line is not
        # a witness
        has_witness = False
        n_sols = 0
        for ln in body:
            if ln.strip().isdigit():
                continue
            # a solution line carries >= 5 coordinate tuples, either as
            # ((x, y, z), ...) or as (x,y,z)(x,y,z)... (Shirakawa SVG format)
            if ln.count("(") >= 5:
                has_witness = True
                n_sols += 1
        entries.append({
            "file": name,
            "piece": piece,
            "box": box,
            "box_str": "x".join(map(str, box)),
            "bytes": path.stat().st_size,
            "has_witness": has_witness,
            "n_sol_lines": n_sols,
        })
    return entries


def classify(entry, concrete, families):
    """Classify one solution-file entry against the corpus."""
    piece = entry["piece"]
    box = entry["box"]
    recs = concrete.get((piece, box), [])
    fams = [f for f in families.get(piece, []) if pattern_covers(f["pattern"], box)]

    if recs:
        statuses = sorted({r["status"] for r in recs})
        rec = recs[0]
        if "0" in statuses:
            return {
                "classification": "STATUS_0",
                "concrete": recs,
                "families": fams,
                "note": f"concrete record status {statuses}",
            }
        return {
            "classification": "EXPLICIT_RECORD",
            "concrete": recs,
            "families": fams,
            "note": f"concrete record status {statuses}",
        }
    if fams:
        statuses = sorted({f["status"] for f in fams})
        if "0" in statuses:
            return {
                "classification": "STATUS_0",
                "concrete": [],
                "families": fams,
                "note": f"family/range statement status {statuses}",
            }
        return {
            "classification": "FAMILY_COVERED",
            "concrete": [],
            "families": fams,
            "note": f"family/range statement status {statuses}",
        }
    return {
        "classification": "NO_RECORD",
        "concrete": [],
        "families": [],
        "note": "no concrete record and no family/range statement",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="write JSON report to this path")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    concrete, families = parse_shirakawa()
    entries = parse_solution_files()

    n_concrete = sum(len(v) for v in concrete.values())
    n_status0 = sum(
        1 for v in concrete.values() if any(r["status"] == "0" for r in v)
    )
    n_family = sum(len(v) for v in families.values())

    results = []
    for e in entries:
        cls = classify(e, concrete, families)
        results.append({**e, **cls})

    report = {
        "corpus": {
            "files": len(list(SHIRAKAWA.glob("*.md"))),
            "concrete_records": n_concrete,
            "concrete_status0_boxes": n_status0,
            "family_statements": n_family,
        },
        "solution_files": {
            "total": len(entries),
            "with_witness": sum(1 for r in results if r["has_witness"]),
        },
        "results": results,
    }

    if args.out:
        Path(args.out).write_text(json.dumps(report, indent=2))
        print(f"wrote {args.out}")

    # compact table
    print(f"corpus: {n_concrete} concrete records, {n_status0} status-0 boxes, "
          f"{n_family} family statements")
    print(f"files: {len(entries)} total, "
          f"{report['solution_files']['with_witness']} with witness\n")
    hdr = f"{'file':44} {'piece':5} {'box':10} {'witness':8} {'classification':16} note"
    print(hdr)
    print("-" * len(hdr))
    for r in results:
        print(f"{r['file']:44} {r['piece']:5} {r['box_str']:10} "
              f"{str(r['has_witness']):8} {r['classification']:16} {r['note']}")


if __name__ == "__main__":
    main()