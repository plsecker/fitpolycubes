#!/usr/bin/env bash
# TW1-37 differential test runner. Synthetic tests only — never launches
# a production solver search (no V/KSSref/W invocation anywhere here).
set -euo pipefail
cd "$(dirname "$0")"
CXX="${CXX:-g++}"

echo "=== normal build ==="
$CXX -O2 -std=c++17 -pthread mrv_scan_differential_test.cpp \
    -o mrv_scan_differential_test 2>&1 | tee build_normal.log
echo "=== normal run ==="
./mrv_scan_differential_test 2>&1 | tee test_output.txt

echo "=== sanitizer build (ASan+UBSan) ==="
$CXX -O1 -g -std=c++17 -pthread -fsanitize=address,undefined \
    -fno-omit-frame-pointer mrv_scan_differential_test.cpp \
    -o mrv_scan_differential_test_asan 2>&1 | tee build_asan.log
echo "=== sanitizer run ==="
./mrv_scan_differential_test_asan 2>&1 | tee asan_output.txt

echo "=== results summary ==="
grep -h "DIFFERENTIAL-TESTS" test_output.txt asan_output.txt
echo "ALL DIFFERENTIAL TESTS COMPLETE"
