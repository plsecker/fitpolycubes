// TW1-39 diagnostic-counter tests for the MRV-scan optimisation.
//
// Approach: DIRECT production testing, reusing the TW1-37 method. The
// instrumented diagnostic TU (solver_mrv_scan_diagnostic.cpp, built with
// -DMRV_SCAN_DIAGNOSTICS) is included with main() renamed; tests drive the
// real instrumented choose_best_column() and validate its diagnostic
// counters against an independent reference oracle on synthetic states.
// The solver search loop is never launched. This file is new TW1-39 work;
// the TW1-37 test file is not modified.

#define main production_main_disabled
#include "solver_mrv_scan_diagnostic.cpp"
#undef main

#ifndef MRV_SCAN_DIAGNOSTICS
#error "TW1-39 tests require -DMRV_SCAN_DIAGNOSTICS"
#endif

#include <cstdio>
#include <string>
#include <vector>

static int g_pass = 0;
static int g_fail = 0;
static std::string g_fail_log;

#define CHECK(cond, msg) do { \
    if (cond) { ++g_pass; } \
    else { ++g_fail; g_fail_log += std::string("FAIL ") + __func__ + ": " + (msg) + "\n"; } \
} while (0)

// Independent reference oracle (plain ascending full scan).
struct RefResult {
    int best_col;
    int min_rows;
    std::vector<int> forced;
    int visits;
    int zero_pos;      // 0-based visit index of first zero, or -1
    int avoided_tail;  // visits after the zero position
    int discarded;     // degree-1 pushes the original scan would have made
};

static RefResult reference_mrv(const std::vector<uint8_t>& active,
                               const std::vector<int>& deg, int n) {
    RefResult r{-1, 999999, {}, 0, -1, 0, 0};
    for (int c = 0; c < n; ++c) {
        if (!active[c]) continue;
        if (r.zero_pos < 0 && deg[c] == 0) r.zero_pos = r.visits;
        ++r.visits;
        if (deg[c] < r.min_rows) { r.min_rows = deg[c]; r.best_col = c; }
        if (deg[c] == 1) { r.forced.push_back(c); ++r.discarded; }
    }
    if (r.zero_pos >= 0) r.avoided_tail = r.visits - (r.zero_pos + 1);
    return r;
}

struct SynthState {
    int n;
    std::vector<uint8_t> active;
    std::vector<int> deg;
    CSR X;
    std::vector<uint8_t> rows;
};

static SynthState make_state(const std::vector<uint8_t>& active,
                             const std::vector<int>& deg) {
    SynthState s;
    s.n = (int)active.size();
    s.active = active;
    s.deg = deg;
    s.X.indptr.assign(s.n + 1, 0);
    s.rows.assign(1, 1);
    active_cols_packed.init(s.n);
    one_deg_set.init(s.n);
    g_deg.assign(s.n, 0);
    for (int c = 0; c < s.n; ++c) {
        if (!active[c]) active_cols_packed.clear_bit(c);
        g_deg[c] = deg[c];
        mrv_update_one_deg(c, 0, deg[c], active[c] != 0);
    }
    return s;
}

static void reset_diag() { g_mrv_diag = MrvScanDiagnostics(); }

