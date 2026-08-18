# Z-Frontier: Strongest Observed Constraints in the 100 Sampled Frontiers

Source: the 100 layer-1 frontiers (states in
`docs/z_frontier_state_stats_1m.md`, lines 140-239). Component shapes
and numbering follow `docs/z_frontier_component_shapes.md`; pair data
follow `docs/z_frontier_component_relations.md`.

## 1. Most frequent co-occurring pairs

Counts are numbers of records (of 100) in which the pair occurs as
components of the same frontier.

| Pair | Records |
|---|---|
| 1 + 1 (two isolated cells) | 1728 cell-pairs |
| 1 + 2 | 225 |
| 1 + 3 | 163 |
| 1 + 6 | 36 |
| 1 + 7 | 34 |
| 1 + 8 | 28 |
| 1 + 4 | 24 |
| 1 + 9 | 18 |
| 1 + 5 | 13 |
| 1 + 15 | 10 |
| 2 + 3 | 8 |

- The most frequent pairs are all of the form 1 + X: every frontier
  contains isolated cells, so the single cell co-occurs with every
  other shape.
- The strongest distinct-shape pairs are 1 + 2 (225 records) and
  1 + 3 (163 records).
- The strongest pair not involving the single cell is 2 + 3
  (8 records); every other non-1 pair occurs in at most 5 records.

## 2. Never co-occurring pairs

111 of the 136 distinct-shape pairs never occur in the same frontier.

- No two shapes of size >= 3 ever co-occur: every pair among shapes
  4-17 is absent.
- Every pair of non-single-cell components includes a domino
  (shape 2 or 3).
- Partner sets (distinct shapes only):

| Shape | Co-occurs with |
|---|---|
| 1 | all 16 other shapes |
| 2 | 1, 3, 4, 5, 6, 7, 8, 12, 14 |
| 3 | 1, 2, 8 |
| 8 | 1, 2, 3 |
| 4, 5, 6, 7, 12, 14 | 1, 2 |
| 9, 10, 11, 13, 15, 16, 17 | 1 only |

## 3. Dominance of isolated cells

- 620 of 729 components (85%) are isolated cells.
- Every one of the 100 frontiers contains at least one isolated cell.
- In 99 of 100 frontiers, isolated cells are a strict majority of the
  components (the single exception has 2 isolated cells of 5
  components).
- The minimum number of isolated cells in a frontier is 2.

## 4. Class-level exclusivity

- A size-3+ component (shapes 4-17) appears either as the only
  non-single component of its frontier, or together with dominoes
  only. Observed non-1 component patterns: (7), (6), (4), (9), (5),
  (8), (15), (10), (11), (13), (16), (17), (2,6), (2,8), (3,8),
  (2,2,4), (2,4), (2,5), (2,7), (2,12), (2,14).
- Shape 2 (vertical domino) is the only non-single shape that
  co-occurs with many others; shape 3 (horizontal domino) is the most
  restricted domino (only with 1, 2, 8); shape 8 is the only size-3+
  shape that ever accompanies a horizontal domino (3 + 8, 2 records).
- The only frontier with two copies of a non-single shape alongside
  another non-single shape is the (2, 2, 4) pattern (two vertical
  dominoes plus one horizontal triomino).