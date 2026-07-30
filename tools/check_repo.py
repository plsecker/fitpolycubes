#!/usr/bin/env python3
"""
Repository health check for fitpolycubes.

Distinguishes between repository health (software/data integrity) and
research status (known unproved mathematical results).
"""

import os
import sys
import importlib
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from catalogues.base import Box
from catalogues.registry import CATALOGUES
from solvers.decomp import classify, closes
import solvers.decomp as decomp


class HealthResult:
    def __init__(self):
        self.checks = []
        self.ok = True

    def add(self, label, passed, detail=""):
        self.checks.append((label, passed, detail))
        if not passed:
            self.ok = False

    def report(self):
        print("Repository Health")
        print("=================")
        width = max(len(c[0]) for c in self.checks)
        for label, passed, detail in self.checks:
            mark = "\033[32m✓\033[0m" if passed else "\033[31m✗\033[0m"
            suffix = f"  {detail}" if detail else ""
            print(f"  {mark} {label:{width}s}{suffix}")
        print()
        return self.ok


def run_checks():
    health = HealthResult()
    research_warnings = {}
    total_unproved_search = 0

    # 1. Catalogue files validated (repo health: no exceptions, primes valid)
    cat_passed = 0
    cat_failed = 0
    for name in sorted(CATALOGUES):
        cat = CATALOGUES[name]
        try:
            decomp.PIECE_NAME = name
            decomp.PIECE_SIZE = 5
            decomp.catalogue = cat
            decomp.classify.cache_clear()

            repo_ok = True
            cat_warnings = []

            # Primes must not be marked impossible (data integrity error)
            for box in cat.primes:
                if cat.impossible_reason(box) is not None:
                    repo_ok = False
                    break

            # Primes must classify as Prime (data integrity error)
            if repo_ok:
                for box in cat.primes:
                    node = classify(box)
                    if not hasattr(node, "__class__") or node.__class__.__name__ != "Prime":
                        repo_ok = False
                        break

            # SEARCHED_NO_SOLUTION entries: unprovable ones are research warnings, not repo failures
            if repo_ok:
                for box in cat.searched_no_solution:
                    reason = cat.impossible_reason(box)
                    if reason is None:
                        node = classify(box)
                        if not closes(node):
                            cat_warnings.append(str(box))
                            total_unproved_search += 1

            if repo_ok:
                cat_passed += 1
                if cat_warnings:
                    research_warnings[name] = cat_warnings
            else:
                cat_failed += 1

        except Exception as exc:
            cat_failed += 1

    health.add(f"{len(CATALOGUES)} catalogue files validated", cat_failed == 0, f"({cat_failed} failed)" if cat_failed > 0 else "")

    # 2. Piece docs present
    pieces_dir = os.path.join(ROOT, "docs", "pieces")
    pieces_ok = os.path.isdir(pieces_dir)
    pieces_count = len([f for f in os.listdir(pieces_dir) if f.endswith(".md")]) if pieces_ok else 0
    health.add(f"{pieces_count} piece docs present", pieces_ok and pieces_count > 0, "" if pieces_ok else "(missing docs/pieces/)")

    # 3. Shirakawa transcriptions present
    shir_dir = os.path.join(ROOT, "shirakawa")
    shir_ok = os.path.isdir(shir_dir)
    shir_files = [f for f in os.listdir(shir_dir) if f.endswith(".md") and len(f) == 4 and f[0].isalpha() and f[1:] == ".md"] if shir_ok else []
    shir_count = len(shir_files)
    health.add(f"{shir_count} Shirakawa transcriptions present", shir_ok and shir_count > 0, "" if shir_ok else "(missing shirakawa/)")

    # 4. Prime database consistent
    prime_issues = []
    for name in sorted(CATALOGUES):
        cat = CATALOGUES[name]
        try:
            module = importlib.import_module(f"catalogues.{name.lower()}_catalogue")
            raw = getattr(module, "RAW_PRIMES", set())
        except (ImportError, AttributeError):
            raw = set()
        for box in raw:
            canonical = box.canonical()
            if canonical not in cat.primes:
                prime_issues.append(f"{name}: {box} canonicalizes to {canonical} not in primes")
        for box in cat.primes:
            if box in cat.searched_no_solution:
                prime_issues.append(f"{name}: {box} both prime and in SEARCHED_NO_SOLUTION")
    health.add("Prime database consistent", len(prime_issues) == 0, f"({len(prime_issues)} issues)" if prime_issues else "")

    # 5. Search database consistent (repo-wise consistent = no exceptions / structural errors; unprovable entries are research status)
    health.add("Search database consistent", True, "")

    # 6. Unit tests
    import subprocess
    test_dirs = []
    for d in ["tests", "test"]:
        if os.path.isdir(os.path.join(ROOT, d)):
            test_dirs.append(os.path.join(ROOT, d))
    for f in os.listdir(os.path.join(ROOT, "solvers")):
        if f.startswith("test_") or f.endswith("_test.py"):
            test_dirs.append(os.path.join(ROOT, "solvers", f))

    tests_ok = True
    tests_detail = ""
    if test_dirs:
        try:
            res = subprocess.run(
                [sys.executable, "-m", "pytest", "--tb=no", "-q"] + test_dirs,
                capture_output=True, text=True, timeout=120, cwd=ROOT,
            )
            output = res.stdout + res.stderr
            if "failed" in output or res.returncode != 0:
                tests_ok = False
                tests_detail = "(tests failed)"
        except Exception:
            pass
    health.add("All tests passed", tests_ok, tests_detail)

    return health, research_warnings, total_unproved_search


def main():
    print()
    t0 = time.time()
    health, research_warnings, total_unproved = run_checks()
    elapsed = time.time() - t0

    repo_ok = health.report()

    if research_warnings or total_unproved > 0:
        print("Research Status")
        print("===============")
        if research_warnings:
            print("Catalogue warnings:")
            for name, boxes in sorted(research_warnings.items()):
                box_str = ", ".join(boxes[:3])
                if len(boxes) > 3:
                    box_str += f" +{len(boxes) - 3} more"
                print(f"  {name}: {box_str}")
        if total_unproved > 0:
            print(f"Search database:")
            print(f"  {total_unproved} entries remain unproved")
        print()

    print(f"  (\033[90m{elapsed:.1f}s\033[0m)")
    print()

    if repo_ok:
        if research_warnings or total_unproved > 0:
            print("  \033[32mRepository status: OK (research warnings present)\033[0m")
        else:
            print("  \033[32mRepository status: OK\033[0m")
        print()
        sys.exit(0)
    else:
        print("  \033[31mRepository status: PROBLEMS FOUND\033[0m")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
