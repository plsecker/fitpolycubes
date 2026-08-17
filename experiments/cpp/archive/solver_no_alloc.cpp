#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

constexpr int CELLS_PER_PLACEMENT = 5;

// These bounds are deliberately generous for the current pentacube solver.
// They eliminate dynamic allocation from the DFS hot path.
// For larger/polycube cases, these can later be replaced by per-depth
// preallocated scratch storage.
constexpr int MAX_DEACTIVATED_ROWS = 4096;
constexpr int MAX_DECREMENTED_COUNTS = 16384;

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
    int max_depth = 0;
};

std::vector<Placement> load_placements(const std::string& filename)
{
    std::ifstream file(filename);

    if (!file) {
        throw std::runtime_error(
            "Could not open placements file: " + filename);
    }

    int count = 0;

    if (!(file >> count) || count < 0) {
        throw std::runtime_error("Invalid placement count");
    }

    std::vector<Placement> placements(
        static_cast<size_t>(count));

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

// Build X: column/cell -> placement rows covering it.
CSR build_x_csr(
    const std::vector<Placement>& placements,
    int num_cols)
{
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
    x.indptr.resize(
        static_cast<size_t>(num_cols) + 1,
        0);

    for (int c = 0; c < num_cols; ++c) {
        x.indptr[c + 1] =
            x.indptr[c] + counts[c];
    }

    x.data.resize(
        static_cast<size_t>(x.indptr[num_cols]));

    std::vector<int> cursor = x.indptr;

    for (int r = 0;
         r < static_cast<int>(placements.size());
         ++r) {

        for (int j = 0;
             j < CELLS_PER_PLACEMENT;
             ++j) {

            const int c = placements[r].cells[j];
            x.data[cursor[c]++] = r;
        }
    }

    return x;
}

// Build Y: placement row -> the five cells it covers.
CSR build_y_csr(
    const std::vector<Placement>& placements)
{
    CSR y;
    const int num_rows =
        static_cast<int>(placements.size());

    y.indptr.resize(
        static_cast<size_t>(num_rows) + 1,
        0);

    for (int r = 0; r < num_rows; ++r) {
        y.indptr[r + 1] =
            y.indptr[r] + CELLS_PER_PLACEMENT;
    }

    y.data.resize(
        static_cast<size_t>(y.indptr[num_rows]));

    for (int r = 0; r < num_rows; ++r) {
        const int start = y.indptr[r];

        for (int j = 0;
             j < CELLS_PER_PLACEMENT;
             ++j) {

            y.data[start + j] =
                placements[r].cells[j];
        }
    }

    return y;
}

// Exact Algorithm X search with incrementally maintained candidate counts.
//
// Important: this deliberately preserves the same search-tree semantics as
// the Numba implementation. Only the storage of the undo state changes.
void search(
    const CSR& X,
    const CSR& Y,
    std::vector<uint8_t>& active_cols,
    std::vector<uint8_t>& active_rows,
    std::vector<int>& candidate_counts,
    int num_cols,
    int depth,
    SearchStats& stats)
{
    ++stats.nodes;

    if (depth > stats.max_depth) {
        stats.max_depth = depth;
    }

    // Same "all columns covered" check as the Numba solver.
    bool any_active_col = false;

    for (int c = 0; c < num_cols; ++c) {
        if (active_cols[c]) {
            any_active_col = true;
            break;
        }
    }

    if (!any_active_col) {
        ++stats.solutions;
        return;
    }

    // Same tie-breaking as Numba:
    // first active column with the minimum active-row count.
    int best_col = -1;
    int min_rows = std::numeric_limits<int>::max();

    for (int c = 0; c < num_cols; ++c) {
        if (!active_cols[c]) {
            continue;
        }

        const int count = candidate_counts[c];

        if (count < min_rows) {
            min_rows = count;
            best_col = c;

            if (count == 0) {
                break;
            }
        }
    }

    if (best_col == -1 || min_rows == 0) {
        ++stats.dead_ends;
        return;
    }

    // Fixed-size undo buffers: no heap allocation in the DFS.
    int deactivated_cols[CELLS_PER_PLACEMENT];
    int deactivated_rows[MAX_DEACTIVATED_ROWS];
    int decremented_cols[MAX_DECREMENTED_COUNTS];

    const int row_start = X.indptr[best_col];
    const int row_end = X.indptr[best_col + 1];

    for (int k = row_start; k < row_end; ++k) {
        const int r = X.data[k];

        if (!active_rows[r]) {
            continue;
        }

        int deactivated_col_count = 0;
        int deactivated_row_count = 0;
        int decremented_col_count = 0;

        // Select row r.
        //
        // For every column covered by r:
        //   1. deactivate that column;
        //   2. deactivate every still-active row touching it;
        //   3. when such a row is deactivated, decrement the candidate count
        //      of each still-active column that the row covers.
        const int y_start = Y.indptr[r];
        const int y_end = Y.indptr[r + 1];

        for (int j = y_start; j < y_end; ++j) {
            const int c = Y.data[j];

            if (!active_cols[c]) {
                continue;
            }

            if (deactivated_col_count >= CELLS_PER_PLACEMENT) {
                throw std::runtime_error(
                    "Internal error: too many deactivated columns");
            }

            active_cols[c] = 0;
            deactivated_cols[deactivated_col_count++] = c;

            const int x_start = X.indptr[c];
            const int x_end = X.indptr[c + 1];

            for (int q = x_start; q < x_end; ++q) {
                const int other = X.data[q];

                if (!active_rows[other]) {
                    continue;
                }

                if (deactivated_row_count >= MAX_DEACTIVATED_ROWS) {
                    throw std::runtime_error(
                        "MAX_DEACTIVATED_ROWS exceeded");
                }

                active_rows[other] = 0;
                deactivated_rows[deactivated_row_count++] = other;

                const int other_y_start = Y.indptr[other];
                const int other_y_end = Y.indptr[other + 1];

                for (int p = other_y_start;
                     p < other_y_end;
                     ++p) {

                    const int other_col = Y.data[p];

                    if (!active_cols[other_col]) {
                        continue;
                    }

                    if (decremented_col_count >=
                        MAX_DECREMENTED_COUNTS) {
                        throw std::runtime_error(
                            "MAX_DECREMENTED_COUNTS exceeded");
                    }

                    --candidate_counts[other_col];
                    decremented_cols[
                        decremented_col_count++] =
                        other_col;
                }
            }
        }

        search(
            X,
            Y,
            active_cols,
            active_rows,
            candidate_counts,
            num_cols,
            depth + 1,
            stats);

        // Exact reversal of candidate-count decrements.
        for (int i = 0;
             i < decremented_col_count;
             ++i) {

            ++candidate_counts[
                decremented_cols[i]];
        }

        // Restore rows.
        for (int i = 0;
             i < deactivated_row_count;
             ++i) {

            active_rows[
                deactivated_rows[i]] = 1;
        }

        // Restore columns.
        for (int i = 0;
             i < deactivated_col_count;
             ++i) {

            active_cols[
                deactivated_cols[i]] = 1;
        }
    }
}

int main(int argc, char* argv[])
{
    if (argc != 4) {
        std::cerr
            << "Usage: "
            << argv[0]
            << " X Y Z\n";
        return 1;
    }

    try {
        const int Xdim = std::stoi(argv[1]);
        const int Ydim = std::stoi(argv[2]);
        const int Zdim = std::stoi(argv[3]);

        if (Xdim <= 0 ||
            Ydim <= 0 ||
            Zdim <= 0) {

            throw std::invalid_argument(
                "Box dimensions must be positive");
        }

        const int num_cols =
            Xdim * Ydim * Zdim;

        const std::string filename =
            "placements_N_" +
            std::to_string(Xdim) + "x" +
            std::to_string(Ydim) + "x" +
            std::to_string(Zdim) + ".txt";

        std::cout
            << "Box: "
            << Xdim << " x "
            << Ydim << " x "
            << Zdim << '\n';

        std::cout
            << "Cells: "
            << num_cols << '\n';

        const auto placements =
            load_placements(filename);

        const int num_rows =
            static_cast<int>(placements.size());

        std::cout
            << "Placements loaded: "
            << num_rows << '\n';

        const CSR X =
            build_x_csr(placements, num_cols);

        const CSR Y =
            build_y_csr(placements);

        std::cout
            << "X CSR: "
            << X.data.size()
            << " entries\n";

        std::cout
            << "Y CSR: "
            << Y.data.size()
            << " entries\n";

        std::vector<uint8_t> active_cols(
            static_cast<size_t>(num_cols),
            1);

        std::vector<uint8_t> active_rows(
            static_cast<size_t>(num_rows),
            1);

        std::vector<int> candidate_counts(
            static_cast<size_t>(num_cols),
            0);

        // Initially every row is active, so the candidate count for each
        // column is simply the length of its X CSR segment.
        for (int c = 0; c < num_cols; ++c) {
            candidate_counts[c] =
                X.indptr[c + 1] -
                X.indptr[c];
        }

        SearchStats stats;

        const auto start =
            std::chrono::steady_clock::now();

        search(
            X,
            Y,
            active_cols,
            active_rows,
            candidate_counts,
            num_cols,
            0,
            stats);

        const auto end =
            std::chrono::steady_clock::now();

        const double seconds =
            std::chrono::duration<double>(
                end - start).count();

        std::cout << '\n';

        std::cout
            << "Nodes: "
            << stats.nodes
            << '\n';

        std::cout
            << "Solutions: "
            << stats.solutions
            << '\n';

        std::cout
            << "Dead ends: "
            << stats.dead_ends
            << '\n';

        std::cout
            << "Max depth: "
            << stats.max_depth
            << '\n';

        std::cout
            << "Time: "
            << seconds
            << " s\n";

        if (seconds > 0.0) {
            std::cout
                << "Nodes/sec: "
                << static_cast<double>(stats.nodes) /
                   seconds
                << '\n';
        }

    } catch (const std::exception& e) {
        std::cerr
            << "Error: "
            << e.what()
            << '\n';

        return 1;
    }

    return 0;
}
