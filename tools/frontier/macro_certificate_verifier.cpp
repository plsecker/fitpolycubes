// Macro-walk certificate verifier — independent C++17 implementation.
//
// Implements Layer A of the frozen protocol documented in
// docs/frontier/macro_certificate_format.md (fitpolycubes.macro-walk v1,
// semantics_id "fitpolycubes.macro-walk/semantics-1").
//
// Deliberately implemented WITHOUT looking at the repository's Python checker:
// the specification used is the format document + JSON schema only.
// Dependencies: C++17 standard library ONLY.
//
// Arbitrary-precision strategy: states are stored as two layer masks
// (l0, l1), each an array of 64-bit limbs sized to NCELLS bits. Decimal
// mask values are parsed digit-by-digit (mul10-add), so mask width is
// limited only by memory, not by 64 bits. No packed big integers are ever
// formed; shift semantics act on layers directly.
//
// Usage: macro_certificate_verifier <cert.json> [<cert.json> ...]
// Exit 0 iff every certificate passes all Layer-A checks.

#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <vector>

static const char* SEMANTICS_ID = "fitpolycubes.macro-walk/semantics-1";

// ---------------------------------------------------------------------------
// Minimal JSON value + recursive-descent parser (stdlib only).
// ---------------------------------------------------------------------------

struct JV {
    enum Kind { OBJ, ARR, STR, NUM, BOOL, NUL } kind = NUL;
    std::map<std::string, JV> obj;
    std::vector<JV> arr;
    std::string str;
    std::string num;   // raw numeric token (for exact integer handling)
    bool b = false;

    bool has(const std::string& k) const {
        return kind == OBJ && obj.count(k) != 0;
    }
    const JV* get(const std::string& k) const {
        if (kind != OBJ) return nullptr;
        auto it = obj.find(k);
        return it == obj.end() ? nullptr : &it->second;
    }
    bool is_int_token() const {
        if (kind != NUM) return false;
        const std::string& t = num;
        size_t i = 0;
        if (i < t.size() && (t[i] == '-' || t[i] == '+')) i++;
        if (i >= t.size()) return false;
        for (size_t j = i; j < t.size(); j++)
            if (t[j] < '0' || t[j] > '9') return false;
        return true;
    }
};

class JsonParser {
public:
    explicit JsonParser(const std::string& text) : s_(text), i_(0) {}

    JV parse() {
        skip_ws();
        JV v = parse_value();
        skip_ws();
        if (i_ != s_.size()) fail("trailing content after JSON value");
        return v;
    }

private:
    std::string s_;      // by value: callers may pass temporaries (ss.str())
    size_t i_;

    [[noreturn]] static void fail(const std::string& m) {
        throw std::runtime_error("JSON parse error: " + m);
    }
    void skip_ws() {
        while (i_ < s_.size() &&
               (s_[i_] == ' ' || s_[i_] == '\t' || s_[i_] == '\n' || s_[i_] == '\r'))
            i_++;
    }
    char peek() {
        if (i_ >= s_.size()) fail("unexpected end of input");
        return s_[i_];
    }
    void expect(char c) {
        if (peek() != c) fail(std::string("expected '") + c + "'");
        i_++;
    }

