#!/usr/bin/env python3
"""
Phase-10 certificate rejection tests for V.

Positive control: the honest 3×5×6 cycle certificate passes both the isolated
Layer-A generic checker and the claim verifier.
Negative controls: each mutation must be REJECTED —
  M1 moved fill cell            (Layer A: shift/legality)
  M2 flipped state bit          (Layer A: walk consistency)
  M3 duplicated placement       (Layer A: exact cover)
  M4 wrong piece geometry       (Layer A: congruence)
  M5 bare GLOBAL claim without evidence      (claim verifier)
  M6 GLOBAL claim asserting tileable z=10    (claim verifier: REFUTED by
     exact walk-length computation; 3×5×10 is published-impossible)

Usage: python3 tools/frontier/v_piece/test_v_certificate_rejection.py
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CERT = REPO_ROOT / "data/frontier/v_piece/v_3x5x6_macro_cycle_certificate.json"
CHECKER = REPO_ROOT / "tools/frontier/macro_certificate_generic_checker.py"
CLAIMVER = REPO_ROOT / "tools/frontier/v_piece/v_claim_verifier.py"
CLOSURE = REPO_ROOT / "data/frontier/v_piece/v_3x5_closure_analysis.json"
LENGTHS = REPO_ROOT / "data/frontier/v_piece/v_3x5_exact_walk_lengths.json"


def run_layer_a(path: Path) -> int:
    return subprocess.run(
        [sys.executable, "-I", str(CHECKER), str(path)],
        capture_output=True, text=True,
        cwd=tempfile.gettempdir(),
    ).returncode


def run_claims(path: Path, with_evidence: bool) -> tuple[int, str]:
    cmd = [sys.executable, str(CLAIMVER), str(path)]
    if with_evidence:
        cmd += ["--closure", str(CLOSURE), "--lengths", str(LENGTHS)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout


def main() -> int:
    doc = json.loads(CERT.read_text())
    tmp = Path(tempfile.mkdtemp(prefix="v_cert_tests_"))
    results: list[tuple[str, bool]] = []

    def mutate(name, fn):
        m = copy.deepcopy(doc)
        fn(m)
        p = tmp / f"{name}.json"
        p.write_text(json.dumps(m))
        return p

    # positive control
    rc, out = run_claims(CERT, True)
    results.append(("control: original passes claim verification", rc == 0))
    results.append(("control: original passes Layer A", run_layer_a(CERT) == 0))

    p = mutate("m1", lambda m: m["edge_fills"][0][0][0].__setitem__(0, m["edge_fills"][0][0][0][0] + 1))
    results.append(("M1 moved fill cell rejected by Layer A", run_layer_a(p) != 0))

    p = mutate("m2", lambda m: m["walk"][2].__setitem__("l0", m["walk"][2]["l0"] ^ 1))
    results.append(("M2 flipped state bit rejected by Layer A", run_layer_a(p) != 0))

    def dup(m):
        m["box_tiling"].append(copy.deepcopy(m["box_tiling"][0]))
    p = mutate("m3", dup)
    results.append(("M3 duplicated placement rejected by Layer A", run_layer_a(p) != 0))

    def wrong_geom(m):
        m["piece"]["geometry"] = [[0, 0, 0], [1, 0, 0], [2, 0, 0], [1, 1, 0], [1, 2, 0]]
    p = mutate("m4", wrong_geom)
    results.append(("M4 T-shaped geometry rejected by Layer A", run_layer_a(p) != 0))

    def bare_global(m):
        m["claims"] = [{"id": "X1", "status": "GLOBAL",
                        "statement": "the whole 3x5 family is classified"}]
    p = mutate("m5", bare_global)
    rc, out = run_claims(p, False)
    results.append(("M5 bare GLOBAL claim without evidence rejected",
                    rc != 0 and "[REJECT] GLOBAL overclaim" in out))

    def global_z10(m):
        m["claims"] = [{"id": "X2", "status": "GLOBAL",
                        "statement": "a 3x5x10 box is tileable",
                        "scope": {"box_family": {"a": 3, "b": 5},
                                  "asserts_tileable_z": [10]}}]
    p = mutate("m6", global_z10)
    rc, out = run_claims(p, True)
    results.append(("M6 tileability-of-10 claim REFUTED by exact lengths",
                    rc != 0 and "[REJECT]" in out and "REFUTED" in out))

    print("V certificate rejection tests")
    print("=" * 60)
    allok = True
    for name, passed in results:
        print(f"  {'✓' if passed else '✗'} {name}")
        allok &= passed
    print()
    print("ALL PASS" if allok else "FAILURES PRESENT")
    return 0 if allok else 1


if __name__ == "__main__":
    raise SystemExit(main())
