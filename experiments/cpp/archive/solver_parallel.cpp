
#include <atomic>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

constexpr int CELLS_PER_PLACEMENT = 5;

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

struct UndoFrame {
    int deactivated_cols[CELLS_PER_PLACEMENT]{};
    int deactivated_col_prev[CELLS_PER_PLACEMENT]{};
    int deactivated_col_next[CELLS_PER_PLACEMENT]{};
    int deactivated_col_count = 0;

    std::vector<int> deactivated_rows;
    std::vector<int> decremented_cols;
};

struct SearchState {
    std::vector<uint8_t> active_rows;
    std::vector<int> candidate_counts;
    std::vector<int> next_col;
    std::vector<int> prev_col;
    int active_head = -1;
    int active_col_count = 0;
};

struct Task {
    std::vector<int> prefix;
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
    x.indptr.resize(static_cast<size_t>(num_cols) + 1, 0);

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

CSR build_y_csr(const std::vector<Placement>& placements)
{
    CSR y;
    const int num_rows = static_cast<int>(placements.size());

    y.indptr.resize(static_cast<size_t>(num_rows) + 1, 0);

    for (int r = 0; r < num_rows; ++r) {
        y.indptr[r + 1] =
            y.indptr[r] + CELLS_PER_PLACEMENT;
    }

    y.data.resize(static_cast<size_t>(y.indptr[num_rows]));

    for (int r = 0; r < num_rows; ++r) {
        for (int j = 0; j < CELLS_PER_PLACEMENT; ++j) {
            y.data[y.indptr[r] + j] = placements[r].cells[j];
        }
    }

    return y;
}

void init_state(
    SearchState& s,
    int num_rows,
    int num_cols,
    const CSR& X)
{
    s.active_rows.assign(static_cast<size_t>(num_rows), 1);
    s.candidate_counts.assign(static_cast<size_t>(num_cols), 0);
    s.next_col.resize(static_cast<size_t>(num_cols));
    s.prev_col.resize(static_cast<size_t>(num_cols));

    for (int c = 0; c < num_cols; ++c) {
        s.candidate_counts[c] =
            X.indptr[c + 1] - X.indptr[c];

        s.prev_col[c] = (c == 0) ? -1 : c - 1;
        s.next_col[c] =
            (c == num_cols - 1) ? -1 : c + 1;
    }

    s.active_head = (num_cols == 0) ? -1 : 0;
    s.active_col_count = num_cols;
}

int choose_best_col(const SearchState& s)
{
    int best_col = -1;
    int min_rows = std::numeric_limits<int>::max();

    for (int c = s.active_head; c != -1; c = s.next_col[c]) {
        const int count = s.candidate_counts[c];

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

void apply_row(
    const CSR& X,
    const CSR& Y,
    SearchState& s,
    int r,
    UndoFrame& frame)
{
    frame.deactivated_rows.clear();
    frame.decremented_cols.clear();
    frame.deactivated_col_count = 0;

    const int y_start = Y.indptr[r];
    const int y_end = Y.indptr[r + 1];

    for (int j = y_start; j < y_end; ++j) {
        const int c = Y.data[j];

        if (s.next_col[c] == -2) {
            continue;
        }

        const int p = s.prev_col[c];
        const int n = s.next_col[c];

        if (p == -1) {
            s.active_head = n;
        } else {
            s.next_col[p] = n;
        }

        if (n != -1) {
            s.prev_col[n] = p;
        }

        s.prev_col[c] = -2;
        s.next_col[c] = -2;

        const int i = frame.deactivated_col_count++;
        frame.deactivated_cols[i] = c;
        frame.deactivated_col_prev[i] = p;
        frame.deactivated_col_next[i] = n;

        const int x_start = X.indptr[c];
        const int x_end = X.indptr[c + 1];

        for (int q = x_start; q < x_end; ++q) {
            const int other = X.data[q];

            if (!s.active_rows[other]) {
                continue;
            }

            s.active_rows[other] = 0;
            frame.deactivated_rows.push_back(other);

            const int other_y_start = Y.indptr[other];
            const int other_y_end = Y.indptr[other + 1];

            for (int pp = other_y_start;
                 pp < other_y_end;
                 ++pp) {

                const int other_col = Y.data[pp];

                if (s.next_col[other_col] != -2) {
                    --s.candidate_counts[other_col];
                    frame.decremented_cols.push_back(other_col);
                }
            }
        }
    }

    s.active_col_count -= frame.deactivated_col_count;
}

void undo_row(
    SearchState& s,
    UndoFrame& frame)
{
    for (int c : frame.decremented_cols) {
        ++s.candidate_counts[c];
    }

    for (int r : frame.deactivated_rows) {
        s.active_rows[r] = 1;
    }

    for (int i = frame.deactivated_col_count - 1;
         i >= 0;
         --i) {

        const int c = frame.deactivated_cols[i];
        const int p = frame.deactivated_col_prev[i];
        const int n = frame.deactivated_col_next[i];

        s.prev_col[c] = p;
        s.next_col[c] = n;

        if (p == -1) {
            s.active_head = c;
        } else {
            s.next_col[p] = c;
        }

        if (n != -1) {
            s.prev_col[n] = c;
        }
    }

    s.active_col_count += frame.deactivated_col_count;
}

void search_recursive(
    const CSR& X,
    const CSR& Y,
    SearchState& s,
    int depth,
    SearchStats& stats,
    std::vector<UndoFrame>& frames,
    std::atomic<uint64_t>& global_nodes)
{
    ++stats.nodes;

    // Low-frequency heartbeat accounting: one atomic increment per
    // million local nodes, so it does not materially perturb the search.
    if ((stats.nodes & ((1ULL << 20) - 1)) == 0) {
        global_nodes.fetch_add(1ULL << 20,
                               std::memory_order_relaxed);
    }

    if (depth > stats.max_depth) {
        stats.max_depth = depth;
    }

    if (s.active_col_count == 0) {
        ++stats.solutions;
        return;
    }

    const int best_col = choose_best_col(s);

    if (best_col == -1 || s.candidate_counts[best_col] == 0) {
        ++stats.dead_ends;
        return;
    }

    UndoFrame& frame = frames[depth];

    const int row_start = X.indptr[best_col];
    const int row_end = X.indptr[best_col + 1];

    for (int k = row_start; k < row_end; ++k) {
        const int r = X.data[k];

        if (!s.active_rows[r]) {
            continue;
        }

        apply_row(X, Y, s, r, frame);

        search_recursive(
            X, Y, s, depth + 1, stats,
            frames, global_nodes);

        undo_row(s, frame);
    }
}

void generate_tasks_recursive(
    const CSR& X,
    const CSR& Y,
    SearchState& s,
    int depth,
    int split_depth,
    std::vector<int>& prefix,
    std::vector<Task>& tasks,
    std::vector<UndoFrame>& frames)
{
    if (depth == split_depth ||
        s.active_col_count == 0) {

        tasks.push_back(Task{prefix});
        return;
    }

    const int best_col = choose_best_col(s);

    if (best_col == -1 ||
        s.candidate_counts[best_col] == 0) {

        tasks.push_back(Task{prefix});
        return;
    }

    UndoFrame& frame = frames[depth];

    const int row_start = X.indptr[best_col];
    const int row_end = X.indptr[best_col + 1];

    for (int k = row_start; k < row_end; ++k) {
        const int r = X.data[k];

        if (!s.active_rows[r]) {
            continue;
        }

        prefix.push_back(r);

        apply_row(X, Y, s, r, frame);

        generate_tasks_recursive(
            X, Y, s, depth + 1,
            split_depth, prefix, tasks, frames);

        undo_row(s, frame);

        prefix.pop_back();
    }
}

void heartbeat_thread(
    std::atomic<bool>& finished,
    std::atomic<uint64_t>& global_nodes,
    const std::chrono::steady_clock::time_point& start)
{
    while (!finished.load(std::memory_order_relaxed)) {
        std::this_thread::sleep_for(std::chrono::seconds(10));

        if (finished.load(std::memory_order_relaxed)) {
            break;
        }

        const auto now = std::chrono::steady_clock::now();
        const double elapsed =
            std::chrono::duration<double>(
                now - start).count();

        const uint64_t nodes =
            global_nodes.load(std::memory_order_relaxed);

        const double rate =
            elapsed > 0.0
                ? static_cast<double>(nodes) / elapsed
                : 0.0;

        std::cerr
            << "[heartbeat] nodes=" << nodes
            << " elapsed=" << elapsed << "s"
            << " rate=" << rate << " nodes/s\n";
    }
}

int main(int argc, char* argv[])
{
    if (argc != 8 ||
        std::string(argv[2]) != "--box" ||
        std::string(argv[6]) != "--workers") {

        std::cerr
            << "Usage: "
            << argv[0]
            << " PIECE --box X Y Z --workers N\n";
        return 1;
    }

    try {
        const std::string piece = argv[1];
        const int Xdim = std::stoi(argv[3]);
        const int Ydim = std::stoi(argv[4]);
        const int Zdim = std::stoi(argv[5]);
        const int workers = std::stoi(argv[7]);

        if (piece.empty() ||
            Xdim <= 0 || Ydim <= 0 || Zdim <= 0 ||
            workers <= 0) {

            throw std::invalid_argument(
                "Invalid piece, dimensions, or worker count");
        }

        const int num_cols = Xdim * Ydim * Zdim;

        const std::string filename =
            "placements_" + piece + "_" +
            std::to_string(Xdim) + "x" +
            std::to_string(Ydim) + "x" +
            std::to_string(Zdim) + ".txt";

        std::cout
            << "Piece: " << piece << '\n'
            << "Box: " << Xdim << " x "
            << Ydim << " x " << Zdim << '\n'
            << "Cells: " << num_cols << '\n';

        const auto placements =
            load_placements(filename);

        const int num_rows =
            static_cast<int>(placements.size());

        const CSR X =
            build_x_csr(placements, num_cols);

        const CSR Y =
            build_y_csr(placements);

        std::cout
            << "Placements loaded: " << num_rows << '\n'
            << "X CSR: " << X.data.size() << " entries\n"
            << "Y CSR: " << Y.data.size() << " entries\n";

        const int max_depth =
            (num_cols + CELLS_PER_PLACEMENT - 1) /
            CELLS_PER_PLACEMENT;

        // Build enough independent subtrees for the workers.
        int split_depth = 1;
        std::vector<Task> tasks;

        while (true) {
            SearchState split_state;
            init_state(
                split_state,
                num_rows,
                num_cols,
                X);

            std::vector<UndoFrame> split_frames(
                static_cast<size_t>(split_depth + 1));

            for (auto& frame : split_frames) {
                frame.deactivated_rows.reserve(
                    static_cast<size_t>(num_rows));
                frame.decremented_cols.reserve(
                    static_cast<size_t>(num_rows) *
                    CELLS_PER_PLACEMENT);
            }

            std::vector<int> prefix;
            tasks.clear();

            generate_tasks_recursive(
                X, Y,
                split_state,
                0,
                split_depth,
                prefix,
                tasks,
                split_frames);

            if (static_cast<int>(tasks.size()) >= workers * 4 ||
                split_depth >= 6 ||
                split_depth >= max_depth) {

                break;
            }

            ++split_depth;
        }

        std::cout
            << "Split depth: " << split_depth << '\n'
            << "Tasks: " << tasks.size() << '\n'
            << "Workers: " << workers << '\n';

        std::atomic<int> next_task{0};
        std::atomic<uint64_t> global_nodes{0};
        std::atomic<bool> finished{false};

        const auto start =
            std::chrono::steady_clock::now();

        std::thread heartbeat(
            heartbeat_thread,
            std::ref(finished),
            std::ref(global_nodes),
            start);

        std::vector<SearchStats> worker_stats(
            static_cast<size_t>(workers));

        std::vector<std::thread> threads;
        threads.reserve(static_cast<size_t>(workers));

        for (int w = 0; w < workers; ++w) {
            threads.emplace_back([&, w]() {
                SearchState state;
                init_state(
                    state,
                    num_rows,
                    num_cols,
                    X);

                std::vector<UndoFrame> frames(
                    static_cast<size_t>(max_depth + 1));

                for (auto& frame : frames) {
                    frame.deactivated_rows.reserve(
                        static_cast<size_t>(num_rows));
                    frame.decremented_cols.reserve(
                        static_cast<size_t>(num_rows) *
                        CELLS_PER_PLACEMENT);
                }

                while (true) {
                    const int task_index =
                        next_task.fetch_add(
                            1,
                            std::memory_order_relaxed);

                    if (task_index >=
                        static_cast<int>(tasks.size())) {

                        break;
                    }

                    const Task& task =
                        tasks[task_index];

                    init_state(
                        state,
                        num_rows,
                        num_cols,
                        X);

                    for (int depth = 0;
                         depth <
                         static_cast<int>(task.prefix.size());
                         ++depth) {

                        apply_row(
                            X,
                            Y,
                            state,
                            task.prefix[depth],
                            frames[depth]);
                    }

                    SearchStats local;

                    search_recursive(
                        X,
                        Y,
                        state,
                        static_cast<int>(task.prefix.size()),
                        local,
                        frames,
                        global_nodes);

                    worker_stats[w].nodes +=
                        local.nodes;

                    worker_stats[w].solutions +=
                        local.solutions;

                    worker_stats[w].dead_ends +=
                        local.dead_ends;

                    if (local.max_depth >
                        worker_stats[w].max_depth) {

                        worker_stats[w].max_depth =
                            local.max_depth;
                    }
                }
            });
        }

        for (auto& thread : threads) {
            thread.join();
        }

        finished.store(
            true,
            std::memory_order_relaxed);

        heartbeat.join();

        uint64_t total_nodes = 0;
        uint64_t total_solutions = 0;
        uint64_t total_dead_ends = 0;
        int max_depth_seen = 0;

        for (const auto& stats : worker_stats) {
            total_nodes += stats.nodes;
            total_solutions += stats.solutions;
            total_dead_ends += stats.dead_ends;

            if (stats.max_depth > max_depth_seen) {
                max_depth_seen = stats.max_depth;
            }
        }

        const auto end =
            std::chrono::steady_clock::now();

        const double seconds =
            std::chrono::duration<double>(
                end - start).count();

        std::cout
            << '\n'
            << "Nodes: " << total_nodes << '\n'
            << "Solutions: " << total_solutions << '\n'
            << "Dead ends: " << total_dead_ends << '\n'
            << "Max depth: " << max_depth_seen << '\n'
            << "Time: " << seconds << " s\n";

        if (seconds > 0.0) {
            std::cout
                << "Nodes/sec: "
                << static_cast<double>(total_nodes) /
                   seconds
                << '\n';
        }

    } catch (const std::exception& e) {
        std::cerr
            << "Error: " << e.what() << '\n';
        return 1;
    }

    return 0;
}
