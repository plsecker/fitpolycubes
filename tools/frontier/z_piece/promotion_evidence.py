#!/usr/bin/env python3
"""Promotion evidence replay for the Z catalogue.

Reconciles the Shirakawa Z page (authoritative source) against the audit's
published-evidence table, replays the recorded 102 proof trees through the
CURRENT decomposition engine + validator, classifies each closure by evidence
path, runs truth-table conflict checks, and audits the five Breadth closures.

Read-only with respect to all catalogue truth tables.
Writes a JSON summary for the promotion document.

Usage: .venv/bin/python tools/frontier/z_piece/promotion_evidence.py [--json OUT]
"""
import argparse
import dataclasses
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).parent))

import solvers.decomp as decomp  # noqa: E402
from catalogues.base import Box  # noqa: E402
from catalogues.z_catalogue import Z_CATALOGUE  # noqa: E402
from validate_proof_tree import validate  # noqa: E402

# ---------------------------------------------------------------------------
# Verbatim flattened 3D section of https://puzzlewillbeplayed.com/Shirakawa/Z.html
# (fetched 2026-08-27 and 2026-08-28; identical both times, page footer
#  "Feb 18, 2015 by k16@chiba.email.ne.jp").  Lines only, 3D section.
# ---------------------------------------------------------------------------
PAGE_3D_TEXT = """
3x[3-22]xNs:02013Shirakawa
6903x23x50s:02013Shirakawa
2,0703x23x1501+2014Shirakawa
2,4153x23x1751+2014Shirakawa
2,7603x23x2001+2014Shirakawa
3,1053x23x2251+2014Shirakawa
3,4503x23x2501+2014Shirakawa
3,7953x23x2751+2014Shirakawa
4,3203x24x3001+2014Shirakawa
9453x25x631+2014Shirakawa
1,1103x25x741+2014Shirakawa
4x[4-9]xNs:02013Shirakawa
4x10x[10-45]02013Shirakawa
4004x10x502 prime2014Shirakawa
4404x10x551+ prime2014Shirakawa
4804x10x601+ prime2014Shirakawa
5204x10x651+ prime2014Shirakawa
5604x10x701+ prime2014Shirakawa
6004x10x751+ prime2014Shirakawa
6404x10x801+ prime2014Shirakawa
6804x10x851+ prime2014Shirakawa
7204x10x901+ prime2014Shirakawa
7604x10x951+ prime2014Shirakawa
4x10xNs:02013Shirakawa
4x11x2502013Shirakawa
4404x11x501+ prime2014Shirakawa
4x11xNs:02013Shirakawa
4804x12x501+2013Shirakawa
7204x12x751+2013Shirakawa
5204x13x501+2013Shirakawa
7804x13x751+2013Shirakawa
2804x14x251+ prime2013Shirakawa
3604x15x301+2013Shirakawa
4204x15x351+2013Shirakawa
4804x15x401+2013Shirakawa
5404x15x451+2013Shirakawa
6004x15x501+2013Shirakawa
6604x15x551+2013Shirakawa
3204x16x251+ prime2013Shirakawa
3404x17x251+ prime2013Shirakawa
3604x18x251+ prime2013Shirakawa
3804x19x251+ prime2013Shirakawa
3204x20x201+ prime2013Shirakawa
4004x20x251+ prime2013Shirakawa
4804x20x301+2013Shirakawa
5604x20x351+2013Shirakawa
4204x21x251+ prime2014Shirakawa
4404x22x251+ prime2014Shirakawa
4804x24x251+2015Shirakawa
5004x25x251+2015Shirakawa
5204x25x261+2015Shirakawa
5x[5-7]xNs:02013Shirakawa
5x8x1002013Shirakawa
5x8x1502013Shirakawa
1605x8x2010 prime2013Shirakawa
5x8x2502013Shirakawa
5x8x3002013Shirakawa
2805x8x351+ prime2014Shirakawa
3605x8x451+ prime2014Shirakawa
4005x8x501+ prime2014Shirakawa
5x8xNs:02013Shirakawa
5x9x1002013Shirakawa
1355x9x152 prime2014Shirakawa
5x9x2002013Shirakawa
2255x9x251+ prime2014Shirakawa
3155x9x351+ prime2014Shirakawa
5x9xNs:02013Shirakawa
5x10x[10-18]02013Shirakawa
3305x10x331+ prime2013Shirakawa
3605x10x361+ prime2013Shirakawa
3705x10x371+ prime2013Shirakawa
3905x10x391+2013Shirakawa
4005x10x401+2013Shirakawa
4105x10x411+2013Shirakawa
4205x10x421+2013Shirakawa
4305x10x431+2013Shirakawa
4405x10x441+2013Shirakawa
4505x10x451+2013Shirakawa
4605x10x461+2013Shirakawa
4705x10x471+2013Shirakawa
4805x10x481+2013Shirakawa
4905x10x491+2013Shirakawa
5005x10x501+2013Shirakawa
5105x10x511+2013Shirakawa
5205x10x521+2013Shirakawa
5305x10x531+2013Shirakawa
5405x10x541+2013Shirakawa
5505x10x551+2013Shirakawa
5605x10x561+2013Shirakawa
5705x10x571+2013Shirakawa
5805x10x581+2013Shirakawa
5905x10x591+2013Shirakawa
6005x10x601+2013Shirakawa
6105x10x611+2013Shirakawa
6205x10x621+2013Shirakawa
6305x10x631+2013Shirakawa
6405x10x641+2013Shirakawa
6505x10x651+2013Shirakawa
6705x10x671+2013Shirakawa
6805x10x681+2013Shirakawa
7105x10x711+2013Shirakawa
4405x11x401+2013Shirakawa
6605x11x601+2013Shirakawa
7155x11x651+2014Shirakawa
7705x11x701+2013Shirakawa
8255x11x751+2014Shirakawa
9355x11x851+2014Shirakawa
9905x11x901+2013Shirakawa
1,0455x11x951+2014Shirakawa
2405x12x201+ prime2013Shirakawa
3005x12x251+ prime2013Shirakawa
3605x12x301+2013Shirakawa
4205x12x351+2013Shirakawa
3255x13x251+ prime2013Shirakawa
3905x13x301+2013Shirakawa
4555x13x351+2014Shirakawa
5205x13x401+2013Shirakawa
5855x13x451+2014Shirakawa
2805x14x201+ prime2013Shirakawa
3505x14x251+ prime2013Shirakawa
4205x14x301+2013Shirakawa
4905x14x351+2013Shirakawa
2555x15x171+ prime2014Shirakawa
2855x15x191+ prime2014Shirakawa
3005x15x201+2014Shirakawa
3155x15x211+2014Shirakawa
3305x15x221+2013Shirakawa
3455x15x231+2014Shirakawa
3605x15x241+2013Shirakawa
3755x15x251+2014Shirakawa
4005x16x251+ prime2014Shirakawa
4805x16x301+2014Shirakawa
3405x17x201+ prime2014Shirakawa
1806x6x251+ prime1997Shindo
2106x7x251+ prime2014Shirakawa
2406x8x251+ prime2013Shirakawa
2706x9x251+ prime2013Shirakawa
1206x10x1011+ prime minimal1997Shindo
1806x10x151+ prime2013Shirakawa
3306x11x251+ prime2013Shirakawa
2706x15x151+ prime2014Shirakawa
7x7xNs:02013Shirakawa
2807x8x251+ prime2013Shirakawa
3157x9x251+ prime2013Shirakawa
1407x10x101+ prime2013Shirakawa
2107x10x151+ prime2013Shirakawa
3857x11x251+ prime2013Shirakawa
3208x8x251+ prime2013Shirakawa
3608x9x251+ prime2013Shirakawa
1608x10x101+ prime2013Shirakawa
2408x10x151+ prime2013Shirakawa
3608x15x151+ prime2014Shirakawa
1809x10x101+ prime2013Shirakawa
20010x10x101+ prime2013Shirakawa
22010x10x111+ prime2013Shirakawa
"""

