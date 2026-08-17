#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

constexpr int CELLS_PER_PLACEMENT = 5;
constexpr int MASK_WORDS = 3;

// ------------------------------------------------------------
// Placement representation
// ------------------------------------------------------------

struct Placement {
    int cells[CELLS_PER_PLACEMENT];
    uint64_t mask[MASK_WORDS] = {0, 0, 0};
};

// ------------------------------------------------------------
// Load placements
// ------------------------------------------------------------

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
        static_cast<std::size_t>(count));

    for (int i = 0; i < count; ++i) {
        for (int j = 0; j < CELLS_PER_PLACEMENT; ++j) {
            if (!(file >> placements[i].cells[j])) {
                throw std::runtime_error(
                    "Invalid placement data at placement " +
                    std::to_string(i));
            }

            const int cell = placements[i].cells[j];

            if (cell < 0) {
                throw std::runtime_error(
                    "Negative cell ID in placement data");
            }

            const int word = cell / 64;
            const int bit = cell % 64;

            if (word >= MASK_WORDS) {
                throw std::runtime_error(
                    "Cell ID exceeds current mask capacity");
            }

            placements[i].mask[word] |=
                (uint64_t{1} << bit);
        }
    }

    return placements;
}

// ------------------------------------------------------------
// Fast placement test
// ------------------------------------------------------------

bool fits(
    const uint64_t occupied[MASK_WORDS],
    const Placement& placement)
{
    for (int word = 0; word < MASK_WORDS; ++word) {
        if ((occupied[word] & placement.mask[word]) != 0) {
            return false;
        }
    }

    return true;
}

// ------------------------------------------------------------
// Place / undo
// ------------------------------------------------------------

void place(
    uint64_t occupied[MASK_WORDS],
    const Placement& placement)
{
    for (int word = 0; word < MASK_WORDS; ++word) {
        occupied[word] |= placement.mask[word];
    }
}

void undo(
    uint64_t occupied[MASK_WORDS],
    const Placement& placement)
{
    for (int word = 0; word < MASK_WORDS; ++word) {
        occupied[word] &= ~placement.mask[word];
    }
}

// ------------------------------------------------------------
// Choose the most constrained uncovered cell
//
// This is the key Algorithm X heuristic:
// choose the active column with the fewest legal rows.
// ------------------------------------------------------------

int choose_best_cell(
    const uint64_t occupied[MASK_WORDS],
    const std::vector<Placement>& placements,
    const std::vector<std::vector<int>>& placements_by_cell,
    int total_cells)
{
    int best_cell = -1;
    int best_count = std::numeric_limits<int>::max();

    for (int cell = 0; cell < total_cells; ++cell) {
        const int word = cell / 64;
        const int bit = cell % 64;

        // Already covered.
        if ((occupied[word] & (uint64_t{1} << bit)) != 0) {
            continue;
        }

        int count = 0;

        for (const int placement_index :
             placements_by_cell[cell]) {

            if (fits(
                    occupied,
                    placements[placement_index])) {
                ++count;

                // No need to count further once this cell
                // is already worse than the current best.
                if (count >= best_count) {
                    break;
                }
            }
        }

        // No legal placement can cover this cell:
        // this node is an immediate dead end.
        if (count == 0) {
            return cell;
        }

        if (count < best_count) {
            best_count = count;
            best_cell = cell;
        }
    }

    return best_cell;
}

// ------------------------------------------------------------
// Search statistics
// ------------------------------------------------------------

struct SearchStats {
    uint64_t nodes = 0;
    uint64_t solutions = 0;
    int max_depth = 0;
};

// ------------------------------------------------------------
// Recursive Algorithm X search
// ------------------------------------------------------------

void search(
    const std::vector<Placement>& placements,
    const std::vector<std::vector<int>>& placements_by_cell,
    uint64_t occupied[MASK_WORDS],
    int total_cells,
    int depth,
    SearchStats& stats)
{
    ++stats.nodes;

    if (depth > stats.max_depth) {
        stats.max_depth = depth;
    }

    const int cell = choose_best_cell(
        occupied,
        placements,
        placements_by_cell,
        total_cells);

    // No uncovered cells remain: complete tiling.
    if (cell < 0) {
        ++stats.solutions;
        return;
    }

    // Try only placements that cover the selected cell.
    for (const int placement_index :
         placements_by_cell[cell]) {

        const Placement& placement =
            placements[placement_index];

        if (!fits(occupied, placement)) {
            continue;
        }

        place(occupied, placement);

        search(
            placements,
            placements_by_cell,
            occupied,
            total_cells,
            depth + 1,
            stats);

        undo(occupied, placement);
    }
}

// ------------------------------------------------------------
// Main
// ------------------------------------------------------------

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
        const int X = std::stoi(argv[1]);
        const int Y = std::stoi(argv[2]);
        const int Z = std::stoi(argv[3]);

        if (X <= 0 || Y <= 0 || Z <= 0) {
            throw std::invalid_argument(
                "Box dimensions must be positive");
        }

        const int total_cells = X * Y * Z;

        if (total_cells > MASK_WORDS * 64) {
            throw std::runtime_error(
                "Box is too large for the current "
                "3-word mask");
        }

        const std::string filename =
            "placements_N_" +
            std::to_string(X) + "x" +
            std::to_string(Y) + "x" +
            std::to_string(Z) + ".txt";

        std::cout
            << "Box: "
            << X << " x "
            << Y << " x "
            << Z << '\n';

        std::cout
            << "Cells: "
            << total_cells << '\n';

        const auto placements =
            load_placements(filename);

        std::cout
            << "Placements loaded: "
            << placements.size() << '\n';

        // Reverse index:
        // cell -> all placements covering that cell.
        std::vector<std::vector<int>>
            placements_by_cell(total_cells);

        for (int i = 0;
             i < static_cast<int>(placements.size());
             ++i) {

            for (int j = 0;
                 j < CELLS_PER_PLACEMENT;
                 ++j) {

                const int cell =
                    placements[i].cells[j];

                if (cell < 0 || cell >= total_cells) {
                    throw std::runtime_error(
                        "Placement contains cell "
                        "outside the box");
                }

                placements_by_cell[cell].push_back(i);
            }
        }

        std::cout
            << "Placement index built.\n";

        uint64_t occupied[MASK_WORDS] =
            {0, 0, 0};

        SearchStats stats;

        const auto start =
            std::chrono::steady_clock::now();

        search(
            placements,
            placements_by_cell,
            occupied,
            total_cells,
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
                << static_cast<double>(stats.nodes)
                   / seconds
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
