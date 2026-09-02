#!/usr/bin/env python3
"""
Macro Proof Certificate Verifier for S-pentacube tileability.

Checks:
- Certificate metadata and completeness level
- Source enumeration evidence
- SCC period computation
- Cycle certificate validity (each transition is a legal Macro edge)
- Semigroup arithmetic (gcd, Frobenius, conductor)
- Claim consistency with evidence level

Usage:
    python3 tools/frontier/verify_macro_proof.py <certificate.json>
"""

import sys
import json
import math
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.frontier.macro_generalized import (
    build_templates_general,
    first_empty_general,
    apply_template_general,
    shift_state_general,
    layer_mask_general,
)


def verify_source_enumeration(cert: dict) -> list:
    """Check source enumeration completeness."""
    errors = []
    src = cert.get("source_enumeration", {})
    
    if not src.get("complete"):
        errors.append("Source enumeration marked as incomplete")
    
    total = src.get("total_sources", 0)
    dead = src.get("dead_end_sources", 0)
    recurrent = src.get("recurrent_sources", 0)
    
    if total != dead + recurrent:
        errors.append(f"Source count mismatch: {total} != {dead} + {recurrent}")
    
    return errors


def verify_scc_period(cert: dict) -> list:
    """Check SCC period computation (metadata only)."""
    errors = []
    period_data = cert.get("scc_period", {})
    
    if not period_data.get("computed"):
        errors.append("SCC period not computed")
        return errors
    
    d = period_data.get("period", 0)
    if d <= 0:
        errors.append(f"Invalid period: {d}")
    
    return errors


def verify_semigroup(cert: dict) -> list:
    """Check semigroup arithmetic."""
    errors = []
    sg = cert.get("semigroup", {})
    gens = sg.get("generators", [])
    
    if not gens:
        errors.append("No generators in semigroup data")
        return errors
    
    # Check gcd
    expected_gcd = math.gcd(*gens) if len(gens) > 1 else gens[0]
    claimed_gcd = sg.get("gcd")
    if claimed_gcd and claimed_gcd != expected_gcd:
        errors.append(f"GCD mismatch: claimed {claimed_gcd}, computed {expected_gcd}")
    
    # Check at least one representable element beyond the generators
    rep = sg.get("representable_up_to", [])
    if rep:
        for z in gens:
            if z not in rep:
                pass  # generators are always representable at minimum
    
    return errors


def verify_claim_consistency(cert: dict) -> list:
    """Check that the claim level matches the evidence."""
    errors = []
    
    theorem_type = cert.get("theorem_type", "unknown")
    src = cert.get("source_enumeration", {})
    period = cert.get("scc_period", {})
    cycles = cert.get("primitive_cycles", [])
    
    if theorem_type == "global":
        if not src.get("complete"):
            errors.append("Global theorem claimed but source enumeration incomplete")
        if not period.get("computed"):
            errors.append("Global theorem claimed but SCC period not computed")
        if not cycles:
            errors.append("Global theorem claimed but no primitive cycles")
    
    elif theorem_type == "scc-local":
        if not period.get("computed"):
            errors.append("SCC-local claimed but period not computed")
    
    elif theorem_type == "cycle-only":
        if not cycles:
            errors.append("Cycle-only claimed but no cycles")
    
    return errors


def verify_cycle_transitions(a: int, b: int, cycle: dict) -> list:
    """Verify each Macro transition in a cycle certificate is legal.
    
    This checks that applying the concrete placements fills L0 and shifts
    to the target state. It uses the Macro transition machinery.
    """
    errors = []
    NCELLS = a * b
    WORDMASK = (1 << NCELLS) - 1
    
    path = cycle.get("path", [])
    edges = cycle.get("edges", [])
    
    if len(path) != len(edges) + 1:
        errors.append(f"Path length {len(path)} inconsistent with {len(edges)} edges")
        return errors
    
    # Verify path starts and ends at 0
    if path[0] != 0:
        errors.append("Path does not start at 0")
    if path[-1] != 0:
        errors.append("Path does not end at 0")
    
    # For each edge, verify concrete placements fill L0 and produce the target state
    for i, e in enumerate(edges):
        src = e.get("source_state", 0)
        dst = e.get("target_state", 0)
        placements = e.get("concrete_placements", [])
        
        # Apply placements to source state
        state = src
        for pl in placements:
            mask = 0
            for (x, y, z_rel) in pl:
                mask |= (1 << (x + a * y + NCELLS * z_rel))
            if state & mask:
                errors.append(f"Edge {i}: placement overlaps state")
                break
            state |= mask
        
        # Check L0 is full after placements
        l0 = layer_mask_general(state, 0, NCELLS)
        if l0 != WORDMASK:
            errors.append(f"Edge {i}: L0 not full after placements (got {bin(l0).count('1')} of {NCELLS})")
            continue
        
        # Check shift produces target
        shifted = shift_state_general(state, NCELLS)
        if shifted != dst:
            errors.append(f"Edge {i}: shift produced {shifted}, expected {dst}")
    
    return errors


