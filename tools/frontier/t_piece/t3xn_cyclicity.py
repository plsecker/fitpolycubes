#!/usr/bin/env python3
"""
T 3xN Cyclicity Analysis Tool.

Determines whether the T-pentacube Macro graph is cyclic for a given 3xN
cross-section, using the exact algorithm:

    first-gen BFS -> terminal profiles -> arithmetic check -> 9-state flat-T automaton
"""

from __future__ import annotations
import argparse
import json
import sys
import time
from collections import deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.registry import PENTACUBES
from tools.frontier.piece_utils import (
    build_templates, layer_mask, first_empty, apply_template, shift_state
)

T_COL_MASKS = [
    (0b111, 0b010, 0b010),
    (0b100, 0b111, 0b100),
    (0b001, 0b111, 0b001),
    (0b010, 0b010, 0b111),
]


def flat_t_tileable(E_cols):
    """Check if a 3xN subset E is tileable by flat T orientations.
    Uses the 9-state automaton (verified exact against 512-state DP)."""
    N = len(E_cols)
    reachable = {0}
    for y in range(N):
        t0 = E_cols[y]
        t1 = E_cols[y + 1] if y + 1 < N else 0
        t2 = E_cols[y + 2] if y + 2 < N else 0
        is_last = (y >= N - 1)
        new_reachable = set()
        for state in reachable:
            already = state & 0b111
            remaining = t0 & ~already
            if remaining == 0:
                new_reachable.add(state >> 3)
                continue
            first = (remaining & -remaining).bit_length() - 1
            for c0, c1, c2 in T_COL_MASKS:
                if not (c0 & (1 << first)):
                    continue
                if c0 & ~t0 or c0 & already:
                    continue
                if is_last:
                    if c1 or c2:
                        continue
                else:
                    if c1 & ~t1 or c2 & ~t2:
                        continue
                    if c1 & (state >> 3):
                        continue
                if (t0 & ~(already | c0)):
                    continue
                if is_last:
                    new_reachable.add(0)
                else:
                    new_reachable.add((state >> 3) | c1 | (c2 << 3))
        reachable = new_reachable
        if not reachable:
            return False
    return 0 in reachable


def check_cyclicity(N, max_states=5000000, verbose=False):
    """Check if T 3xN is cyclic."""
    a, b = 3, N
    NCELLS = a * b
    full_mask = (1 << NCELLS) - 1

    t0 = time.time()
    templates, _, WORD_MASK, _, _ = build_templates(PENTACUBES['T'], a, b)

    seen = {0}
    queue = deque([0])
    terminal_profiles = []

    while queue and len(seen) < max_states:
        state = queue.popleft()

        if layer_mask(state, 0, NCELLS) == WORD_MASK:
            shifted = shift_state(state, NCELLS)
            if shifted not in seen:
                seen.add(shifted)
                queue.append(shifted)
            continue

        if (layer_mask(state, 1, NCELLS) == 0 and
            layer_mask(state, 2, NCELLS) == 0 and
            state != 0):
            l0 = layer_mask(state, 0, NCELLS)
            l0_count = bin(l0).count('1')
            remaining = NCELLS - l0_count
            viable = (remaining % 5 == 0 and remaining > 0)
            if viable:
                e_mask = full_mask & ~l0
                E_cols = [
                    sum((1 << x) for x in range(3) if e_mask & (1 << (x + 3 * y)))
                    for y in range(N)
                ]
                tileable = flat_t_tileable(E_cols)
            else:
                tileable = False
            terminal_profiles.append({
                'l0_count': l0_count,
                'remaining': remaining,
                'viable': viable,
                'tileable': tileable,
                'l0_mask': int(l0),
            })

        target = first_empty(layer_mask(state, 0, NCELLS), NCELLS)
        for template in templates[target]:
            nxt = apply_template(state, template)
            if nxt is None or nxt in seen:
                continue
            seen.add(nxt)
            queue.append(nxt)

    elapsed = time.time() - t0
    queue_empty = len(queue) == 0
    cap_hit = len(seen) >= max_states

    viable = [p for p in terminal_profiles if p['viable']]
    tileable = [p for p in terminal_profiles if p['viable'] and p['tileable']]

    cyclic = len(tileable) > 0
    completeness = 'COMPLETE' if queue_empty else 'BOUNDED'

    return {
        'N': N,
        'cyclic': cyclic,
        'states_explored': len(seen),
        'terminal_profiles': len(terminal_profiles),
        'viable_profiles': len(viable),
        'tileable_profiles': len(tileable),
        'completeness': completeness,
        'queue_empty': queue_empty,
        'cap_hit': cap_hit,
        'elapsed': elapsed,
        'viable_l0': sorted(set(p['l0_count'] for p in viable)),
        'tileable_l0': sorted(set(p['l0_count'] for p in tileable)),
    }


def main():
    parser = argparse.ArgumentParser(description='T 3xN Cyclicity Analysis Tool')
    parser.add_argument('--N', type=int, help='Cross-section width')
    parser.add_argument('--range', type=int, nargs=2, metavar=('START', 'END'),
                        help='Range of N to analyze')
    parser.add_argument('--max-states', type=int, default=5000000,
                        help='Maximum states to explore')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()

    if args.range:
        Ns = range(args.range[0], args.range[1] + 1)
    elif args.N:
        Ns = [args.N]
    else:
        parser.print_help()
        return 1

    results = []
    for N in Ns:
        result = check_cyclicity(N, max_states=args.max_states, verbose=args.verbose)
        results.append(result)

        status = 'CYCLIC' if result['cyclic'] else 'ACYCLIC'
        s = "  "
        print(f"3x{N:2d}: {status:8s}{s}states={result['states_explored']:8,}{s}"
              f"term={result['terminal_profiles']:3d}{s}"
              f"viable={result['viable_profiles']:2d}{s}"
              f"tileable={result['tileable_profiles']:2d}{s}"
              f"{result['completeness']:8s}{s}{result['elapsed']:.3f}s")

    if args.json:
        print(json.dumps(results, indent=2))

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
