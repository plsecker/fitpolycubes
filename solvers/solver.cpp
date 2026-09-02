#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

constexpr int CELLS_PER_PLACEMENT = 5;

// ============================================================
// Feature toggles (default OFF = baseline behaviour preserved)
//   --connectivity[=N]  prune when the remaining region has a
//                       connected component whose size is not a
//                       multiple of the piece size (N = only check
//                       while remaining cells <= N; 0/omitted = always)
//   --symmetry          chiral-safe corner-canonical symmetry breaking
// ============================================================
static bool g_connectivity = false;
static long g_conn_threshold = 0;  // 0 = always check
static bool g_symmetry = false;

// ---- Region feasibility research (overnight task) ----
// --region-prune=colour-global : O(1) incremental checkerboard test on the
//   whole remaining region: |B-W| <= pieces remaining (valid when every
//   placement has colour imbalance exactly 1, verified at startup).
// --region-prune=colour       : same test per connected component, fused
//   into the connectivity BFS (also runs the size % 5 test).
// --research-deadends=K       : sample every K-th MRV dead end and dump the
//   component structure (sizes + colour imbalances) for offline analysis.
static bool g_prune_colour_global = false;
static bool g_prune_colour_comp = false;
static bool g_prune_propagate = false;    // unit propagation on deg-1 cells
static long g_research_every = 0;

static bool g_colour_strong = false;      // all placements have |B-W| == 1
static int g_colour_maxdiff = 0;
static std::vector<uint8_t> g_cell_parity; // (x+y+z) & 1 per cell id
static long long g_rem_colors[2] = {0, 0}; // active cells per parity
static long long g_expected_pieces = 0;    // total pieces in a full tiling
static std::vector<int> g_deg;             // per-cell active placement degree
static std::string g_dump_file;    // --dump=FILE: one solution per line

struct Placement {
    int cells[CELLS_PER_PLACEMENT];
};

struct CSR {
    std::vector<int> data;
    std::vector<int> indptr;
};

struct SearchStats {
    uint64_t nodes = 0;
    uint64_t solutions = 0;
    uint64_t dead_ends = 0;
    uint64_t conn_checks = 0;
    uint64_t conn_pruned = 0;
    uint64_t rej_colour_global = 0;
    uint64_t rej_colour_global_mrv = 0;  // overlap: MRV also dead here
    uint64_t rej_colour_comp = 0;
    uint64_t rej_colour_comp_mrv = 0;
    uint64_t rej_propagate = 0;
    uint64_t propagate_forced_total = 0;  // placements forced across all runs
    uint64_t research_deadends = 0;
    uint64_t research_deadend_mrv_total = 0;
    std::vector<uint64_t> new_rej_depth_hist;  // genuine-new rejections by depth bucket
    int hist_buckets = 32;
    int max_depth = 0;
    uint64_t max_nodes = 0;  // 0 = unlimited
    std::chrono::steady_clock::time_point start_time;
};

std::vector<Placement> load_placements(const std::string& filename) {
    std::ifstream file(filename);
    if (!file) {
        throw std::runtime_error(
            "Could not open placements file: " + filename);
    }

    int count = 0;
    if (!(file >> count) || count < 0) {
        throw std::runtime_error("Invalid placement count");
    }

    std::vector<Placement> placements(static_cast<size_t>(count));

    for (int r = 0; r < count; ++r) {
        for (int j = 0; j < CELLS_PER_PLACEMENT; ++j) {
            if (!(file >> placements[r].cells[j])) {
                throw std::runtime_error(
                    "Invalid placement data at row " +
                    std::to_string(r));
            }

            if (placements[r].cells[j] < 0) {
                throw std::runtime_error(
                    "Negative cell ID in placement data");
            }
        }
    }

    return placements;
}

CSR build_x_csr(const std::vector<Placement>& placements, int num_cols) {
    std::vector<int> counts(num_cols, 0);

    for (const auto& p : placements) {
        for (int j = 0; j < CELLS_PER_PLACEMENT; ++j) {
            const int c = p.cells[j];

            if (c < 0 || c >= num_cols) {
                throw std::runtime_error(
                    "Placement contains cell outside the box");
            }

            ++counts[c];
        }
    }

    CSR x;
    x.indptr.resize(static_cast<size_t>(num_cols) + 1);
    x.indptr[0] = 0;

    for (int c = 0; c < num_cols; ++c) {
        x.indptr[c + 1] = x.indptr[c] + counts[c];
    }

    x.data.resize(static_cast<size_t>(x.indptr[num_cols]));

    std::vector<int> cursor = x.indptr;

    for (int r = 0; r < static_cast<int>(placements.size()); ++r) {
        for (int j = 0; j < CELLS_PER_PLACEMENT; ++j) {
            const int c = placements[r].cells[j];
            x.data[cursor[c]++] = r;
        }
    }

    return x;
}

CSR build_y_csr(const std::vector<Placement>& placements) {
    CSR y;
    const int num_rows = static_cast<int>(placements.size());

    y.indptr.resize(static_cast<size_t>(num_rows) + 1);
    y.indptr[0] = 0;

    for (int r = 0; r < num_rows; ++r) {
        y.indptr[r + 1] = y.indptr[r] + CELLS_PER_PLACEMENT;
    }

    y.data.resize(static_cast<size_t>(y.indptr[num_rows]));

    for (int r = 0; r < num_rows; ++r) {
        const int start = y.indptr[r];

        for (int j = 0; j < CELLS_PER_PLACEMENT; ++j) {
            y.data[start + j] = placements[r].cells[j];
        }
    }

    return y;
}

int choose_best_column(
    const CSR& X,
    const std::vector<uint8_t>& active_cols,
    const std::vector<uint8_t>& active_rows,
    int num_cols,
    int& min_rows,
    int* deg_out = nullptr,
    std::vector<int>* forced_out = nullptr)
{
    int best_col = -1;
    min_rows = 999999;

    for (int c = 0; c < num_cols; ++c) {
        if (!active_cols[c]) {
            continue;
        }

        int count = 0;

        const int start = X.indptr[c];
        const int end = X.indptr[c + 1];

        for (int k = start; k < end; ++k) {
            if (active_rows[X.data[k]]) {
                ++count;
            }
        }

        if (deg_out) {
            deg_out[c] = count;
        }
        if (forced_out && count == 1) {
            forced_out->push_back(c);
        }

        if (count < min_rows) {
            min_rows = count;
            best_col = c;

            if (count == 0) {
                break;
            }
        }
    }

    return best_col;
}

