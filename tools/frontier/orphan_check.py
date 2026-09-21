#!/usr/bin/env python3
"""Detect likely orphaned research/solver child processes (report-only).

OpenWork launches long-running research jobs (V45 shard workers,
validation runs, ...) as subprocesses.  Those children share the
launcher's process group/session (subprocess.Popen without
start_new_session), so when the OpenWork session crashes the children
are reparented to init (pid 1) and keep running -- silently consuming
CPU until noticed (incident 2026-09-21: four validate_bfs_packed.py
processes).

This script is the minimal safety mechanism:

  --register   record a launched job in the registry
               (data/ck6_reuse/openwork_jobs.jsonl)
  --check      (default) report jobs whose launcher is gone (likely
               orphans) and jobs abandoned with an orphaned launcher.
               NEVER kills anything.  Exit code 2 when likely orphans
               are found, 0 otherwise.
  --prune      drop registry entries for dead PIDs or finished jobs.

Policy: report/ask, never blanket-kill.  A new OpenWork session must
run --check before starting any expensive task (see
docs/frontier/OPENWORK_STATUS.md).
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
REGISTRY = os.path.join(REPO, "data", "ck6_reuse", "openwork_jobs.jsonl")


def _now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _ppid_of(pid):
    """Current parent pid of pid, or None if it cannot be read."""
    try:
        with open(f"/proc/{pid}/stat") as f:
            data = f.read()
        # comm may contain spaces and ')' -- everything up to the last
        # ')' is the comm field; ppid follows the state field.
        fields = data[data.rfind(")") + 2:].split()
        return int(fields[1])
    except (OSError, ValueError, IndexError):
        return None


def _load():
    if not os.path.exists(REGISTRY):
        return []
    out = []
    with open(REGISTRY) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"[orphan] skipping unparseable registry line: "
                      f"{line[:80]!r}", file=sys.stderr)
    return out


def register_job(pid, ppid, cmd, done_file=None, expected_s=None,
                 workdir=None):
    """Append one job record to the registry (used by launchers)."""
    os.makedirs(os.path.dirname(REGISTRY), exist_ok=True)
    entry = {
        "pid": int(pid),
        "ppid": int(ppid),
        "cmd": cmd,
        "start": _now_iso(),
        "expected_s": expected_s,
        "done_file": done_file,
        "workdir": workdir,
    }
    with open(REGISTRY, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[orphan] registered pid {pid} (ppid {ppid}) in {REGISTRY}",
          flush=True)


def _classify(entry):
    """Return (kind, detail); kind in
    {'finished','stale','active','orphan'}."""
    pid = entry.get("pid")
    done_file = entry.get("done_file")
    if done_file:
        path = done_file if os.path.isabs(done_file) else \
            os.path.join(REPO, done_file)
        if os.path.exists(path):
            return "finished", "done_file exists"
    if not _alive(pid):
        return "stale", "pid not alive"
    rec_ppid = entry.get("ppid")
    cur_ppid = _ppid_of(pid)
    if rec_ppid is not None and not _alive(rec_ppid):
        return "orphan", \
            f"launcher pid {rec_ppid} is gone (now ppid {cur_ppid})"
    return "active", f"running under launcher pid {rec_ppid}"


def _elapsed(entry):
    try:
        start = datetime.fromisoformat(entry["start"])
        return max(0, int(time.time() - start.timestamp()))
    except (KeyError, ValueError):
        return None


def cmd_check(args):
    entries = _load()
    if not entries:
        print("[orphan] no registered jobs")
        return 0
    kinds = {"finished": [], "stale": [], "active": [], "orphan": [],
             "abandoned": []}
    for e in entries:
        kind, detail = _classify(e)
        kinds[kind].append((e, detail))
    # jobs whose launcher is itself a likely orphan are abandoned with it
    orphan_pids = {e["pid"] for e, _ in kinds["orphan"]}
    if orphan_pids:
        for kind in ("active", "stale"):
            kept = []
            for e, detail in kinds[kind]:
                if e.get("ppid") in orphan_pids:
                    kinds["abandoned"].append(
                        (e, f"launcher pid {e.get('ppid')} is itself "
                             "orphaned"))
                else:
                    kept.append((e, detail))
            kinds[kind] = kept
    for e, detail in kinds["orphan"] + kinds["abandoned"]:
        el = _elapsed(e)
        exp = e.get("expected_s")
        print(f"[orphan] LIKELY ORPHAN pid {e['pid']}: "
              f"{e.get('cmd', '')!r} started {e.get('start')} "
              f"elapsed {el}s"
              + (f" (expected <= {exp}s)" if exp else "")
              + f" -- {detail}")
    for e, detail in kinds["active"]:
        print(f"[orphan] active pid {e['pid']} ({e.get('cmd', '')!r}, "
              f"elapsed {_elapsed(e)}s) -- {detail}")
    for e, detail in kinds["stale"]:
        print(f"[orphan] exited pid {e['pid']} "
              f"({e.get('cmd', '')!r}) -- {detail}")
    for e, detail in kinds["finished"]:
        print(f"[orphan] finished pid {e['pid']} "
              f"({e.get('cmd', '')!r}) -- {detail}")
    n_orphans = len(kinds["orphan"]) + len(kinds["abandoned"])
    print(f"[orphan] {len(entries)} registered: {len(kinds['orphan'])} "
          f"orphan(s), {len(kinds['abandoned'])} abandoned-with-launcher, "
          f"{len(kinds['active'])} active, {len(kinds['stale'])} exited, "
          f"{len(kinds['finished'])} finished")
    if n_orphans:
        print("[orphan] likely orphans found -- verify with the human and "
              "stop only confirmed abandoned jobs (never blanket-kill)",
              file=sys.stderr)
        return 2
    return 0


def cmd_prune(args):
    entries = _load()
    kept = []
    for e in entries:
        kind, _ = _classify(e)
        if kind in ("stale", "finished"):
            print(f"[orphan] pruning pid {e.get('pid')} ({kind})")
        else:
            kept.append(e)
    with open(REGISTRY, "w") as f:
        for e in kept:
            f.write(json.dumps(e) + "\n")
    print(f"[orphan] pruned {len(entries) - len(kept)} of {len(entries)} "
          f"entries; {len(kept)} remain")
    return 0


def cmd_register(args):
    register_job(pid=args.pid, ppid=args.ppid, cmd=args.cmd,
                 done_file=args.done_file, expected_s=args.expected_s,
                 workdir=args.workdir)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--register", action="store_true",
                    help="register a launched job (used by launchers)")
    ap.add_argument("--pid", type=int, help="job pid")
    ap.add_argument("--ppid", type=int, help="launcher pid")
    ap.add_argument("--cmd", help="command line of the job (string)")
    ap.add_argument("--done-file",
                    help="repo-relative or absolute path whose existence "
                         "marks the job finished")
    ap.add_argument("--expected-s", type=int,
                    help="expected duration in seconds (optional)")
    ap.add_argument("--workdir", help="job working directory (optional)")
    ap.add_argument("--prune", action="store_true",
                    help="drop entries for dead or finished jobs")
    args = ap.parse_args()
    if args.register:
        if args.pid is None or args.ppid is None or not args.cmd:
            ap.error("--register requires --pid, --ppid and --cmd")
        return cmd_register(args)
    if args.prune:
        return cmd_prune(args)
    return cmd_check(args)


if __name__ == "__main__":
    sys.exit(main())