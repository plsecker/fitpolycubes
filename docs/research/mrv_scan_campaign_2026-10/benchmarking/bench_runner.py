#!/usr/bin/env python3
"""Fail-closed paired benchmark harness for the Fit-Polycubes solver campaign.

Modes (default is safe: nothing executes a solver):
  preflight   verify manifest, file existence and exact SHA256 hashes
  readiness   run the >=75s host-readiness observation (no solver started)
  dry-run     print the exact commands that WOULD run (never executes)
  run         execute the five paired runs (requires --execute + --run-dir)
  analyze     analyze an existing run directory's runs.csv
  evidence    verify correctness-evidence references against actual files

Exit codes:
  0  success
  2  invalid configuration / manifest
  3  preflight failure (missing file or hash mismatch; nothing executed)
  4  host gate BLOCKED (no solver started)
  5  correctness-evidence failure (benchmarking refused)
  6  execution error (solver failure, interruption handling, I/O)

Only the Python standard library is used. Argument vectors are passed as
explicit lists (never shell strings). Solver-internal time and external
wall-clock time are recorded in separate fields.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import signal
import statistics
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

EXIT_OK = 0
EXIT_CONFIG = 2
EXIT_PREFLIGHT = 3
EXIT_BLOCKED = 4
EXIT_EVIDENCE = 5
EXIT_EXEC = 6

# ---------------------------------------------------------------------------
# Schemas (defined before any runner logic)
# ---------------------------------------------------------------------------

RUN_CSV_FIELDS = [
    "run_id", "pair", "order_in_pair", "impl",
    "source_path", "source_sha256",
    "binary_path", "binary_sha256",
    "placement_path", "placement_sha256",
    "argv_json",
    "start_utc", "end_utc",
    "exit_status",
    "nodes", "solutions", "dead_ends",
    "internal_elapsed_s", "internal_nodes_per_sec",
    "external_elapsed_s",
    "peak_rss_kb",
    "pre_host_json", "post_host_json",
    "stdout_log", "stderr_log",
    "status", "warning",
]

PAIR_CSV_FIELDS = [
    "pair", "baseline_run_id", "candidate_run_id",
    "baseline_internal_s", "candidate_internal_s",
    "ratio", "reduction_percent",
    "counter_match", "warning",
]

# Byte markers that identify a non-release (instrumented/diagnostic) build.
# Note: b"__gmon_start__" is deliberately NOT listed: it is a normal glibc
# symbol present in plain -Ofast binaries (see TW1-20 perf report).
INSTRUMENTED_MARKERS = [
    b"_mcount",
    b"__asan",
    b"__ubsan",
    b"__sancov",
    b"ACTIVEX-INVARIANT",
    b"__gcov",
    b"GCOV",
    b"DEBUG_COMPARE_HOOK",
]

PAIR_ORDER = [
    (1, "baseline"), (1, "candidate"),
    (2, "candidate"), (2, "baseline"),
    (3, "baseline"), (3, "candidate"),
    (4, "candidate"), (4, "baseline"),
    (5, "baseline"), (5, "candidate"),
]


class HarnessError(Exception):
    """Base error carrying a distinct exit code."""

    def __init__(self, message: str, exit_code: int):
        super().__init__(message)
        self.exit_code = exit_code


class ConfigError(HarnessError):
    def __init__(self, message: str):
        super().__init__(message, EXIT_CONFIG)


class PreflightError(HarnessError):
    def __init__(self, message: str):
        super().__init__(message, EXIT_PREFLIGHT)


class BlockedError(HarnessError):
    def __init__(self, message: str):
        super().__init__(message, EXIT_BLOCKED)


class EvidenceError(HarnessError):
    def __init__(self, message: str):
        super().__init__(message, EXIT_EVIDENCE)


class ExecutionError(HarnessError):
    def __init__(self, message: str):
        super().__init__(message, EXIT_EXEC)


# ---------------------------------------------------------------------------
# Hashing / files
# ---------------------------------------------------------------------------

def sha256_file(path: str) -> str:
    """Return the full hex SHA256 of a file. Raises PreflightError if unreadable."""
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError as exc:
        raise PreflightError(f"cannot read file for hashing: {path}: {exc}")


def verify_file_hash(path: str, expected: str, label: str) -> str:
    """Verify existence + exact hash. Returns actual hash or raises PreflightError."""
    if not os.path.isfile(path):
        raise PreflightError(f"{label}: file not found: {path}")
    actual = sha256_file(path)
    if actual != expected:
        raise PreflightError(
            f"{label}: SHA256 mismatch for {path}\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}"
        )
    return actual


def detect_instrumented(binary_path: str) -> List[str]:
    """Scan a binary for instrumentation markers. Returns matched marker names."""
    try:
        with open(binary_path, "rb") as f:
            data = f.read()
    except OSError as exc:
        raise PreflightError(f"cannot scan binary {binary_path}: {exc}")
    return [m.decode("ascii", "replace") for m in INSTRUMENTED_MARKERS if m in data]


def atomic_write_text(path: str, content: str) -> None:
    """Write text atomically via temp file + os.replace."""
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".tmp_")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def atomic_write_json(path: str, obj: Any) -> None:
    atomic_write_text(path, json.dumps(obj, indent=2, sort_keys=True) + "\n")


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

REQUIRED_MANIFEST_KEYS = [
    "workload", "node_cap", "search_options",
    "baseline", "candidate", "placement",
    "compiler", "build_flags",
    "expected_counters", "correctness_evidence",
    "readiness", "pair_order",
]

REQUIRED_IMPL_KEYS = ["label", "source_path", "source_sha256",
                      "binary_path", "binary_sha256"]


def load_manifest(path: str) -> Dict[str, Any]:
    """Load and validate a manifest. Raises ConfigError on any problem."""
    try:
        with open(path) as f:
            manifest = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"cannot load manifest {path}: {exc}")
    if not isinstance(manifest, dict):
        raise ConfigError("manifest root must be a JSON object")
    for key in REQUIRED_MANIFEST_KEYS:
        if key not in manifest:
            raise ConfigError(f"manifest missing required key: {key}")
    for impl_key in ("baseline", "candidate"):
        impl = manifest[impl_key]
        if not isinstance(impl, dict):
            raise ConfigError(f"manifest[{impl_key}] must be an object")
        for key in REQUIRED_IMPL_KEYS:
            if key not in impl:
                raise ConfigError(f"manifest[{impl_key}] missing key: {key}")
    placement = manifest["placement"]
    for key in ("path", "sha256"):
        if key not in placement:
            raise ConfigError(f"manifest[placement] missing key: {key}")
    readiness = manifest["readiness"]
    for key in ("min_observation_s", "min_avg_idle_pct",
                "max_load_1min", "allow_swap_occupancy"):
        if key not in readiness:
            raise ConfigError(f"manifest[readiness] missing key: {key}")
    if not isinstance(manifest["pair_order"], list) or not manifest["pair_order"]:
        raise ConfigError("manifest[pair_order] must be a non-empty list")
    return manifest


# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------

@dataclass
class PreflightRecord:
    label: str
    path: str
    expected_sha256: str
    actual_sha256: str
    ok: bool = True


def preflight(manifest: Dict[str, Any], run_dir: str) -> List[PreflightRecord]:
    """Verify every pinned file. Raises PreflightError on the first failure.

    Also refuses to use a run directory that already contains results
    (never overwrite a previous experiment).
    """
    if os.path.exists(run_dir):
        existing = os.listdir(run_dir)
        if existing:
            raise PreflightError(
                f"run directory already exists and is non-empty: {run_dir} "
                f"({len(existing)} entries). Refusing to overwrite."
            )
    records: List[PreflightRecord] = []
    items = [
        ("baseline source", manifest["baseline"]["source_path"],
         manifest["baseline"]["source_sha256"]),
        ("candidate source", manifest["candidate"]["source_path"],
         manifest["candidate"]["source_sha256"]),
        ("baseline binary", manifest["baseline"]["binary_path"],
         manifest["baseline"]["binary_sha256"]),
        ("candidate binary", manifest["candidate"]["binary_path"],
         manifest["candidate"]["binary_sha256"]),
        ("placement file", manifest["placement"]["path"],
         manifest["placement"]["sha256"]),
    ]
    for label, path, expected in items:
        actual = verify_file_hash(path, expected, label)
        records.append(PreflightRecord(label, path, expected, actual))
    # Build-type separation: reject instrumented binaries from release runs.
    if not manifest.get("allow_instrumented", False):
        for impl_key in ("baseline", "candidate"):
            bpath = manifest[impl_key]["binary_path"]
            markers = detect_instrumented(bpath)
            if markers:
                raise PreflightError(
                    f"{impl_key} binary {bpath} shows instrumentation markers "
                    f"{markers}; refusing release comparison."
                )
    argv = build_argv(manifest, manifest["baseline"]["binary_path"])
    if argv[1:] != manifest.get("expected_argv_tail"):
        raise PreflightError(
            f"manifest argument vector does not match workload settings: "
            f"{argv[1:]} != {manifest.get('expected_argv_tail')}"
        )
    return records


def build_argv(manifest: Dict[str, Any], binary_path: str) -> List[str]:
    """Build the explicit argument array (no shell strings)."""
    w = manifest["workload"]
    return ([binary_path, w["piece"]]
            + [str(x) for x in w["dims"]]
            + [manifest["placement"]["path"], str(manifest["node_cap"])]
            + list(manifest["search_options"]))


# ---------------------------------------------------------------------------
# Host metrics (injectable for tests)
# ---------------------------------------------------------------------------

def read_proc_stat_cpu() -> Tuple[int, int]:
    """Return (idle_ticks, total_ticks) from the aggregate cpu line."""
    with open("/proc/stat") as f:
        parts = f.readline().split()
    if parts[0] != "cpu":
        raise ExecutionError("unexpected /proc/stat format")
    nums = [int(x) for x in parts[1:]]
    idle = nums[3] + nums[4]  # idle + iowait
    return idle, sum(nums)


def read_loadavg() -> Tuple[float, float, float]:
    with open("/proc/loadavg") as f:
        parts = f.read().split()
    return float(parts[0]), float(parts[1]), float(parts[2])


def read_meminfo() -> Dict[str, int]:
    out: Dict[str, int] = {}
    with open("/proc/meminfo") as f:
        for line in f:
            key, _, rest = line.partition(":")
            key = key.strip()
            if key in ("MemTotal", "MemAvailable", "SwapTotal", "SwapFree"):
                out[key] = int(rest.strip().split()[0])  # kB
    return out


def read_pressure(path: str = "/proc/pressure/memory") -> Optional[Dict[str, float]]:
    try:
        with open(path) as f:
            text = f.read()
    except OSError:
        return None
    m10 = re.search(r"avg10=([0-9.]+)", text)
    m60 = re.search(r"avg60=([0-9.]+)", text)
    m300 = re.search(r"avg300=([0-9.]+)", text)
    if not (m10 and m60 and m300):
        return None
    return {"avg10": float(m10.group(1)), "avg60": float(m60.group(1)),
            "avg300": float(m300.group(1))}


def read_swap_activity() -> Tuple[int, int]:
    """Return (pswpin, pswpout) cumulative page counts from /proc/vmstat."""
    pin = pout = 0
    with open("/proc/vmstat") as f:
        for line in f:
            if line.startswith("pswpin"):
                pin = int(line.split()[1])
            elif line.startswith("pswpout"):
                pout = int(line.split()[1])
    return pin, pout


def find_competing_processes(patterns: Tuple[str, ...] = ("solver", "benchmark")) -> List[str]:
    """List process command lines matching solver/benchmark patterns.

    The harness's own python process and the monitor daemons are excluded
    by callers via the manifest's ignore list; this function reports raw.
    """
    found: List[str] = []
    try:
        out = subprocess.run(["ps", "-eo", "args"], capture_output=True,
                             text=True, timeout=15).stdout.splitlines()
    except (OSError, subprocess.SubprocessError):
        return found
    for line in out:
        low = line.lower()
        if any(p in low for p in patterns) and "bench_runner" not in low:
            found.append(line.strip()[:200])
    return found


def top_consumers(n: int = 8) -> List[str]:
    """Top CPU consumers as 'pcpu pmem args' lines (informational only)."""
    try:
        out = subprocess.run(
            ["ps", "-eo", "pcpu,pmem,args", "--sort=-pcpu"],
            capture_output=True, text=True, timeout=15).stdout.splitlines()
    except (OSError, subprocess.SubprocessError):
        return []
    return [line.strip()[:200] for line in out[1:n + 1]]


@dataclass
class HostSample:
    ts_utc: str
    epoch: int
    idle_pct: Optional[float]
    load_1min: float
    load_5min: float
    mem_available_kb: int
    mem_total_kb: int
    pressure_some_avg10: Optional[float]
    swapin_delta: int
    swapout_delta: int


def observe_host(duration_s: float,
                 sample_interval_s: float = 5.0,
                 stat_reader: Callable[[], Tuple[int, int]] = read_proc_stat_cpu,
                 load_reader: Callable[[], Tuple[float, float, float]] = read_loadavg,
                 mem_reader: Callable[[], Dict[str, int]] = read_meminfo,
                 pressure_reader: Callable[[], Optional[Dict[str, float]]] = read_pressure,
                 swap_reader: Callable[[], Tuple[int, int]] = read_swap_activity,
                 sleep_fn: Callable[[float], None] = time.sleep,
                 clock_fn: Callable[[], int] = lambda: int(time.time()),
                 ) -> Tuple[List[HostSample], str, str]:
    """Genuine host observation with verified start/end timestamps.

    Returns (samples, start_utc, end_utc). Duration is enforced from the
    real (or injected) clock, not from sample counts.
    """
    start_epoch = clock_fn()
    start_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(start_epoch))
    samples: List[HostSample] = []
    prev_idle, prev_total = stat_reader()
    prev_pin, prev_pout = swap_reader()
    while clock_fn() - start_epoch < duration_s:
        sleep_fn(sample_interval_s)
        idle, total = stat_reader()
        load1, load5, _ = load_reader()
        mem = mem_reader()
        press = pressure_reader()
        pin, pout = swap_reader()
        idle_pct = None
        if total > prev_total:
            idle_pct = 100.0 * (idle - prev_idle) / (total - prev_total)
        samples.append(HostSample(
            ts_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(clock_fn())),
            epoch=clock_fn(),
            idle_pct=idle_pct,
            load_1min=load1, load_5min=load5,
            mem_available_kb=mem.get("MemAvailable", -1),
            mem_total_kb=mem.get("MemTotal", -1),
            pressure_some_avg10=(press or {}).get("avg10"),
            swapin_delta=pin - prev_pin,
            swapout_delta=pout - prev_pout,
        ))
        prev_idle, prev_total = idle, total
        prev_pin, prev_pout = pin, pout
    end_epoch = clock_fn()
    end_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(end_epoch))
    if end_epoch - start_epoch < duration_s:
        raise ExecutionError("observation ended before minimum duration")
    return samples, start_utc, end_utc


@dataclass
class GateResult:
    passed: bool
    avg_idle_pct: Optional[float]
    max_load_1min: Optional[float]
    reasons: List[str] = field(default_factory=list)


def gate_thresholds(manifest: Dict[str, Any]) -> Tuple[float, float, float, int]:
    """Single source of truth for host-health thresholds (initial + inter-pair)."""
    cfg = manifest["readiness"]
    return (
        float(cfg["min_avg_idle_pct"]),
        float(cfg["max_load_1min"]),
        float(cfg.get("max_pressure_avg10", 5.0)),
        int(cfg.get("max_swap_pages_per_sample", 1000)),
    )


def evaluate_gate(samples: List[HostSample],
                  competing: List[str],
                  min_avg_idle_pct: float,
                  max_load_1min: float,
                  max_pressure_avg10: float = 5.0,
                  max_swap_pages_per_sample: int = 1000) -> GateResult:
    """Apply readiness criteria. Occupied swap alone is never a failure."""
    reasons: List[str] = []
    if competing:
        reasons.append(f"competing processes present: {competing[:5]}")
    idles = [s.idle_pct for s in samples if s.idle_pct is not None]
    avg_idle = sum(idles) / len(idles) if idles else None
    if avg_idle is None:
        reasons.append("no valid idle samples")
    elif avg_idle <= min_avg_idle_pct:
        reasons.append(f"avg idle {avg_idle:.1f}% <= {min_avg_idle_pct}%")
    loads = [s.load_1min for s in samples]
    max_load = max(loads) if loads else None
    if max_load is None:
        reasons.append("no load samples")
    elif max_load >= max_load_1min:
        reasons.append(f"1-min load reached {max_load:.2f} (>= {max_load_1min})")
    pressures = [s.pressure_some_avg10 for s in samples
                 if s.pressure_some_avg10 is not None]
    if pressures and max(pressures) >= max_pressure_avg10:
        reasons.append(f"memory pressure avg10 reached {max(pressures):.2f}")
    swaps = [(s.swapin_delta, s.swapout_delta) for s in samples]
    sustained = [s for s in swaps
                 if s[0] > max_swap_pages_per_sample
                 or s[1] > max_swap_pages_per_sample]
    if len(sustained) >= 2:
        reasons.append(f"sustained swapping in {len(sustained)} samples")
    return GateResult(passed=not reasons, avg_idle_pct=avg_idle,
                      max_load_1min=max_load, reasons=reasons)


def inter_pair_health_check(
    manifest: Dict[str, Any],
    duration_s: float = 20.0,
    sample_interval_s: float = 5.0,
    competing_finder: Callable[[], List[str]] = find_competing_processes,
    **observe_kwargs: Any,
) -> Tuple[GateResult, List[HostSample], List[str]]:
    """Short documented health check between pairs (not the full 75 s gate).

    Uses the same thresholds as the initial gate via gate_thresholds().
    Never kills, suspends, renices, or otherwise modifies other processes.
    Returns (gate_result, samples, competing_processes).
    """
    cfg = manifest["readiness"]
    competing = [p for p in competing_finder()
                 if not any(ign in p for ign in cfg.get("ignore_patterns", []))]
    samples, _, _ = observe_host(duration_s, sample_interval_s,
                                 **observe_kwargs)
    min_idle, max_load, max_press, max_swap = gate_thresholds(manifest)
    gate = evaluate_gate(samples, competing, min_idle, max_load,
                         max_press, max_swap)
    return gate, samples, competing


# ---------------------------------------------------------------------------
# Correctness evidence
# ---------------------------------------------------------------------------

def check_correctness_evidence(manifest: Dict[str, Any]) -> List[str]:
    """Refuse to benchmark unless evidence matches the exact pinned binaries.

    Verifies: (a) both binaries hash to the manifest pins (already done in
    preflight, re-checked here against the evidence record), (b) every
    referenced evidence log exists and hashes to its recorded value, (c) the
    evidence record names the same binary hashes as the manifest.
    Returns human-readable confirmation lines.
    """
    ev = manifest["correctness_evidence"]
    confirmed: List[str] = []
    for impl_key in ("baseline", "candidate"):
        pinned = manifest[impl_key]["binary_sha256"]
        recorded = ev.get("binary_sha256", {}).get(impl_key)
        if recorded != pinned:
            raise EvidenceError(
                f"evidence record names {impl_key} binary {recorded}, but "
                f"manifest pins {pinned}: refusing to reuse evidence."
            )
        actual = sha256_file(manifest[impl_key]["binary_path"])
        if actual != pinned:
            raise EvidenceError(
                f"{impl_key} binary changed since evidence was recorded; "
                f"fresh correctness validation required."
            )
    for ref in ev.get("log_refs", []):
        actual = verify_file_hash(ref["path"], ref["sha256"],
                                  f"evidence log {ref.get('label', ref['path'])}")
        confirmed.append(f"{ref.get('label', ref['path'])}: {actual[:12]}... ok")
    counters = ev.get("expected_counters", {})
    for workload, expect in counters.items():
        confirmed.append(
            f"{workload}: expect nodes={expect.get('nodes')} "
            f"solutions={expect.get('solutions')} dead_ends={expect.get('dead_ends')}"
        )
    return confirmed


# ---------------------------------------------------------------------------
# Solver output parsing (internal vs external timings stay separate)
# ---------------------------------------------------------------------------

def parse_solver_stdout(text: str) -> Dict[str, Optional[float]]:
    """Parse deterministic counters + internal timing from solver stdout."""
    def grab(pattern: str) -> Optional[float]:
        m = re.search(pattern, text)
        return float(m.group(1)) if m else None

    return {
        "nodes": grab(r"Nodes:\s+([0-9]+)"),
        "solutions": grab(r"Solutions:\s+([0-9]+)"),
        "dead_ends": grab(r"Dead ends:\s+([0-9]+)"),
        "internal_elapsed_s": grab(r"Time:\s+([0-9.]+)"),
        "internal_nodes_per_sec": grab(r"Nodes/sec:\s+([0-9.]+)"),
    }


def parse_peak_rss(time_v_output: str) -> Optional[int]:
    m = re.search(r"Maximum resident set size[^:]*:\s+([0-9]+)", time_v_output)
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# Journal (benchmark-orchestration recovery, not solver checkpointing)
# ---------------------------------------------------------------------------

JOURNAL_NAME = "journal.jsonl"


def journal_append(run_dir: str, record: Dict[str, Any]) -> None:
    path = os.path.join(run_dir, JOURNAL_NAME)
    with open(path, "a") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def journal_read(run_dir: str) -> List[Dict[str, Any]]:
    path = os.path.join(run_dir, JOURNAL_NAME)
    if not os.path.exists(path):
        return []
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def journal_status(run_dir: str) -> Dict[str, str]:
    """Latest state per run_id. Incomplete runs are never counted as valid."""
    status: Dict[str, str] = {}
    for rec in journal_read(run_dir):
        if "run_id" in rec and "state" in rec:
            status[rec["run_id"]] = rec["state"]
    return status


# ---------------------------------------------------------------------------
# Paired execution
# ---------------------------------------------------------------------------

@dataclass
class RunSpec:
    run_id: str
    pair: int
    order_in_pair: str
    impl: str  # "baseline" | "candidate"
    argv: List[str]


def plan_runs(manifest: Dict[str, Any]) -> List[RunSpec]:
    """Expand manifest pair_order into the 10-run execution plan."""
    specs: List[RunSpec] = []
    for pair, impl in manifest["pair_order"]:
        order = "first" if len([s for s in specs if s.pair == pair]) == 0 else "second"
        binary = manifest[impl]["binary_path"]
        run_id = f"p{pair}_{impl}_{order}"
        specs.append(RunSpec(run_id, pair, order, impl, build_argv(manifest, binary)))
    return specs


class SingleFlight:
    """Guards against concurrent solver processes + handles interruption."""

    def __init__(self) -> None:
        self.active: Optional[subprocess.Popen] = None
        self.interrupted = False
        self._prev_int = None
        self._prev_term = None

    def __enter__(self) -> "SingleFlight":
        self._prev_int = signal.signal(signal.SIGINT, self._on_signal)
        self._prev_term = signal.signal(signal.SIGTERM, self._on_signal)
        return self

    def __exit__(self, *args: Any) -> None:
        signal.signal(signal.SIGINT, self._prev_int)
        signal.signal(signal.SIGTERM, self._prev_term)

    def _on_signal(self, signum: int, frame: Any) -> None:
        self.interrupted = True
        if self.active is not None and self.active.poll() is None:
            try:
                self.active.terminate()
            except OSError:
                pass


def default_launcher(argv: List[str], stdout_path: str, stderr_path: str,
                     guard: SingleFlight) -> Tuple[int, float]:
    """Launch one solver process (explicit argv, separate logs). No shell."""
    if guard.active is not None and guard.active.poll() is None:
        raise ExecutionError("refusing to launch: another solver is running")
    start = time.monotonic()
    with open(stdout_path, "w") as out, open(stderr_path, "w") as err:
        proc = subprocess.Popen(argv, stdout=out, stderr=err,
                                executable=argv[0])
        guard.active = proc
        try:
            proc.wait()
        finally:
            guard.active = None
    elapsed = time.monotonic() - start
    return proc.returncode, elapsed


def timev_launcher(argv: List[str], stdout_path: str, stderr_path: str,
                   guard: SingleFlight,
                   time_bin: str = "/usr/bin/time") -> Tuple[int, float]:
    """Launch via `/usr/bin/time -v` for portable peak-RSS capture.

    The solver's argv and binary identity are unchanged: `time` only
    prefixes the argument vector and appends its resource report to the
    solver's stderr stream (parsed by parse_peak_rss). Solver stdout is
    untouched. Falls back to default_launcher when the time binary is
    absent (peak_rss_kb recorded as unavailable, never invented).
    """
    if not (os.path.isfile(time_bin) and os.access(time_bin, os.X_OK)):
        return default_launcher(argv, stdout_path, stderr_path, guard)
    if guard.active is not None and guard.active.poll() is None:
        raise ExecutionError("refusing to launch: another solver is running")
    start = time.monotonic()
    with open(stdout_path, "w") as out, open(stderr_path, "w") as err:
        proc = subprocess.Popen([time_bin, "-v"] + argv,
                                stdout=out, stderr=err,
                                executable=time_bin)
        guard.active = proc
        try:
            proc.wait()
        finally:
            guard.active = None
    elapsed = time.monotonic() - start
    return proc.returncode, elapsed


def execute_plan(manifest: Dict[str, Any],
                 run_dir: str,
                 specs: List[RunSpec],
                 launcher: Callable[..., Tuple[int, float]] = default_launcher,
                 host_snapshot: Callable[[], Dict[str, Any]] | None = None,
                 inter_pair_check: Callable[[], Tuple[GateResult, List[HostSample], List[str]]] | None = None,
                 ) -> List[Dict[str, Any]]:
    """Run the plan strictly sequentially with journaling. Returns run rows.

    Before starting each new pair (pairs after the first), the optional
    inter_pair_check runs a short host-health observation. If it fails,
    no further solver process is started: completed rows are preserved,
    the stop reason is journalled + written to host_stop.json, and the
    incomplete pair is left incomplete (never fabricated). A running
    solver is always allowed to finish normally before the next check.
    """
    os.makedirs(os.path.join(run_dir, "logs"), exist_ok=True)
    rows: List[Dict[str, Any]] = []
    prior = journal_status(run_dir)
    ambiguous = [r for r, s in prior.items() if s in ("RUNNING", "PLANNED")]
    if ambiguous:
        raise ExecutionError(
            f"refusing to continue with ambiguous prior states {ambiguous}; "
            f"operator must resolve the journal first."
        )
    seen_pairs: set = set()
    with SingleFlight() as guard:
        for spec in specs:
            if guard.interrupted:
                journal_append(run_dir, {"run_id": spec.run_id,
                                         "state": "INTERRUPTED"})
                break
            if spec.pair not in seen_pairs and seen_pairs and inter_pair_check:
                seen_pairs.add(spec.pair)
                gate, samples, competing = inter_pair_check()
                if not gate.passed:
                    stop_record = {
                        "event": "HOST_STOP",
                        "before_pair": spec.pair,
                        "reasons": gate.reasons,
                        "avg_idle_pct": gate.avg_idle_pct,
                        "max_load_1min": gate.max_load_1min,
                        "competing_processes": competing,
                        "samples": [asdict(s) for s in samples],
                        "completed_runs": len(rows),
                        "ts_utc": utcnow(),
                    }
                    atomic_write_json(os.path.join(run_dir, "host_stop.json"),
                                      stop_record)
                    journal_append(run_dir, {
                        "run_id": f"pair_{spec.pair}",
                        "state": "HOST_STOPPED",
                        "reasons": gate.reasons,
                        "ts_utc": utcnow(),
                    })
                    break  # preserve completed rows; never start the next solver
            else:
                seen_pairs.add(spec.pair)
            journal_append(run_dir, {"run_id": spec.run_id, "state": "RUNNING",
                                     "argv": spec.argv,
                                     "ts_utc": utcnow()})
            stdout_log = os.path.join(run_dir, "logs", spec.run_id + ".stdout.log")
            stderr_log = os.path.join(run_dir, "logs", spec.run_id + ".stderr.log")
            pre = host_snapshot() if host_snapshot else {}
            start_utc = utcnow()
            mono_start = time.monotonic()
            try:
                exit_status, _launcher_elapsed = launcher(
                    spec.argv, stdout_log, stderr_log, guard)
            except Exception as exc:
                journal_append(run_dir, {"run_id": spec.run_id,
                                         "state": "FAILED",
                                         "error": str(exc)})
                raise ExecutionError(f"run {spec.run_id} failed to launch: {exc}")
            external_elapsed = time.monotonic() - mono_start
            end_utc = utcnow()
            post = host_snapshot() if host_snapshot else {}
            with open(stdout_log) as f:
                parsed = parse_solver_stdout(f.read())
            peak = None
            if os.path.exists(stderr_log):
                with open(stderr_log) as f:
                    peak = parse_peak_rss(f.read())
            impl_cfg = manifest[spec.impl]
            state = "COMPLETED" if exit_status == 0 else "FAILED"
            if guard.interrupted and state == "COMPLETED":
                state = "INTERRUPTED"  # never trust a timing under signal
            row = {
                "run_id": spec.run_id, "pair": spec.pair,
                "order_in_pair": spec.order_in_pair, "impl": spec.impl,
                "source_path": impl_cfg["source_path"],
                "source_sha256": impl_cfg["source_sha256"],
                "binary_path": impl_cfg["binary_path"],
                "binary_sha256": impl_cfg["binary_sha256"],
                "placement_path": manifest["placement"]["path"],
                "placement_sha256": manifest["placement"]["sha256"],
                "argv_json": json.dumps(spec.argv),
                "start_utc": start_utc, "end_utc": end_utc,
                "exit_status": exit_status,
                "nodes": parsed["nodes"], "solutions": parsed["solutions"],
                "dead_ends": parsed["dead_ends"],
                "internal_elapsed_s": parsed["internal_elapsed_s"],
                "internal_nodes_per_sec": parsed["internal_nodes_per_sec"],
                "external_elapsed_s": round(external_elapsed, 2),
                "peak_rss_kb": peak,
                "pre_host_json": json.dumps(pre),
                "post_host_json": json.dumps(post),
                "stdout_log": stdout_log, "stderr_log": stderr_log,
                "status": state, "warning": "",
            }
            journal_append(run_dir, {"run_id": spec.run_id, "state": state,
                                     "exit_status": exit_status,
                                     "end_utc": end_utc})
            rows.append(row)
            if state != "COMPLETED":
                break  # record the failure; stop further performance runs
    return rows


def utcnow() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def analyze_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Pair baseline/candidate runs. Missing pairs stay missing."""
    by_pair: Dict[Any, Dict[str, Dict[str, Any]]] = {}
    for r in rows:
        if r.get("status") != "COMPLETED":
            continue
        by_pair.setdefault(r["pair"], {})[r["impl"]] = r
    pairs = []
    for pair in sorted(by_pair):
        impls = by_pair[pair]
        if "baseline" not in impls or "candidate" not in impls:
            continue  # incomplete pair: never fabricated
        b, c = impls["baseline"], impls["candidate"]
        bt, ct = b["internal_elapsed_s"], c["internal_elapsed_s"]
        ratio = reduction = None
        if bt and ct:
            ratio = ct / bt
            reduction = 100.0 * (1.0 - ratio)
        counters_match = (
            b["nodes"] == c["nodes"]
            and b["solutions"] == c["solutions"]
            and b["dead_ends"] == c["dead_ends"]
            and b["nodes"] is not None
        )
        pairs.append({
            "pair": pair,
            "baseline_run_id": b["run_id"], "candidate_run_id": c["run_id"],
            "baseline_internal_s": bt, "candidate_internal_s": ct,
            "ratio": ratio, "reduction_percent": reduction,
            "counter_match": counters_match, "warning": "",
        })
    baselines = [p["baseline_internal_s"] for p in pairs
                 if p["baseline_internal_s"] is not None]
    candidates = [p["candidate_internal_s"] for p in pairs
                  if p["candidate_internal_s"] is not None]
    reductions = [p["reduction_percent"] for p in pairs
                  if p["reduction_percent"] is not None]
    return {
        "pairs": pairs,
        "complete_pairs": len(pairs),
        "median_baseline_s": statistics.median(baselines) if baselines else None,
        "median_candidate_s": statistics.median(candidates) if candidates else None,
        "median_reduction_percent": (statistics.median(reductions)
                                     if reductions else None),
        "baseline_range": [min(baselines), max(baselines)] if baselines else None,
        "candidate_range": [min(candidates), max(candidates)] if candidates else None,
    }