WHO = r"(Shirakawa|Shindo|Sillke|Postl|Hamlyn|Beeler|G[oö]bel)"
SIZE_RE = re.compile(r"\d+x\d+x(?:\d+|\[[^\]]+\])")
COUNT_TOKENS = ("s:0", "11+", "1+", "10", "2", "0")   # longest-first
_TAIL_RE = re.compile(r"(\d+)$")
_YEAR_WHO_RE = re.compile(rf"^(?:\s?(prime minimal|prime))?(\d{{4}}){WHO}$")


def parse_page3d(text):
    """Parse flattened rows. Returns (box_rows, family_rows).

    Each box row: <pieces?><size><count><marker?><year><who>, all concatenated.
    The pieces/size/count digit boundary is ambiguous in flattened text, so
    every (left, size, tail-trim) split is tried and the unique split with
    volume == 5*pieces wins (for rows carrying a piece count).
    """
    box_rows, family_rows = [], []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parsed = None
        for start in range(len(line)):
            if not line[start].isdigit():
                continue
            m = SIZE_RE.match(line, start)
            if not m:
                continue
            left = line[:start]
            if left and not re.fullmatch(r"[\d,]+", left):
                continue
            pieces = int(left.replace(",", "")) if left else None
            size_raw = m.group(0)
            tm = _TAIL_RE.search(size_raw)
            tail_digits = tm.group(1) if tm else ""
            for k in range(0, len(tail_digits) + 1):
                size_str = size_raw[:len(size_raw) - k]
                trimmed = tail_digits[len(tail_digits) - k:]
                try:
                    a, b, c = map(int, size_str.split("x"))
                except ValueError:
                    continue
                if not (a <= b <= c):
                    continue          # every Z page row is sorted ascending
                if pieces is not None and a * b * c != 5 * pieces:
                    continue
                if pieces is None and not trimmed:
                    # no piece count and nothing trimmed -> only the count
                    # token itself can follow; handled below naturally.
                    pass
                remainder = trimmed + line[m.end():] if k else line[m.end():]
                for ctok in COUNT_TOKENS:
                    if not remainder.startswith(ctok):
                        continue
                    after = remainder[len(ctok):]
                    ym = _YEAR_WHO_RE.match(after)
                    if not ym:
                        continue
                    parsed = {
                        "pieces": pieces, "dims": (a, b, c), "count": ctok,
                        "marker": (ym.group(1) or "").strip(),
                        "year": int(ym.group(2)), "who": ym.group(3),
                        "row": line,
                    }
                    break
                if parsed:
                    break
            if parsed:
                break
                if parsed:
                    break
            if parsed:
                break
        if parsed:
            if parsed["pieces"] is not None:
                assert parsed["dims"][0] * parsed["dims"][1] * parsed["dims"][2] \
                    == 5 * parsed["pieces"], parsed
            box_rows.append(parsed)
            continue
        m = re.match(rf"^(\S+?)(s:0|0)20(\d{{2}}){WHO}$", line)
        if m:
            family_rows.append({"size_class": m.group(1), "sols": m.group(2),
                                "year": int("20" + m.group(3)),
                                "who": m.group(4)})
            continue
        raise AssertionError(f"unparsed 3D row: {line!r}")
    return box_rows, family_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    # ------------------------------------------------------------------
    # 1. Parse the page; split rows into primes / composites / zero rows.
    # ------------------------------------------------------------------
    solvable_rows, family_rows = parse_page3d(PAGE_3D_TEXT)
    prime_rows = [r for r in solvable_rows if "prime" in r["marker"]]
    composite_rows = [r for r in solvable_rows
                      if "prime" not in r["marker"]
                      and r["count"] in {"1+", "11+"}]
    zero_rows = [r for r in solvable_rows
                 if "prime" not in r["marker"]
                 and r["count"] not in {"1+", "11+"}]
    print(f"parsed 3D rows: {len(prime_rows)} prime-marked, "
          f"{len(composite_rows)} published composites (count 1+/11+), "
          f"{len(zero_rows)} explicit zero-box rows, "
          f"{len(family_rows)} family/zero rows")
    page_nonprime = {Box(*r["dims"]).canonical(): r for r in composite_rows}
    page_prime = {Box(*r["dims"]).canonical(): r for r in prime_rows}

    # -------------------------------------------------------------------
    # 6a. conflict: page primes vs RAW_PRIMES (both directions)
    # -------------------------------------------------------------------
    conflicts = {
        "page_prime_not_in_RAW_PRIMES": sorted(
            str(b) for b in set(page_prime) - Z_CATALOGUE.primes),
        "RAW_PRIMES_not_marked_prime_on_page": sorted(
            str(b) for b in Z_CATALOGUE.primes - set(page_prime)),
        "page_nonprime_overlaps_RAW_PRIMES": sorted(
            str(b) for b in set(page_nonprime) & Z_CATALOGUE.primes),
        "page_nonprime_inside_impossible_rules": sorted(
            str(b) for b in set(page_nonprime)
            if Z_CATALOGUE.impossible_reason(b) is not None),
    }

