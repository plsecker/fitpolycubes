# Macro-closure multiprocessing experiment

The multiprocessing prototype in `tools/frontier/scc_aware_analysis_mp.py`
is retained as research code.

It achieved substantial raw throughput improvements over the serial
macro-closure implementation, but the wave/batch execution order changes
the bounded closure semantics.

The decisive test was a fresh 30M-state parallel closure:

    parallel closure: 30,001,599 states
    SCC containing state 0: 1 state
    129-edge walks: 0

The established serial 30M closure has:

    SCC containing state 0: 478 states
    SCC internal edges: 514
    129-edge walks: 2048

Thus naïve wave/batch multiprocessing is NOT a valid replacement for the
serial bounded closure.

This does not mean multiprocessing is impossible. The prototype is retained
because a future implementation may be able to parallelize the expensive
source exploration while preserving the mathematical semantics required by
the bounded closure.

Future work should start from the serial algorithm as the specification and
investigate more tightly controlled/speculative parallel approaches rather
than assuming wave-based BFS is equivalent.

Do not use the current multiprocessing implementation for production
macro-closure results.