    JV parse_value() {
        skip_ws();
        char c = peek();
        switch (c) {
            case '{': return parse_obj();
            case '[': return parse_arr();
            case '"': { JV v; v.kind = JV::STR; v.str = parse_string(); return v; }
            case 't': lit("true");  { JV v; v.kind = JV::BOOL; v.b = true;  return v; }
            case 'f': lit("false"); { JV v; v.kind = JV::BOOL; v.b = false; return v; }
            case 'n': lit("null");  { JV v; v.kind = JV::NUL; return v; }
            default:  return parse_num();
        }
    }
    void lit(const char* w) {
        for (const char* p = w; *p; p++) {
            if (i_ >= s_.size() || s_[i_] != *p) fail("bad literal");
            i_++;
        }
    }
    JV parse_obj() {
        expect('{');
        JV v; v.kind = JV::OBJ;
        skip_ws();
        if (peek() == '}') { i_++; return v; }
        while (true) {
            skip_ws();
            std::string k = parse_string();
            skip_ws(); expect(':'); skip_ws();
            v.obj[k] = parse_value();
            skip_ws();
            if (peek() == ',') { i_++; continue; }
            expect('}');
            break;
        }
        return v;
    }
    JV parse_arr() {
        expect('[');
        JV v; v.kind = JV::ARR;
        skip_ws();
        if (peek() == ']') { i_++; return v; }
        while (true) {
            skip_ws();
            v.arr.push_back(parse_value());
            skip_ws();
            if (peek() == ',') { i_++; continue; }
            expect(']');
            break;
        }
        return v;
    }
    std::string parse_string() {
        expect('"');
        std::string out;
        while (true) {
            if (i_ >= s_.size()) fail("unterminated string");
            char c = s_[i_++];
            if (c == '"') break;
            if (c == '\\') {
                if (i_ >= s_.size()) fail("bad escape");
                char e = s_[i_++];
                switch (e) {
                    case '"': out += '"'; break;
                    case '\\': out += '\\'; break;
                    case '/': out += '/'; break;
                    case 'n': out += '\n'; break;
                    case 't': out += '\t'; break;
                    case 'r': out += '\r'; break;
                    case 'b': case 'f': break;
                    case 'u':
                        if (i_ + 4 > s_.size()) fail("bad \\u");
                        i_ += 4;          // content unused by this protocol
                        out += '?';
                        break;
                    default: fail("bad escape");
                }
            } else {
                out += c;
            }
        }
        return out;
    }
    JV parse_num() {
        size_t start = i_;
        if (peek() == '-' || peek() == '+') i_++;
        bool digits = false;
        while (i_ < s_.size() && ((s_[i_] >= '0' && s_[i_] <= '9') ||
                                  s_[i_] == '.' || s_[i_] == 'e' || s_[i_] == 'E' ||
                                  s_[i_] == '+' || s_[i_] == '-')) {
            digits = digits || (s_[i_] >= '0' && s_[i_] <= '9');
            i_++;
        }
        if (!digits) fail("bad number");
        JV v; v.kind = JV::NUM; v.num = s_.substr(start, i_ - start);
        return v;
    }
};

// ---------------------------------------------------------------------------
// Layer masks with decimal (arbitrary-width) parsing.
// ---------------------------------------------------------------------------

struct Mask {
    std::vector<uint64_t> w;

    static Mask zero(size_t bits) {
        return Mask{std::vector<uint64_t>((bits + 63) / 64, 0)};
    }

    static Mask from_dec(const std::string& tok) {
        Mask r = zero(1);
        for (char ch : tok) {
            if (ch < '0' || ch > '9')
                throw std::runtime_error("state mask is not a decimal integer");
            // r = r*10 + digit
            uint64_t carry = static_cast<uint64_t>(ch - '0');
            for (auto& word : r.w) {
                unsigned __int128 cur =
                    static_cast<unsigned __int128>(word) * 10ULL + carry;
                word = static_cast<uint64_t>(cur);
                carry = static_cast<uint64_t>(cur >> 64);
            }
            if (carry) r.w.push_back(carry);
        }
        return r;
    }
    void trim() {
        while (w.size() > 1 && w.back() == 0) w.pop_back();
    }
    void set_bit(size_t i) {
        if (i / 64 >= w.size()) w.resize(i / 64 + 1, 0);
        w[i / 64] |= (1ULL << (i % 64));
    }
    bool test(size_t i) const {
        size_t k = i / 64;
        return k < w.size() && ((w[k] >> (i % 64)) & 1ULL);
    }
    int popcount_trimmed() const {
        int c = 0;
        for (size_t k = 0; k * 64 < w.size() * 64 && k < w.size(); k++)
            c += __builtin_popcountll(w[k]);
        return c;
    }
    bool operator==(const Mask& o) const {
        size_t n = std::max(w.size(), o.w.size());
        for (size_t k = 0; k < n; k++) {
            uint64_t x = k < w.size() ? w[k] : 0;
            uint64_t y = k < o.w.size() ? o.w[k] : 0;
            if (x != y) return false;
        }
        return true;
    }
};

