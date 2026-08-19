#!/usr/bin/env python3
"""
Enumerate the COMPLETE outgoing MacroState successors of state 0.

This script performs an uncap BFS from the empty frontier state (0),
collecting all post-shift states reachable by filling layer 0 and shifting.

The complete first-generation exploration contains 3,162,387 intermediate
states, so we use a cap of 4,000,000 to ensure completeness.

Output:
    - Complete succ[0]: <number> successors, <number> intermediate states
    - Is s* in succ[0]? <True/False>
    - first-generation source count = 331765
    - whether the computed successor count equals 331765
"""

from __future__ import annotations

import sys
import time
from collections import deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from solvers.s_z_frontier_packed import (
    WORD_MASK,
    apply_template,
    build_templates,
    first_empty,
    layer_mask,
    shift_state,
)

# The known first-generation source
S_STAR = 6163195513375031274

# Expected counts from previous runs
EXPECTED_INTERMEDIATE = 3_162_387
EXPECTED_SOURCES = 331_765

# Use a cap well above the known intermediate count
MAX_INTERMEDIATE = 4_000_000


def main() -> int:
    print("Building templates...", flush=True)
    t0 = time.perf_counter()
    templates, concrete_count = build_templates()
    total_templates = sum(len(v) for v in templates.values())
    t1 = time.perf_counter()
    print(
        f"  concrete placements={concrete_count} "
        f"target templates={total_templates} ({t1 - t0:.2f}s)",
        flush=True,
    )

    print("\nEnumerating complete succ[0]...", flush=True)
    t2 = time.perf_counter()

    source = 0
    seen = {source}
    queue = deque([source])
    successors = set()

    while queue:
        state = queue.popleft()

        if layer_mask(state, 0) == WORD_MASK:
            successors.add(shift_state(state))
            continue

        target = first_empty(layer_mask(state, 0))

        for template in templates[target]:
            nxt = apply_template(state, template)
            if nxt is not None and nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)

    t3 = time.perf_counter()

    intermediate_count = len(seen) - 1  # exclude the source state itself
    successor_count = len(successors)

    print(f"\nComplete succ[0]: {successor_count} successors, {intermediate_count} intermediate states")
    print(f"Is s* in succ[0]? {S_STAR in successors}")
    print(f"\nfirst-generation source count = {EXPECTED_SOURCES}")
    print(f"computed successor count = {successor_count}")
    print(f"counts match? {successor_count == EXPECTED_SOURCES}")

    print(f"\nElapsed: {t3 - t2:.2f}s")

    # Verification
    if intermediate_count != EXPECTED_INTERMEDIATE:
        print(f"\nWARNING: intermediate count {intermediate_count} != expected {EXPECTED_INTERMEDIATE}")

    if successor_count != EXPECTED_SOURCES:
        print(f"\nWARNING: successor count {successor_count} != expected {EXPECTED_SOURCES}")

    if len(seen) > MAX_INTERMEDIATE:
        print(f"\nWARNING: exceeded MAX_INTERMEDIATE cap of {MAX_INTERMEDIATE}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
