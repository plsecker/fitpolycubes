#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

constexpr int CELLS_PER_PLACEMENT = 5;
constexpr int MASK_WORDS = 3;

struct Placement {
    int cells[CELLS_PER_PLACEMENT];
    uint64_t mask[MASK_WORDS] = {0, 0, 0};
};

std::vector<Placement> load_placements(const std::string& filename) {
    std::ifstream file(filename);
    if (!file) {
        throw std::runtime_error("Could not open placements file: " + filename);
    }

    int count = 0;
    if (!(file >> count) || count < 0) {
        throw std::runtime_error("Invalid placement count");
    }

    std::vector<Placement> placements(static_cast<size_t>(count));

    for (int i = 0; i < count; ++i) {
        for (int j = 0; j < CELLS_PER_PLACEMENT; ++j) {
            if (!(file >> placements[i].cells[j])) {
                throw std::runtime_error(
                    "Invalid placement data at placement " + std::to_string(i));
            }

            const int cell = placements[i].cells[j];
            if (cell < 0 || cell >= MASK_WORDS * 64) {
                throw std::runtime_error("Cell ID outside mask capacity");
            }

            const int word = cell / 64;
            const int bit = cell % 64;
            placements[i].mask[word] |= (uint64_t{1} << bit);
        }
    }

    return placements;
}

struct SearchStats {
    uint64_t nodes = 0;
    uint64_t solutions = 0;
    uint64_t dead_ends = 0;
    int max_depth = 0;
};

void search(
    const std::vector<Placement>& placements,
    const std::vector<std::vector<int>>& X_rows,
    const std::vector<std::vector<int>>& Y_cols,
    std::vector<uint8_t>& active_cols,
    std::vector<uint8_t>& active_rows,
    int depth,
    SearchStats& stats)
{
    ++stats.nodes;
    if (depth > stats.max_depth) {
        stats.max_depth = depth;
    }

    // Exact equivalent of the Numba "all columns covered" check.
    bool any_active_col = false;
    for (uint8_t active : active_cols) {
        if (active) {
            any_active_col = true;
            break;
        }
    }

    if (!any_active_col) {
        ++stats.solutions;
        return;
    }

    // Choose active column with fewest active rows.
    int best_col = -1;
    int min_rows = 999999;

    for (int c = 0; c < static_cast<int>(active_cols.size()); ++c) {
        if (!active_cols[c]) {
            continue;
        }

        int count = 0;

        for (int r : X_rows[c]) {
            if (active_rows[r]) {
                ++count;
            }
        }

        if (count < min_rows) {
            min_rows = count;
            best_col = c;

            // Exact Numba early break.
            if (count == 0) {
                break;
            }
        }
    }

    if (min_rows == 0 || best_col == -1) {
        ++stats.dead_ends;
        return;
    }

    // Try each active row covering the selected column.
    for (int r : X_rows[best_col]) {
        if (!active_rows[r]) {
            continue;
        }

        // Match Numba's depth guard.
        if (depth >= static_cast<int>(placements.size())) {
            continue;
        }

        std::vector<int> deactivated_cols;
        std::vector<int> deactivated_rows;

        // Select: deactivate columns covered by row r,
        // then deactivate rows intersecting those columns.
        for (int c : Y_cols[r]) {
            if (active_cols[c]) {
                active_cols[c] = 0;
                deactivated_cols.push_back(c);

                for (int i : X_rows[c]) {
                    if (active_rows[i]) {
                        active_rows[i] = 0;
                        deactivated_rows.push_back(i);
                    }
                }
            }
        }

        search(
            placements,
            X_rows,
            Y_cols,
            active_cols,
            active_rows,
            depth + 1,
            stats);

        // Deselect: exact reverse of the Numba backtrack.
        for (int i : deactivated_rows) {
            active_rows[i] = 1;
        }

        for (int c : deactivated_cols) {
            active_cols[c] = 1;
        }
    }
}

int main(int argc, char* argv[]) {
    if (argc != 4) {
        std::cerr << "Usage: " << argv[0] << " X Y Z\n";
        return 1;
    }

    try {
        const int X = std::stoi(argv[1]);
        const int Y = std::stoi(argv[2]);
        const int Z = std::stoi(argv[3]);

        if (X <= 0 || Y <= 0 || Z <= 0) {
            throw std::invalid_argument("Box dimensions must be positive");
        }

        const int total_cells = X * Y * Z;
        if (total_cells > MASK_WORDS * 64) {
            throw std::runtime_error(
                "Box is too large for the current 3-word mask");
        }

        const std::string filename =
            "placements_N_" +
            std::to_string(X) + "x" +
            std::to_string(Y) + "x" +
            std::to_string(Z) + ".txt";

        std::cout << "Box: " << X << " x " << Y << " x " << Z << '\n';
        std::cout << "Cells: " << total_cells << '\n';

        const auto placements = load_placements(filename);
        const int num_rows = static_cast<int>(placements.size());
        const int num_cols = total_cells;

        std::cout << "Placements loaded: " << num_rows << '\n';

        // X_rows[c] = placement rows covering column/cell c.
        std::vector<std::vector<int>> X_rows(num_cols);

        // Y_cols[r] = columns/cells covered by placement row r.
        std::vector<std::vector<int>> Y_cols(num_rows);

        for (int r = 0; r < num_rows; ++r) {
            Y_cols[r].reserve(CELLS_PER_PLACEMENT);

            for (int j = 0; j < CELLS_PER_PLACEMENT; ++j) {
                const int c = placements[r].cells[j];

                if (c < 0 || c >= num_cols) {
                    throw std::runtime_error(
                        "Placement contains cell outside the box");
                }

                Y_cols[r].push_back(c);
                X_rows[c].push_back(r);
            }
        }

        std::vector<uint8_t> active_cols(num_cols, 1);
        std::vector<uint8_t> active_rows(num_rows, 1);

        SearchStats stats;

        const auto start = std::chrono::steady_clock::now();

        search(
            placements,
            X_rows,
            Y_cols,
            active_cols,
            active_rows,
            0,
            stats);

        const auto end = std::chrono::steady_clock::now();
        const double seconds =
            std::chrono::duration<double>(end - start).count();

        std::cout << "\n";
        std::cout << "Nodes: " << stats.nodes << '\n';
        std::cout << "Solutions: " << stats.solutions << '\n';
        std::cout << "Dead ends: " << stats.dead_ends << '\n';
        std::cout << "Max depth: " << stats.max_depth << '\n';
        std::cout << "Time: " << seconds << " s\n";

        if (seconds > 0.0) {
            std::cout << "Nodes/sec: "
                      << static_cast<double>(stats.nodes) / seconds
                      << '\n';
        }

        return stats.solutions > 0 ? 0 : 0;

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << '\n';
        return 1;
    }
}