// ---------------------------------------------------------------------------
// Certificate checking.
// ---------------------------------------------------------------------------

using Cell = std::array<int, 3>;
using Piece = std::vector<Cell>;   // exactly 5 cells


struct Checker {
    const JV& root;
    long a = 0, b = 0, z = 0;
    long ncells = 0;
    std::vector<Piece> orientations;
    std::vector<std::string> lines;
    bool ok = true;

    explicit Checker(const JV& r) : root(r) {}

    void rec(const std::string& m) { lines.push_back(m); }
    [[noreturn]] void bad(const std::string& m) {
        lines.push_back("[FAIL] " + m);
        throw int(0);
    }
#define REQUIRE(cond, msg) do { if (!(cond)) bad(msg); } while (0)

    Cell cell_of(const JV& v) {
        REQUIRE(v.kind == JV::ARR && v.arr.size() == 3,
                "cell must be an array of 3 integers");
        Cell c;
        for (int i = 0; i < 3; i++) {
            REQUIRE(v.arr[size_t(i)].kind == JV::NUM &&
                    v.arr[size_t(i)].is_int_token(),
                    "non-integer coordinate");
            const std::string& t = v.arr[size_t(i)].num;
            REQUIRE(t.size() <= 18, "coordinate magnitude out of supported range");
            c[size_t(i)] = std::stoi(t);
        }
        return c;
    }

    static Piece norm(const Piece& p) {
        int mn[3] = {p[0][0], p[0][1], p[0][2]};
        for (auto& c : p)
            for (int i = 0; i < 3; i++) mn[i] = std::min(mn[i], c[i]);
        Piece q = p;
        for (auto& c : q)
            for (int i = 0; i < 3; i++) c[i] -= mn[i];
        std::sort(q.begin(), q.end());
        return q;
    }

    void build_orientations(const Piece& g) {
        std::vector<int> perm = {0, 1, 2};
        do {
            for (int sx = -1; sx <= 1; sx += 2)
                for (int sy = -1; sy <= 1; sy += 2)
                    for (int sz = -1; sz <= 1; sz += 2) {
                        int sgn[3] = {sx, sy, sz};
                        // determinant = perm_sign * product(signs)
                        int psign = 1;
                        for (size_t i = 0; i < 3; i++)
                            for (size_t j = i + 1; j < 3; j++)
                                if (perm[i] > perm[j]) psign = -psign;
                        int det = psign * sx * sy * sz;
                        if (det != 1) continue;
                        Piece img(5);
                        for (int i = 0; i < 5; i++)
                            for (int k = 0; k < 3; k++)
                                img[size_t(i)][k] = sgn[k] * g[size_t(i)][perm[size_t(k)]];
                        orientations.push_back(norm(img));
                    }
        } while (std::next_permutation(perm.begin(), perm.end()));
        std::sort(orientations.begin(), orientations.end());
        orientations.erase(std::unique(orientations.begin(), orientations.end()),
                           orientations.end());
    }

    bool congruent(const Piece& p) const {
        return std::binary_search(orientations.begin(), orientations.end(),
                                  norm(p));
    }

    std::string run() {
        try {
            do_check();
            ok = true;
        } catch (int) {
            ok = false;
        } catch (const std::exception& e) {
            lines.push_back(std::string("[FAIL] malformed certificate: ") + e.what());
            ok = false;
        }
        return ok ? "LAYER-A VALID" : "INVALID";
    }

    void do_check();

    // helpers shared by C2/C4/C6/C7g
    struct State {
        Mask l0, l1;
    };
};

