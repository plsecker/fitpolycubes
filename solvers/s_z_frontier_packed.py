#!/usr/bin/env python3
"""
Packed z-frontier / transfer-state explorer for S in 4x8.

State:
    one Python integer containing three 32-bit z-layer masks.

    bits   0..31   = layer 0
    bits  32..63   = layer 1
    bits  64..95   = layer 2

Layer 3 is not stored: no S placement template ever reaches rel = 3
(see docs/z_frontier_live_cells.md), so the fourth layer is always
zero and carries no information.

This is the same state model as s_z_frontier.py, but packed into one integer
to reduce Python tuple/set overhead.

The experiment:
  * discover reachable interior frontier states;
  * count duplicate/repeated states;
  * report branching and layer shifts;
  * optionally stop at a state cap.

Diagnostic mode (--diagnostics):
  * record, for each processed frontier state, its out-degree, whether
    the transition is a layer shift, and how many successors were
    already seen;
  * write the summary metrics, the first 100 duplicate-transition
    records, and the first 100 layer-shift records to a markdown file
    (no full per-state record is written).

Post-shift diagnostic mode (--postshift-diagnostics):
  * record EVERY layer-shift event (up to the state limit) as a
    (pre_shift_state, post_shift_state) pair, where
    post_shift_state = pre_shift_state >> 32: total shift events,
    unique pre-shift and post-shift state counts, and the complete
    per-event state list.  No ordinary frontier state is recorded.

We deliberately do NOT retain the entire transition graph in memory yet.
Once the reachable state space is small enough, we can add SCC analysis.
"""

from __future__ import annotations

import argparse
import resource
import sys
import time
from collections import Counter, deque
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements

X_SIZE = 4
Y_SIZE = 8
NCELLS = X_SIZE * Y_SIZE
LAYERS = 3
WORD_MASK = (1 << NCELLS) - 1


def rss_mb() -> float:
    return resource.getrusage(
        resource.RUSAGE_SELF
    ).ru_maxrss / 1024.0


def cell_id(x: int, y: int) -> int:
    return x + X_SIZE * y


def layer_mask(state: int, layer: int) -> int:
    return (
        state >>
        (layer * NCELLS)
    ) & WORD_MASK


def first_empty(mask: int) -> int:
    missing = WORD_MASK & ~mask

    if not missing:
        return -1

    low = missing & -missing
    return low.bit_length() - 1


def pack_layers(
    layers: Sequence[int],
) -> int:
    state = 0

    for i, mask in enumerate(layers):
        state |= (
            mask
            << (i * NCELLS)
        )

    return state


def make_shifted_template(
    placement_cells: Sequence[Tuple[int, int, int]],
    target_z: int,
) -> int | None:
    """
    Translate a concrete S placement so that the chosen target occurrence
    lies on frontier layer 0.

    Return packed 96-bit occupancy (three 32-bit layer masks).
    """
    min_z = min(
        z for _, _, z in placement_cells
    )

    shifted_masks = [0] * LAYERS

    # target_z is measured relative to the placement minimum z.
    target_rel = target_z - min_z

    for x, y, z in placement_cells:
        rel = (
            z - min_z
            - target_rel
        )

        if rel < 0 or rel >= LAYERS:
            return None

        shifted_masks[rel] |= (
            1 << cell_id(x, y)
        )

    return pack_layers(shifted_masks)


def build_templates():
    raw, _ = generate_placements(
        PENTACUBES["S"],
        (X_SIZE, Y_SIZE, 20),
        break_symmetry=False,
    )

    result = {
        cell: []
        for cell in range(NCELLS)
    }

    seen = {
        cell: set()
        for cell in range(NCELLS)
    }

    concrete_count = len(raw)

    for placement in raw.values():
        cells = tuple(placement)

        for x, y, z in cells:
            target = cell_id(x, y)

            packed = make_shifted_template(
                cells,
                z,
            )

            if packed is None:
                continue

            if packed in seen[target]:
                continue

            seen[target].add(packed)
            result[target].append(packed)

    return result, concrete_count


def apply_template(
    state: int,
    template: int,
) -> int | None:
    if state & template:
        return None

    return state | template


def shift_state(state: int) -> int:
    return state >> NCELLS


