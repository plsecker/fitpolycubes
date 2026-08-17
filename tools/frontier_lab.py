#!/usr/bin/env python3
"""
Experiment harness for the polycube frontier prototypes.

Examples:
  python tools/frontier_lab.py run \
      --name s_diag \
      --cmd "python solvers/s_diagonal_frontier_exposed2.py --box 4 8 10 --max-states 1000000" \
      --timeout 300

  python tools/frontier_lab.py sweep \
      --name s_diag \
      --cmd "python solvers/s_diagonal_frontier_exposed2.py --box 4 8 {N} --max-states 1000000" \
      --values 10 15 20 \
      --timeout 300

Each run gets:
  experiments/<timestamp>_<name>/
    command.txt
    stdout.log
    stderr.log
    summary.json
    result.txt

The harness records wall time, exit status, timeout status, and basic
metric extraction from common solver output.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXPERIMENTS = ROOT / "experiments"

METRIC_PATTERNS = {
    "states": re.compile(r"\b(?:States|Memo states|Interior states):\s*([0-9,]+)"),
    "calls": re.compile(r"\bCalls:\s*([0-9,]+)"),
    "memo_hits": re.compile(r"\bMemo hits:\s*([0-9,]+)"),
    "memo": re.compile(r"\bMemo(?:ized states)?=?:?\s*([0-9,]+)"),
    "nodes": re.compile(r"\bNodes:\s*([0-9,]+)"),
    "dead_ends": re.compile(r"\bDead ends:\s*([0-9,]+)"),
    "solutions": re.compile(r"\bSolutions:\s*([0-9,]+)"),
    "placements": re.compile(r"\bPlacements(?: loaded)?:\s*([0-9,]+)"),
    "placement_tried": re.compile(r"\bPlacements tried:\s*([0-9,]+)"),
    "placement_accepted": re.compile(r"\bPlacements accepted:\s*([0-9,]+)"),
    "plane_shifts": re.compile(r"\bPlane shifts:\s*([0-9,]+)"),
    "forgotten": re.compile(r"\bForgotten frontier cells:\s*([0-9,]+)"),
    "elapsed": re.compile(r"\b(?:Elapsed|Time|Search time):\s*([0-9.]+)\s*s"),
    "rate": re.compile(r"\bNodes/sec:\s*([0-9.eE+\-]+)"),
    "max_depth": re.compile(r"\bMax depth:\s*([0-9]+)"),
    "sccs": re.compile(r"\bSCCs:\s*([0-9,]+)"),
    "nontrivial_sccs": re.compile(r"\bNontrivial SCCs:\s*([0-9,]+)"),
    "branching_states": re.compile(r"\bBranching states:\s*([0-9,]+)"),
    "max_degree": re.compile(r"\bMaximum out-degree:\s*([0-9]+)|\bMax out-degree:\s*([0-9]+)"),
    "positive_advance": re.compile(r"\bPositive-advance transitions:\s*([0-9,]+)"),
}


def parse_metrics(text: str) -> dict:
    metrics = {}
    for name, pattern in METRIC_PATTERNS.items():
        match = pattern.search(text)
        if not match:
            continue
        value = next(
            (g for g in match.groups() if g is not None),
            None,
        )
        if value is None:
            continue
        value = value.replace(",", "")
        if name in {"elapsed", "rate"}:
            metrics[name] = float(value)
        else:
            metrics[name] = int(value)
    return metrics


def run_one(
    name: str,
    command: str,
    timeout: float,
    extra_env: dict[str, str] | None = None,
) -> dict:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name)
    run_dir = EXPERIMENTS / f"{timestamp}_{safe_name}"
    run_dir.mkdir(parents=True, exist_ok=False)

    (run_dir / "command.txt").write_text(command + "\n")

    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    start = time.perf_counter()
    timed_out = False

    stdout_path = run_dir / "stdout.log"
    stderr_path = run_dir / "stderr.log"

    print(f"[run] {command}", flush=True)
    print(f"[run] log dir: {run_dir}", flush=True)

    try:
        proc = subprocess.run(
            command,
            cwd=ROOT,
            shell=True,
            executable="/bin/bash",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            env=env,
        )
        returncode = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = None
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")

    elapsed = time.perf_counter() - start

    stdout_path.write_text(stdout)
    stderr_path.write_text(stderr)

    combined = stdout + "\n" + stderr
    metrics = parse_metrics(combined)

    summary = {
        "name": name,
        "command": command,
        "returncode": returncode,
        "timed_out": timed_out,
        "wall_seconds": elapsed,
        "metrics": metrics,
        "log_dir": str(run_dir.relative_to(ROOT)),
    }

    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )

    result_lines = [
        f"name: {name}",
        f"returncode: {returncode}",
        f"timed_out: {timed_out}",
        f"wall_seconds: {elapsed:.3f}",
    ]
    for key, value in metrics.items():
        result_lines.append(f"{key}: {value}")

    (run_dir / "result.txt").write_text(
        "\n".join(result_lines) + "\n"
    )

    print(
        f"[done] exit={returncode} timeout={timed_out} "
        f"wall={elapsed:.3f}s",
        flush=True,
    )

    for key in sorted(metrics):
        print(f"[metric] {key}={metrics[key]}", flush=True)

    return summary


def cmd_run(args: argparse.Namespace) -> int:
    run_one(
        name=args.name,
        command=args.cmd,
        timeout=args.timeout,
    )
    return 0


def cmd_sweep(args: argparse.Namespace) -> int:
    all_results = []

    for value in args.values:
        name = f"{args.name}_{value}"
        command = args.cmd.replace("{N}", str(value))
        result = run_one(
            name=name,
            command=command,
            timeout=args.timeout,
        )
        all_results.append(result)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = EXPERIMENTS / f"{timestamp}_{args.name}_sweep.json"
    out.write_text(
        json.dumps(all_results, indent=2) + "\n"
    )

    print(f"[sweep] summary: {out}", flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run and record polycube experiments."
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)

    run = sub.add_parser("run")
    run.add_argument("--name", required=True)
    run.add_argument("--cmd", required=True)
    run.add_argument("--timeout", type=float, default=300.0)
    run.set_defaults(func=cmd_run)

    sweep = sub.add_parser("sweep")
    sweep.add_argument("--name", required=True)
    sweep.add_argument("--cmd", required=True)
    sweep.add_argument("--values", nargs="+", type=int, required=True)
    sweep.add_argument("--timeout", type=float, default=300.0)
    sweep.set_defaults(func=cmd_sweep)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
