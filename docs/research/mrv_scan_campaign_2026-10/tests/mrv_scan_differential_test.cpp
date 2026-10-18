// TW1-37 differential tests for the TW1-29 MRV-scan optimisation.
//
// Approach: DIRECT production testing. The actual production translation
// unit is included with its main() renamed, so these tests drive the real
// PackedActiveCols::for_each_until, the real choose_best_column(), the real
// mrv_update_one_deg() and the real one_deg_set — never a re-implementation.
// The solver's search loop is never launched; only synthetic states are fed
// to the MRV functions. The oracle is an independent, obviously-correct
// ascending full scan written from the reference semantics (not a copy of
// the candidate logic).
//
// Build: g++ -O2 -std=c++17 -pthread (plus -fsanitize=address,undefined
// for the sanitizer variants). See run_tests.sh.

#define main production_main_disabled
// TW43 archive adaptation: original line was
//   #include "/tmp/pentacube-bench/tw29/solver_mrv_scan.cpp"
// rewritten to a path relative to this archive so the test builds on any
// machine. The referenced file is the verbatim TW1-29 candidate
// (SHA256 274c3796c00658e1e4eee4b56304c86a7a470e05bd8f3aa3bef6e6be85bfb418).
#include "../sources/candidates/solver_mrv_scan.cpp"
#undef main

#include <cstdio>
#include <random>
#include <set>
#include <string>
#include <vector>

// ---------------------------------------------------------------------------
// Minimal test framework (no dependencies)
// ---------------------------------------------------------------------------
static int g_pass = 0;
static int g_fail = 0;
static std::string g_fail_log;

#define CHECK(cond, msg) do { \
    if (cond) { ++g_pass; } \
    else { ++g_fail; g_fail_log += std::string("FAIL ") + __func__ + ": " + (msg) + "\n"; } \
} while (0)

// ---------------------------------------------------------------------------
// Independent reference oracle (plain ascending scan over vectors)
// ---------------------------------------------------------------------------
struct RefResult {
    int best_col;
    int min_rows;
    std::vector<int> forced;  // ascending degree-1 active columns
    int visits;               // columns examined by the full scan
};

static RefResult reference_mrv(const std::vector<uint8_t>& active,
                               const std::vector<int>& deg, int n) {
    RefResult r{-1, 999999, {}, 0};
    for (int c = 0; c < n; ++c) {
        if (!active[c]) continue;
        ++r.visits;
        if (deg[c] < r.min_rows) { r.min_rows = deg[c]; r.best_col = c; }
        if (deg[c] == 1) r.forced.push_back(c);
    }
    return r;
}

