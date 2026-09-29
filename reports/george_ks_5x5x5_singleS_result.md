# George — K + S on 5×5×5

## Question

Can a 5×5×5 cube be tiled using a combination of K and S pentacubes, with S kept to its canonical handedness (no reflection)?

## Exhaustive result

**No tiling was found.**

The search was exhaustive over the complete mixed K+S placement set used by the solver.

## Search setup

- Box: 5×5×5 = 125 cells
- Pieces per tiling: 25 pentacubes
- K placements: 1,152
- Single-handed S placements: 576
- Combined placement rows: 1,728
- Solver: `solver_a` C++ exact-cover engine
- Connectivity pruning: enabled
- Symmetry: enabled
- Colour-region pruning: enabled
- Propagation pruning: enabled
- Parallel workers: 2
- Checkpoint: `data/checkpoints/ks_5x5x5_singleS.ckpt`
- Placement file: `placements_KS_5x5x5.txt`

## Completion evidence

The checkpoint reports `task_cnt = 51`.

The completed-task file contains **51 completed tasks**, i.e. the entire generated search space was processed.

No solution file was produced:
`data/checkpoints/ks_5x5x5_singleS.solutions` was absent after completion.

## Interpretation

This establishes a computational negative result for the **single-handed S** version: no 5×5×5 tiling exists using K and the canonical handed S represented by the repository.

The C++ solver's nominal piece argument was `K`; the actual search rows were the combined K+S placement set above.

The reflection-allowed case is a separate search and is not included in this result.