def write_runs_csv(path: str, rows: List[Dict[str, Any]]) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RUN_CSV_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: ("" if r.get(k) is None else r.get(k))
                             for k in RUN_CSV_FIELDS})


def write_pairs_csv(path: str, analysis: Dict[str, Any]) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=PAIR_CSV_FIELDS)
        writer.writeheader()
        for p in analysis["pairs"]:
            writer.writerow({k: ("" if p.get(k) is None else p.get(k))
                             for k in PAIR_CSV_FIELDS})


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_preflight(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.manifest)
    records = preflight(manifest, args.run_dir)
    print(f"preflight OK: {len(records)} pinned files verified")
    for r in records:
        print(f"  {r.label}: {r.actual_sha256[:12]}... ok")
    return EXIT_OK


def cmd_readiness(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.manifest)
    cfg = manifest["readiness"]
    competing = [p for p in find_competing_processes()
                 if not any(ign in p for ign in cfg.get("ignore_patterns", []))]
    samples, start_utc, end_utc = observe_host(cfg["min_observation_s"])
    gate = evaluate_gate(samples, competing, cfg["min_avg_idle_pct"],
                         cfg["max_load_1min"])
    diag = {
        "start_utc": start_utc, "end_utc": end_utc,
        "duration_s": cfg["min_observation_s"],
        "samples": [asdict(s) for s in samples],
        "competing_processes": competing,
        "top_consumers": top_consumers(),
        "avg_idle_pct": gate.avg_idle_pct,
        "max_load_1min": gate.max_load_1min,
        "passed": gate.passed, "reasons": gate.reasons,
    }
    os.makedirs(args.run_dir, exist_ok=True)
    atomic_write_json(os.path.join(args.run_dir, "readiness.json"), diag)
    lines = [f"host readiness: {'PASS' if gate.passed else 'FAIL'}",
             f"  window {start_utc} .. {end_utc}",
             f"  avg idle: {gate.avg_idle_pct}",
             f"  max 1-min load: {gate.max_load_1min}"]
    lines += [f"  BLOCKED: {r}" for r in gate.reasons]
    atomic_write_text(os.path.join(args.run_dir, "readiness.txt"),
                      "\n".join(lines) + "\n")
    print("\n".join(lines))
    if not gate.passed:
        raise BlockedError("host gate failed; no solver started")
    return EXIT_OK


