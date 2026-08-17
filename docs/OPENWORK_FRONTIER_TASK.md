OPENWORK TASK — FRONTIER EXPERIMENT INFRASTRUCTURE

Repository: /home/philip/Work/fitpolycubes

Goal:
Build engineering infrastructure around the experimental S 4x8 frontier/automaton work. Do NOT invent or change the mathematical frontier model.

Tasks:
1. Inspect the existing solver/prototype scripts under solvers/ and tools/.
2. Review tools/frontier_lab.py.
3. Add only engineering improvements needed to make experiments reproducible:
   - capture stdout/stderr
   - timeouts
   - exit status
   - memory/RSS where practical
   - machine-readable JSON summaries
   - preserve exact command and relevant source/config hashes
   - support repeatable sweeps over N and prototype variants
4. Do not modify the mathematical search algorithms.
5. Do not replace existing placement-generation logic.
6. Add a short docs/frontier_lab.md explaining usage and output layout.
7. Run a small smoke test on S 4x8x10 with a strict timeout and record the result.

Deliverables:
- tools/frontier_lab.py (improved version if needed)
- docs/frontier_lab.md
- smoke-test evidence/logs

Important:
This is infrastructure work only. Do not "fix" the automaton by inventing new geometry or state definitions. Report any correctness concerns separately.