// ---------------------------------------------------------------------------
// State setup through the REAL production maintenance path
// ---------------------------------------------------------------------------
struct SynthState {
    int n;
    std::vector<uint8_t> active;
    std::vector<int> deg;
    CSR X;  // dummy (scan does not read X; kept for call signature)
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
    // Reset production structures exactly as the search maintains them:
    // packed bits mirror the active vector (init() sets all bits, then
    // clear_bit() removes inactive ones — mirroring production, where
    // init runs at depth 0 with all columns active and clear_bit fires
    // on deactivation); g_deg holds degrees; one_deg_set is built
    // through the real mrv_update_one_deg().
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

struct CandResult {
    int best_col;
    int min_rows;
    std::vector<int> forced;
    int scan_visits;  // counted via a parallel for_each_until probe
};

static CandResult run_candidate(SynthState& s, int* deg_out,
                                std::vector<int>* forced_out) {
    CandResult r;
    if (forced_out) forced_out->clear();
    int mr = 999999;
    r.best_col = choose_best_column(s.X, s.active, s.rows, s.n, mr,
                                    deg_out, forced_out);
    r.min_rows = mr;
    if (forced_out) r.forced = *forced_out;
    // Count visits with an identical probe (same order, same stop rule).
    int visits = 0;
    active_cols_packed.for_each_until([&](int c) {
        ++visits;
        return g_deg[c] == 0;
    });
    r.scan_visits = visits;
    return r;
}

// ---------------------------------------------------------------------------
// A. Packed active-column iteration
// ---------------------------------------------------------------------------
static void test_packed_empty() {
    active_cols_packed.init(100);
    active_cols_packed.clear();  // init() sets all bits; clear empties
    int visits = 0;
    active_cols_packed.for_each([&](int) { ++visits; });
    CHECK(visits == 0, "empty set: for_each visits 0");
    visits = 0;
    active_cols_packed.for_each_until([&](int) { ++visits; return true; });
    CHECK(visits == 0, "empty set: for_each_until visits 0");
}

static void test_packed_single() {
    active_cols_packed.init(100);
    active_cols_packed.clear();
    active_cols_packed.set(42);
    std::vector<int> got;
    active_cols_packed.for_each([&](int c) { got.push_back(c); });
    CHECK(got.size() == 1 && got[0] == 42, "single column yielded");
    int visits = 0;
    active_cols_packed.for_each_until([&](int c) {
        ++visits;
        return c == 42;
    });
    CHECK(visits == 1, "single column early-stop visits 1");
}

static void test_packed_ascending_order() {
    active_cols_packed.init(200);
    active_cols_packed.clear();
    std::vector<int> expect = {0, 1, 63, 64, 65, 127, 128, 199};
    for (int c : expect) active_cols_packed.set(c);
    std::vector<int> got;
    active_cols_packed.for_each([&](int c) { got.push_back(c); });
    CHECK(got == expect, "ascending order across word boundaries");
}

static void test_packed_stop_positions() {
    active_cols_packed.init(200);
    active_cols_packed.clear();
    for (int c = 10; c < 20; ++c) active_cols_packed.set(c);
    int visits = 0;
    active_cols_packed.for_each_until([&](int) { ++visits; return true; });
    CHECK(visits == 1, "stop at first element visits 1");
    visits = 0;
    active_cols_packed.for_each_until([&](int c) {
        ++visits;
        return c == 14;
    });
    CHECK(visits == 5, "stop in middle visits 5");
    visits = 0;
    active_cols_packed.for_each_until([&](int c) {
        ++visits;
        return c == 19;
    });
    CHECK(visits == 10, "stop at final element visits 10");
    visits = 0;
    active_cols_packed.for_each_until([&](int) { ++visits; return false; });
    CHECK(visits == 10, "never-stop visits all 10");
}

static void test_packed_word_boundaries() {
    // Boundary indices 63/64, 127/128; final partial word; inactive gaps.
    active_cols_packed.init(130);  // 3 words, last holds 130-128=2 bits
    active_cols_packed.clear();
    std::vector<int> expect = {0, 62, 63, 64, 65, 126, 127, 128, 129};
    for (int c : expect) active_cols_packed.set(c);
    std::vector<int> got;
    active_cols_packed.for_each([&](int c) { got.push_back(c); });
    CHECK(got == expect, "word boundaries incl. partial final word");
    // Inactive bits never yielded: set then clear a neighbour.
    active_cols_packed.set(100);
    active_cols_packed.clear_bit(100);
    got.clear();
    active_cols_packed.for_each([&](int c) { got.push_back(c); });
    CHECK(got == expect, "cleared bit never yielded");
    // Padding bits beyond num_cols never yielded.
    active_cols_packed.init(65);  // word 1 has 1 valid bit
    for (int c = 0; c < 65; ++c) active_cols_packed.set(c);
    got.clear();
    active_cols_packed.for_each([&](int c) { got.push_back(c); });
    CHECK((int)got.size() == 65 && got.back() == 64, "no padding bits yielded");
}

static void test_packed_until_matches_foreach_when_no_stop() {
    active_cols_packed.init(150);
    active_cols_packed.clear();
    for (int c = 0; c < 150; c += 3) active_cols_packed.set(c);
    std::vector<int> a, b;
    active_cols_packed.for_each([&](int c) { a.push_back(c); });
    active_cols_packed.for_each_until([&](int c) {
        b.push_back(c);
        return false;
    });
    CHECK(a == b, "for_each_until(false) == for_each sequence");
}

// ---------------------------------------------------------------------------
// B. MRV minimum and tie-breaking (candidate vs independent reference)
// ---------------------------------------------------------------------------
static void check_state(const std::vector<uint8_t>& active,
                        const std::vector<int>& deg, const char* tag) {
    SynthState s = make_state(active, deg);
    RefResult ref = reference_mrv(active, deg, s.n);
    std::vector<int> degbuf(s.n, -999);
    std::vector<int> forced;
    CandResult cand = run_candidate(s, degbuf.data(), &forced);
    CHECK(cand.best_col == ref.best_col,
          std::string(tag) + ": best_col match");
    CHECK(cand.min_rows == ref.min_rows,
          std::string(tag) + ": min_rows match");
    CHECK(cand.forced == ref.forced,
          std::string(tag) + ": forced set match");
    // Early exit must return the same column as the full scan even with
    // several degree-0 columns (ascending order => lowest index wins).
    if (ref.min_rows == 0) {
        int first_zero = -1;
        for (int c = 0; c < s.n; ++c)
            if (active[c] && deg[c] == 0) { first_zero = c; break; }
        CHECK(cand.best_col == first_zero,
              std::string(tag) + ": zero tie-break = lowest index");
    }
}

static void test_mrv_targeted_states() {
    // All positive, unique min first/middle/last.
    check_state({1, 1, 1, 1}, {1, 5, 3, 4}, "min-first");
    check_state({1, 1, 1, 1}, {5, 1, 3, 4}, "min-middle");
    check_state({1, 1, 1, 1}, {5, 3, 4, 1}, "min-last");
    // Ties.
    check_state({1, 1, 1, 1}, {2, 2, 2, 2}, "all-tie");
    check_state({1, 1, 1, 1}, {3, 1, 4, 1}, "tie-middle-last");
    // Zero minima.
    check_state({1, 1, 1, 1}, {0, 5, 3, 4}, "zero-first");
    check_state({1, 1, 1, 1}, {5, 0, 3, 4}, "zero-middle");
    check_state({1, 1, 1, 1}, {5, 3, 4, 0}, "zero-last");
    check_state({1, 1, 1, 1}, {0, 5, 0, 4}, "multi-zero");
    check_state({1, 1, 1, 1}, {0, 0, 0, 0}, "all-zero");
    // Inactive zero-degree columns must not win.
    check_state({0, 1, 1, 0}, {0, 5, 3, 0}, "inactive-zero-ignored");
    // Empty / single / all-one.
    check_state({0, 0, 0, 0}, {0, 0, 0, 0}, "no-active");
    check_state({0, 0, 1, 0}, {9, 9, 7, 9}, "single-active");
    check_state({1, 1, 1}, {1, 1, 1}, "all-one");
    // Zero-degree active plus degree-1 columns (forced still collected).
    check_state({1, 1, 1, 1}, {0, 1, 1, 2}, "zero-plus-forced");
    // Degree-1 columns before and after the minimum.
    check_state({1, 1, 1, 1, 1}, {1, 4, 1, 2, 1}, "ones-around-min");
}

// ---------------------------------------------------------------------------
// C. Forced-placement collection incl. zero-degree path + one_deg_set order
// ---------------------------------------------------------------------------
static void test_forced_consumption_contract() {
    // The production caller returns on (best==-1 || min==0) BEFORE reading
    // prop_forced. Here we verify the candidate still produces the complete
    // reference forced set on zero-degree states (so even a future caller
    // reading it would see correct contents), and that the empty case works.
    {
        SynthState s = make_state({1, 1, 1}, {0, 1, 2});
        std::vector<int> forced;
        CandResult cand = run_candidate(s, nullptr, &forced);
        CHECK(cand.best_col == 0 && cand.min_rows == 0, "zero state selected");
        CHECK(forced == std::vector<int>({1}), "forced complete on zero path");
    }
    {
        SynthState s = make_state({1, 1}, {3, 4});
        std::vector<int> forced;
        run_candidate(s, nullptr, &forced);
        CHECK(forced.empty(), "no degree-1 => empty forced");
    }
    {
        // Inactive column with stored degree 1 must not appear.
        SynthState s = make_state({1, 0, 1}, {1, 1, 1});
        std::vector<int> forced;
        run_candidate(s, nullptr, &forced);
        CHECK(forced == (std::vector<int>{0, 2}), "inactive deg-1 excluded");
    }
}

static void test_one_deg_set_order_and_membership() {
    const int n = 200;
    active_cols_packed.init(n);
    one_deg_set.init(n);
    g_deg.assign(n, 5);
    // Insert in scrambled order through the real maintenance function.
    std::vector<int> cols = {150, 3, 64, 63, 129, 0, 199};
    for (int c : cols) {
        active_cols_packed.set(c);
        g_deg[c] = 1;
        mrv_update_one_deg(c, 5, 1, true);
    }
    std::vector<int> got;
    one_deg_set.for_each([&](int c) { got.push_back(c); });
    std::vector<int> expect = {0, 3, 63, 64, 129, 150, 199};
    CHECK(got == expect, "one_deg_set iterates ascending regardless of insert order");
    // Erase half; order preserved, size tracked.
    mrv_update_one_deg(63, 1, 4, true);
    mrv_update_one_deg(0, 1, 0, false);  // deactivated
    got.clear();
    one_deg_set.for_each([&](int c) { got.push_back(c); });
    CHECK(got == (std::vector<int>{3, 64, 129, 150, 199}), "erase paths correct");
    CHECK(one_deg_set.size() == 5, "size tracked");
}

// ---------------------------------------------------------------------------
// D. Aliased output pointers
// ---------------------------------------------------------------------------
static void test_deg_out_alias_invariant() {
    // Production call sites (verified by source audit): the only non-null
    // deg_out is g_deg.data() (self-copy), others pass nullptr.
    SynthState s = make_state({1, 1, 1, 1}, {4, 0, 2, 1});
    std::vector<int> before = g_deg;
    std::vector<int> forced;
    run_candidate(s, g_deg.data(), &forced);
    CHECK(g_deg == before, "aliased deg_out write is a self-copy no-op");
    // nullptr deg_out path.
    SynthState s2 = make_state({1, 1, 1, 1}, {4, 0, 2, 1});
    CandResult cand = run_candidate(s2, nullptr, &forced);
    CHECK(cand.best_col == 1 && cand.min_rows == 0, "nullptr deg_out path correct");
}

static void test_deg_out_distinct_buffer_bound() {
    // With a DISTINCT buffer, early exit leaves trailing columns unwritten.
    // Document the exact bound: every visited column matches the reference;
    // divergence is confined to columns after the first degree-0 column.
    const int n = 8;
    SynthState s = make_state({1, 1, 1, 1, 1, 1, 1, 1},
                              {5, 4, 0, 3, 2, 1, 6, 7});
    std::vector<int> buf(n, -999);
    std::vector<int> forced;
    CandResult cand = run_candidate(s, buf.data(), &forced);
    CHECK(cand.best_col == 2, "early exit selects lowest zero");
    for (int c = 0; c <= 2; ++c)
        CHECK(buf[c] == s.deg[c], "visited columns written");
    for (int c = 3; c < n; ++c)
        CHECK(buf[c] == -999, "unvisited trailing columns untouched");
    CHECK(cand.forced == std::vector<int>({5}), "forced still complete");
}

// ---------------------------------------------------------------------------
// E. State variants: exhaustive small + deterministic pseudorandom
// ---------------------------------------------------------------------------
static void test_exhaustive_small_states() {
    // n=3: all active masks x degrees 0..2 on active cols.
    int checked = 0;
    for (int mask = 0; mask < 8; ++mask) {
        std::vector<int> actives;
        for (int c = 0; c < 3; ++c)
            if (mask & (1 << c)) actives.push_back(c);
        std::vector<int> degs(3, 0);
        // Enumerate degree assignments via base-3 counter over active cols.
        int total = 1;
        for (size_t i = 0; i < actives.size(); ++i) total *= 3;
        for (int code = 0; code < total; ++code) {
            std::vector<uint8_t> active(3, 0);
            std::vector<int> deg(3, 0);
            int tmp = code;
            for (int c : actives) {
                active[c] = 1;
                deg[c] = tmp % 3;
                tmp /= 3;
            }
            SynthState s = make_state(active, deg);
            RefResult ref = reference_mrv(active, deg, 3);
            std::vector<int> forced;
            CandResult cand = run_candidate(s, nullptr, &forced);
            if (cand.best_col != ref.best_col ||
                cand.min_rows != ref.min_rows || cand.forced != ref.forced) {
                ++g_fail;
                g_fail_log += "FAIL exhaustive n=3 mask=" +
                              std::to_string(mask) + " code=" +
                              std::to_string(code) + "\n";
            } else {
                ++g_pass;
            }
            ++checked;
        }
    }
    CHECK(checked == 64, "exhaustive n=3 state count (sum 3^popcount = 4^3)");
}

static void test_pseudorandom_states() {
    std::mt19937 rng(20261017u);  // fixed seed, printed on failure
    const int NSTATE = 3000;
    for (int t = 0; t < NSTATE; ++t) {
        int n = 1 + (int)(rng() % 200);  // 1..200 cols (multi-word + edges)
        std::vector<uint8_t> active(n);
        std::vector<int> deg(n);
        for (int c = 0; c < n; ++c) {
            active[c] = (rng() % 100) < 60 ? 1 : 0;
            deg[c] = (int)(rng() % 8);  // 0..7 incl. zeros and ones
        }
        if (t % 7 == 0 && n > 64) {
            // Force word-boundary coverage.
            active[63] = 1;
            active[64] = 1;
            deg[63] = (int)(rng() % 3);
            deg[64] = (int)(rng() % 3);
        }
        SynthState s = make_state(active, deg);
        RefResult ref = reference_mrv(active, deg, n);
        std::vector<int> degbuf(n, -999);
        std::vector<int> forced;
        CandResult cand = run_candidate(s, degbuf.data(), &forced);
        bool ok = (cand.best_col == ref.best_col) &&
                  (cand.min_rows == ref.min_rows) &&
                  (cand.forced == ref.forced);
        // deg_out: visited prefix must match; allow unwritten tail only
        // after a degree-0 early exit.
        if (ok) {
            int stop = n;
            if (ref.min_rows == 0) {
                for (int c = 0; c < n; ++c)
                    if (active[c] && deg[c] == 0) { stop = c + 1; break; }
            }
            for (int c = 0; c < stop && ok; ++c)
                if (active[c] && degbuf[c] != deg[c]) ok = false;
        }
        if (!ok) {
            ++g_fail;
            g_fail_log += "FAIL random t=" + std::to_string(t) + " n=" +
                          std::to_string(n) + " seed=20261017\n";
        } else {
            ++g_pass;
        }
    }
}

int main() {
    test_packed_empty();
    test_packed_single();
    test_packed_ascending_order();
    test_packed_stop_positions();
    test_packed_word_boundaries();
    test_packed_until_matches_foreach_when_no_stop();
    test_mrv_targeted_states();
    test_forced_consumption_contract();
    test_one_deg_set_order_and_membership();
    test_deg_out_alias_invariant();
    test_deg_out_distinct_buffer_bound();
    test_exhaustive_small_states();
    test_pseudorandom_states();
    std::printf("DIFFERENTIAL-TESTS pass=%d fail=%d\n", g_pass, g_fail);
    if (!g_fail_log.empty()) std::printf("%s", g_fail_log.c_str());
    return g_fail == 0 ? 0 : 1;
}
