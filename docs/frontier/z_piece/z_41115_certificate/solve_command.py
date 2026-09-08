#!/usr/bin/env python3
"""Exact commands that produced this package's CNF and proof.

The certified run (2026-09-04):
  1. CNF build   : tools/sat/sat_certificate_workflow.py prepare
                   (repo generate_placements cross-checked against an
                   independent regeneration; plain ALO+AMO, canonical
                   deduplicated form)
  2. Solve+proof : native CaDiCaL 1.5.3, binary DRAT
                   cadical z_4x11x15.cnf z_4x11x15_native2.drat
                   (2117.5 s, exit 20 = UNSATISFIABLE)
  3. Check       : drat-trim z_4x11x15.cnf z_4x11x15_native2.drat
                   (2458.2 s, s VERIFIED)

Reproduce with the current tooling:
  python3 tools/sat/sat_certificate_workflow.py prepare \
      --piece Z --box 4 11 15 --out <pkg_dir>
  <cadical> <pkg_dir>/z_4x11x15.cnf <pkg_dir>/z_4x11x15.drat
  <drat-trim> <pkg_dir>/z_4x11x15.cnf <pkg_dir>/z_4x11x15.drat

The rebuilt CNF is deterministic: sorted placements (by sorted cell list),
variable ids 1..4096 in that order, sorted-literal clauses, deduplicated,
sorted clause sequence.  A faithful rebuild is byte-identical to
z_4x11x15.cnf (sha256 ecb549ac...44c16, see hashes.txt).
"""