def cmd_evidence(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.manifest)
    for line in check_correctness_evidence(manifest):
        print(f"  {line}")
    print("correctness evidence OK for the pinned binary pair")
    return EXIT_OK


def cmd_dry_run(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.manifest)
    specs = plan_runs(manifest)
    print("dry-run: the following commands WOULD run (nothing executed):")
    for s in specs:
        print(f"  pair {s.pair} {s.order_in_pair} [{s.impl}]: {' '.join(s.argv)}")
    print("dry-run complete: no solver started (pass --execute to run).")
    return EXIT_OK


def cmd_run(args: argparse.Namespace) -> int:
    if not args.execute:
        print("refusing to execute: pass --execute to launch real binaries.")
        print("Use 'dry-run' to preview commands.")
        return EXIT_CONFIG
    manifest = load_manifest(args.manifest)
    records = preflight(manifest, args.run_dir)
    os.makedirs(args.run_dir, exist_ok=True)
    atomic_write_json(os.path.join(args.run_dir, "preflight.json"),
                      [asdict(r) for r in records])
    for line in check_correctness_evidence(manifest):
        print(f"  evidence: {line}")
    cfg = manifest["readiness"]
    competing = [p for p in find_competing_processes()
                 if not any(ign in p for ign in cfg.get("ignore_patterns", []))]
    samples, start_utc, end_utc = observe_host(cfg["min_observation_s"])
    gate = evaluate_gate(samples, competing, cfg["min_avg_idle_pct"],
                         cfg["max_load_1min"])
    atomic_write_json(os.path.join(args.run_dir, "readiness.json"), {
        "start_utc": start_utc, "end_utc": end_utc,
        "samples": [asdict(s) for s in samples],
        "passed": gate.passed, "reasons": gate.reasons})
    if not gate.passed:
        raise BlockedError(f"host gate failed: {gate.reasons}")
    specs = plan_runs(manifest)
    print("executing:")
    for s in specs:
        print(f"  pair {s.pair} {s.order_in_pair} [{s.impl}]: {' '.join(s.argv)}")

    def _inter_pair() -> Tuple[GateResult, List[HostSample], List[str]]:
        return inter_pair_health_check(
            manifest,
            duration_s=float(cfg.get("inter_pair_observation_s", 20.0)),
            sample_interval_s=5.0)

    launcher = (timev_launcher if manifest.get("use_time_v", True)
                else default_launcher)
    rows = execute_plan(manifest, args.run_dir, specs,
                        launcher=launcher,
                        inter_pair_check=_inter_pair)
    write_runs_csv(os.path.join(args.run_dir, "runs.csv"), rows)
    analysis = analyze_rows(rows)
    write_pairs_csv(os.path.join(args.run_dir, "pairs.csv"), analysis)
    atomic_write_json(os.path.join(args.run_dir, "analysis.json"), analysis)
    print(f"completed {len(rows)} runs, {analysis['complete_pairs']} complete pairs")
    print(f"median reduction: {analysis['median_reduction_percent']}")
    return EXIT_OK