// ============================================================
// Connectivity / component pruning
//
// Every remaining piece is a face-connected polycube of exactly
// CELLS_PER_PLACEMENT cells. A piece therefore covers cells inside a
// single connected component of the uncovered region, so each
// component must be exactly tileable by whole pieces and its cell
// count must be a multiple of CELLS_PER_PLACEMENT. A region with any
// component whose size % CELLS_PER_PLACEMENT != 0 is provably
// untileable -> prune. This is a necessary condition only; it never
// removes a solvable subtree.
// ============================================================
struct Connectivity {
    int num_cols = 0;
    std::vector<int> nbr_start;              // num_cols+1 (up to 6 neighbours)
    std::vector<int> nbr_flat;               // neighbour ids (-1 padding)
    std::vector<int> stamp;                  // visited stamps per cell
    std::vector<int> queue;                  // BFS queue buffer
    long long gen = 0;

    void init(int a, int b, int c) {
        num_cols = a * b * c;
        nbr_start.assign(static_cast<size_t>(num_cols) + 1, 0);
        // id = x + a*y + a*b*z
        std::vector<int> tmp;
        tmp.reserve(6);
        for (int id = 0; id < num_cols; ++id) {
            const int x = id % a;
            const int y = (id / a) % b;
            const int z = id / (a * b);
            tmp.clear();
            if (x > 0)     tmp.push_back(id - 1);
            if (x < a - 1) tmp.push_back(id + 1);
            if (y > 0)     tmp.push_back(id - a);
            if (y < b - 1) tmp.push_back(id + a);
            if (z > 0)     tmp.push_back(id - a * b);
            if (z < c - 1) tmp.push_back(id + a * b);
            for (int n : tmp) {
                nbr_flat.push_back(n);
            }
            nbr_start[id + 1] = static_cast<int>(nbr_flat.size());
        }
        stamp.assign(static_cast<size_t>(num_cols), 0);
        queue.assign(static_cast<size_t>(num_cols), 0);
        gen = 0;
    }

    // Walks the connected components of the active cells.
    // Returns 0 = feasible, 1 = size % 5 failure, 2 = colour failure.
    // Per component: size must be a multiple of CELLS_PER_PLACEMENT and,
    // when the strong colour invariant holds (every placement covers a
    // 3/2 checkerboard split), the colour imbalance must satisfy
    // |B - W| <= size / CELLS_PER_PLACEMENT.
    int region_tileable(const std::vector<uint8_t>& active_cols,
                        long long* bw_out = nullptr) {
        ++gen;
        int reason = 0;
        if (bw_out) { *bw_out = 0; }
        for (int s = 0; s < num_cols; ++s) {
            if (!active_cols[s] || stamp[s] == gen) {
                continue;
            }
            // BFS one component; count cells and checkerboard imbalance
            int head = 0;
            int tail = 0;
            queue[tail++] = s;
            stamp[s] = gen;
            long long size = 0;
            long long black = 0;
            while (head < tail) {
                const int u = queue[head++];
                ++size;
                if (!g_cell_parity.empty()) {
                    black += g_cell_parity[u];
                }
                for (int k = nbr_start[u]; k < nbr_start[u + 1]; ++k) {
                    const int v = nbr_flat[k];
                    if (active_cols[v] && stamp[v] != gen) {
                        stamp[v] = gen;
                        queue[tail++] = v;
                    }
                }
            }
            if (size % CELLS_PER_PLACEMENT != 0) {
                if (reason == 0) {
                    reason = 1;
                }
                if (!g_prune_colour_comp) {
                    return reason;  // old --connectivity behaviour
                }
            } else if (g_colour_strong && g_prune_colour_comp) {
                const long long white = size - black;
                const long long bw = black - white;
                if (bw_out && reason == 0) { *bw_out = bw; }
                const long long need = size / CELLS_PER_PLACEMENT;
                if ((bw < 0 ? -bw : bw) > need) {
                    return 2;
                }
            }
        }
        return reason;
    }

    // Research variant: no pruning — collect (size, B-W) per component.
    // Returns the whole-region colour imbalance.
    long long region_analyse(
        const std::vector<uint8_t>& active_cols,
        std::vector<std::pair<long long, long long>>& comps) {
        comps.clear();
        ++gen;
        long long region_black = 0;
        long long region_size = 0;
        for (int s = 0; s < num_cols; ++s) {
            if (!active_cols[s] || stamp[s] == gen) {
                continue;
            }
            int head = 0;
            int tail = 0;
            queue[tail++] = s;
            stamp[s] = gen;
            long long size = 0;
            long long black = 0;
            while (head < tail) {
                const int u = queue[head++];
                ++size;
                if (!g_cell_parity.empty()) {
                    black += g_cell_parity[u];
                }
                for (int k = nbr_start[u]; k < nbr_start[u + 1]; ++k) {
                    const int v = nbr_flat[k];
                    if (active_cols[v] && stamp[v] != gen) {
                        stamp[v] = gen;
                        queue[tail++] = v;
                    }
                }
            }
            comps.emplace_back(size, 2 * black - size);
            region_black += black;
            region_size += size;
        }
        return 2 * region_black - region_size;
    }
};

static Connectivity g_conn;

// ============================================================
// Unit propagation on forced placements (research prototype).
//
// A cell with exactly one remaining legal placement forces that
// placement in any completion. Placing it tentatively eliminates
// every overlapping placement, which may starve other cells
// (degree 0 => provably no completion) or create new forced cells.
// Transitively propagating all forced placements detects
// "connected but untileable" states that MRV alone would only find
// after further branching. Sound: forced placements appear in every
// completion, so a derived contradiction is a genuine dead end.
// ============================================================
struct Propagator {
    std::vector<int> deg;            // working copy of cell degrees
    std::vector<uint32_t> kill;      // per-row stamp (killed this run)
    std::vector<uint32_t> covered;   // per-cell stamp (satisfied this run)
    std::vector<int> q;              // forced-cell queue
    uint32_t gen = 0;
    int num_cols = 0;
    int num_rows = 0;

    void init(int nc, int nr) {
        num_cols = nc;
        num_rows = nr;
        deg.assign(static_cast<size_t>(nc), 0);
        kill.assign(static_cast<size_t>(nr), 0);
        covered.assign(static_cast<size_t>(nc), 0);
        q.assign(static_cast<size_t>(nc), 0);
        gen = 0;
    }

