#!/usr/bin/env bash
# TW1-39 future workload diagnostic run. NOT executed during TW1-39.
# The operator runs this manually ONLY after the harness readiness gate
# passes, and only to collect workload-exposure counters — never for
# release-performance comparison.
set -euo pipefail
cd "$(dirname "$0")"

DIAG_BIN="./solver_mrv_scan_diagnostic"
PLACEMENT="/home/philip/Work/fitpolycubes/placements_W_5x7x9.txt"
OUTDIR="${1:?usage: run_workload_diagnostic.sh <fresh-output-dir>}"

if [ -e "$OUTDIR" ]; then
    echo "REFUSING: output dir already exists: $OUTDIR" >&2
    exit 2
fi
echo "=== preflight (expected hashes pinned below) ==="
echo "diagnostic source: f337984abaa67abbc75b505b9f38fdcd30d84cb3defc6c780dafb34d3df5c5b3"
sha256sum solver_mrv_scan_diagnostic.cpp
echo "placement (W 5x7x9): a7a421cde69049fcfa7fd7ee8aa71a82a4ad4c7bfc9631c04ab035d663f8b045"
sha256sum "$PLACEMENT"
sha256sum "$DIAG_BIN"
strings "$DIAG_BIN" | grep -q "MRV-DIAG" \
    || { echo "REFUSING: binary lacks MRV-DIAG marker (not the diagnostic build)" >&2; exit 2; }

mkdir -p "$OUTDIR"
echo "=== workload run (instrumented; elapsed time NOT for release comparison) ==="
echo "CMD: $DIAG_BIN W 5 7 9 $PLACEMENT 2500000 --connectivity --symmetry --region-prune=propagate"
"$DIAG_BIN" W 5 7 9 "$PLACEMENT" 2500000 \
    --connectivity --symmetry --region-prune=propagate \
    > "$OUTDIR/workload_stdout.log" 2> "$OUTDIR/workload_stderr.log"
echo "exit=$?"
echo "=== MRV-DIAG counters ==="
grep "MRV-DIAG" "$OUTDIR/workload_stderr.log" || echo "(no MRV-DIAG line found)"
echo "logs in $OUTDIR"