def cmd_analyze(args: argparse.Namespace) -> int:
    path = os.path.join(args.run_dir, "runs.csv")
    if not os.path.isfile(path):
        raise ConfigError(f"no runs.csv in {args.run_dir}")
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in ("pair", "exit_status"):
            if r.get(k) not in (None, ""):
                r[k] = int(r[k])
        for k in ("nodes", "solutions", "dead_ends", "peak_rss_kb"):
            if r.get(k) not in (None, ""):
                try:
                    r[k] = int(float(r[k]))
                except ValueError:
                    pass
        for k in ("internal_elapsed_s", "internal_nodes_per_sec",
                  "external_elapsed_s"):
            if r.get(k) not in (None, ""):
                try:
                    r[k] = float(r[k])
                except ValueError:
                    pass
    analysis = analyze_rows(rows)
    print(json.dumps(analysis, indent=2))
    return EXIT_OK


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail-closed paired benchmark harness (dry-run by default).")
    parser.add_argument("--manifest", default="benchmark_manifest.json")
    parser.add_argument("--run-dir", default="run")
    sub = parser.add_subparsers(dest="mode", required=True)
    sub.add_parser("preflight")
    sub.add_parser("readiness")
    sub.add_parser("evidence")
    sub.add_parser("dry-run")
    run_p = sub.add_parser("run")
    run_p.add_argument("--execute", action="store_true",
                       help="explicit opt-in: actually launch solver binaries")
    sub.add_parser("analyze")
    args = parser.parse_args(argv)
    try:
        if args.mode == "preflight":
            return cmd_preflight(args)
        if args.mode == "readiness":
            return cmd_readiness(args)
        if args.mode == "evidence":
            return cmd_evidence(args)
        if args.mode == "dry-run":
            return cmd_dry_run(args)
        if args.mode == "run":
            return cmd_run(args)
        if args.mode == "analyze":
            return cmd_analyze(args)
    except HarnessError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return exc.exit_code
    return EXIT_CONFIG


if __name__ == "__main__":
    sys.exit(main())