    // degrees: per-cell active-row counts from the MRV scan;
    // forced: cells whose degree is exactly 1.
    // Returns true when a contradiction (a starved uncovered cell)
    // is derived.
    bool run(const CSR& X, const CSR& Y,
             const std::vector<uint8_t>& active_rows,
             const std::vector<int>& forced) {
        ++gen;
        const uint32_t g = gen;
        std::copy(g_deg.begin(), g_deg.begin() + num_cols, deg.begin());
        int head = 0;
        int tail = 0;
        for (const int c : forced) {
            q[tail++] = c;
        }
        while (head < tail) {
            const int c = q[head++];
            if (covered[c] == g) {
                continue;  // satisfied by an already-placed row
            }
            if (deg[c] == 0) {
                return true;  // starved uncovered cell
            }
            if (deg[c] != 1) {
                continue;  // no longer forced
            }
            // find the unique surviving row covering c
            int r = -1;
            for (int k = X.indptr[c]; k < X.indptr[c + 1]; ++k) {
                const int rn = X.data[k];
                if (active_rows[rn] && kill[rn] != g) {
                    r = rn;
                    break;
                }
            }
            if (r < 0) {
                return true;  // starved
            }
            // tentatively place r: cover its cells, eliminate every
            // other active row that shares a cell with it
            kill[r] = g;
            for (int j = Y.indptr[r]; j < Y.indptr[r + 1]; ++j) {
                const int e = Y.data[j];
                covered[e] = g;
                for (int k2 = X.indptr[e]; k2 < X.indptr[e + 1]; ++k2) {
                    const int r2 = X.data[k2];
                    if (r2 == r || kill[r2] == g || !active_rows[r2]) {
                        continue;
                    }
                    kill[r2] = g;
                    for (int jj = Y.indptr[r2]; jj < Y.indptr[r2 + 1]; ++jj) {
                        const int u = Y.data[jj];
                        if (covered[u] == g) {
                            continue;  // already satisfied
                        }
                        if (--deg[u] == 0) {
                            return true;  // starved
                        }
                        if (deg[u] == 1) {
                            q[tail++] = u;
                        }
                    }
                }
            }
        }
        return false;
    }
};

static Propagator g_prop;

// ============================================================
// Chiral-safe symmetry breaking (v2, soundness-hardened)
//
// Candidate group elements are the 48 cube symmetries expressed as
// (axis permutation, sign flips), restricted to those that:
//   1. map the box onto itself (permuted dims match), and
//   2. map the piece's placement set onto itself.
// Condition 2 excludes reflections for chiral pieces automatically
// (a reflected placement of a chiral piece is not a placement of the
// piece), and excludes dim-mismatching permutations because placements
// would land outside the box. No chirality table is needed.
//
// Canonicalisation anchor (soundness):
//
// A filter "keep placement p only if p is the group-minimum of its
// orbit" is sound iff, for every tiling T and its orbit, some member
// T' of that orbit survives. Choosing T' = u(T) requires u to map the
// anchor cell to itself, so that the piece of T covering the anchor
// maps to the piece of u(T) covering the anchor. Hence:
//
//   * all dims odd  -> anchor = centre cell (fixed by EVERY box
//     symmetry, so the full preservation-checked group |G| is usable);
//   * otherwise     -> anchor = cell 0, restricted to the subgroup
//     G0 of elements that fix cell 0 (all signs +1).
//
// The earlier corner rule that canonicalised against the full group
// was UNSOUND: sign-flip elements move cell 0, the orbit minimum can
// be a non-corner image, and solution orbits could be lost entirely.
//
// Centre-pair extension (exactly one even dimension; generalises to
// any anchor SET fixed setwise by G): let S be the product over axes
// of {mid} (odd axis) or {k-1, k} (even axis, d = 2k). Every element
// of G maps S onto itself (sign flips exchange the pair, axis
// permutations map even axes to even axes). Every tiling covers all
// |S| cells of S; write t(T) for the |S|-tuple of covering placements,
// ordered by the fixed cell order on S, and Sum(t) for the sequence of
// placement signatures. Define T canonical iff Sum(t(T)) is the lex
// minimum of { Sum(t(u(T))) : u in G }.
//
// Soundness:
//   (1) Orbit survival: for any T pick u* attaining the lex minimum;
//       the orbit of u*(T) equals the orbit of T, so Sum(t(u*(T))) is
//       still the minimum and u*(T) is canonical. Every orbit retains
//       at least one representative. Note u* need NOT fix any cell:
//       the canonicalisation object is the S-indexed TUPLE, which u
//       permutes within S, and the slot re-ordering in the comparison
//       accounts for that.
//   (2) Pruning correctness: the S-cells of a partial state, once
//       covered, are covered by the same placements in every
//       completion. If the partial S-tuple t is not tuple-canonical,
//       some u has Sum(u.t) < Sum(t); for every completion T,
//       Sum(t(u(T))) = Sum(u.t) < Sum(t) = Sum(t(T)), so T was not
//       canonical either — pruning loses no canonical tiling.
//   (3) Static over-approximation: a placement is pre-deactivated iff
//       it participates in no canonical S-tuple; canonical tilings
//       only use canonical tuples, so none is removed.
//   The full group is used BECAUSE the anchor set is only setwise
//   fixed: the tuple re-ordering makes the action well defined. This
//   is why the corner/full-group rule was unsound (the corner is moved
//   and there is no set structure to re-order into) while the
//   centre-pair/full-group rule is sound.
//
// Cells use the placements-file convention id = x + a*y + a*b*z.
// ============================================================
struct Symmetry {
    bool active = false;
    int group_size = 0;          // preservation-checked |G|
    int filter_group_size = 0;   // subgroup used for canonicalisation
    int anchor_cell = 0;         // centre cell or 0
    const char* anchor_name = "corner0";
    int anchor_total = 0;
    int anchor_removed = 0;
    std::vector<std::vector<int>> maps;  // per element: id -> id'

    // ---- centre-pair scheme (|anchor set| == 2, exactly one even dim) ----
    // The anchor set S = {cell_neg, cell_pos} (ordered by cell id) is fixed
    // SETWISE by every element of G, so the full group is usable: the
    // canonicalisation object is the S-indexed tuple of placement
    // signatures, not an individual placement. See the block comment on
    // setup_symmetry for the soundness proof.
    bool pair_mode = false;
    int cell_neg = -1;
    int cell_pos = -1;
    std::vector<uint8_t> covers_neg;   // per placement row
    std::vector<uint8_t> covers_pos;   // per placement row
    std::vector<std::vector<int>> partners;  // neg-row -> canonical pos-rows
    long long pair_candidates = 0;
    long long pair_canonical = 0;
    long long pair_pruned_rows = 0;
    long long pair_checks = 0;      // runtime: joint checks performed
    long long pair_pruned = 0;      // runtime: branches cut by the joint check
};

static Symmetry g_sym;

static uint64_t cell_key(int id, int a, int b, int c, uint64_t K) {
    const int x = id % a;
    const int y = (id / a) % b;
    const int z = id / (a * b);
    return (static_cast<uint64_t>(x) * K + y) * K + z;  // orders like (x,y,z) lex
}

// Lex-min cell key of a sorted placement signature: the anchor slot's
// representative cell for tuple canonicality comparisons.
static inline uint64_t first_key(
    const std::array<uint64_t, CELLS_PER_PLACEMENT>& sig) {
    return sig[0];
}

// Build one group element's cell map; returns false if the element
// does not map the box onto itself.
static bool build_sym_map(const int perm[3], const int signs[3],
                          int a, int b, int c, std::vector<int>& map) {
    const int dims[3] = {a, b, c};
    for (int i = 0; i < 3; ++i) {
        if (dims[i] != dims[perm[i]]) {
            return false;
        }
    }
    map.assign(static_cast<size_t>(a) * b * c, -1);
    for (int id = 0; id < a * b * c; ++id) {
        const int coords[3] = {id % a, (id / a) % b, id / (a * b)};
        int n[3];
        for (int i = 0; i < 3; ++i) {
            n[i] = coords[perm[i]];
            if (signs[i] == -1) {
                n[i] = dims[i] - 1 - n[i];
            }
            if (n[i] < 0 || n[i] >= dims[i]) {
                return false;
            }
        }
        map[id] = n[0] + a * n[1] + a * b * n[2];
    }
    return true;
}