# -------------------------------------------------------------------
    # Evidence catalogue (runtime copy only) from parsed page rows.
    # -------------------------------------------------------------------
    EV = dataclasses.replace(
        Z_CATALOGUE,
        published_solutions=Z_CATALOGUE.published_solutions | set(page_nonprime),
    )
    assert EV.impossible_reason(Box(3, 10, 10)) == "published_impossible"

    # the recorded 102 (from the committed test fixture) + all direct rows
    from test_z_frontier_closures import NEWLY_CLOSED_DIMS
    boxes_needed = {Box(*d) for d in NEWLY_CLOSED_DIMS} | set(page_nonprime)

    # baseline pass (current truth tables)
    decomp.catalogue = Z_CATALOGUE
    decomp.classify.cache_clear()
    baseline_cls = {bx: decomp.classify(bx).__class__.__name__
                    for bx in sorted(boxes_needed)}
    # evidence pass
    decomp.catalogue = EV
    decomp.classify.cache_clear()
    ev_cls = {bx: decomp.classify(bx) for bx in sorted(boxes_needed)}

    replayed, broken = [], []
    for bx in sorted(boxes_needed):
        node = ev_cls[bx]
        t = node.__class__.__name__
        closes = decomp.closes(node)
        ok_tree = True
        if t not in ("Impossible", "Unknown"):
            ok_tree = validate(node)
        if not closes or not ok_tree:
            broken.append((str(bx), t, closes, ok_tree))
        leaf_kinds = set()
        _collect_leaves(node, leaf_kinds)
        has_pub = "PublishedSolution" in leaf_kinds
        was_unknown = baseline_cls[bx] == "Unknown"
        if t == "PublishedSolution":
            path = "A"
        elif not was_unknown:
            path = "C"          # already closed before page evidence (primes only)
        elif has_pub:
            path = "B"          # decomposition whose proof uses published rows
        else:
            path = "D"
        replayed.append({
            "box": str(bx), "type": t, "closes": closes, "valid": ok_tree,
            "baseline": baseline_cls[bx], "path": path,
            "leaves": sorted(leaf_kinds),
        })

    closed_now = [r for r in replayed if r["closes"]]
    newly = [r for r in closed_now if r["baseline"] == "Unknown"]
    print(f"\nreplayed {len(replayed)} recorded boxes: closes={len(closed_now)}, "
          f"newly-closed-vs-baseline={len(newly)}, broken={len(broken)}")
    if broken:
        print("BROKEN TREES (STOP condition):")
        for b in broken:
            print("   ", b)

    from collections import Counter
    print("evidence paths:", dict(Counter(r["path"] for r in newly)))

    breadth = [r for r in newly if ev_cls[Box._from_str(r["box"])]
               .__class__.__name__ == "Breadth"] if hasattr(Box, "_from_str") else []
    breadth = [r for r in newly
               if ev_cls[Box(*map(int, r["box"].split("x")))].__class__.__name__
               == "Breadth"]
    print(f"\nBreadth closures ({len(breadth)}):")
    for r in breadth:
        print(f"   {r['box']}  path={r['path']} valid={r['valid']}")

    # published rows inside/outside the replay window
    inside = [r for r in composite_rows
              if max(r["dims"]) <= 60]
    print(f"\npublished rows within dims<=60 window: {len(inside)} "
          f"(outside: {len(composite_rows) - len(inside)})")

    if args.json:
        payload = {
            "page_rows": {"prime": len(prime_rows),
                          "nonprime": len(composite_rows),
                          "family_zero": len(family_rows)},
            "nonprime_rows": [
                {**r, "dims": list(r["dims"])} for r in composite_rows],
            "conflicts": conflicts,
            "replay": replayed,
            "breadth": breadth,
            "broken": broken,
        }
        Path(args.json).write_text(json.dumps(payload, indent=1))
        print(f"wrote {args.json}")
    return 1 if broken else 0


def _collect_leaves(node, out):
    name = node.__class__.__name__
    if name in ("Prime", "PublishedSolution", "Unknown", "Impossible"):
        out.add(name)
        return
    if name == "Generator":
        for p in node.parts:
            _collect_leaves(p, out)
        return
    _collect_leaves(node.left, out)
    _collect_leaves(node.right, out)


if __name__ == "__main__":
    sys.exit(main())