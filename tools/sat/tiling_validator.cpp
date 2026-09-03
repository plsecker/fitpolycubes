// tiling_validator.cpp — standalone exact-cover tiling validator.
//
// Independently validates a claimed tiling of a W x H x NZ box by copies of
// one polycube.  Deliberately shares NO code with the Python SAT pipeline,
// the C++ search backend, or the repo's placement generators: the piece
// geometry is taken from the command line and all orientation/c legality
// checks are recomputed here from first principles.
//
// Usage:
//   tiling_validator W H NZ "x,y,z;x,y,z;..." TILING_FILE
//
// TILING_FILE format (produced by the SAT workflow for every SAT witness):
//   line 1: N  (number of pieces)
//   lines 2..N+1: piece_size*3 integers — x1 y1 z1 x2 y2 z2 ... per piece
//
// Checks:
//   1. volume divisibility and piece count N == W*H*NZ / piece_size
//   2. every piece has exactly piece_size cells, all inside the box
//   3. every piece is congruent (proper rotation + translation, NO
//      reflection) to the declared piece
//   4. the multiset of all piece cells is exactly the box: no overlap,
//      no gap
//
// Output: "VALID ..." and exit 0, or "INVALID: <reason>" and exit 1.
// Build: zig c++ -O2 -o tiling_validator tiling_validator.cpp
//        (any C++11 compiler works)

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <set>
#include <string>
#include <tuple>
#include <vector>

typedef std::tuple<int, int, int> Cell;
typedef std::vector<Cell> Shape;

static Shape parse_piece(const char* spec) {
    Shape out;
    const char* p = spec;
    while (*p) {
        int v[3];
        for (int i = 0; i < 3; i++) {
            char* end;
            long x = strtol(p, &end, 10);
            if (end == p) { fprintf(stderr, "bad piece spec\n"); exit(2); }
            v[i] = (int)x;
            p = end;
            if (i < 2) { if (*p == ',') p++; else { fprintf(stderr, "bad piece spec\n"); exit(2); } }
        }
        out.push_back(Cell(v[0], v[1], v[2]));
        if (*p == ';') p++;
        else if (*p == 0) break;
        else { fprintf(stderr, "bad piece spec\n"); exit(2); }
    }
    return out;
}

static Shape normalize(const Shape& s) {
    int mn[3] = {0, 0, 0};
    for (int i = 0; i < 3; i++) mn[i] = 1 << 29;
    for (const Cell& c : s)
        for (int i = 0; i < 3; i++) {
            int v = i == 0 ? std::get<0>(c) : i == 1 ? std::get<1>(c)
                                                     : std::get<2>(c);
            if (v < mn[i]) mn[i] = v;
        }
    Shape out;
    for (const Cell& c : s) {
        Cell t(std::get<0>(c) - mn[0], std::get<1>(c) - mn[1],
               std::get<2>(c) - mn[2]);
        out.push_back(t);
    }
    std::sort(out.begin(), out.end());
    return out;
}

// All 24 proper rotations: every permutation of axes with sign flips of
// determinant +1 (no reflections).
static std::vector<Shape> orientations(const Shape& piece) {
    std::vector<Shape> out;
    int perm[6][3] = {{0, 1, 2}, {0, 2, 1}, {1, 0, 2},
                      {1, 2, 0}, {2, 0, 1}, {2, 1, 0}};
    for (int pi = 0; pi < 6; pi++)
        for (int sx = -1; sx <= 1; sx += 2)
            for (int sy = -1; sy <= 1; sy += 2)
                for (int sz = -1; sz <= 1; sz += 2) {
                    int signs[3] = {sx, sy, sz};
                    int p[3] = {perm[pi][0], perm[pi][1], perm[pi][2]};
                    // det(M) = (product of signs) * sgn(permutation),
                    // with sgn(permutation) = (-1)^inversions
                    int inv = 0;
                    for (int i = 0; i < 3; i++)
                        for (int j = i + 1; j < 3; j++)
                            if (p[i] > p[j]) inv++;
                    int det_sign = (inv % 2 == 0) ? 1 : -1;
                    (void)signs;
                    if (sx * sy * sz * det_sign != 1) continue;
                    Shape rot;
                    for (const Cell& c : piece) {
                        int v[3] = {std::get<0>(c), std::get<1>(c),
                                    std::get<2>(c)};
                        rot.push_back(Cell(v[p[0]] * sx, v[p[1]] * sy,
                                           v[p[2]] * sz));
                    }
                    Shape n = normalize(rot);
                    bool seen = false;
                    for (const Shape& o : out)  // dedupe symmetric repeats
                        if (o == n) { seen = true; break; }
                    if (!seen) out.push_back(n);
                }
    return out;
}

