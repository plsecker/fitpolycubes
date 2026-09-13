# V45 MIN-ID 3590 REFINED ENUMERATION

**STATUS: COMPLETE**

- Commit: `9a305871e717e75eb5c255d51fdb8dbf920154dc` (`9a30587`)
- Start: 2026-09-13T10:03:47+1200
- End: 2026-09-13T10:33:10+1200
- Completed: all 5 children (3592, 3854, 3855, 3894, 3895)

## Children (refined connection-orbit partition, root S = {3590, 3591}, base 3591)

| Child | Forbidden F | Targets | States |
|---|---|---|---|
| (S, 3592) | ∅ | 2,455,878 | 22,222,353 |
| (S, 3854) | {3592} | 1,937,345 | 17,102,083 |
| (S, 3855) | {3592, 3854} | 1,201,199 | 10,803,148 |
| (S, 3894) | {3592, 3854, 3855} | 993,680 | 6,701,832 |
| (S, 3895) | {3592, 3854, 3855, 3894} | 582,434 | 3,306,602 |
| **Total** | | **7,170,536** | **60,136,018** |

## Results

- Targets: **7,170,536** (expected 7,170,536 — exact match)
- States: **60,136,018** (expected 60,136,018 — exact match)
- Coverage candidates (pass coverage): **1,536**
- SAT: **0** — Witnesses: **0**
- Funnel totals: reject `<k` contained placements 4,782,924; reject uncovered cell 2,386,076; pass coverage 1,536; reject exact-cover UNSAT 1,536
- Elapsed: 1,744.9 s (29.1 min); States/sec: 34,462; Targets/sec: 4,109
- Peak RSS: 3,449 MB; Min available RAM: 20,129 MB; Peak swap: 2,780 MB (no swap growth)

## Validation

- Target partition exact: **True** (per-child and total sums match the verified decomposition exactly)
- Duplicate-free: **True** (7,170,536 unique 16-byte orbit-set digests across all children)
- Independent validation: repo-M funnel reproduces the George B-9 smoke test exactly — `funnel_and_cover` on the corpus-frame target returns **SAT(12)** (12 M-piece covers), matching the published smoke-test result
- George target (oh-109166b4c83a): **present = True** (min orbit 3590, centre-adjacent orbits [3652, 3937], 16 orbits, cost 22)
- George target V cover count: **0** (funnel stage `reject_cov` — the V-piece does not tile it; consistent with SAT = 0 across the whole enumeration)
- George target classification: **CK6**, symmetry order 4 (identity, inversion, c2_diag, mirror_diag)

## Conclusion

The full min-id-3590 V45 enumeration is complete and exact: 7,170,536 CK6 targets in 60,136,018 states, partitioned across the 5 refined connection-orbit children with no duplicates and no gaps. The V-piece tiles **none** of them (0 SAT, 0 witnesses) — including George Sicherman's B-9 target, which is present in the corpus but is not V-tileable (it is M-tileable with exactly 12 covers, independently confirmed). The earlier smoke-test figure of 3,430,348 targets for this subtree is superseded: it was produced by an incomplete pre-shifted-mask walk and is inconsistent with the exact partition verified here.

## Artifacts

- `final.json` — aggregate results + validation
- `manifest.json` — per-child completion manifest (restart-safe)
- `child_{c}.json` — raw per-child results (targets, states, funnel counters, witnesses)
- `child_{c}.digests.bin` — per-child orbit-set digests (duplicate check + George presence)
- `run.log` — full run log