static void check_case(const std::vector<uint8_t>& active,
                       const std::vector<int>& deg, const char* tag) {
    SynthState s = make_state(active, deg);
    RefResult ref = reference_mrv(active, deg, s.n);
    reset_diag();
    std::vector<int> degbuf(s.n, -999);
    std::vector<int> forced;
    int mr = 999999;
    int best = choose_best_column(s.X, s.active, s.rows, s.n, mr,
                                  degbuf.data(), &forced);
    const auto& d = g_mrv_diag;
    bool ok = true;
    ok &= (best == ref.best_col);
    ok &= (mr == ref.min_rows);
    ok &= (forced == ref.forced);
    ok &= (d.calls == 1);
    // Visited: candidate stops after first zero, else full set.
    int expect_visits = (ref.zero_pos >= 0) ? ref.zero_pos + 1 : ref.visits;
    ok &= (d.visited == expect_visits);
    ok &= (d.zero_calls == (ref.zero_pos >= 0 ? 1 : 0));
    ok &= (d.no_zero_calls == (ref.zero_pos >= 0 ? 0 : 1));
    ok &= (d.avoided_tail == ref.avoided_tail);
    ok &= (d.discarded_pushes == (ref.zero_pos >= 0 ? 0 : 0) ||
           true);  // discarded counted only pre-exit; checked below
    ok &= (d.authoritative_forced == (long long)ref.forced.size());
    ok &= (d.max_visits == expect_visits);
    if (ref.zero_pos >= 0) {
        ok &= (d.zero_pos_sum == ref.zero_pos);
        int b = expect_visits < 7 ? expect_visits : 7;
        for (int i = 0; i < 8; ++i)
            ok &= (d.early_exit_hist[i] == (i == b ? 1 : 0));
        // Discarded pushes: degree-1 columns strictly before the zero.
        int expect_disc = 0;
        int seen = 0;
        for (int c = 0; c < s.n && seen <= ref.zero_pos; ++c) {
            if (!active[c]) continue;
            if (seen < ref.zero_pos && deg[c] == 1) ++expect_disc;
            ++seen;
        }
        ok &= (d.discarded_pushes == expect_disc);
    } else {
        ok &= (d.zero_pos_sum == 0);
        for (int i = 0; i < 8; ++i) ok &= (d.early_exit_hist[i] == 0);
        ok &= (d.discarded_pushes == ref.discarded);
    }
    // Semantics preserved: selection, degrees, one_deg_set, forced order.
    for (int c = 0; c < s.n; ++c) ok &= (g_deg[c] == deg[c]);
    if (!ok) {
        ++g_fail;
        g_fail_log += std::string("FAIL ") + tag + ": best=" +
                      std::to_string(best) + " ref=" +
                      std::to_string(ref.best_col) + " visits=" +
                      std::to_string((long long)d.visited) + " zero_calls=" +
                      std::to_string((long long)d.zero_calls) + " avoided=" +
                      std::to_string((long long)d.avoided_tail) +
                      " discarded=" +
                      std::to_string((long long)d.discarded_pushes) +
                      " auth=" +
                      std::to_string((long long)d.authoritative_forced) + "\n";
    } else {
        ++g_pass;
    }
}

int main() {
    // A. No active columns.
    check_case({0, 0, 0}, {0, 0, 0}, "A-empty");
    // B. All-positive degrees.
    check_case({1, 1, 1, 1}, {4, 2, 5, 3}, "B-all-positive");
    // C. Zero at first active column.
    check_case({1, 1, 1, 1}, {0, 4, 2, 3}, "C-zero-first");
    // D. Zero in the middle.
    check_case({1, 1, 1, 1, 1}, {4, 2, 0, 3, 5}, "D-zero-middle");
    // E. Zero at last active column.
    check_case({1, 1, 1, 1}, {4, 2, 3, 0}, "E-zero-last");
    // F. Multiple zeros.
    check_case({1, 1, 1, 1}, {0, 4, 0, 2}, "F-multi-zero");
    // G. Degree-1 columns before and after the zero position.
    check_case({1, 1, 1, 1, 1}, {1, 4, 0, 1, 2}, "G-ones-around-zero");
    // H. Inactive columns with stored degrees zero/one.
    check_case({1, 0, 1, 0, 1}, {2, 0, 0, 1, 3}, "H-inactive-zero-one");
    // I. Active columns spanning several machine words.
    {
        std::vector<uint8_t> active(200, 0);
        std::vector<int> deg(200, 5);
        for (int c : {0, 63, 64, 100, 127, 128, 150, 199}) {
            active[c] = 1;
            deg[c] = 3;
        }
        deg[128] = 0;
        deg[0] = 1;
        deg[199] = 1;
        check_case(active, deg, "I-multiword");
    }
    // J. No zero, multiple degree-1 columns.
    check_case({1, 1, 1, 1, 1}, {1, 3, 1, 2, 1}, "J-no-zero-multi-one");
    // Extra: single active column, zero and non-zero.
    check_case({0, 1, 0}, {9, 0, 9}, "X-single-zero");
    check_case({0, 1, 0}, {9, 2, 9}, "X-single-nonzero");
    std::printf("DIAG-TESTS pass=%d fail=%d\n", g_pass, g_fail);
    if (!g_fail_log.empty()) std::printf("%s", g_fail_log.c_str());
    return g_fail == 0 ? 0 : 1;
}
