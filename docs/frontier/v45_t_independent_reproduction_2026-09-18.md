# Independent T × V45 Reproduction — 2026-09-18

## Purpose

This records an independent reproduction of the T-piece V45 exhaustive
search on the spare compute machine, using the current
`solvers/t_ck6_oddity_v35_search.py` implementation.

The run was performed independently of the large `visited_v45.db` search
database previously used on the main machine.

## Command

```bash
python solvers/t_ck6_oddity_v35_search.py run \
  --volume 45 \
  --shards 6 \
  --parallel 6 \
  --workdir data/ck6_reuse/lunch_v45


## Target enumeration

The fresh V45 count reported:

- **1,469,999 targets**
- **86 distinct candidate min-ids**

The count completed in approximately **1053 seconds (17.6 minutes)**.

The aggregate check reported:

```text
AGGREGATE: targets 1469999 / expected 1469999 match=True
