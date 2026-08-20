#!/bin/bash
# Systematic testing of all unresolved S-pentacube cross-sections
# Tests each cross-section with checkpoint/resume support for portability

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PYTHON="${REPO_ROOT}/.venv/bin/python3"
MACRO_SCRIPT="${REPO_ROOT}/tools/frontier/macro_generalized.py"
RESULTS_DIR="/tmp/macro_cross_section_tests"
CHECKPOINT_DIR="/tmp/macro_checkpoints"

mkdir -p "${RESULTS_DIR}"
mkdir -p "${CHECKPOINT_DIR}"

echo "=== S-Pentacube Cross-Section Systematic Test ==="
echo "Started at: $(date)"
echo "Results directory: ${RESULTS_DIR}"
echo "Checkpoint directory: ${CHECKPOINT_DIR}"
echo ""

# Function to test a cross-section with checkpoint support
test_cross_section() {
    local a=$1
    local b=$2
    local max_states=$3
    local timeout_secs=$4
    
    # Canonicalize dimensions (a <= b)
    if [ $a -gt $b ]; then
        local temp=$a
        a=$b
        b=$temp
    fi
    
    local output_file="${RESULTS_DIR}/${a}x${b}_max${max_states}.txt"
    local log_file="${RESULTS_DIR}/${a}x${b}_max${max_states}.log"
    local checkpoint_path="${CHECKPOINT_DIR}/${a}x${b}.ckpt"
    
    echo "Testing ${a}×${b} with max_states=${max_states}, timeout=${timeout_secs}s"
    
    # Check if already completed
    if [ -f "${output_file}" ]; then
        echo "  ✓ Already completed - skipping"
        echo ""
        return 0
    fi
    
    # Check if checkpoint exists (resume)
    local resume_flag=""
    if [ -d "${checkpoint_path}" ]; then
        echo "  Found checkpoint, resuming..."
        resume_flag="--resume ${checkpoint_path}"
    else
        resume_flag="--a ${a} --b ${b}"
    fi
    
    # Run with timeout and checkpointing
    if timeout "${timeout_secs}" "${PYTHON}" "${MACRO_SCRIPT}" \
        ${resume_flag} \
        --max-states "${max_states}" \
        --checkpoint "${checkpoint_path}" \
        --checkpoint-interval 500000 \
        > "${log_file}" 2>&1; then
        
        # Copy results file
        if [ -f "/tmp/macro_generalized_${a}x${b}_results.txt" ]; then
            cp "/tmp/macro_generalized_${a}x${b}_results.txt" "${output_file}"
            echo "  ✓ Completed - results in ${output_file}"
            
            # Optionally remove checkpoint after successful completion
            # rm -rf "${checkpoint_path}"
        else
            echo "  ✗ No results file generated"
        fi
    else
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            echo "  ⏱ Timeout - checkpoint saved at ${checkpoint_path}"
            echo "     Resume with: --resume ${checkpoint_path}"
        else
            echo "  ✗ Error (exit code ${exit_code}) - check ${log_file}"
        fi
    fi
    echo ""
}

# Test matrix: (a, b, max_states, timeout_seconds)
# Start with smaller/easier cases, progress to larger ones

echo "=== Phase 1: Small cross-sections (already done, for reference) ==="
# 4×5: 1,538 states (1s)
# 5×6: 7.9M states (6min)
# 4×8: 30M states (existing work)

echo "=== Phase 2: Medium cross-sections (10M cap, 10min timeout) ==="
test_cross_section 4 9 10000000 600
test_cross_section 5 7 10000000 600
test_cross_section 6 6 10000000 600
test_cross_section 4 10 10000000 600

echo "=== Phase 3: Larger cross-sections (20M cap, 20min timeout) ==="
test_cross_section 5 9 20000000 1200
test_cross_section 6 7 20000000 1200
test_cross_section 4 13 20000000 1200

echo "=== Phase 4: Very large cross-sections (50M cap, 30min timeout) ==="
test_cross_section 6 9 50000000 1800
test_cross_section 7 8 50000000 1800
test_cross_section 4 14 50000000 1800
test_cross_section 5 10 50000000 1800

echo "=== Phase 5: Extremely large cross-sections (100M cap, 60min timeout) ==="
test_cross_section 6 10 100000000 3600
test_cross_section 8 8 100000000 3600
test_cross_section 4 15 100000000 3600

echo "=== Phase 6: Maximum scale (200M cap, 120min timeout) ==="
test_cross_section 8 9 200000000 7200

echo ""
echo "=== Testing Complete ==="
echo "Finished at: $(date)"
echo ""
echo "Results summary:"
ls -lh "${RESULTS_DIR}"/*.txt 2>/dev/null || echo "No results files found"
echo ""
echo "Checkpoints:"
ls -lh "${CHECKPOINT_DIR}"/*.ckpt 2>/dev/null || echo "No checkpoint files found"