void Checker::do_check() {
    // format tag
    const JV* fmt = root.get("format");
    REQUIRE(fmt && fmt->kind == JV::STR &&
            fmt->str.find("macro-walk") != std::string::npos,
            "not a macro-walk certificate");

    // pinned semantics  [protocol rev 2026-08-26a]
    const JV* conv = root.get("conventions");
    REQUIRE(conv && conv->kind == JV::OBJ, "missing conventions");
    const JV* sid = conv->get("semantics_id");
    REQUIRE(sid && sid->kind == JV::STR && sid->str == SEMANTICS_ID,
            std::string("conventions.semantics_id must be ") + SEMANTICS_ID);

    // box
    const JV* box = root.get("box");
    REQUIRE(box && box->kind == JV::OBJ, "missing box");
    const JV* va = box->get("a"); const JV* vb = box->get("b");
    const JV* vz = box->get("z");
    REQUIRE(va && vb && vz && va->kind == JV::NUM && vb->kind == JV::NUM &&
            vz->kind == JV::NUM && va->is_int_token() && vb->is_int_token() &&
            vz->is_int_token(), "box dimensions must be integers");
    a = std::stol(va->num); b = std::stol(vb->num); z = std::stol(vz->num);
    REQUIRE(a >= 1 && b >= 1 && z >= 1, "box dimensions must be positive");
    ncells = a * b;

    // piece geometry: C0 sanity
    const JV* piece = root.get("piece");
    REQUIRE(piece && piece->kind == JV::OBJ, "missing piece");
    const JV* geomv = piece->get("geometry");
    REQUIRE(geomv && geomv->kind == JV::ARR && geomv->arr.size() == 5,
            "pentacube certificates must have exactly 5 cells");
    const JV* cc = piece->get("cell_count");
    REQUIRE(cc && cc->kind == JV::NUM && cc->is_int_token() &&
            std::stol(cc->num) == 5, "cell_count must be 5");
    Piece g;
    for (const JV& c : geomv->arr) g.push_back(cell_of(c));
    REQUIRE(std::set<Cell>(g.begin(), g.end()).size() == 5,
            "geometry contains duplicate cells");
    {
        // face-connectivity BFS
        std::set<Cell> cs(g.begin(), g.end());
        std::set<Cell> seen{g[0]};
        std::vector<Cell> st{g[0]};
        while (!st.empty()) {
            Cell c = st.back(); st.pop_back();
            Cell nb[6] = {{c[0]+1,c[1],c[2]}, {c[0]-1,c[1],c[2]},
                          {c[0],c[1]+1,c[2]}, {c[0],c[1]-1,c[2]},
                          {c[0],c[1],c[2]+1}, {c[0],c[1],c[2]-1}};
            for (auto& nn : nb)
                if (cs.count(nn) && !seen.count(nn)) { seen.insert(nn); st.push_back(nn); }
        }
        REQUIRE(seen.size() == 5, "geometry is not face-connected");
    }
    build_orientations(g);
    rec("C0 geometry: 5 distinct face-connected cells; proper-rotation "
        "orientation set derived (" + std::to_string(orientations.size()) +
        " images); semantics pinned");

    // C1 volume
    REQUIRE((a * b * z) % 5 == 0, "volume not divisible by cell count");
    rec("C1 box " + std::to_string(a) + "x" + std::to_string(b) + "x" +
        std::to_string(z) + "; volume " + std::to_string(a * b * z) +
        "; " + std::to_string(a * b * z / 5) + " pieces");

    // C2 stored tiling (dual-key conflict refused)
    const JV* bt = root.get("box_tiling");
    const JV* pl = root.get("placements");
    REQUIRE(bt || pl, "missing box_tiling/placements");
    if (bt && pl) {
        // normalized comparison: sorted pieces of sorted cells
        auto norm_repr = [this](const JV& t) {
            std::vector<Piece> ps;
            for (const JV& p : t.arr) {
                Piece pc;
                for (const JV& c : p.arr) pc.push_back(cell_of(c));
                std::sort(pc.begin(), pc.end());
                ps.push_back(pc);
            }
            std::sort(ps.begin(), ps.end());
            return ps;
        };
        REQUIRE(norm_repr(*bt) == norm_repr(*pl),
                "both box_tiling and placements present and inconsistent");
    }
    const JV& tiling = bt ? *bt : *pl;
    REQUIRE(tiling.kind == JV::ARR &&
            tiling.arr.size() == size_t(a * b * z / 5), "wrong piece count");
    std::set<Cell> allcells;
    for (const JV& pjv : tiling.arr) {
        REQUIRE(pjv.kind == JV::ARR && pjv.arr.size() == 5, "bad piece size");
        Piece pc;
        for (const JV& cjv : pjv.arr) {
            Cell c = cell_of(cjv);
            REQUIRE(0 <= c[0] && c[0] < a && 0 <= c[1] && c[1] < b &&
                    0 <= c[2] && c[2] < z,
                    "placement cell out of bounds");
            REQUIRE(allcells.insert(c).second, "overlapping cells");
            pc.push_back(c);
        }
        REQUIRE(congruent(pc), "placement not congruent to embedded geometry");
    }
    rec("C2 stored tiling: bounds ok, exact disjoint cover, all shapes "
        "congruent to embedded geometry under proper rotations");

    // C3 walk structure
    const JV* walkv = root.get("walk");
    REQUIRE(walkv && walkv->kind == JV::ARR &&
            walkv->arr.size() == size_t(z + 1), "walk must have z+1 states");
    auto state_masks = [&](const JV& st) -> std::pair<Mask, Mask> {
        REQUIRE(st.kind == JV::OBJ, "walk state must be an object");
        const JV* l0 = st.get("l0"); const JV* l1 = st.get("l1");
        REQUIRE(l0 && l1 && l0->kind == JV::NUM && l1->kind == JV::NUM &&
                l0->is_int_token() && l1->is_int_token(),
                "walk state needs integer l0 and l1");
        REQUIRE(l0->num[0] != '-', "negative state mask");
        REQUIRE(l1->num[0] != '-', "negative state mask");
        return {Mask::from_dec(l0->num), Mask::from_dec(l1->num)};
    };
    const JV* st0 = &walkv->arr[0];
    auto m0pair = state_masks(*st0);
    REQUIRE(m0pair.first.popcount_trimmed() == 0 &&
            m0pair.second.popcount_trimmed() == 0, "does not start at 0");
    const JV* stz = &walkv->arr[size_t(z)];
    auto mzpair = state_masks(*stz);
    REQUIRE(mzpair.first.popcount_trimmed() == 0 &&
            mzpair.second.popcount_trimmed() == 0, "does not end at 0");
    for (size_t k = 0; k < walkv->arr.size(); k++) {
        const JV* sp = walkv->arr[k].get("step");
        if (sp) {
            REQUIRE(sp->kind == JV::NUM && sp->is_int_token() &&
                    std::stol(sp->num) == long(k),
                    "walk step label does not match position");
        }
    }

    // C4/C5 edges
    const JV* fills = root.get("edge_fills");
    REQUIRE(fills && fills->kind == JV::ARR && fills->arr.size() == size_t(z),
            "edge_fills must have z entries");
    Mask cur0 = Mask::zero(size_t(ncells)), cur1 = Mask::zero(size_t(ncells));
    for (long k = 0; k < z; k++) {
        const JV& edge = fills->arr[size_t(k)];
        REQUIRE(edge.kind == JV::ARR, "edge must be an array");
        std::vector<Cell> allcells;
        for (const JV& pjv : edge.arr) {
            REQUIRE(pjv.kind == JV::ARR && pjv.arr.size() == 5,
                    "edge piece must have 5 cells");
            Piece pc;
            for (const JV& cjv : pjv.arr) {
                Cell c = cell_of(cjv);
                REQUIRE(0 <= c[0] && c[0] < a && 0 <= c[1] && c[1] < b,
                        "edge fill cell out of window bounds");
                REQUIRE(0 <= c[2] && c[2] <= 2,
                        "edge fill window layer must be 0..2");
                pc.push_back(c);
                allcells.push_back(c);
            }
            REQUIRE(congruent(pc), "edge fill piece not congruent to geometry");
        }
        std::sort(allcells.begin(), allcells.end());
        REQUIRE(std::adjacent_find(allcells.begin(), allcells.end()) ==
                allcells.end(), "edge pieces overlap each other or the state");
        for (const Cell& c : allcells) {
            long cid = c[0] + a * c[1];
            bool occupied = (c[2] == 0) ? cur0.test(size_t(cid))
                                        : (c[2] == 1) ? cur1.test(size_t(cid))
                                                      : false;
            REQUIRE(!occupied, "edge fill hits occupied cell");
        }
        // slot-0 completion
        long covered = 0;
        for (long i = 0; i < ncells; i++)
            covered += cur0.test(size_t(i)) ? 1 : 0;
        for (const Cell& c : allcells)
            if (c[2] == 0 && !cur0.test(size_t(c[0] + a * c[1]))) covered++;
        REQUIRE(covered == ncells, "edge does not complete slot 0");
        // successor
        Mask nx0 = cur1, nx1 = Mask::zero(size_t(ncells));
        for (const Cell& c : allcells) {
            long cid = c[0] + a * c[1];
            if (c[2] == 1) nx0.set_bit(size_t(cid));
            if (c[2] == 2) nx1.set_bit(size_t(cid));
        }
        auto nxt = state_masks(walkv->arr[size_t(k + 1)]);
        REQUIRE(nx0 == nxt.first && nx1 == nxt.second,
                "shift(source+fill) != stored successor state");
        cur0 = nx0; cur1 = nx1;
    }
    REQUIRE(cur0.popcount_trimmed() == 0 && cur1.popcount_trimmed() == 0,
            "recomputed walk does not close at 0");
    rec("C4/C5 all " + std::to_string(z) +
        " edges legal by set arithmetic; recomputed walk equals stored; "
        "closes at 0 after " + std::to_string(z) + " edges");

    // C6 reconstruction equals stored tiling
    std::set<std::set<Cell>> rebuilt;
    for (long k = 0; k < z; k++)
        for (const JV& pjv : fills->arr[size_t(k)].arr) {
            std::set<Cell> fs;
            for (const JV& cjv : pjv.arr) {
                Cell c = cell_of(cjv);
                fs.insert(Cell{c[0], c[1], int(k) + c[2]});
            }
            REQUIRE(rebuilt.insert(fs).second, "reconstruction overlap");
        }
    std::set<std::set<Cell>> storedset;
    for (const JV& pjv : tiling.arr) {
        std::set<Cell> fs;
        for (const JV& cjv : pjv.arr) fs.insert(cell_of(cjv));
        storedset.insert(fs);
    }
    REQUIRE(rebuilt == storedset, "reconstruction != stored tiling");
    rec("C6 edge fills reconstruct exactly the stored box tiling");

    // C7g terminal observations (facts only)
    const JV* pred = &walkv->arr[size_t(z - 1)];
    auto pp = state_masks(*pred);
    long pc_count = pp.first.popcount_trimmed();
    long remaining = ncells - pc_count;
    const JV& last_edge = fills->arr[size_t(z - 1)];
    bool all_slot0 = true;
    for (const JV& pjv : last_edge.arr)
        for (const JV& cjv : pjv.arr)
            if (cell_of(cjv)[2] != 0) all_slot0 = false;
    bool covers = true;
    {
        std::set<long> cov;
        for (const JV& pjv : last_edge.arr) {
            std::set<long> m;
            for (const JV& cjv : pjv.arr) {
                Cell c = cell_of(cjv);
                if (c[2] != 0) covers = false;
                m.insert(c[0] + a * c[1]);
            }
            for (long v : m)
                if (cov.count(v) || pp.first.test(size_t(v))) covers = false;
            cov.insert(m.begin(), m.end());
        }
        long comp_size = ncells - pc_count;
        covers = covers && long(cov.size()) == comp_size;
    }
    rec("C7g terminal predecessor (state " + std::to_string(z - 1) +
        "): L1 empty = " + (pp.second.popcount_trimmed() == 0 ? "true" : "false") +
        "; |L0|=" + std::to_string(pc_count) + "; remaining=" +
        std::to_string(remaining) + "; final edge all-slot0 = " +
        (all_slot0 ? "true" : "false") + "; final edge exactly covers "
        "complement = " + (covers ? "true" : "false"));
    rec("NOTE layer boundary: piece-specific gate claims are NOT evaluated "
        "by this generic checker.");

    // optional terminal block cross-check
    const JV* term = root.get("terminal");
    if (term && term->kind == JV::OBJ) {
        auto eqi = [&](const char* k, long v) {
            const JV* t = term->get(k);
            if (!t) return true;   // absent fields not checked
            REQUIRE(t->kind == JV::NUM && t->is_int_token() &&
                    std::stol(t->num) == v,
                    std::string("terminal.") + k + " mismatch");
            return true;
        };
        const JV* psi = term->get("predecessor_state_index");
        if (psi) REQUIRE(psi->kind == JV::NUM && psi->is_int_token() &&
                         std::stol(psi->num) == z - 1,
                         "terminal.predecessor_state_index mismatch");
        eqi("l0_popcount", pc_count);
        eqi("remaining_cells", remaining);
        const JV* fas = term->get("final_edge_all_slot0");
        if (fas) REQUIRE(fas->kind == JV::BOOL && fas->b == all_slot0,
                         "terminal.final_edge_all_slot0 mismatch");
        const JV* fcc = term->get("final_edge_covers_complement");
        if (fcc) REQUIRE(fcc->kind == JV::BOOL && fcc->b == covers,
                         "terminal.final_edge_covers_complement mismatch");
        rec("`terminal` block present and consistent with computed facts");
    }
}

