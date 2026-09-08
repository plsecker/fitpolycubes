#!/usr/bin/env python3
"""
4x9 S-pentacube Macro structural analysis.
Phase 2: Bounded run to gather structural statistics.
"""

import sys, time, json
from collections import deque, Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements

def build_templates(a, b):
    NCELLS = a * b
    WORD_MASK = (1 << NCELLS) - 1
    LAYERS = 3
    raw, _ = generate_placements(PENTACUBES['S'], (a, b, 20), break_symmetry=False)
    templates = {cell: [] for cell in range(NCELLS)}
    seen_t = {cell: set() for cell in range(NCELLS)}
    concrete_count = len(raw)
    for placement in raw.values():
        cells = tuple(placement)
        min_z = min(z for _, _, z in cells)
        for x, y, z in cells:
            target = x + a * y
            target_rel = z - min_z
            shifted_masks = [0] * LAYERS
            valid = True
            for cx, cy, cz in cells:
                rel = cz - min_z - target_rel
                if rel < 0 or rel >= LAYERS:
                    valid = False
                    break
                cell_id = cx + a * cy
                shifted_masks[rel] |= (1 << cell_id)
            if not valid:
                continue
            packed = 0
            for i, mask in enumerate(shifted_masks):
                packed |= (mask << (i * NCELLS))
            if packed in seen_t[target]:
                continue
            seen_t[target].add(packed)
            templates[target].append(packed)
    total_templates = sum(len(v) for v in templates.values())
    return templates, NCELLS, (1 << NCELLS) - 1, concrete_count, total_templates


def layer_mask(state, layer, NCELLS):
    return (state >> (layer * NCELLS)) & ((1 << NCELLS) - 1)


def first_empty(mask, NCELLS):
    WORD_MASK = (1 << NCELLS) - 1
    missing = WORD_MASK & ~mask
    if not missing:
        return -1
    low = missing & -missing
    return low.bit_length() - 1


def apply_template(state, template):
    if state & template:
        return None
    return state | template


def shift_state(state, NCELLS):
    return state >> NCELLS


