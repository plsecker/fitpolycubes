#!/usr/bin/env bash
# TW1-40 bounded MRV-scan workload diagnostic.
# INSTRUMENTED BUILD — its elapsed time must NEVER be used for release
# performance comparison. Collects MRV-DIAG workload-exposure counters only.
set -euo pipefail
cd "$(dirname "$0")"

DIAG_SRC="/tmp/pentacube-bench/tw39/solver_mrv_scan_diagnostic.cpp"
DIAG_BIN="/tmp/pentacube-bench/tw39/solver_mrv_scan_diagnostic"
PLACEMENT="/home/philip/Work/fitpolycubes/placements_W_5x7x9.txt"
EXP_SRC="f337984abaa67abbc75b505b9f38fdcd30d84cb3defc6c780dafb34d3df5c5b3"
EXP_BIN="07ab1f93b0e22f4981f8547448f9d0ef3be4d4fabc1e5cf99e24189e4eca00c3"
EXP_PLACE="a7a421cde69049fcfa7fd7ee8aa71a82a4ad4c7bfc9631c04ab035d663f8b045"
OUTDIR="/tmp/pentacube-bench/tw40/diag_run1"
TIMEOUT_S=180
NODE_CAP=250000

if [ "${1:-}" != "--execute" ]; then
    echo "DRY-RUN (no execution). Planned command:" >&2
    echo "  timeout $TIMEOUT_S $DIAG_BIN W 5 7 9 $PLACEMENT $NODE_CAP --connectivity --symmetry --region-prune=propagate" >&2
    echo "Pass --execute to run once. Refusing to execute without opt-in." >&2
    exit 2
fi
if [ -e "$OUTDIR" ]; then
    echo "REFUSING: output dir exists: $OUTDIR" >&2
    exit 2
fi
for spec in "$DIAG_SRC:$EXP_SRC:diagnostic source" "$DIAG_BIN:$EXP_BIN:diagnostic binary" "$PLACEMENT:$EXP_PLACE:placement"; do
    path="${spec%%:*}"; rest="${spec#*:}"; exp="${rest%%:*}"; label="${rest#*:}"
    act="$(sha256sum "$path" | awk '{print $1}')"
    if [ "$act" != "$exp" ]; then
        echo "REFUSING: $label hash mismatch: $act != $exp" >&2
        exit 3
    fi
    echo "hash ok: $label"
done
strings "$DIAG_BIN" | grep -q "MRV-DIAG" \
    || { echo "REFUSING: binary lacks MRV-DIAG marker" >&2; exit 3; }
if pgrep -f "solver_baseline|solver_mrv_scan|solver_activex|solver_overlap" | grep -v pgrep >/dev/null 2>&1; then
    echo "REFUSING: competing solver process present" >&2
    exit 4
fi
mkdir -p "$OUTDIR"
START_TS="$(date -Iseconds)"
PIN0="$(awk '/pswpin/{print $2}' /proc/vmstat)"
POUT0="$(awk '/pswpout/{print $2}' /proc/vmstat)"
echo "INSTRUMENTED diagnostic run starting at $START_TS (timeout ${TIMEOUT_S}s, cap $NODE_CAP nodes)"
set +e
timeout "$TIMEOUT_S" "$DIAG_BIN" W 5 7 9 "$PLACEMENT" "$NODE_CAP" \
    --connectivity --symmetry --region-prune=propagate \
    > "$OUTDIR/workload_stdout.log" 2> "$OUTDIR/workload_stderr.log"
EXIT_STATUS=$?
set -e
END_TS="$(date -Iseconds)"
PIN1="$(awk '/pswpin/{print $2}' /proc/vmstat)"
POUT1="$(awk '/pswpout/{print $2}' /proc/vmstat)"
{
    echo "executable: INSTRUMENTED ($DIAG_BIN)"
    echo "command: timeout $TIMEOUT_S $DIAG_BIN W 5 7 9 $PLACEMENT $NODE_CAP --connectivity --symmetry --region-prune=propagate"
    echo "exit_status: $EXIT_STATUS (124 means external timeout)"
    echo "start_ts: $START_TS"
    echo "end_ts: $END_TS"
    echo "swapin_delta: $((PIN1 - PIN0))"
    echo "swapout_delta: $((POUT1 - POUT0))"
    echo "NOTE: elapsed time is INSTRUMENTED overhead-inclusive; never use for release comparison."
} > "$OUTDIR/run_record.txt"
cat "$OUTDIR/run_record.txt"
echo "=== MRV-DIAG line ==="
grep "MRV-DIAG" "$OUTDIR/workload_stderr.log" || echo "(no MRV-DIAG line)"
exit 0