def discover(
    templates: Dict[int, List[int]],
    max_states: int,
    report_every: float,
    diagnostics: bool = False,
    postshift_diagnostics: bool = False,
):
    start_state = 0

    queue: deque[int] = deque(
        [start_state]
    )
    seen = {start_state}

    processed = 0
    generated = 0
    accepted = 0
    duplicates = 0
    shifts = 0
    branching = 0
    max_degree = 0

    # Diagnostics mode: keep only the summary histogram plus the first
    # 100 duplicate-transition records and the first 100 layer-shift
    # records.  No full per-state record is retained.
    if diagnostics:
        degree_counter: Counter = Counter()
        dup_records: List[Tuple[int, int, bool, int]] = []
        shift_records: List[Tuple[int, int, bool, int]] = []
    else:
        degree_counter = None
        dup_records = None
        shift_records = None

    # Post-shift diagnostics mode: record EVERY layer-shift event
    # (pre_shift_state, post_shift_state = state >> 32) up to the
    # state limit.  No ordinary frontier state is recorded.
    if postshift_diagnostics:
        postshift_counter: Counter = Counter()
        shift_events: List[Tuple[int, int]] = []
    else:
        postshift_counter = None
        shift_events = None

    start_time = time.perf_counter()
    last_report_time = start_time
    last_report_processed = 0

    while queue:
        if len(seen) >= max_states:
            print(
                f"[limit] reached "
                f"{max_states:,} states",
                flush=True,
            )
            break

        state = queue.popleft()
        processed += 1

        current = layer_mask(state, 0)

        if current == WORD_MASK:
            nxt = shift_state(state)
            shifts += 1

            if nxt in seen:
                duplicates += 1
                dup_count = 1
            else:
                seen.add(nxt)
                queue.append(nxt)
                dup_count = 0

            if degree_counter is not None:
                degree_counter[1] += 1

                if len(shift_records) < 100:
                    shift_records.append(
                        (state, 1, True, dup_count)
                    )

                if dup_count > 0 and len(dup_records) < 100:
                    dup_records.append(
                        (state, 1, True, dup_count)
                    )

            if postshift_counter is not None:
                postshift_counter[nxt] += 1
                shift_events.append((state, nxt))

            # Shift has exactly one outgoing edge.
        else:
            target = first_empty(current)

            outgoing = set()

            for template in templates[target]:
                generated += 1

                nxt = apply_template(
                    state,
                    template,
                )

                if nxt is None:
                    continue

                accepted += 1
                outgoing.add(nxt)

            degree = len(outgoing)

            if degree > 1:
                branching += 1

            if degree > max_degree:
                max_degree = degree

            dup_count = 0

            for nxt in outgoing:
                if nxt in seen:
                    duplicates += 1
                    dup_count += 1
                    continue

                seen.add(nxt)
                queue.append(nxt)

            if degree_counter is not None:
                degree_counter[degree] += 1

                if dup_count > 0 and len(dup_records) < 100:
                    dup_records.append(
                        (state, degree, False, dup_count)
                    )

        now = time.perf_counter()

        if now - last_report_time >= report_every:
            delta = (
                processed -
                last_report_processed
            )
            dt = now - last_report_time
            rate = delta / dt if dt > 0 else 0.0

            last_report_time = now
            last_report_processed = processed

            print(
                f"[progress] "
                f"states={len(seen):,} "
                f"queue={len(queue):,} "
                f"processed={processed:,} "
                f"generated={generated:,} "
                f"accepted={accepted:,} "
                f"dup={duplicates:,} "
                f"shifts={shifts:,} "
                f"branch={branching:,} "
                f"maxdeg={max_degree} "
                f"rate={rate:,.0f}/s "
                f"rss={rss_mb():,.0f} MB",
                flush=True,
            )

    elapsed = time.perf_counter() - start_time

    result = {
        "states": len(seen),
        "processed": processed,
        "generated": generated,
        "accepted": accepted,
        "duplicates": duplicates,
        "shifts": shifts,
        "branching": branching,
        "max_degree": max_degree,
        "elapsed": elapsed,
        "rss_mb": rss_mb(),
        "queue_remaining": len(queue),
    }

    if degree_counter is not None:
        result["degree_counter"] = degree_counter
        result["dup_records"] = dup_records
        result["shift_records"] = shift_records

    if postshift_counter is not None:
        result["postshift_counter"] = postshift_counter
        result["shift_events"] = shift_events

    return result


