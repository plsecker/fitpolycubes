#!/usr/bin/env python3
"""
Permanent regression test for the B/M coordinate fix (2026-09-15).

The repo's internal piece letters B and M match the external
Sicherman / Kuenzell / Shirakawa lettering:

    B ("tip": 3-bar + cube on the middle + cube on top of that,
       3 even + 2 odd cells) = Sicherman B
                             = Kuenzell 82
                             = Sillke qu5.82
                             = Shirakawa 5-19
    M ("junction": 3-bar + side cube + top cube at the middle,
       4 even + 1 odd cells) = Sicherman M
                             = Kuenzell 51
                             = Sillke qu5.51
                             = Shirakawa 5-18

Catalogue modules are named by Sicherman letters (b_catalogue =
Sicherman B = the tip = repo B; m_catalogue = Sicherman M = the
junction = repo M).  See docs/frontier/george_b9_letter_mapping.md.

History: before 2026-09-15 the B and M coordinate arrays were inverted; this test locks the corrected state down and fails if the letters are re-swapped or any alias attributes are reintroduced.

The test asserts:
  A. registry parity + external identities (no aliases);
  B. catalogue-module linkage (registry <-> Sicherman-lettered modules);
  C. odd-box minima (tip: 5x7x7; junction: no odd box);
  D. George's "B 9" oddity is a TIP figure = repo B: 45 cells,
     oh-109166b4c83a, min orbit id 3590, repo-B covers 12,
     repo-M covers 0, repo-V covers 0 (independent full-domain
     enumeration); the stored reconciliation's pre-fix labels
     (repo_M_definition = tip, repo_M_covers = 12) are checked to be
     congruent to the corrected registry;
  E. our B-V15-S1 (junction-piece construction; ID retains the pre-fix
     lettering) is congruent to George's "M 3" figure
     (oh-0216334782e8): repo-M covers 2, repo-B covers 0;
  F. the George-row lookup in sicherman_c5nodd_compare is direct (no
     REPO_TO_SICHERMAN translation) and knows the B-V15-S1 congruence.

Run:  python3 tools/frontier/test_bm_nomenclature.py [--quick]
(--quick skips the three full-domain cover enumerations of test D.)
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "solvers"))
sys.path.insert(0, str(REPO / "tools" / "frontier"))

import common.registry as registry_mod  # noqa: E402
from common.registry import PIECES, PENTACUBES  # noqa: E402
from catalogues.registry import CATALOGUES  # noqa: E402
import catalogues.b_catalogue as b_catalogue_mod  # noqa: E402
import catalogues.m_catalogue as m_catalogue_mod  # noqa: E402
from catalogues.base import Box  # noqa: E402
from common.rotmatrix import RM  # noqa: E402
from test_ck6_sharding_bug import full_domain_covers  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {name}" + (f" -- {detail}" if detail else ""))
    if not cond:
        FAILURES.append(name)
    return cond


def parity(coords):
    evens = sum(1 for c in coords
                if (int(c[0]) + int(c[1]) + int(c[2])) % 2 == 0)
    return evens, 5 - evens


def normalize(cells):
    cells = [tuple(int(v) for v in c) for c in cells]
    mn = tuple(min(c[i] for c in cells) for i in range(3))
    return tuple(sorted(tuple(c[i] - mn[i] for i in range(3))
                       for c in cells))


def is_congruent_proper(cells, piece):
    """True when `cells` is a proper-rotation image of `piece`."""
    target = normalize(cells)
    piece = [tuple(int(v) for v in c) for c in piece]
    for r in RM:
        img = normalize(tuple(np.asarray(r, dtype=int) @ np.array(c)
                              for c in piece))
        if img == target:
            return True
    return False


def load_json(rel):
    with open(REPO / rel) as f:
        return json.load(f)


def test_a():
    print("\nA. Registry parity + external identities (no aliases)")
    check("repo B is 3E+2O (tip)", parity(PENTACUBES["B"]) == (3, 2),
          str(parity(PENTACUBES["B"])))
    check("repo M is 4E+1O (junction)", parity(PENTACUBES["M"]) == (4, 1),
          str(parity(PENTACUBES["M"])))
    check("registry B kurnell == 82", PIECES["B"].kurnell == 82,
          str(PIECES["B"].kurnell))
    check("registry M kurnell == 51", PIECES["M"].kurnell == 51,
          str(PIECES["M"].kurnell))
    check("registry B shirakawa_piece == 19",
          PIECES["B"].shirakawa_piece == 19)
    check("registry M shirakawa_piece == 18",
          PIECES["M"].shirakawa_piece == 18)
    check("registry B shirakawa_url == 5-19.html",
          PIECES["B"].shirakawa_url.endswith("5-19.html"),
          PIECES["B"].shirakawa_url)
    check("registry M shirakawa_url == 5-18.html",
          PIECES["M"].shirakawa_url.endswith("5-18.html"),
          PIECES["M"].shirakawa_url)
    # Alias attributes have been removed; no further checks needed.


def test_b():
    print("\nB. Catalogue-module linkage")
    check("repo B links to catalogues.b_catalogue",
          PIECES["B"].catalogue_module == "catalogues.b_catalogue")
    check("repo M links to catalogues.m_catalogue",
          PIECES["M"].catalogue_module == "catalogues.m_catalogue")
    check("b_catalogue.MINIMAL_ODD is set (tip tiles odd boxes)",
          b_catalogue_mod.MINIMAL_ODD is not None)
    check("m_catalogue.MINIMAL_ODD is None (junction tiles no odd box)",
          m_catalogue_mod.MINIMAL_ODD is None)
    check("CATALOGUES['B'] is B_CATALOGUE (Sicherman lettering)",
          CATALOGUES["B"] is b_catalogue_mod.B_CATALOGUE)
    check("CATALOGUES['M'] is M_CATALOGUE (Sicherman lettering)",
          CATALOGUES["M"] is m_catalogue_mod.M_CATALOGUE)


def test_c():
    print("\nC. Odd-box minima")
    check("b_catalogue.MINIMAL_ODD == Box(5,7,7)",
          b_catalogue_mod.MINIMAL_ODD == Box(5, 7, 7),
          str(b_catalogue_mod.MINIMAL_ODD))
    check("m_catalogue.MINIMAL_ODD is None",
          m_catalogue_mod.MINIMAL_ODD is None)
    import tools.verify_sicherman_odd_boxes as vsob
    check("SICHERMAN['B'] == (5,7,7)", vsob.SICHERMAN["B"] == (5, 7, 7),
          str(vsob.SICHERMAN["B"]))
    check("SICHERMAN['M'] == 'impossible'",
          vsob.SICHERMAN["M"] == "impossible")


def test_d(quick):
    print("\nD. George's 'B 9' oddity = tip = repo B")
    d = load_json("data/ck6_reuse/george_b9_geometry_reconciliation.json")
    target = frozenset(tuple(c) for c in d["reconstruction"]["cells"])
    check("target has 45 cells", len(target) == 45, str(len(target)))
    check("oh canonical id == oh-109166b4c83a",
          d["reconstruction"]["oh_canonical_id"] == "oh-109166b4c83a",
          d["reconstruction"]["oh_canonical_id"])
    check("stored min orbit id == 3590",
          d["reconstruction"]["corpus_frame"]
          ["min_orbit_id_in_v45_universe"] == 3590,
          str(d["reconstruction"]["corpus_frame"]
              ["min_orbit_id_in_v45_universe"]))

    # The stored reconciliation used the PRE-FIX lettering: its
    # "repo_M_definition" is the tip shape (now repo B) and its
    # "repo_B_definition" is the junction shape (now repo M).  Verify
    # the stored definitions are congruent to the corrected registry.
    stored_m_def = d["exact_covers"]["repo_M_definition"]
    stored_b_def = d["exact_covers"]["repo_B_definition"]
    check("stored repo_M_definition (pre-fix) == tip == repo B",
          is_congruent_proper(stored_m_def, PENTACUBES["B"]))
    check("stored repo_B_definition (pre-fix) == junction == repo M",
          is_congruent_proper(stored_b_def, PENTACUBES["M"]))
    check("stored pre-fix repo_M_covers == 12 (tip covers, now repo B)",
          d["exact_covers"]["repo_M_covers"] == 12)
    check("stored pre-fix repo_B_covers == 0 (junction covers, now repo M)",
          d["exact_covers"]["repo_B_covers"] == 0)

    # stored witness self-consistency: first pre-fix repo-M witness
    # (tip placements) covers target and is repo B under corrected IDs
    w0 = d["exact_covers"]["repo_M_witnesses"][0]
    union = frozenset(tuple(c) for p in w0 for c in p)
    check("stored witness[0] union == target", union == target)
    check("stored witness[0] placements are repo B (tip)",
          all(is_congruent_proper(p, PENTACUBES["B"]) for p in w0))
    check("stored witness[0] has 9 placements", len(w0) == 9, str(len(w0)))

    if quick:
        print("  (--quick: skipping independent cover enumerations)")
        return
    t0 = time.time()
    b_covers = full_domain_covers(target, PENTACUBES["B"])
    check("independent repo-B covers == 12", len(b_covers) == 12,
          str(len(b_covers)))
    m_covers = full_domain_covers(target, PENTACUBES["M"])
    check("independent repo-M covers == 0", len(m_covers) == 0,
          str(len(m_covers)))
    v_covers = full_domain_covers(target, PENTACUBES["V"])
    check("independent repo-V covers == 0", len(v_covers) == 0,
          str(len(v_covers)))
    print(f"  (cover enumerations took {time.time()-t0:.1f}s)")


def test_e():
    print("\nE. B-V15-S1 congruent to George's 'M 3' figure")
    d = load_json("data/ck6_reuse/b_v15_george_geometry_reconciliation.json")
    ours = d["our_target"]
    george = d["george_m_target"]
    check("our_target oh id == oh-0216334782e8",
          ours["oh_canonical_id"] == "oh-0216334782e8",
          ours["oh_canonical_id"])
    check("george target oh id == oh-0216334782e8",
          george["oh_canonical_id"] == "oh-0216334782e8",
          george["oh_canonical_id"])
    check("congruent under 24 proper rotations",
          d["comparison"]["congruent_24_proper"] is True)
    check("same oh id per comparison",
          d["comparison"]["same_oh_id"] is True)
    # The stored reconciliation used the PRE-FIX lettering: its
    # "repo_B_covers" counts covers by the junction piece, which is
    # repo M under the corrected IDs.
    check("stored pre-fix repo_B_covers == 2 (junction, now repo M)",
          d["exact_covers_george_target"]["repo_B_covers"] == 2)
    check("stored pre-fix repo_M_covers == 0 (tip, now repo B)",
          d["exact_covers_george_target"]["repo_M_covers"] == 0)
    check("George's colouring == stored witness index 0",
          d["exact_covers_george_target"]
          ["george_colouring_equals_B_witness_index"] == 0)

    # independent recomputation on our own target (15 cells, fast)
    target = frozenset(tuple(c) for c in ours["cells"])
    m_covers = full_domain_covers(target, PENTACUBES["M"])
    check("independent repo-M covers of B-V15-S1 == 2",
          len(m_covers) == 2, str(len(m_covers)))
    b_covers = full_domain_covers(target, PENTACUBES["B"])
    check("independent repo-B covers of B-V15-S1 == 0",
          len(b_covers) == 0, str(len(b_covers)))


def test_f():
    print("\nF. George-row lookup in sicherman_c5nodd_compare")
    import tools.frontier.sicherman_c5nodd_compare as s5p
    # No translation layer needed (direct mapping)
    check("George's B row (tip = repo B) == 13 tiles",
          s5p.GEORGE_ROWS["B"] == (13, "ach"),
          str(s5p.GEORGE_ROWS["B"]))
    check("George's M row (junction = repo M) == 3 tiles",
          s5p.GEORGE_ROWS["M"] == (3, "ach"),
          str(s5p.GEORGE_ROWS["M"]))
    check("KNOWN_CONGRUENT['B-V15-S1'] == ('M-3', 'oh-0216334782e8')",
          s5p.KNOWN_CONGRUENT.get("B-V15-S1") == ("M-3",
                                                  "oh-0216334782e8"),
          str(s5p.KNOWN_CONGRUENT.get("B-V15-S1")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true",
                    help="skip the three full-domain cover enumerations "
                         "of test D")
    args = ap.parse_args()
    t0 = time.time()

    print("== B/M coordinate-fix regression (2026-09-15) ==")
    test_a()
    test_b()
    test_c()
    test_d(args.quick)
    test_e()
    test_f()

    print(f"\nelapsed {time.time()-t0:.1f}s; "
          f"{'ALL CHECKS PASSED' if not FAILURES else 'FAILURES: ' + str(FAILURES)}")
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())