int main(int argc, char** argv) {
    if (argc != 6) {
        fprintf(stderr,
                "usage: %s W H NZ \"x,y,z;x,y;z,...\" TILING_FILE\n",
                argv[0]);
        return 2;
    }
    int W = atoi(argv[1]), H = atoi(argv[2]), NZ = atoi(argv[3]);
    Shape piece = normalize(parse_piece(argv[4]));
    int psz = (int)piece.size();

    std::vector<Shape> oris = orientations(piece);
    if (oris.size() == 0) { printf("INVALID: no orientations\n"); return 1; }

    FILE* f = fopen(argv[5], "r");
    if (!f) { printf("INVALID: cannot open tiling file\n"); return 1; }
    long N;
    if (fscanf(f, "%ld", &N) != 1) {
        printf("INVALID: missing piece count\n"); return 1;
    }

    long long volume = (long long)W * H * NZ;
    if (volume % psz != 0) {
        printf("INVALID: volume %lld not divisible by piece size %d\n",
               volume, psz);
        return 1;
    }
    if (N != volume / psz) {
        printf("INVALID: piece count %ld != volume/size %lld\n", N,
               volume / psz);
        return 1;
    }

    std::vector<Cell> all;  // multiset via sort after collection
    all.reserve(N * psz);
    for (long i = 0; i < N; i++) {
        Shape s;
        for (int k = 0; k < psz; k++) {
            int v[3];
            for (int d = 0; d < 3; d++)
                if (fscanf(f, "%d", &v[d]) != 1) {
                    printf("INVALID: truncated piece %ld\n", i + 1);
                    return 1;
                }
            s.push_back(Cell(v[0], v[1], v[2]));
        }
        if (s.size() != psz) { printf("INVALID: piece %ld size\n", i + 1); return 1; }
        for (const Cell& c : s) {
            long x = std::get<0>(c), y = std::get<1>(c), z = std::get<2>(c);
            if (x < 0 || x >= W || y < 0 || y >= H || z < 0 || z >= NZ) {
                printf("INVALID: piece %ld cell (%ld,%ld,%ld) out of box\n",
                       i + 1, x, y, z);
                return 1;
            }
        }
        Shape n = normalize(s);
        bool ok = false;
        for (const Shape& o : oris)
            if (o == n) { ok = true; break; }
        if (!ok) {
            printf("INVALID: piece %ld is not a proper orientation of the "
                   "declared piece\n", i + 1);
            return 1;
        }
        for (const Cell& c : s) all.push_back(c);
    }
    fclose(f);

    if ((long)all.size() != volume) {
        printf("INVALID: total cells %zu != volume %lld\n", all.size(),
               volume);
        return 1;
    }
    std::sort(all.begin(), all.end());
    for (size_t i = 1; i < all.size(); i++)
        if (all[i] == all[i - 1]) {
            printf("INVALID: overlapping cell (%d,%d,%d)\n",
                   std::get<0>(all[i]), std::get<1>(all[i]),
                   std::get<2>(all[i]));
            return 1;
        }
    // exact cover: sorted distinct cells must equal the whole box, and the
    // count already matches, so no gap is possible after the overlap check
    // (count == volume, all distinct, all in box) — but verify explicitly.
    std::set<Cell> box;
    for (int x = 0; x < W; x++)
        for (int y = 0; y < H; y++)
            for (int z = 0; z < NZ; z++) box.insert(Cell(x, y, z));
    for (const Cell& c : all)
        if (!box.count(c)) {
            printf("INVALID: unexpected cell\n");
            return 1;
        }

    printf("VALID: %ld pieces x %d cells = %lld cells, exact cover of "
           "%dx%dx%d, all pieces proper orientations (%zu distinct)\n",
           N, psz, volume, W, H, NZ, oris.size());
    return 0;
}
