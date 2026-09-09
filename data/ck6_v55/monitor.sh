#!/bin/bash
echo "=== V=55 Status $(date) ==="
echo "Processes:"
ps aux | grep "[t]_ck6_v55_search" | grep -v grep | awk '{print "  PID "$2" CPU "$3"% RSS "($6/1024)"MB elapsed="$10}'
echo "Shard results:"
for f in data/ck6_v55/shard_*.json; do
    [ -f "$f" ] && echo "  $f: $(python3 -c "
import json; r = json.load(open('$f'))
print('targets', r.get('target_occurrences', r.get('targets','?')), 
      'sat', r.get('sat','?'), 'status', r.get('status','?'))" 2>/dev/null)"
done
echo "Checkpoints:"
for f in data/ck6_v55/shard_*.checkpoint.json; do
    [ -f "$f" ] && echo "  $f: $(python3 -c "
import json; r = json.load(open('$f'))
print('targets', r.get('target_occurrences', r.get('targets','?')),
      'elapsed', r.get('elapsed_s','?'))" 2>/dev/null)"
done
echo "STOP marker: $(ls data/ck6_v55/STOP 2>/dev/null || echo 'not present')"
echo "SAT marker: $(ls data/ck6_v55/SAT_FOUND.json 2>/dev/null || echo 'not present')"
echo "Report: $(ls data/ck6_v55/report.json 2>/dev/null || echo 'not present')"
