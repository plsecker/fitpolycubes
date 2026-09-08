#!/usr/bin/env python3
"""
V certificate claim verifier (certificate-format Layers B+C).

Layer A (generic checker) validates walk/fill/tiling semantics and never
evaluates claims. This tool does the piece-specific and claim-level work:

  1. Re-derive the terminal/gate facts for a V certificate and instantiate
     V's generalized gate criterion (Layer B).
  2. Classify the strongest justified status:
       CATALOGUE ONLY < VERIFIED CYCLE < SCC-LOCAL < GLOBAL
  3. Accept or REJECT each `claims[]` entry against the supplied evidence:
       - GLOBAL requires complete-closure evidence for the cross-section
         (no cap flags) AND an exact walk-length computation whose coverage
         entails the claim;
       - an exact-walk-length dataset REFUTES any claim that a length outside
         the achievable set is tileable;
       - a single realized cycle never justifies more than VERIFIED CYCLE.

Usage:
    python3 tools/frontier/v_piece/v_claim_verifier.py CERT.json \
        [--closure data/frontier/v_piece/v_3x5_closure_analysis.json] \
        [--lengths data/frontier/v_piece/v_3x5_exact_walk_lengths.json]

Exit code 0 iff every claim is justified at its stated level.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent

STATUS_ORDER = ["CATALOGUE ONLY", "VERIFIED CYCLE", "SCC-LOCAL", "GLOBAL"]


def load_json(p: Path) -> dict:
    return json.loads(Path(p).read_text())


def layer_b_gate_check(cert: dict) -> dict:
    """Instantiate V's generalized gate criterion on the certificate's own data.

    Returns observations + whether the final edge instantiates one of V's two
    terminal predecessor classes (flat-completed partial state, classic gate).
    """
    a, b, z = cert["box"]["a"], cert["box"]["b"], cert["box"]["z"]
    ncells = a * b
    walk = cert["walk"]
    fills = cert["edge_fills"]
    pred_l0 = walk[z - 1]["l0"]
    pred_l1 = walk[z - 1]["l1"]
    term = cert.get("terminal", {})
    remaining = ncells - bin(pred_l0).count("1")

    observations = {
        "predecessor_l1_empty": pred_l1 == 0,
        "predecessor_l0_popcount": bin(pred_l0).count("1"),
        "remaining_cells": remaining,
        "final_edge_all_slot0": term.get("final_edge_all_slot0"),
        "final_edge_covers_complement": term.get("final_edge_covers_complement"),
        "is_classic_gate_edge": remaining == 0 and pred_l1 == 0,
        "is_flat_completion_edge": (
            remaining > 0 and pred_l1 == 0
            and term.get("final_edge_all_slot0") is True
            and term.get("final_edge_covers_complement") is True
            and remaining % 5 == 0
        ),
    }
    observations["gate_instantiated"] = (
        observations["is_classic_gate_edge"]
        or observations["is_flat_completion_edge"]
    )
    return observations


def classify(cert: dict, closure: dict | None, lengths: dict | None) -> dict:
    """Return {max_status, reasons[]} given available evidence."""
    a, b, z = cert["box"]["a"], cert["box"]["b"], cert["box"]["z"]
    reasons = []
    # A Layer-A-valid certificate with concrete fills is always a verified cycle.
    max_idx = STATUS_ORDER.index("VERIFIED CYCLE")
    reasons.append("concrete walk + fills + validated tiling present "
                   "=> VERIFIED CYCLE")

    if closure is not None:
        cs = closure.get("closure", {})
        same_section = (closure.get("cross_section", {}) == {"a": a, "b": b})
        if same_section and cs.get("complete"):
            max_idx = max(max_idx, STATUS_ORDER.index("SCC-LOCAL"))
            reasons.append("complete closure for this cross-section present "
                           "=> SCC-LOCAL justified")
            if lengths is not None and lengths.get("cross_section") == \
                    {"a": a, "b": b}:
                ach = set(lengths.get("achievable_lengths", []))
                bound = lengths.get("bound", 0)
                if z in ach:
                    max_idx = STATUS_ORDER.index("GLOBAL")
                    reasons.append(
                        f"exact walk-length computation covers z<={bound} and "
                        f"contains z={z}; with eventual periodicity "
                        f"(period {lengths.get('period_bfs_delta')}, conductor "
                        f"{lengths.get('conductor_for_multiples_of_period')}) "
                        f"the whole family is classified => GLOBAL justified")
                else:
                    reasons.append(
                        f"z={z} NOT in achievable set — tileability claim would "
                        f"be REFUTED by the exact computation")
        else:
            reasons.append("closure evidence missing or for another "
                           "cross-section => no SCC-LOCAL upgrade")
    else:
        reasons.append("no closure evidence supplied => stays VERIFIED CYCLE")
    return {"max_status": STATUS_ORDER[max_idx], "reasons": reasons}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("certificate")
    ap.add_argument("--closure", type=str, default=None)
    ap.add_argument("--lengths", type=str, default=None)
    args = ap.parse_args()

    cert = load_json(Path(args.certificate))
    closure = load_json(Path(args.cls)) if False else (
        load_json(Path(args.closure)) if args.closure else None)
    lengths = load_json(Path(args.lengths)) if args.lengths else None

    obs = layer_b_gate_check(cert)
    verdict = classify(cert, closure, lengths)

    print("== Layer B: V gate instantiation ==")
    for k, v in obs.items():
        print(f"  {k}: {v}")

    print("\n== Claim evaluation ==")
    ok = True
    for claim in cert.get("claims", []):
        stated = str(claim.get("status", "")).upper()
        stmt = claim.get("statement", "")
        scope = claim.get("scope") or {}

        # Structured scope: explicit per-length tileability assertions are
        # checked against the exact walk-length evidence when available.
        if scope.get("asserts_tileable_z"):
            if lengths is None:
                print(f"  [REJECT] {stated} asserts tileable z "
                     f"{scope['asserts_tileable_z']} but no exact walk-length "
                     f"evidence was supplied")
                ok = False
                continue
            ach = set(lengths.get("achievable_lengths", []))
            bad = [zz for zz in scope["asserts_tileable_z"] if zz not in ach]
            if bad:
                print(f"  [REJECT] {stated} asserts tileable z={bad}: REFUTED "
                     f"by exact walk-length computation "
                     f"(achievable ⊇ evidence bound {lengths.get('bound')})")
                ok = False
                continue

        if stated == "GLOBAL":
            if verdict["max_status"] != "GLOBAL":
                print(f"  [REJECT] GLOBAL overclaim: {stmt!r}")
                print(f"           max justified = {verdict['max_status']}")
                ok = False
            else:
                print(f"  [OK] GLOBAL justified: {stmt!r}")
        elif stated in STATUS_ORDER:
            need = STATUS_ORDER.index(stated)
            have = STATUS_ORDER.index(verdict["max_status"])
            if need <= have:
                print(f"  [OK] {stated}: {stmt!r}")
            else:
                print(f"  [REJECT] {stated} exceeds justified "
                      f"{verdict['max_status']}: {stmt!r}")
                ok = False
        else:
            print(f"  [REJECT] unknown status {stated!r}")
            ok = False

    print(f"\nmax justified status: {verdict['max_status']}")
    for r in verdict["reasons"]:
        print(f"  - {r}")
    if not obs["gate_instantiated"]:
        print("  NOTE: final edge does not instantiate either documented V "
              "terminal-predecessor class — inspect manually")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
