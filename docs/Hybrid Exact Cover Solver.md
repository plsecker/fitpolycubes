# Hybrid Exact-Cover Solver Parallelization Improvements

## Current Problem

The current multiprocessing implementation only parallelizes at depth 1 of the search tree:

```python
first_col = box_list[0]
row_choices = list(X0[first_col])
```

This creates only a small number of top-level tasks.

Example observed behavior:

```text
Parallel fan-out: 2 initial branches
Using a pool of 8 workers.
```

Result:

* only 2 worker processes are busy
* remaining workers are idle
* CPU utilization remains low despite large worker pool

This is a classic exact-cover / DLX load-balancing problem.

---

# Recommended Changes

---

## 1. Generate Tasks Recursively (Most Important)

### Current

Only first-level branches are dispatched to workers.

### Problem

Search trees are highly unbalanced:

```text
root
 ├── tiny branch
 └── enormous branch
```

This causes:

* poor CPU utilization
* workers sitting idle
* one process running for hours

### Recommended

Generate partial search states recursively before dispatching to workers.

Example:

```python
def generate_tasks(state, depth, max_depth, tasks):
    if depth >= max_depth:
        tasks.append(state)
        return

    col = choose_min_column(state)

    if col == -1:
        tasks.append(state)
        return

    rows = get_rows_for_column(state, col)

    for row in rows:
        child = apply_row(state, row)
        generate_tasks(child, depth + 1, max_depth, tasks)
```

Then:

```python
tasks = []
generate_tasks(initial_state, 0, SPLIT_DEPTH, tasks)
```

This can increase task count from:

* 2 tasks
  to:
* hundreds or thousands

allowing full CPU saturation.

---

## 2. Use Adaptive Task Generation

### Current

Fixed split depth.

### Recommended

Generate tasks until target count reached:

```python
TARGET_TASKS = num_cores * 16
```

Stop splitting once:

```python
len(tasks) >= TARGET_TASKS
```

This adapts automatically to:

* varying branching factors
* different box sizes
* different pentacubes

---

## 3. Replace `starmap()` With Dynamic Scheduling

### Current

```python
pool.starmap(solve_worker, args_list)
```

### Problem

Static scheduling performs poorly for highly uneven search trees.

### Recommended

Use:

```python
pool.imap_unordered(worker_wrapper, args_list, chunksize=1)
```

or:

```python
pool.apply_async(...)
```

Benefits:

* workers can steal new tasks
* better load balancing
* avoids long idle periods

---

## 4. Improve Column Selection Heuristic

### Current

```python
first_col = box_list[0]
```

### Problem

Arbitrary column choice.

### Recommended

Choose the column with the fewest candidate rows:

```python
first_col = min(X0.keys(), key=lambda c: len(X0[c]))
```

This is the standard Algorithm X heuristic.

Benefits:

* earlier failures
* smaller search trees
* better branching
* improved parallel decomposition

---

## 5. Add Instrumentation

Add diagnostics immediately after task generation:

```python
print(f"Initial tasks generated: {len(tasks)}")
```

Optional:

* estimate branch sizes
* print average branching factor
* monitor worker progress

Useful for diagnosing:

* imbalance
* shallow fan-out
* pathological searches

---

## 6. Replace `Manager().Queue()`

### Current

```python
manager = mp.Manager()
out_q = manager.Queue()
```

### Problem

Manager queues are slow because they route through a manager server process.

### Recommended

Use:

```python
out_q = mp.Queue()
```

Benefits:

* lower IPC overhead
* faster solution throughput
* reduced latency

---

## 7. Batch Solution Writes

### Current

Likely sending every solution individually through queue.

### Problem

High IPC overhead.

### Recommended

Workers buffer solutions locally:

```python
local_buffer = []

if found_solution:
    local_buffer.append(sol)

if len(local_buffer) >= 100:
    out_q.put(local_buffer)
    local_buffer.clear()
```

Benefits:

* drastically fewer queue operations
* improved throughput
* reduced synchronization overhead

---

## 8. Consider Shared Memory for Immutable Arrays

Potential issue:

```python
X_data
X_indptr
Y_data
Y_indptr
```

may be copied/pickled for workers depending on platform.

Linux `fork()` helps, but shared memory is safer and portable.

Possible solution:

* `multiprocessing.shared_memory`
* memory-mapped NumPy arrays

Lower priority than search-tree fixes.

---

## 9. Add Worker Progress Reporting

Long exact-cover searches appear hung.

Recommended periodic reporting:

```python
(depth, nodes_visited, solutions_found)
```

Useful for:

* debugging
* estimating runtime
* detecting stalled branches

---

# Highest Impact Minimal Changes

If implementing only a few improvements, prioritize:

## A. Better Column Selection

Replace:

```python
first_col = box_list[0]
```

with:

```python
first_col = min(X0.keys(), key=lambda c: len(X0[c]))
```

---

## B. Recursive Task Generation

Generate tasks deeper in the search tree before dispatching.

---

## C. Dynamic Scheduling

Replace:

```python
pool.starmap(...)
```

with:

```python
pool.imap_unordered(..., chunksize=1)
```

---

# Expected Outcome

Current behavior:

* ~2 cores utilized
* poor load balancing
* shallow parallelization

Expected after improvements:

* near-full CPU utilization
* much better worker balance
* substantially improved solve throughput
* scalable multicore performance on larger searches