// small helper used above (complement membership for C7g): a cell id belongs
// to the complement of pred.L0 iff its bit is clear — inlined at use site.

int main(int argc, char** argv) {
    if (argc < 2) {
        std::fprintf(stderr,
            "usage: %s <cert.json> [...]\n"
            "Independent C++17 Layer-A verifier for fitpolycubes.macro-walk v1\n",
            argv[0]);
        return 2;
    }
    bool all_ok = true;
    for (int i = 1; i < argc; i++) {
        std::ifstream f(argv[i]);
        if (!f) {
            std::cerr << "cannot open " << argv[i] << "\n";
            all_ok = false;
            continue;
        }
        std::stringstream ss;
        ss << f.rdbuf();
        std::cout << "cpp-generic-check: " << argv[i] << "\n";
        bool ok = false;
        try {
            JsonParser jp(ss.str());
            JV root = jp.parse();
            Checker chk{root};
            std::string verdict = chk.run();
            for (const auto& l : chk.lines) {
                if (l.rfind("[FAIL]", 0) == 0)
                    std::cout << "  [FAIL] " << l.substr(7) << "\n";
                else
                    std::cout << "  [OK] " << l << "\n";
            }
            std::cout << "  => " << verdict << "\n\n";
            ok = (verdict == "LAYER-A VALID");
        } catch (const std::exception& e) {
            std::cout << "  [FAIL] unparseable certificate: " << e.what()
                      << "\n  => INVALID\n\n";
            ok = false;
        } catch (int) {
            std::cout << "  => INVALID\n\n";
            ok = false;
        }
        all_ok = all_ok && ok;
    }
    return all_ok ? 0 : 1;
}