// Chiral-safe symmetry group + anchor canonicalisation.
// Returns the number of anchor placements masked out.
static int setup_symmetry(const std::vector<Placement>& placements,
                          int num_cols, int a, int b, int c,
                          std::vector<uint8_t>& active_rows)
{
    const uint64_t K = static_cast<uint64_t>(std::max(std::max(a, b), c)) + 1;

    // Sorted cell-key signature of every placement + lookup set.
    std::vector<std::array<uint64_t, CELLS_PER_PLACEMENT>> sigs(
        placements.size());
    for (size_t r = 0; r < placements.size(); ++r) {
        for (int j = 0; j < CELLS_PER_PLACEMENT; ++j) {
            sigs[r][j] = cell_key(placements[r].cells[j], a, b, c, K);
        }
        std::sort(sigs[r].begin(), sigs[r].end());
    }
    const std::set<std::array<uint64_t, CELLS_PER_PLACEMENT>> sig_set(
        sigs.begin(), sigs.end());

    // Candidate group elements: 6 axis permutations x 8 sign choices,
    // kept only if they map the box onto itself AND the placement set
    // onto itself (the latter excludes reflections for chiral pieces).
    std::vector<std::vector<int>> maps;
    std::vector<std::pair<int, int>> map_kind;  // (perm index, signs hash)
    const int perms[6][3] = {
        {0, 1, 2}, {0, 2, 1}, {1, 0, 2},
        {1, 2, 0}, {2, 0, 1}, {2, 1, 0},
    };
    std::vector<int> map;
    for (int pi = 0; pi < 6; ++pi) {
        for (int sx = 1; sx >= -1; sx -= 2) {
            for (int sy = 1; sy >= -1; sy -= 2) {
                for (int sz = 1; sz >= -1; sz -= 2) {
                    const int signs[3] = {sx, sy, sz};
                    if (!build_sym_map(perms[pi], signs, a, b, c, map)) {
                        continue;
                    }
                    bool preserves = true;
                    for (const auto& p : placements) {
                        std::array<uint64_t, CELLS_PER_PLACEMENT> img{};
                        for (int j = 0; j < CELLS_PER_PLACEMENT; ++j) {
                            const int id2 = map[p.cells[j]];
                            if (id2 < 0) {
                                preserves = false;
                                break;
                            }
                            img[j] = cell_key(id2, a, b, c, K);
                        }
                        if (!preserves) {
                            break;
                        }
                        std::sort(img.begin(), img.end());
                        if (sig_set.find(img) == sig_set.end()) {
                            preserves = false;
                            break;
                        }
                    }
                    if (preserves) {
                        maps.push_back(map);
                        const bool fixes_origin =
                            (sx == 1 && sy == 1 && sz == 1);
                        map_kind.emplace_back(pi, fixes_origin ? 1 : 0);
                    }
                }
            }
        }
    }

    g_sym.group_size = static_cast<int>(maps.size());

    // Anchor choice (soundness, see block comment):
    //   all dims odd          -> centre cell, full group (static filter);
    //   exactly one even dim  -> centre pair, full group (tuple filter:
    //                            static allowed-set + joint runtime check);
    //   otherwise             -> cell 0, subgroup fixing cell 0.
    bool all_odd = (a % 2 == 1) && (b % 2 == 1) && (c % 2 == 1);
    const int dims[3] = {a, b, c};
    int even_axes[3];
    int n_even = 0;
    for (int i = 0; i < 3; ++i) {
        if (dims[i] % 2 == 0) {
            even_axes[n_even++] = i;
        }
    }
    int anchor;
    if (all_odd) {
        anchor = (a / 2) + a * (b / 2) + a * b * (c / 2);
        g_sym.anchor_name = "centre";
        g_sym.filter_group_size = static_cast<int>(maps.size());
        // every box symmetry fixes the centre when all dims are odd
        for (const auto& m : maps) {
            if (m[anchor] != anchor) {
                throw std::logic_error(
                    "symmetry element does not fix the centre cell");
            }
        }
    } else if (n_even == 1) {
        // ----- centre-pair scheme -----
        const int ax = even_axes[0];
        const int dim_ax = dims[ax];
        const int stride[3] = {1, a, a * b};
        auto cell_at = [&](const int mid[3]) {
            return mid[0] * stride[0] + mid[1] * stride[1] + mid[2] * stride[2];
        };
        int lo[3], hi[3];
        for (int i = 0; i < 3; ++i) {
            const int m = (dims[i] - 1) / 2;
            lo[i] = (i == ax) ? dim_ax / 2 - 1 : m;
            hi[i] = (i == ax) ? dim_ax / 2 : m;
        }
        const int cn = cell_at(lo);
        const int cp = cell_at(hi);
        g_sym.cell_neg = (cn < cp) ? cn : cp;
        g_sym.cell_pos = (cn < cp) ? cp : cn;
        g_sym.pair_mode = true;
        g_sym.anchor_name = "centre-pair";
        g_sym.filter_group_size = static_cast<int>(maps.size());
        g_sym.anchor_cell = g_sym.cell_neg;
        // S must be setwise fixed by every group element
        for (const auto& m : maps) {
            const int im = m[g_sym.cell_neg];
            if (im != g_sym.cell_neg && im != g_sym.cell_pos) {
                throw std::logic_error(
                    "symmetry element does not preserve the centre pair");
            }
        }

        // Enumerate realisable S-tuples (disjoint placements; a single
        // placement covering both anchor cells is the degenerate tuple)
        // and keep the tuple-canonical ones. The tuple (r, s) is canonical
        // iff its slot-ordered signature sequence (neg slot first) is the
        // lex minimum over all group images, where each image is ordered
        // back into (neg, pos) slot order. Full 5-cell signatures are
        // compared, so each placement has a unique signature and each
        // pair orbit has exactly one canonical member.
        using Sig = std::array<uint64_t, CELLS_PER_PLACEMENT>;
        std::map<Sig, int> sig2row;
        for (size_t r = 0; r < placements.size(); ++r) {
            sig2row[sigs[r]] = static_cast<int>(r);
        }

        const int num_rows = static_cast<int>(placements.size());
        g_sym.covers_neg.assign(static_cast<size_t>(num_rows), 0);
        g_sym.covers_pos.assign(static_cast<size_t>(num_rows), 0);
        std::vector<int> rows_neg;
        std::vector<int> rows_pos;
        for (int r = 0; r < num_rows; ++r) {
            for (int j = 0; j < CELLS_PER_PLACEMENT; ++j) {
                if (placements[r].cells[j] == g_sym.cell_neg) {
                    g_sym.covers_neg[r] = 1;
                    rows_neg.push_back(r);
                }
                if (placements[r].cells[j] == g_sym.cell_pos) {
                    g_sym.covers_pos[r] = 1;
                    rows_pos.push_back(r);
                }
            }
        }

        std::vector<std::vector<int>> ok_partners(
            static_cast<size_t>(num_rows));
        std::vector<uint8_t> neg_ok(static_cast<size_t>(num_rows), 0);
        std::vector<uint8_t> pos_ok(static_cast<size_t>(num_rows), 0);
        for (const int r : rows_neg) {
            for (const int s : rows_pos) {
                if (r != s) {
                    // (r, s) is a realisable tuple only if disjoint;
                    // overlap also covers the "both cover one anchor
                    // cell" cases. r == s is the degenerate both-cells
                    // tuple and is always self-consistent here.
                    bool overlap = false;
                    for (int j = 0; j < CELLS_PER_PLACEMENT && !overlap; ++j) {
                        for (int k2 = 0; k2 < CELLS_PER_PLACEMENT; ++k2) {
                            if (placements[r].cells[j] ==
                                placements[s].cells[k2]) {
                                overlap = true;
                                break;
                            }
                        }
                    }
                    if (overlap) {
                        continue;
                    }
                }
                ++g_sym.pair_candidates;
                // canonicality of the tuple (r, s): lex-min slot-ordered
                // signature pair over all group images
                const Sig& sr = sigs[r];
                const Sig& ss = sigs[s];
                bool canonical = true;
                for (const auto& m : maps) {
                    Sig ir{};
                    Sig is{};
                    for (int j = 0; j < CELLS_PER_PLACEMENT; ++j) {
                        ir[j] = cell_key(m[placements[r].cells[j]], a, b, c, K);
                        is[j] = cell_key(m[placements[s].cells[j]], a, b, c, K);
                    }
                    std::sort(ir.begin(), ir.end());
                    std::sort(is.begin(), is.end());
                    const Sig& rn = sigs[sig2row.at(ir)];
                    const Sig& sn = sigs[sig2row.at(is)];
                    // slot order after the map: the placement covering
                    // cell_neg is rn if m fixes the neg cell, else sn
                    std::array<Sig, 2> image_seq;
                    if (m[g_sym.cell_neg] == g_sym.cell_neg) {
                        image_seq = {rn, sn};
                    } else {
                        image_seq = {sn, rn};
                    }
                    const std::array<Sig, 2> own = {sr, ss};
                    if (image_seq < own) {  // std::array: lex, elementwise
                        canonical = false;
                        break;
                    }
                }
                if (canonical) {
                    ++g_sym.pair_canonical;
                    ok_partners[r].push_back(s);
                    neg_ok[r] = 1;
                    pos_ok[s] = 1;
                }
            }
        }
        for (auto& p : ok_partners) {
            std::sort(p.begin(), p.end());
        }
        g_sym.partners = std::move(ok_partners);

        // static over-approximation: deactivate placements covering an
        // anchor cell that participates in no canonical tuple
        int removed = 0;
        for (int r = 0; r < num_rows; ++r) {
            if ((g_sym.covers_neg[r] && !neg_ok[r]) ||
                (g_sym.covers_pos[r] && !pos_ok[r])) {
                active_rows[r] = 0;
                ++removed;
            }
        }
        g_sym.pair_pruned_rows = removed;
        g_sym.anchor_total = static_cast<int>(rows_neg.size() +
                                              rows_pos.size());
        anchor = g_sym.cell_neg;
    } else {
        anchor = 0;
        g_sym.anchor_name = "corner0";
        std::vector<std::vector<int>> g0;
        for (size_t i = 0; i < maps.size(); ++i) {
            if (map_kind[i].second == 1 && maps[i][0] == 0) {
                g0.push_back(maps[i]);
            }
        }
        g_sym.filter_group_size = static_cast<int>(g0.size());
        g0.swap(maps);   // canonicalise only against the sound subgroup
    }
    g_sym.maps = std::move(maps);
    g_sym.active = !g_sym.maps.empty();
    g_sym.anchor_cell = anchor;

    // Canonical restriction on placements covering the anchor cell.
    int removed = 0;
    int anchor_total = 0;
    for (size_t r = 0; r < placements.size(); ++r) {
        bool covers_anchor = false;
        for (int j = 0; j < CELLS_PER_PLACEMENT; ++j) {
            if (placements[r].cells[j] == g_sym.anchor_cell) {
                covers_anchor = true;
                break;
            }
        }
        if (!covers_anchor) {
            continue;
        }
        ++anchor_total;
        std::array<uint64_t, CELLS_PER_PLACEMENT> best{};
        bool first = true;
        for (const auto& m : g_sym.maps) {
            std::array<uint64_t, CELLS_PER_PLACEMENT> img{};
            for (int j = 0; j < CELLS_PER_PLACEMENT; ++j) {
                img[j] = cell_key(m[placements[r].cells[j]], a, b, c, K);
            }
            std::sort(img.begin(), img.end());
            if (first || img < best) {
                best = img;
                first = false;
            }
        }
        if (sigs[r] != best) {
            active_rows[r] = 0;
            ++removed;
        }
    }

    g_sym.anchor_total = anchor_total;
    return removed;
}

