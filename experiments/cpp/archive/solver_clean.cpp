#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

constexpr int CELLS_PER_PLACEMENT = 5;

// Convert a 3D box coordinate into a flat cell index.
int cell_id(int x, int y, int z, int X, int Y, int Z) {
    if (x < 0 || x >= X ||
        y < 0 || y >= Y ||
        z < 0 || z >= Z) {
        throw std::out_of_range("Cell coordinate outside box");
    }

    return x + X * (y + Y * z);
}

// Convert a flat cell index back to (x,y,z) for diagnostics.
void print_cell(int id, int X, int Y) {
    const int x = id % X;
    const int t = id / X;
    const int y = t % Y;
    const int z = t / Y;

    std::cout << "(" << x << "," << y << "," << z << ")";
}

struct Placement {
    int cells[CELLS_PER_PLACEMENT];
};

// Return true when two placements share at least one box cell.
bool placements_overlap(const Placement& a, const Placement& b) {
    for (int i = 0; i < CELLS_PER_PLACEMENT; ++i) {
        for (int j = 0; j < CELLS_PER_PLACEMENT; ++j) {
            if (a.cells[i] == b.cells[j]) {
                return true;
            }
        }
    }

    return false;
}

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

    std::vector<Placement> placements(static_cast<std::size_t>(count));

    for (int i = 0; i < count; ++i) {
        for (int j = 0; j < CELLS_PER_PLACEMENT; ++j) {
            if (!(file >> placements[i].cells[j])) {
                throw std::runtime_error(
                    "Invalid placement data at placement " +
                    std::to_string(i));
            }

            if (placements[i].cells[j] < 0) {
                throw std::runtime_error(
                    "Negative cell ID in placement data");
            }
        }
    }

    return placements;
}

void print_placement(
    const Placement& placement,
    int index,
    int X,
    int Y,
    int total_cells)
{
    std::cout << "Placement #" << index << ":\n";

    for (int i = 0; i < CELLS_PER_PLACEMENT; ++i) {
        const int cell = placement.cells[i];

        if (cell < 0 || cell >= total_cells) {
            throw std::runtime_error(
                "Placement contains cell outside the box");
        }

        std::cout << "  cell[" << i << "] = "
                  << cell << " = ";

        print_cell(cell, X, Y);
        std::cout << '\n';
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
            throw std::invalid_argument(
                "Box dimensions must be positive");
        }

        const int total_cells = X * Y * Z;

        std::cout << "Box: "
                  << X << " x " << Y << " x " << Z << '\n';
        std::cout << "Cells: " << total_cells << "\n\n";

        const std::string filename =
            "placements_N_" +
            std::to_string(X) + "x" +
            std::to_string(Y) + "x" +
            std::to_string(Z) + ".txt";

        const auto placements = load_placements(filename);

        std::cout << "Placements loaded: "
                  << placements.size() << "\n\n";

        const int reference_index = 424;

        if (reference_index >= static_cast<int>(placements.size())) {
            throw std::runtime_error(
                "Reference placement #424 does not exist");
        }

        print_placement(
            placements[reference_index],
            reference_index,
            X,
            Y,
            total_cells);

        std::cout << "\nOverlap checks:\n";

        const bool self_overlap =
            placements_overlap(
                placements[reference_index],
                placements[reference_index]);

        std::cout << "  #424 vs #424: "
                  << (self_overlap ? "OVERLAP" : "NO OVERLAP")
                  << '\n';

        if (!self_overlap) {
            throw std::runtime_error(
                "Overlap test failed: placement does not overlap itself");
        }

        int disjoint_index = -1;

        for (int i = 0; i < static_cast<int>(placements.size()); ++i) {
            if (!placements_overlap(
                    placements[reference_index],
                    placements[i])) {
                disjoint_index = i;
                break;
            }
        }

        if (disjoint_index >= 0) {
            std::cout << "  #424 vs #" << disjoint_index
                      << ": NO OVERLAP\n";
        } else {
            throw std::runtime_error(
                "Could not find a disjoint placement");
        }

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << '\n';
        return 1;
    }

    return 0;
}