def write_diagnostics_report(
    path: str,
    degree_counter: Counter,
    dup_records: Sequence[Tuple[int, int, bool, int]],
    shift_records: Sequence[Tuple[int, int, bool, int]],
    result: Dict,
    max_states: int,
) -> None:
    """
    Write the frontier diagnostics summary to a markdown file.

    Keeps the summary metrics, the top out-degree histogram, the first
    100 duplicate-transition records and the first 100 layer-shift
    records.  Each record is (state, out_degree, is_layer_shift,
    successors_already_seen).
    """
    top10 = degree_counter.most_common(10)

    lines = [
        "# Z-Frontier State Statistics (S, 4x8)",
        "",
        f"Run: `solvers/s_z_frontier_packed.py "
        f"--diagnostics --max-states {max_states}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Total states | {result['states']:,} |",
        f"| Processed states (diagnosed) | {result['processed']:,} |",
        f"| Branching states (out-degree > 1) | {result['branching']:,} |",
        f"| Maximum out-degree | {result['max_degree']} |",
        f"| Duplicate transitions | {result['duplicates']:,} |",
        f"| Layer shifts | {result['shifts']:,} |",
        "",
        "## Top 10 out-degree counts",
        "",
        "| Out-degree | States |",
        "|---|---|",
    ]

    for degree, count in top10:
        lines.append(f"| {degree} | {count:,} |")

    lines.append("")
    lines.append(
        f"## First {len(dup_records)} duplicate-transition records"
    )
    lines.append("")
    lines.append(
        "| State | Out-degree | Layer shift | "
        "Successors already seen |"
    )
    lines.append("|---|---|---|---|")

    for state, degree, is_shift, dup in dup_records:
        lines.append(
            f"| {state} | {degree} | "
            f"{'yes' if is_shift else 'no'} | {dup} |"
        )

    lines.append("")
    lines.append(
        f"## First {len(shift_records)} layer-shift records"
    )
    lines.append("")
    lines.append(
        "| State | Out-degree | Layer shift | "
        "Successors already seen |"
    )
    lines.append("|---|---|---|---|")

    for state, degree, is_shift, dup in shift_records:
        lines.append(
            f"| {state} | {degree} | "
            f"{'yes' if is_shift else 'no'} | {dup} |"
        )

    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n")

    print(
        f"Diagnostics written to {out_path}",
        flush=True,
    )


def write_postshift_report(
    path: str,
    postshift_counter: Counter,
    shift_events: Sequence[Tuple[int, int]],
    result: Dict,
    max_states: int,
) -> None:
    """
    Write the post-shift diagnostics report to a markdown file.

    Records EVERY layer-shift event (pre_shift_state,
    post_shift_state = pre_shift_state >> 32) up to the state limit:
    total shift events, unique pre-shift and post-shift state counts,
    and the complete per-event state list.  No ordinary frontier state
    is recorded.
    """
    total = result["shifts"]
    unique_post = len(postshift_counter)
    unique_pre = len({pre for pre, _ in shift_events})

    lines = [
        "# Z-Frontier: All Layer-Shift States (S, 4x8)",
        "",
        f"Run: `solvers/s_z_frontier_packed.py "
        f"--postshift-diagnostics --max-states {max_states}`",
        "",
        "Records EVERY layer-shift event (pre-shift state and "
        "post-shift state, `post_shift_state = pre_shift_state >> 32`) "
        "up to the state limit; no ordinary frontier state is recorded.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Total layer-shift events | {total:,} |",
        f"| Unique pre-shift states | {unique_pre:,} |",
        f"| Unique post-shift states | {unique_post:,} |",
        "",
        f"## All {len(shift_events)} layer-shift events",
        "",
        "| # | Pre-shift state | Post-shift state |",
        "|---|---|---|",
    ]

    for i, (pre, post) in enumerate(shift_events, 1):
        lines.append(f"| {i} | {pre} | {post} |")

    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n")

    print(
        f"Post-shift diagnostics written to {out_path}",
        flush=True,
    )


