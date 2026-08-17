# Z-Frontier: Shift-Pattern Check of the 100 Layer-Shift States

Source: the 100 layer-shift records in
`docs/z_frontier_state_stats_1m.md`, lines 140-239 (each with
out-degree 1, layer shift yes, successors already seen 0).

## Method

- Layer 1 = bits 32-63 of the state; bit = x + 4y, 4 columns by
  8 rows; 4-neighbor connectivity.
- Component-size pattern = multiset of component sizes, largest
  first.

## Distinct component-size patterns and frequencies

| Pattern | Frequency |
|---|---|
| 2+1+1+1+1+1+1+1 | 30 |
| 3+1+1+1+1+1+1 | 17 |
| 2+2+1+1+1+1+1 | 12 |
| 1+1+1+1+1+1+1+1 | 11 |
| 3+2+1+1+1+1 | 10 |
| 4+1+1+1+1+1 | 9 |
| 1+1+1+1+1+1+1+1+1 | 7 |
| 4+2+1+1+1 | 2 |
| 2+2+1+1+1+1 | 1 |
| 3+2+2+1+1 | 1 |

Distinct patterns: 10; records: 100.

## Rule check: no two size>=3 components co-occur

Every one of the 100 frontiers obeys the rule: no frontier
contains two components of size 3 or more. No violations.

## Consistency with the constraints document

Cross-check against `docs/z_frontier_component_constraints.md`:

- Isolated cells: 620 of 729 components (85%); every frontier contains at least one isolated cell (True); isolated cells are a strict majority in 99 of 100 frontiers; minimum per frontier 2. All match the constraints document.
- No pattern contradicts the constraints document: the 10 patterns found are exactly the 10 patterns already listed in `docs/z_frontier_shape_structure.md`, and all
  obey the size>=3 rule and the domino-only accompaniment rule.

