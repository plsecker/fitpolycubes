# Certificate Protocol Interoperability Report

**Date**: 2026-08-26
**Scope**: cross-implementation validation of the frozen
`fitpolycubes.macro-walk` v1 Layer-A protocol (revision 2026-08-26a).

## Implementations compared

| | Reference checker | Independent verifier |
|---|---|---|
| File | `tools/frontier/macro_certificate_generic_checker.py` | `tools/frontier/macro_certificate_verifier.cpp` |
| Language / toolchain | Python ≥3.12 (stdlib only) | C++17, compiled with zig c++ 0.16.0 (LLVM/clang); stdlib only |
| Size | ~300 lines | ~560 lines (includes a from-scratch JSON parser) |
| Mask arithmetic | Python bigints | per-layer limb arrays (`vector<uint64_t>`) with decimal→limbs parser; no packed bigints formed |
| JSON handling | `json` module | hand-written recursive-descent parser with raw numeric tokens and strict int/bool separation |

Independence: the C++ file includes no repository headers and performs no
subprocess calls; it was written against the format document and schema.
Caveat recorded honestly: both implementations share an author, so this
exercise primarily catches *implementation* defects, not shared
*specification* misreadings. It caught one of each (below).

## Certificate results

All **11 certificates VALID in both implementations**: I (synthetic),
V 5×5×6, W 5×7×9 + rot90, S 4×5×6 + rot90, T ×5.

## Adversarial matrix — 21 cases, unanimous verdicts

Rejected by both: shifted fill cell; altered walk state; walk-state bit at
position 70 (>64-bit mask exercise); duplicated placement cell; out-of-window
fill translation; incongruent declared geometry (T); declared mirror geometry
of chiral S; improper-rotation (x-reflected) fill piece on S; malformed
geometry arity; disconnected geometry; duplicate geometry cell; z=0 box;
negative box dimension; conflicting dual tiling keys; invalid step label;
boolean step label; invalid semantics_id; missing semantics_id.
Accepted by both: clean S and W certificates; declared mirror geometry of the
achiral W (identical orientation set); proper-rotation repacks.

## Discrepancies found and resolved

1. **C++ `Mask::zero` brace-init defect** — constructed `{1, 0}` (two limbs,
   bit 0 set) instead of one zeroed limb; every parse silently poisoned.
   Found by running the new implementation against known-good certificates;
   fixed in C++ (`std::vector<uint64_t>(n, 0)`). Python was correct.
2. **Python bool/int coercion defect** — `step: true` at index 1 passed the
   reference check (`True == 1`), and terminal numeric fields had the same
   exposure. Found by the C++ rejection. Fixed in Python with strict
   `type(x) is int` / `type(x) is bool` checks. C++ was correct.

No schema or semantics change was required; both defects were
implementation-level.

## Attention items verified

- arbitrary-width masks: bit 70 mutation rejected identically; decimal
  parsing identical on all current widths;
- negative coordinates: rejected via explicit window bounds before any bit
  indexing (previously a crash class);
- JSON bool-vs-int: strict on both sides after fix;
- rotation determinants: det=+1 filter verified behaviourally (mirror-of-S
  rejected, mirror-of-W accepted, rot90 repacks accepted);
- cross-section transpose under proper rotations: rot90 certificates pass;
- empty final fills: S certificate passes with vacuous complement coverage;
- large dimensions: nothing in the protocol caps NCELLS beyond memory;
  both verifiers scale masks linearly.

## Conclusion

The schema is genuinely implementation-independent: two independent parsers
and checkers agree on all 11 certificates and all 21 adversarial cases, with
the two discrepancies discovered, root-caused, and fixed. Third parties can
re-implement Layer A from the format document alone; the reference Python
checker now also passes its own adversarial matrix against a second
language runtime.