def run_smoke_test(
    templates: Dict[int, List[int]],
    max_states: int = 100_000,
) -> bool:
    """
    Regression check for the Python set[int] implementation: verify
    that a --max-states 100000 run reproduces the known baseline
    metrics (the 100K prefix of the documented 1M baseline in
    docs/z_frontier_state_stats_1m.md).
    """
    expected_metrics = {
        "states": 100_001,
        "processed": 29_086,
        "generated": 521_323,
        "accepted": 100_017,
        "duplicates": 21,
        "shifts": 4,
        "branching": 23_396,
        "max_degree": 11,
        "queue_remaining": 70_915,
    }
    expected_degree_counter = {
        0: 1728,
        1: 3962,
        2: 6838,
        3: 4810,
        4: 2835,
        5: 2852,
        6: 2429,
        7: 2022,
        8: 1068,
        9: 388,
        10: 105,
        11: 49,
    }

    print(
        f"\nSmoke test: Python set[int] regression check "
        f"at --max-states {max_states:,}",
        flush=True,
    )

    res = discover(
        templates,
        max_states,
        report_every=1e9,
        diagnostics=True,
    )

    mismatches = []

    for key, expected in expected_metrics.items():
        if res[key] != expected:
            mismatches.append(
                f"{key}: expected={expected} got={res[key]}"
            )

    if dict(res["degree_counter"]) != expected_degree_counter:
        mismatches.append("degree_counter differs from baseline")

    if mismatches:
        print("SMOKE TEST FAILED:", flush=True)

        for m in mismatches:
            print(f"  - {m}", flush=True)

        return False

    print(
        f"SMOKE TEST PASSED: metrics and out-degree histogram "
        f"match the baseline at {max_states:,} states",
        flush=True,
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Packed 4x8 z-frontier state explorer for S."
        )
    )
    parser.add_argument(
        "--max-states",
        type=int,
        default=10_000_000,
    )
    parser.add_argument(
        "--report-seconds",
        type=float,
        default=2.0,
    )
    parser.add_argument(
        "--diagnostics",
        action="store_true",
        help=(
            "Record per-state out-degree / layer-shift / "
            "already-seen diagnostics and write them to a markdown file."
        ),
    )
    parser.add_argument(
        "--diagnostics-out",
        type=str,
        default="docs/z_frontier_state_stats.md",
        help="Output path for the diagnostics report.",
    )
    parser.add_argument(
        "--postshift-diagnostics",
        action="store_true",
        help=(
            "Record ONLY the state immediately after each layer shift "
            "(post-shift states): totals, unique/repeated counts, and "
            "the first 100 unique and repeated post-shift states."
        ),
    )
    parser.add_argument(
        "--postshift-out",
        type=str,
        default="docs/z_frontier_postshift_states.md",
        help="Output path for the post-shift diagnostics report.",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help=(
            "Regression check: verify the Python set[int] "
            "implementation reproduces the known baseline metrics "
            "at --max-states 100000."
        ),
    )
    args = parser.parse_args()

    print(
        "Generating S placement templates...",
        flush=True,
    )

    start = time.perf_counter()
    templates, concrete_count = build_templates()
    build_time = time.perf_counter() - start

    total_templates = sum(
        len(values)
        for values in templates.values()
    )

    print(
        f"Concrete placements: "
        f"{concrete_count}",
        flush=True,
    )
    print(
        f"Target templates: "
        f"{total_templates}",
        flush=True,
    )
    print(
        f"Template generation: "
        f"{build_time:.3f} s",
        flush=True,
    )
    print(
        f"Initial RSS: "
        f"{rss_mb():.0f} MB",
        flush=True,
    )

    if args.smoke_test:
        ok = run_smoke_test(
            templates,
            max_states=100_000,
        )
        return 0 if ok else 1

    print(
        "\nStarting packed z-frontier exploration...",
        flush=True,
    )

    result = discover(
        templates,
        args.max_states,
        args.report_seconds,
        diagnostics=args.diagnostics,
        postshift_diagnostics=args.postshift_diagnostics,
    )

    print()
    print(
        f"States: {result['states']:,}"
    )
    print(
        f"Processed: {result['processed']:,}"
    )
    print(
        f"Transitions generated: "
        f"{result['generated']:,}"
    )
    print(
        f"Transitions accepted: "
        f"{result['accepted']:,}"
    )
    print(
        f"Duplicate states: "
        f"{result['duplicates']:,}"
    )
    print(
        f"Layer shifts: "
        f"{result['shifts']:,}"
    )
    print(
        f"Branching states: "
        f"{result['branching']:,}"
    )
    print(
        f"Maximum out-degree: "
        f"{result['max_degree']}"
    )
    print(
        f"Queue remaining: "
        f"{result['queue_remaining']:,}"
    )
    print(
        f"Elapsed: "
        f"{result['elapsed']:.3f} s"
    )
    print(
        f"Peak RSS: "
        f"{result['rss_mb']:.0f} MB"
    )

    if args.diagnostics:
        write_diagnostics_report(
            args.diagnostics_out,
            result["degree_counter"],
            result["dup_records"],
            result["shift_records"],
            result,
            args.max_states,
        )

    if args.postshift_diagnostics:
        counter = result["postshift_counter"]
        total = result["shifts"]
        unique_post = len(counter)
        unique_pre = len({pre for pre, _ in result["shift_events"]})

        print()
        print(
            f"Post-shift unique states: "
            f"{unique_post:,}"
        )
        print(
            f"Pre-shift unique states: "
            f"{unique_pre:,}"
        )
        print(
            f"Total layer-shift events: "
            f"{total:,}"
        )

        write_postshift_report(
            args.postshift_out,
            result["postshift_counter"],
            result["shift_events"],
            result,
            args.max_states,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