def main():
    a, b = 4, 9
    NCELLS = a * b
    WORD_MASK = (1 << NCELLS) - 1

    print("=" * 60)
    print("4×9 MACRO STRUCTURAL INVESTIGATION")
    print("=" * 60)

    # Build templates
    print("\n=== BUILDING TEMPLATES ===")
    t0 = time.perf_counter()
    templates, NCELLS, WORD_MASK, concrete_count, total_templates = build_templates(a, b)
    t1 = time.perf_counter()
    print(f"  Concrete placements: {concrete_count}")
    print(f"  Target templates: {total_templates}")
    print(f"  NCELLS: {NCELLS}")
    print(f"  State size: {3 * NCELLS} bits")
    print(f"  Build time: {t1-t0:.1f}s")

    # Template distribution
    layer_spans = Counter()
    for target in range(NCELLS):
        for t in templates[target]:
            l0 = t & WORD_MASK
            l1 = (t >> NCELLS) & WORD_MASK
            l2 = (t >> (2*NCELLS)) & WORD_MASK
            span = (bin(l0).count('1'), bin(l1).count('1'), bin(l2).count('1'))
            layer_spans[span] += 1
    print("\nTemplate contributions (L0, L1, L2 bits):")
    for span, count in sorted(layer_spans.items()):
        print(f"  {span}: {count} templates")

    # Try loading sources from checkpoint
    sources_path = Path("/tmp/macro_checkpoints/4x9.ckpt/sources.json")
    if sources_path.exists():
        print("\n=== LOADING SOURCES FROM CHECKPOINT ===")
        with open(sources_path) as f:
            sources = set(json.load(f))
        print(f"  Loaded {len(sources):,} sources")
    else:
        # Compute first-generation
        print("\n=== FIRST-GENERATION (bounded) ===")
        MAX_FG = 5_000_000
        sources = set()
        seen = {0}
        queue = deque([0])
        t2 = time.perf_counter()

        while queue and len(seen) < MAX_FG:
            state = queue.popleft()
            l0 = layer_mask(state, 0, NCELLS)
            if l0 == WORD_MASK:
                sources.add(shift_state(state, NCELLS))
                continue
            target = first_empty(l0, NCELLS)
            for template in templates[target]:
                nxt = apply_template(state, template)
                if nxt is None or nxt in seen:
                    continue
                seen.add(nxt)
                queue.append(nxt)

        t3 = time.perf_counter()
        print(f"  Tree states: {len(seen):,}")
        print(f"  Sources: {len(sources):,}")
        print(f"  Cap hit: {len(seen) >= MAX_FG}")
        print(f"  Queue remaining: {len(queue):,}")
        print(f"  Elapsed: {t3-t2:.1f}s")

    if len(sources) == 0:
        print("ERROR: No sources found")
        return 1

    # Source analysis
    print("\n=== SOURCE ANALYSIS ===")
    l1_even = sum(1 for s in sources if bin((s >> NCELLS) & WORD_MASK).count('1') % 2 == 0)
    print(f"  Total sources: {len(sources):,}")
    print(f"  L1-even sources: {l1_even}/{len(sources)}")

    sample_sources = list(sources)[:2000]
    source_patterns = Counter()
    for s in sample_sources:
        l0 = s & WORD_MASK
        l1 = (s >> NCELLS) & WORD_MASK
        l2 = (s >> (2*NCELLS)) & WORD_MASK
        source_patterns[(bool(l0), bool(l1), bool(l2))] += 1
    print("  Source layer patterns (sample):")
    for pat, cnt in sorted(source_patterns.items(), key=lambda x: -x[1]):
        print(f"    {pat}: {cnt}/{len(sample_sources)}")

    # Macro closure (bounded)  
    print("\n=== MACRO CLOSURE (bounded) ===")
    MACRO_LIMIT = 3_000_000
    TIME_LIMIT = 300

    macro_seen = set(sources)
    macro_queue = deque(sources)
    succ = {}
    depth = {s: 0 for s in sources}
    edge_count = 0
    max_depth = 0
    total_inter = 0
    processed = 0
    t4 = time.perf_counter()

    while macro_queue and len(macro_seen) < MACRO_LIMIT:
        if time.perf_counter() - t4 > TIME_LIMIT:
            print(f"\n  TIME LIMIT ({TIME_LIMIT}s)")
            break

        src = macro_queue.popleft()
        sd = depth.get(src, 0)
        processed += 1

        # Explore placement interval
        successors = set()
        es = {src}
        eq = deque([src])
        while eq:
            state = eq.popleft()
            l0 = layer_mask(state, 0, NCELLS)
            if l0 == WORD_MASK:
                successors.add(shift_state(state, NCELLS))
                continue
            target = first_empty(l0, NCELLS)
            for template in templates[target]:
                nxt = apply_template(state, template)
                if nxt is None or nxt in es:
                    continue
                es.add(nxt)
                eq.append(nxt)
        total_inter += len(es) - 1

        if successors:
            succ[src] = successors
            edge_count += len(successors)

        for s in successors:
            if s not in macro_seen:
                macro_seen.add(s)
                depth[s] = sd + 1
                if sd + 1 > max_depth:
                    max_depth = sd + 1
                macro_queue.append(s)

        if processed % 1000 == 0:
            elapsed = time.perf_counter() - t4
            print(f"  [{processed:,}] states={len(macro_seen):,} depth={max_depth} queue={len(macro_queue):,} elapsed={elapsed:.0f}s")

    t5 = time.perf_counter()
    print(f"\n=== MACRO CLOSURE RESULTS ===")
    print(f"  Sources processed: {processed:,}")
    print(f"  Macro states: {len(macro_seen):,}")
    print(f"  Macro edges: {edge_count:,}")
    print(f"  Max BFS depth: {max_depth}")
    print(f"  Total intermediate: {total_inter:,}")
    print(f"  Queue remaining: {len(macro_queue):,}")
    print(f"  Elapsed: {t5-t4:.1f}s")
    print(f"  0 in graph: {0 in macro_seen}")
    print(f"  WORD_MASK in graph: {WORD_MASK in macro_seen}")

    # Cycle check
    print(f"\n=== CYCLE ANALYSIS ===")
    back_edges = 0
    for src, succs in succ.items():
        sd = depth.get(src, -1)
        if sd < 0:
            continue
        for v in succs:
            vd = depth.get(v, -1)
            if vd < 0:
                continue
            if vd < sd:
                back_edges += 1
    print(f"  Back edges (cycles): {back_edges}")
    print(f"  Graph is DAG: {back_edges == 0}")

    # Depth distribution
    print(f"\n=== DEPTH DISTRIBUTION ===")
    dc = Counter(depth.values())
    for d in sorted(dc.keys()):
        print(f"  depth {d}: {dc[d]:,}")

    # L1-even check  
    print(f"\n=== L1-EVEN INVARIANT ===")
    sample = list(macro_seen)[:5000]
    l1_even_macro = 0
    for s in sample:
        l1_bits = bin((s >> NCELLS) & WORD_MASK).count('1')
        if l1_bits % 2 == 0:
            l1_even_macro += 1
    print(f"  L1-even in macro state sample: {l1_even_macro}/{len(sample)}")

    print(f"\n{'='*60}")
    print("4×9 STRUCTURAL ANALYSIS COMPLETE")
    print(f"{'='*60}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())