void search(
    const CSR& X,
    const CSR& Y,
    std::vector<uint8_t>& active_cols,
    std::vector<uint8_t>& active_rows,
    int num_cols,
    int depth,
    SearchStats& stats,
    std::vector<int>& solution,
    int anch_neg = -1,
    int anch_pos = -1)
{
    ++stats.nodes;

    // Report progress every 100M nodes
    if (stats.nodes % 100000000 == 0) {
        auto now = std::chrono::steady_clock::now();
        double elapsed = std::chrono::duration<double>(now - stats.start_time).count();
        std::cerr << "Progress: " << stats.nodes << " nodes, "
                  << stats.solutions << " solutions, "
                  << elapsed << " s, "
                  << (stats.nodes / elapsed) << " nodes/s"
                  << std::endl;
    }

    if (stats.max_nodes > 0 && stats.nodes >= stats.max_nodes) {
        return;
    }

    if (depth > stats.max_depth) {
        stats.max_depth = depth;
    }

    bool any_active_col = false;
    int n_active = 0;

    if (g_connectivity && g_conn_threshold > 0) {
        // threshold mode needs the remaining-cell count: full scan
        for (int c = 0; c < num_cols; ++c) {
            if (active_cols[c]) {
                ++n_active;
            }
        }
        any_active_col = n_active > 0;
    } else {
        for (int c = 0; c < num_cols; ++c) {
            if (active_cols[c]) {
                any_active_col = true;
                break;
            }
        }
    }

    if (!any_active_col) {
        ++stats.solutions;
        if (!g_dump_file.empty()) {
            std::vector<int> ids = solution;
            std::sort(ids.begin(), ids.end());
            std::string line;
            for (size_t i = 0; i < ids.size(); ++i) {
                line += std::to_string(ids[i]);
                line.push_back(i + 1 == ids.size() ? '\n' : ' ');
            }
            #pragma omp critical
            {
                std::ofstream f(g_dump_file, std::ios::app);
                f << line;
            }
        }
        // Periodically output solution count (every 10000 solutions)
        if (stats.solutions % 10000 == 0) {
            auto now = std::chrono::steady_clock::now();
            double elapsed = std::chrono::duration<double>(now - stats.start_time).count();
            std::cerr << "SOLCOUNT " << stats.solutions << " solutions at "
                      << stats.nodes << " nodes, " << elapsed << " s"
                      << std::endl;
        }
        return;
    }

    // Region feasibility pruning (overnight research prototypes).
    // Global checkerboard test (O(1)): every remaining piece covers a 3/2
    // colour split, so the remaining region's colour imbalance can never
    // exceed the number of pieces still to be placed.
    if (g_prune_colour_global && g_colour_strong) {
        const long long remaining = g_expected_pieces - depth;
        const long long bw = g_rem_colors[0] - g_rem_colors[1];
        const long long abw = bw < 0 ? -bw : bw;
        if (abw > remaining) {
            ++stats.rej_colour_global;
            int mr_min = 999999;
            choose_best_column(X, active_cols, active_rows, num_cols, mr_min);
            if (mr_min == 0) {
                ++stats.rej_colour_global_mrv;  // MRV also dead here
            } else if (!stats.new_rej_depth_hist.empty()) {
                const int b = static_cast<int>(
                    static_cast<long long>(depth) * stats.hist_buckets /
                    (g_expected_pieces + 1));
                ++stats.new_rej_depth_hist[std::min(b, stats.hist_buckets - 1)];
            }
            ++stats.dead_ends;
            return;
        }
    }

    // Connectivity / component pruning (toggleable). Necessary
    // condition only: some component of the remaining region has a
    // cell count that is not a multiple of the piece size.
    if (g_connectivity &&
        (g_conn_threshold <= 0 || n_active <= g_conn_threshold)) {
        ++stats.conn_checks;
        if (g_conn.region_tileable(active_cols) != 0) {
            ++stats.conn_pruned;
            ++stats.dead_ends;
            return;
        }
    }

    // Per-component checkerboard test, fused into the same BFS walk.
    if (g_prune_colour_comp) {
        ++stats.conn_checks;
        const int reason = g_conn.region_tileable(active_cols);
        if (reason != 0) {
            int mr_min = 999999;
            choose_best_column(X, active_cols, active_rows, num_cols, mr_min);
            if (reason == 2) {
                ++stats.rej_colour_comp;
                if (mr_min == 0) {
                    ++stats.rej_colour_comp_mrv;
                } else if (!stats.new_rej_depth_hist.empty()) {
                    const int b = static_cast<int>(
                        static_cast<long long>(depth) * stats.hist_buckets /
                        (g_expected_pieces + 1));
                    ++stats.new_rej_depth_hist[std::min(b, stats.hist_buckets - 1)];
                }
            } else {
                ++stats.conn_pruned;
            }
            ++stats.dead_ends;
            return;
        }
    }

    int min_rows = 999999;
    static std::vector<int> prop_forced;
    prop_forced.clear();
    const int best_col = choose_best_column(
        X,
        active_cols,
        active_rows,
        num_cols,
        min_rows,
        g_prune_propagate ? g_deg.data() : nullptr,
        g_prune_propagate ? &prop_forced : nullptr);

    if (best_col == -1 || min_rows == 0) {
        ++stats.dead_ends;
        // Research sampler: inspect a sample of MRV dead ends.
        if (g_research_every > 0 &&
            ++stats.research_deadend_mrv_total % g_research_every == 0 &&
            g_conn.num_cols == num_cols) {
            std::vector<std::pair<long long, long long>> comps;
            const long long bw = g_conn.region_analyse(active_cols, comps);
            long long sizefail = 0;
            long long colourfail = 0;
            long long total = 0;
            for (const auto& cb : comps) {
                total += cb.first;
                if (cb.first % CELLS_PER_PLACEMENT != 0) {
                    ++sizefail;
                } else if (g_colour_strong &&
                           (cb.second < 0 ? -cb.second : cb.second) >
                               cb.first / CELLS_PER_PLACEMENT) {
                    ++colourfail;
                }
            }
            const long long remaining = g_expected_pieces - depth;
            const long long abw = bw < 0 ? -bw : bw;
            std::cout << "RD nodes=" << stats.nodes << " depth=" << depth
                      << " comps=" << comps.size() << " cells=" << total
                      << " globalbw=" << bw
                      << " globalrej=" << (abw > remaining ? 1 : 0)
                      << " sizefail=" << sizefail
                      << " colourfail=" << colourfail << " [";
            for (size_t i = 0; i < comps.size() && i < 8; ++i) {
                if (i) {
                    std::cout << ',';
                }
                std::cout << comps[i].first << ':' << comps[i].second;
            }
            if (comps.size() > 8) {
                std::cout << ",...";
            }
            std::cout << "]\n";
        }
        return;
    }

    const int row_start = X.indptr[best_col];
    const int row_end = X.indptr[best_col + 1];

    // Unit propagation on forced placements (research prototype).
    if (g_prune_propagate && !prop_forced.empty()) {
        stats.propagate_forced_total += prop_forced.size();
        if (g_prop.run(X, Y, active_rows, prop_forced)) {
            if (getenv("PROP_DEBUG")) {
                std::cerr << "PROP-REJ depth=" << depth
                          << " nodes=" << stats.nodes
                          << " nforced=" << prop_forced.size()
                          << " path=";
                for (int i = 0; i < depth; ++i) {
                    std::cerr << solution[i] << ",";
                }
                std::cerr << "\n";
                if (getenv("PROP_DEBUG_ONCE")) {
                    std::exit(42);
                }
            }
            ++stats.rej_propagate;
            if (!stats.new_rej_depth_hist.empty()) {
                const int b = static_cast<int>(
                    static_cast<long long>(depth) * stats.hist_buckets /
                    (g_expected_pieces + 1));
                ++stats.new_rej_depth_hist[std::min(b, stats.hist_buckets - 1)];
            }
            ++stats.dead_ends;
            return;
        }
    }

    // Pre-allocate deactivation vectors with reasonable capacity
    std::vector<int> deactivated_cols;
    std::vector<int> deactivated_rows;
    deactivated_cols.reserve(CELLS_PER_PLACEMENT);
    deactivated_rows.reserve(64);

    for (int k = row_start; k < row_end; ++k) {
        const int r = X.data[k];

        if (!active_rows[r]) {
            continue;
        }

        deactivated_cols.clear();
        deactivated_rows.clear();

        // This row covers exactly five columns.
        const int y_start = Y.indptr[r];
        const int y_end = Y.indptr[r + 1];

        for (int j = y_start; j < y_end; ++j) {
            const int c = Y.data[j];

            if (!active_cols[c]) {
                continue;
            }

            active_cols[c] = 0;
            deactivated_cols.push_back(c);
            if (!g_cell_parity.empty()) {
                --g_rem_colors[g_cell_parity[c]];
            }

            const int x_start = X.indptr[c];
            const int x_end = X.indptr[c + 1];

            for (int q = x_start; q < x_end; ++q) {
                const int other = X.data[q];

                if (active_rows[other]) {
                    active_rows[other] = 0;
                    deactivated_rows.push_back(other);
                }
            }
        }

        solution.push_back(r);

        // Centre-pair joint check: when the second anchor cell becomes
        // covered, the S-tuple must be tuple-canonical (partners lookup).
        // The anchor cells can only be covered once per branch, so this
        // fires at most once along a path. Pruning here removes exactly
        // the branches whose S-tuple is not canonical (see block comment
        // on setup_symmetry); at least one tiling per solution orbit has
        // a canonical S-tuple, so no orbit is lost.
        int new_neg = anch_neg;
        int new_pos = anch_pos;
        bool recurse = true;
        if (g_sym.pair_mode) {
            if (g_sym.covers_neg[r]) {
                new_neg = r;
            }
            if (g_sym.covers_pos[r]) {
                new_pos = r;
            }
            if (new_neg >= 0 && new_pos >= 0 &&
                (new_neg != anch_neg || new_pos != anch_pos)) {
                const std::vector<int>& ps = g_sym.partners[new_neg];
                if (!std::binary_search(ps.begin(), ps.end(), new_pos)) {
                    recurse = false;
                    ++stats.dead_ends;
                    ++g_sym.pair_pruned;
                }
                ++g_sym.pair_checks;
            }
        }

        if (recurse) {
            search(
                X,
                Y,
                active_cols,
                active_rows,
                num_cols,
                depth + 1,
                stats,
                solution,
                new_neg,
                new_pos);
        }

        solution.pop_back();

        for (int q : deactivated_rows) {
            active_rows[q] = 1;
        }

        for (int c : deactivated_cols) {
            active_cols[c] = 1;
            if (!g_cell_parity.empty()) {
                ++g_rem_colors[g_cell_parity[c]];
            }
        }
    }
}

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Usage: " << argv[0]
                  << " PIECE X Y Z [placements_file] [max_nodes] [flags]\n";
        std::cerr << "  If placements_file is omitted, uses placements_PIECE_XxYxZ.txt\n";
        std::cerr << "  If max_nodes is specified, stops after that many nodes\n";
        std::cerr << "  Flags:\n";
        std::cerr << "    --connectivity[=N]  component pruning (N = only check while\n";
        std::cerr << "                        remaining cells <= N; default: always)\n";
        std::cerr << "    --symmetry          chiral-safe anchor-canonical symmetry breaking\n";
        std::cerr << "    --dump=FILE         append one line of placement ids per solution\n";
        std::cerr << "    --region-prune=colour-global  O(1) checkerboard test on the whole\n";
        std::cerr << "                        remaining region (needs |B-W|=1 placements)\n";
        std::cerr << "    --region-prune=colour         per-component checkerboard test\n";
        std::cerr << "                        (fused with the connectivity BFS)\n";
        std::cerr << "    --region-prune=propagate      unit propagation on forced (degree-1)\n";
        std::cerr << "                        placements; rejects provably dead states early\n";
        std::cerr << "    --research-deadends=K         sample every K-th MRV dead end and\n";
        std::cout << "    dump component structure to stdout\n";
        return 1;
    }

    try {
        // Split flags from positionals (backward compatible).
        std::vector<std::string> pos;
        for (int i = 1; i < argc; ++i) {
            const std::string s = argv[i];
            if (s.rfind("--connectivity", 0) == 0) {
                g_connectivity = true;
                if (s.size() > 14 && s[14] == '=') {
                    g_conn_threshold = std::stol(s.substr(15));
                }
            } else if (s == "--symmetry") {
                g_symmetry = true;
            } else if (s.rfind("--dump=", 0) == 0) {
                g_dump_file = s.substr(7);
            } else if (s.rfind("--region-prune=", 0) == 0) {
                const std::string mode = s.substr(15);
                if (mode == "colour-global") {
                    g_prune_colour_global = true;
                } else if (mode == "colour") {
                    g_prune_colour_comp = true;
                } else if (mode == "propagate") {
                    g_prune_propagate = true;
                } else {
                    throw std::invalid_argument(
                        "unknown --region-prune mode: " + mode);
                }
            } else if (s.rfind("--research-deadends=", 0) == 0) {
                g_research_every = std::stol(s.substr(20));
                if (g_research_every <= 0) {
                    g_research_every = 0;
                }
            } else {
                pos.push_back(s);
            }
        }
        std::vector<char*> pos_args;
        for (auto& s : pos) {
            pos_args.push_back(&s[0]);
        }
        argv = pos_args.data();
        argc = static_cast<int>(pos_args.size());

        if (argc < 4) {
            throw std::invalid_argument(
                "PIECE X Y Z are required");
        }

        const std::string piece = argv[0];
        const int Xdim = std::stoi(argv[1]);
        const int Ydim = std::stoi(argv[2]);
        const int Zdim = std::stoi(argv[3]);

        if (Xdim <= 0 || Ydim <= 0 || Zdim <= 0) {
            throw std::invalid_argument(
                "Box dimensions must be positive");
        }

        const int num_cols = Xdim * Ydim * Zdim;
        const int expected_pieces = num_cols / CELLS_PER_PLACEMENT;

        std::string filename;
        uint64_t max_nodes = 0;  // 0 = unlimited
        if (argc >= 5) {
            // Check if arg 5 is a number (max_nodes) or a filename
            char* end;
            long val = std::strtol(argv[4], &end, 10);
            if (*end == '\0' && val > 0) {
                max_nodes = static_cast<uint64_t>(val);
                if (argc >= 6) {
                    filename = argv[5];
                } else {
                    filename = "placements_" + piece + "_" +
                               std::to_string(Xdim) + "x" +
                               std::to_string(Ydim) + "x" +
                               std::to_string(Zdim) + ".txt";
                }
            } else {
                filename = argv[4];
                if (argc >= 6) {
                    char* end2;
                    long val2 = std::strtol(argv[5], &end2, 10);
                    if (*end2 == '\0' && val2 > 0) {
                        max_nodes = static_cast<uint64_t>(val2);
                    }
                }
            }
        } else {
            filename = "placements_" + piece + "_" +
                       std::to_string(Xdim) + "x" +
                       std::to_string(Ydim) + "x" +
                       std::to_string(Zdim) + ".txt";
        }

        std::cout
            << "Piece: " << piece << '\n'
            << "Box: " << Xdim << " x " << Ydim << " x " << Zdim << '\n'
            << "Cells: " << num_cols << '\n'
            << "Expected pieces: " << expected_pieces << '\n'
            << "Placements file: " << filename << '\n';

        const auto placements = load_placements(filename);

        const int num_rows = static_cast<int>(placements.size());

        std::cout
            << "Placements loaded: " << num_rows << '\n';

        const CSR X = build_x_csr(placements, num_cols);
        const CSR Y = build_y_csr(placements);

        std::cout
            << "X CSR: " << X.data.size() << " entries\n"
            << "Y CSR: " << Y.data.size() << " entries\n";

        std::vector<uint8_t> active_cols(
            static_cast<size_t>(num_cols), 1);

        std::vector<uint8_t> active_rows(
            static_cast<size_t>(num_rows), 1);

        if (g_symmetry) {
            const int removed = setup_symmetry(
                placements, num_cols, Xdim, Ydim, Zdim, active_rows);
            std::cout
                << "Symmetry: chiral-safe group |G|=" << g_sym.group_size
                << " ; filter subgroup |H|=" << g_sym.filter_group_size
                << " ; anchor=" << g_sym.anchor_name
                << " (cell " << g_sym.anchor_cell << ")"
                << " ; anchor placements " << g_sym.anchor_total
                << ", removed " << removed << '\n';
            if (g_sym.pair_mode) {
                std::cout
                    << "Centre-pair scheme: cells (" << g_sym.cell_neg
                    << "," << g_sym.cell_pos << ")"
                    << " ; S-tuple candidates " << g_sym.pair_candidates
                    << ", canonical " << g_sym.pair_canonical
                    << ", rows pre-deactivated " << g_sym.pair_pruned_rows
                    << '\n';            }
        }
        if (g_connectivity || g_prune_colour_comp || g_research_every > 0) {
            g_conn.init(Xdim, Ydim, Zdim);
        }
        if (g_prune_propagate) {
            g_deg.assign(static_cast<size_t>(num_cols), 0);
            g_prop.init(num_cols, num_rows);
        }
        if (g_connectivity) {
            std::cout
                << "Connectivity pruning: ON"
                << (g_conn_threshold > 0
                        ? (" (threshold " + std::to_string(g_conn_threshold) + ")")
                        : " (always)")
                << '\n';
        }

        // Region-feasibility research setup: cell parities, placement
        // colour signatures, global remaining-colour counters.
        if (g_prune_colour_global || g_prune_colour_comp ||
            g_prune_propagate || g_research_every > 0) {
            g_expected_pieces = expected_pieces;
            g_cell_parity.assign(static_cast<size_t>(num_cols), 0);
            for (int id = 0; id < num_cols; ++id) {
                const int x = id % Xdim;
                const int y = (id / Xdim) % Ydim;
                const int z = id / (Xdim * Ydim);
                g_cell_parity[id] = static_cast<uint8_t>((x + y + z) & 1);
            }
            g_rem_colors[0] = 0;
            g_rem_colors[1] = 0;
            for (int id = 0; id < num_cols; ++id) {
                ++g_rem_colors[g_cell_parity[id]];
            }
            int maxdiff = 0;
            for (const auto& p : placements) {
                int black = 0;
                for (int j = 0; j < CELLS_PER_PLACEMENT; ++j) {
                    black += g_cell_parity[p.cells[j]];
                }
                int d = 2 * black - CELLS_PER_PLACEMENT;
                if (d < 0) {
                    d = -d;
                }
                if (d > maxdiff) {
                    maxdiff = d;
                }
            }
            g_colour_maxdiff = maxdiff;
            g_colour_strong = (maxdiff == 1);
            std::cout
                << "Colour invariant: max placement imbalance = " << maxdiff
                << " -> " << (g_colour_strong
                        ? "STRONG test armed (|B-W| <= pieces)"
                        : "strong test NOT valid (disabled)")
                << '\n';
            if (!g_colour_strong) {
                g_prune_colour_global = false;
                g_prune_colour_comp = false;
            }
        }

        SearchStats stats;
        stats.max_nodes = max_nodes;
        stats.start_time = std::chrono::steady_clock::now();
        stats.new_rej_depth_hist.assign(
            static_cast<size_t>(stats.hist_buckets), 0);

        std::vector<int> solution;
        solution.reserve(expected_pieces);

        const auto start = std::chrono::steady_clock::now();

        search(
            X,
            Y,
            active_cols,
            active_rows,
            num_cols,
            0,
            stats,
            solution);

        const auto end = std::chrono::steady_clock::now();

        const double seconds =
            std::chrono::duration<double>(
                end - start).count();

        std::cout << "\n=== RESULTS ===\n";
        std::cout
            << "Nodes: " << stats.nodes << '\n'
            << "Solutions: " << stats.solutions << '\n'
            << "Dead ends: " << stats.dead_ends << '\n'
            << "Max depth: " << stats.max_depth
            << " / " << expected_pieces << '\n'
            << "Time: " << seconds << " s\n";

        if (seconds > 0.0) {
            std::cout
                << "Nodes/sec: "
                << static_cast<double>(stats.nodes) / seconds
                << '\n';
        }

        if (stats.solutions > 0) {
            std::cout
                << "Solutions/sec: "
                << static_cast<double>(stats.solutions) / seconds
                << '\n';
        }

        if (g_connectivity) {
            std::cout
                << "Connectivity checks: " << stats.conn_checks << '\n'
                << "Pruned by connectivity: " << stats.conn_pruned << '\n';
        }

        if (g_sym.pair_mode) {
            std::cout
                << "Centre-pair runtime checks: " << g_sym.pair_checks << '\n'
                << "Centre-pair runtime prunes: " << g_sym.pair_pruned << '\n';
        }

        if (g_prune_colour_global || g_prune_colour_comp) {
            if (g_prune_colour_global) {
                std::cout
                    << "Colour-global rejections: " << stats.rej_colour_global
                    << " (of which MRV also dead: "
                    << stats.rej_colour_global_mrv << ")\n";
            }
            if (g_prune_colour_comp) {
                std::cout
                    << "Colour-component rejections: " << stats.rej_colour_comp
                    << " (of which MRV also dead: "
                    << stats.rej_colour_comp_mrv << ")\n";
            }
        }
        if (g_prune_propagate) {
            std::cout
                << "Propagation rejections: " << stats.rej_propagate
                << " (forced placements processed: "
                << stats.propagate_forced_total << ")\n";
        }
        if (g_prune_colour_global || g_prune_colour_comp ||
            g_prune_propagate) {
            std::cout << "Genuine-new rejection depth histogram (32 buckets):\n";
            for (int i = 0; i < stats.hist_buckets; ++i) {
                std::cout << "  bucket " << i << ": "
                          << stats.new_rej_depth_hist[static_cast<size_t>(i)]
                          << '\n';
            }
        }

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << '\n';
        return 1;
    }

    return 0;
}