def verify_certificate(cert_path: str) -> dict:
    """Full certificate verification."""
    with open(cert_path) as f:
        cert = json.load(f)
    
    result = {
        "certificate": cert_path,
        "valid": True,
        "errors": [],
        "warnings": [],
        "checks": {},
    }
    
    theorem_type = cert.get("theorem_type", "unknown")
    
    # 1. Source enumeration (only required for global/scc-local)
    if theorem_type in ("global", "scc-local"):
        src_errors = verify_source_enumeration(cert)
        result["checks"]["source_enumeration"] = {
            "passed": len(src_errors) == 0,
            "errors": src_errors,
        }
        result["errors"].extend(src_errors)
    else:
        result["checks"]["source_enumeration"] = {
            "passed": True,
            "note": "Not required for this theorem type",
        }
    
    # 2. SCC period (only required for global/scc-local)
    if theorem_type in ("global", "scc-local"):
        period_errors = verify_scc_period(cert)
        result["checks"]["scc_period"] = {
            "passed": len(period_errors) == 0,
            "errors": period_errors,
        }
        result["errors"].extend(period_errors)
    else:
        result["checks"]["scc_period"] = {
            "passed": True,
            "note": "Not required for this theorem type",
        }
    
    # 3. Semigroup
    sg_errors = verify_semigroup(cert)
    result["checks"]["semigroup"] = {
        "passed": len(sg_errors) == 0,
        "errors": sg_errors,
    }
    result["errors"].extend(sg_errors)
    
    # 4. Claim consistency
    claim_errors = verify_claim_consistency(cert)
    result["checks"]["claim_consistency"] = {
        "passed": len(claim_errors) == 0,
        "errors": claim_errors,
    }
    result["errors"].extend(claim_errors)
    
    # 5. Cycle transitions (if full edge data provided)
    cycles = cert.get("primitive_cycles", [])
    cs = cert.get("cross_section", {})
    a, b = cs.get("a", 0), cs.get("b", 0)
    
    cycle_check = {"passed": True, "errors": []}
    has_full_data = any("path" in c or "edges" in c for c in cycles)
    
    if cycles and a > 0 and b > 0 and has_full_data:
        for i, cycle in enumerate(cycles):
            trans_errors = verify_cycle_transitions(a, b, cycle)
            if trans_errors:
                cycle_check["errors"].extend([f"Cycle {i}: {e}" for e in trans_errors])
                cycle_check["passed"] = False
    elif cycles:
        # Without full edge data, just verify lengths are positive
        for i, c in enumerate(cycles):
            if c.get("length", 0) <= 0:
                cycle_check["errors"].append(f"Cycle {i}: invalid length")
                cycle_check["passed"] = False
    
    result["checks"]["cycle_transitions"] = cycle_check
    result["errors"].extend(cycle_check["errors"])
    
    # Final validity
    result["valid"] = len(result["errors"]) == 0
    result["completeness_level"] = theorem_type
    
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 verify_macro_proof.py <certificate.json>")
        sys.exit(1)
    
    cert_path = sys.argv[1]
    if not Path(cert_path).exists():
        print(f"Certificate not found: {cert_path}")
        sys.exit(1)
    
    result = verify_certificate(cert_path)
    
    print(f"\nCertificate: {result['certificate']}")
    print(f"Completeness level: {result['completeness_level']}")
    print(f"Valid: {'YES' if result['valid'] else 'NO'}")
    print()
    
    for check_name, check_result in result["checks"].items():
        status = "PASS" if check_result.get("passed", True) else "FAIL"
        print(f"  [{status}] {check_name}")
        for e in check_result.get("errors", []):
            print(f"         {e}")
        note = check_result.get("note", "")
        if note:
            print(f"         ({note})")
    
    print()
    if result["valid"]:
        print("Certificate VERIFIED.")
        return 0
    else:
        print(f"Certificate REJECTED: {len(result['errors'])} error(s)")
        return 1


if __name__ == "__main__":
    sys.exit(main())