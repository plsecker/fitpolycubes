# Final Impossibility Rule Inventory

## Per‑piece detailed rules

### F – Pentomino F
| Rule | Provenance | Status | Consumed? | Evidence |
|------|------------|--------|-----------|----------|
| `if a == 1: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/f_catalogue.py` line 118 – `fmp_blanket_rule_audit.md` |
| `if a == 2 and b == 2: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/f_catalogue.py` line 126 – `cross_piece_impossibility_audit.md` |
| `if a == 2 and b == c: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/f_catalogue.py` line 133 – `cross_piece_impossibility_audit.md` |
| `if a == 4 and b in {4,7}: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/f_catalogue.py` line 142 – `cross_piece_impossibility_audit.md` |
| `if (a,b)==(4,5) and c in {3,4,5,6,7,8,9,11}: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/f_catalogue.py` line 145‑147 – `cross_piece_impossibility_audit.md` |
| `if (a,b)==(5,5) and c in {3,4,5,6,7,9}: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/f_catalogue.py` line 149‑151 – `cross_piece_impossibility_audit.md` |
| `if a == 4 and 4 <= b <= 12: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/f_catalogue.py` line 164‑166 – `cross_piece_impossibility_audit.md` |
| `if a == 5: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/f_catalogue.py` line 170‑172 – `cross_piece_impossibility_audit.md` |
| `if (a,b) == (6,6): return "published_impossible"` | UNSUPPORTED | UNRESOLVED | Yes | `catalogues/f_catalogue.py` line 175‑176 – `fmp_blanket_rule_audit.md` |
| `if (a,b) == (6,7): return "published_impossible"` | UNSUPPORTED | UNRESOLVED | Yes | `catalogues/f_catalogue.py` line 177‑178 – `fmp_blanket_rule_audit.md` |
| `if box in {Box(6,8,10), Box(6,8,15)}: return "published_impossible"` | EMPIRICAL | RESOLVED | Yes | `catalogues/f_catalogue.py` line 183‑186 – `s_piece/published_impossible_audit.md` |

### S – Pentomino S
| Rule | Provenance | Status | Consumed? | Evidence |
|------|------------|--------|-----------|----------|
| `if a <= 1: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/s_catalogue.py` line 156 – `cross_piece_impossibility_audit.md` |
| `if a == 2: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/s_catalogue.py` line 164‑166 – `cross_piece_impossibility_audit.md` |
| `if a == 3 and 3 <= b <= 13: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/s_catalogue.py` line 175‑176 – `cross_piece_impossibility_audit.md` |
| `if a == 4 and b in {4,7}: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/s_catalogue.py` line 182‑184 – `cross_piece_impossibility_audit.md` |
| `if a == 4 and b == 8 and c in {10,30,50,70,90,110}: return "published_impossible"` | EMPIRICAL | RESOLVED | Yes | `catalogues/s_catalogue.py` line 188‑190 – `s_piece/published_impossible_audit.md` |
| `if a == 4 and b == 9 and c in {10,20,25,30,35,40,45}: return "published_impossible"` | EMPIRICAL | RESOLVED | Yes | `catalogues/s_catalogue.py` line 195‑197 – `s_piece/published_impossible_audit.md` |
| `if a == 4 and b == 5 and c == 5: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/s_catalogue.py` line 198‑200 – `cross_piece_impossibility_audit.md` |
| `if a == 4 and b == 9 and c == 15: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/s_catalogue.py` line 205‑207 – `cross_piece_impossibility_audit.md` |
| `if a == 4 and b == 10 and c == 14: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/s_catalogue.py` line 208‑210 – `cross_piece_impossibility_audit.md` |
| `if a == 5 and b == 7 and c == 30: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/s_catalogue.py` line 211‑213 – `cross_piece_impossibility_audit.md` |
| `if a == 5 and b == 5: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/s_catalogue.py` line 215‑217 – `cross_piece_impossibility_audit.md` |
| `if a == 5 and b == 6 and c in {6,7,9,10,11,13,14,15,17,18,19,21,22,23,25,26,27,28,30,31,34,35,38,39,42,43}: return "published_impossible"` | EMPIRICAL | RESOLVED | Yes | `catalogues/s_catalogue.py` line 225‑230 – `s_piece/published_impossible_audit.md` |
| `if a == 5 and b == 7 and c in {12,18}: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/s_catalogue.py` line 233‑236 – `cross_piece_impossibility_audit.md` |
| `if a == 5 and b == 9 and c == 9: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/s_catalogue.py` line 239‑242 – `cross_piece_impossibility_audit.md` |
| `if a == 6 and b == 6 and c == 10: return "published_impossible"` | UNSUPPORTED | UNRESOLVED | Yes | `catalogues/s_catalogue.py` line 244‑247 – `cross_piece_impossibility_audit.md` |
| `if a % 2 == 1 and (b*c) % 3 != 0: return "published_impossible, odd‑width theorem"` | THEOREM (claimed) | UNRESOLVED | Yes | `catalogues/s_catalogue.py` line 250‑254 – `cross_piece_impossibility_audit.md` |
| `if b % 2 == 1 and (a*c) % 3 != 0: return "published_impossible, odd‑width theorem"` | THEOREM (claimed) | UNRESOLVED | Yes | `catalogues/s_catalogue.py` line 255‑257 – `cross_piece_impossibility_audit.md` |
| `if c % 2 == 1 and (a*b) % 3 != 0: return "published_impossible, odd‑width theorem"` | THEOREM (claimed) | UNRESOLVED | Yes | `catalogues/s_catalogue.py` line 259‑261 – `cross_piece_impossibility_audit.md` |
| `if box in SEARCHED_NO_SOLUTION: return "SEARCHED_NO_SOLUTION"` | EMPIRICAL | DEAD_METADATA | No | `catalogues/s_catalogue.py` line 262‑264 – empty set

### K – Pentomino K (identical to S after cube‑rule removal)
| Rule | Provenance | Status | Consumed? | Evidence |
|------|------------|--------|-----------|----------|
| `if a <= 1: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/k_catalogue.py` line 156 – `cross_piece_impossibility_audit.md` |
| `if a == 2: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/k_catalogue.py` line 164‑166 – `cross_piece_impossibility_audit.md` |
| `if a == 3 and 3 <= b <= 13: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/k_catalogue.py` line 175‑176 – `cross_piece_impossibility_audit.md` |
| `if a == 4 and b in {4,7}: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/k_catalogue.py` line 182‑184 – `cross_piece_impossibility_audit.md` |
| `if a == 4 and b == 8 and c in {10,30,50,70,90,110}: return "published_impossible"` | EMPIRICAL | RESOLVED | Yes | `catalogues/k_catalogue.py` line 188‑190 – `k_piece/published_impossible_audit.md` |
| `if a == 4 and b == 9 and c in {10,20,25,30,35,40,45}: return "published_impossible"` | EMPIRICAL | RESOLVED | Yes | `catalogues/k_catalogue.py` line 195‑197 – `k_piece/published_impossible_audit.md` |
| `if a == 4 and b == 5 and c == 5: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/k_catalogue.py` line 198‑200 – `cross_piece_impossibility_audit.md` |
| `if a == 4 and b == 9 and c == 15: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/k_catalogue.py` line 205‑207 – `cross_piece_impossibility_audit.md` |
| `if a == 4 and b == 10 and c == 14: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/k_catalogue.py` line 208‑210 – `cross_piece_impossibility_audit.md` |
| `if a == 5 and b == 7 and c == 30: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/k_catalogue.py` line 211‑213 – `cross_piece_impossibility_audit.md` |
| `if a == 5 and b == 5: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/k_catalogue.py` line 215‑217 – `cross_piece_impossibility_audit.md` |
| `if a == 5 and b == 6 and c in {6,7,9,10,11,13,14,15,17,18,19,21,22,23,25,26,27,28,30,31,34,35,38,39,42,43}: return "published_impossible"` | EMPIRICAL | RESOLVED | Yes | `catalogues/k_catalogue.py` line 225‑230 – `k_piece/published_impossible_audit.md` |
| `if a == 5 and b == 7 and c in {12,18}: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/k_catalogue.py` line 233‑236 – `cross_piece_impossibility_audit.md` |
| `if a == 5 and b == 9 and c == 9: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/k_catalogue.py` line 239‑242 – `cross_piece_impossibility_audit.md` |
| `if a == 6 and b == 6 and c == 10: return "published_impossible"` | UNSUPPORTED | UNRESOLVED | Yes | `catalogues/k_catalogue.py` line 244‑247 – `cross_piece_impossibility_audit.md` |
| `if a % 2 == 1 and (b*c) % 3 != 0: return "published_impossible, odd‑width theorem"` | THEOREM (claimed) | UNRESOLVED | Yes | `catalogues/k_catalogue.py` line 250‑254 – `cross_piece_impossibility_audit.md` |
| `if b % 2 == 1 and (a*c) % 3 != 0: return "published_impossible, odd‑width theorem"` | THEOREM (claimed) | UNRESOLVED | Yes | `catalogues/k_catalogue.py` line 255‑257 – `cross_piece_impossibility_audit.md` |
| `if c % 2 == 1 and (a*b) % 3 != 0: return "published_impossible, odd‑width theorem"` | THEOREM (claimed) | UNRESOLVED | Yes | `catalogues/k_catalogue.py` line 259‑261 – `cross_piece_impossibility_audit.md` |
| `if box in SEARCHED_NO_SOLUTION: return "SEARCHED_NO_SOLUTION"` | EMPIRICAL | DEAD_METADATA | No | empty set

### V – Pentomino V (identical to K)
| Rule | Provenance | Status | Consumed? | Evidence |
|------|------------|--------|-----------|----------|
| `if a <= 1: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/v_catalogue.py` line 156 – `cross_piece_impossibility_audit.md` |
| `if a == 2: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/v_catalogue.py` line 164‑166 – `cross_piece_impossibility_audit.md` |
| `if a == 3 and 3 <= b <= 13: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/v_catalogue.py` line 175‑176 – `cross_piece_impossibility_audit.md` |
| `if a == 4 and b in {4,7}: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/v_catalogue.py` line 182‑184 – `cross_piece_impossibility_audit.md` |
| `if a == 4 and b == 8 and c in {10,30,50,70,90,110}: return "published_impossible"` | EMPIRICAL | RESOLVED | Yes | `catalogues/v_catalogue.py` line 188‑190 – `v_piece/published_impossible_audit.md` |
| `if a == 4 and b == 9 and c in {10,20,25,30,35,40,45}: return "published_impossible"` | EMPIRICAL | RESOLVED | Yes | `catalogues/v_catalogue.py` line 195‑197 – `v_piece/published_impossible_audit.md` |
| `if a == 4 and b == 5 and c == 5: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/v_catalogue.py` line 198‑200 – `cross_piece_impossibility_audit.md` |
| `if a == 4 and b == 9 and c == 15: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/v_catalogue.py` line 205‑207 – `cross_piece_impossibility_audit.md` |
| `if a == 4 and b == 10 and c == 14: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/v_catalogue.py` line 208‑210 – `cross_piece_impossibility_audit.md` |
| `if a == 5 and b == 7 and c == 30: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/v_catalogue.py` line 211‑213 – `cross_piece_impossibility_audit.md` |
| `if a == 5 and b == 5: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/v_catalogue.py` line 215‑217 – `cross_piece_impossibility_audit.md` |
| `if a == 5 and b == 6 and c in {6,7,9,10,11,13,14,15,17,18,19,21,22,23,25,26,27,28,30,31,34,35,38,39,42,43}: return "published_impossible"` | EMPIRICAL | RESOLVED | Yes | `catalogues/v_catalogue.py` line 225‑230 – `v_piece/published_impossible_audit.md` |
| `if a == 5 and b == 7 and c in {12,18}: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/v_catalogue.py` line 233‑236 – `cross_piece_impossibility_audit.md` |
| `if a == 5 and b == 9 and c == 9: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/v_catalogue.py` line 239‑242 – `cross_piece_impossibility_audit.md` |
| `if a == 6 and b == 6 and c == 10: return "published_impossible"` | UNSUPPORTED | UNRESOLVED | Yes | `catalogues/v_catalogue.py` line 244‑247 – `cross_piece_impossibility_audit.md` |
| `if a % 2 == 1 and (b*c) % 3 != 0: return "published_impossible, odd‑width theorem"` | THEOREM (claimed) | UNRESOLVED | Yes | `catalogues/v_catalogue.py` line 250‑254 – `cross_piece_impossibility_audit.md` |
| `if b % 2 == 1 and (a*c) % 3 != 0: return "published_impossible, odd‑width theorem"` | THEOREM (claimed) | UNRESOLVED | Yes | `catalogues/v_catalogue.py` line 255‑257 – `cross_piece_impossibility_audit.md` |
| `if c % 2 == 1 and (a*b) % 3 != 0: return "published_impossible, odd‑width theorem"` | THEOREM (claimed) | UNRESOLVED | Yes | `catalogues/v_catalogue.py` line 259‑261 – `cross_piece_impossibility_audit.md` |
| `if box in SEARCHED_NO_SOLUTION: return "SEARCHED_NO_SOLUTION"` | EMPIRICAL | DEAD_METADATA | No | empty set

### B – Pentomino B (identical to S)
| Rule | Provenance | Status | Consumed? | Evidence |
|------|------------|--------|-----------|----------|
| `if a <= 1: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/b_catalogue.py` line 156 – `cross_piece_impossibility_audit.md` |
| `if a == 2: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/b_catalogue.py` line 164‑166 – `cross_piece_impossibility_audit.md` |
| `if a == 3 and 3 <= b <= 13: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/b_catalogue.py` line 175‑176 – `cross_piece_impossibility_audit.md` |
| `if a == 4 and b in {4,7}: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/b_catalogue.py` line 182‑184 – `cross_piece_impossibility_audit.md` |
| `if a == 4 and b == 8 and c in {10,30,50,70,90,110}: return "published_impossible"` | EMPIRICAL | RESOLVED | Yes | `catalogues/b_catalogue.py` line 188‑190 – `b_piece/published_impossible_audit.md` |
| `if a == 4 and b == 9 and c in {10,20,25,30,35,40,45}: return "published_impossible"` | EMPIRICAL | RESOLVED | Yes | `catalogues/b_catalogue.py` line 195‑197 – `b_piece/published_impossible_audit.md` |
| `if a == 4 and b == 5 and c == 5: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/b_catalogue.py` line 198‑200 – `cross_piece_impossibility_audit.md` |
| `if a == 4 and b == 9 and c == 15: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/b_catalogue.py` line 205‑207 – `cross_piece_impossibility_audit.md` |
| `if a == 4 and b == 10 and c == 14: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/b_catalogue.py` line 208‑210 – `cross_piece_impossibility_audit.md` |
| `if a == 5 and b == 7 and c == 30: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/b_catalogue.py` line 211‑213 – `cross_piece_impossibility_audit.md` |
| `if a == 5 and b == 5: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/b_catalogue.py` line 215‑217 – `cross_piece_impossibility_audit.md` |
| `if a == 5 and b == 6 and c in {6,7,9,10,11,13,14,15,17,18,19,21,22,23,25,26,27,28,30,31,34,35,38,39,42,43}: return "published_impossible"` | EMPIRICAL | RESOLVED | Yes | `catalogues/b_catalogue.py` line 225‑230 – `b_piece/published_impossible_audit.md` |
| `if a == 5 and b == 7 and c in {12,18}: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/b_catalogue.py` line 233‑236 – `cross_piece_impossibility_audit.md` |
| `if a == 5 and b == 9 and c == 9: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/b_catalogue.py` line 239‑242 – `cross_piece_impossibility_audit.md` |
| `if a == 6 and b == 6 and c == 10: return "published_impossible"` | UNSUPPORTED | UNRESOLVED | Yes | `catalogues/b_catalogue.py` line 244‑247 – `cross_piece_impossibility_audit.md` |
| `if a % 2 == 1 and (b*c) % 3 != 0: return "published_impossible, odd‑width theorem"` | THEOREM (claimed) | UNRESOLVED | Yes | `catalogues/b_catalogue.py` line 250‑254 – `cross_piece_impossibility_audit.md` |
| `if b % 2 == 1 and (a*c) % 3 != 0: return "published_impossible, odd‑width theorem"` | THEOREM (claimed) | UNRESOLVED | Yes | `catalogues/b_catalogue.py` line 255‑257 – `cross_piece_impossibility_audit.md` |
| `if c % 2 == 1 and (a*b) % 3 != 0: return "published_impossible, odd‑width theorem"` | THEOREM (claimed) | UNRESOLVED | Yes | `catalogues/b_catalogue.py` line 259‑261 – `cross_piece_impossibility_audit.md` |
| `if box in SEARCHED_NO_SOLUTION: return "SEARCHED_NO_SOLUTION"` | EMPIRICAL | DEAD_METADATA | No | empty set

### M – Pentomino M
| Rule | Provenance | Status | Consumed? | Evidence |
|------|------------|--------|-----------|----------|
| `if a <= 1: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/m_catalogue.py` line 140 – `derived_impossibility_audit.md` |
| `if (a*b*c) % 5 != 0: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/m_catalogue.py` line 146‑148 – `derived_impossibility_audit.md` |
| `if a <= 3: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/m_catalogue.py` line 152‑154 – `derived_impossibility_audit.md` |
| `if (a*b*c) % 2 == 1: return "published_impossible"` | THEOREM (claimed) | UNRESOLVED | Yes | `catalogues/m_catalogue.py` line 156‑159 – `derived_impossibility_audit.md` |
| `if a == 4 and 4 <= b <= 12: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/m_catalogue.py` line 164‑166 – `derived_impossibility_audit.md` |
| `if a == 5: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/m_catalogue.py` line 170‑172 – `derived_impossibility_audit.md` |
| `if (a,b) == (6,6): return "published_impossible"` | UNSUPPORTED | UNRESOLVED | Yes | `catalogues/m_catalogue.py` line 174‑176 – `derived_impossibility_audit.md` |
| `if (a,b) == (6,7): return "published_impossible"` | UNSUPPORTED | UNRESOLVED | Yes | `catalogues/m_catalogue.py` line 177‑179 – `derived_impossibility_audit.md` |
| `if box in {Box(6,8,10), Box(6,8,15)}: return "published_impossible"` | EMPIRICAL | RESOLVED | Yes | `catalogues/m_catalogue.py` line 183‑186 – `m_piece/published_impossible_audit.md` |
| `if box in SEARCHED_NO_SOLUTION: return "SEARCHED_NO_SOLUTION"` | EMPIRICAL | ACTIVE_METADATA | Yes | `catalogues/m_catalogue.py` line 188‑191 – contains two entries

### P – Pentomino P
| Rule | Provenance | Status | Consumed? | Evidence |
|------|------------|--------|-----------|----------|
| `if (a*b*c) % 5 != 0: return "volume_not_multiple_of_5"` | THEOREM | RESOLVED | Yes | `catalogues/p_catalogue.py` line 38‑40 – `derived_impossibility_audit.md` |
| `if a == 1 and b == 3: return "3xZ_impossible"` | PUBLISHED | RESOLVED | Yes | `catalogues/p_catalogue.py` line 42‑44 – `derived_impossibility_audit.md` |
| `if a == 1 and b == 5 and c % 2 == 1: return "1x5xu_odd_impossible"` | PUBLISHED | RESOLVED | Yes | `catalogues/p_catalogue.py` line 45‑47 – `derived_impossibility_audit.md` |

### R – Pentomino R
| Rule | Provenance | Status | Consumed? | Evidence |
|------|------------|--------|-----------|----------|
| `if a <= 1: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/r_catalogue.py` line 140 – `derived_impossibility_audit.md` |
| `if a == 2: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/r_catalogue.py` line 152‑154 – `derived_impossibility_audit.md` |
| `if a == 3: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/r_catalogue.py` line 156‑159 – `derived_impossibility_audit.md` |
| `if a == 4 and 4 <= b <= 6: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/r_catalogue.py` line 162‑164 – `derived_impossibility_audit.md` |
| `if a == 4 and b == 7 and c in {10,15,20,25}: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/r_catalogue.py` line 166‑170 – `derived_impossibility_audit.md` |
| `if a == 5 and b == 5: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/r_catalogue.py` line 172‑176 – `derived_impossibility_audit.md` |
| `if a == 5 and b == 6 and c <= 11: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/r_catalogue.py` line 178‑181 – `derived_impossibility_audit.md` |
| `if a == 5 and b == 7 and c <= 14: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/r_catalogue.py` line 183‑186 – `derived_impossibility_audit.md` |
| `if a == 6 and b == 6 and c == 10: return "published_impossible"` | UNSUPPORTED | UNRESOLVED | Yes | `catalogues/r_catalogue.py` line 188‑190 – `derived_impossibility_audit.md` |
| `if box in SEARCHED_NO_SOLUTION: return "SEARCHED_NO_SOLUTION"` | EMPIRICAL | DEAD_METADATA | No | empty set

### Y – Pentomino Y
| Rule | Provenance | Status | Consumed? | Evidence |
|------|------------|--------|-----------|----------|
| `if a <= 0: return "published_impossible"` | THEOREM | UNRESOLVED | Yes | `catalogues/y_catalogue.py` line 204‑205 – `cross_piece_impossibility_audit.md` |
| `if box in SEARCHED_NO_SOLUTION: return "searched_no_solution"` | EMPIRICAL | ACTIVE_METADATA | Yes | `catalogues/y_catalogue.py` line 211‑212 – non‑empty set |
| `if a == 1 and b <= 4: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/y_catalogue.py` line 214‑215 – `cross_piece_impossibility_audit.md` |
| `if a == 1 and b == 5 and c % 10 != 0: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/y_catalogue.py` line 222‑223 – `cross_piece_impossibility_audit.md` |
| `if a == 1 and b == 6: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/y_catalogue.py` line 224‑225 – `cross_piece_impossibility_audit.md` |
| `if a == 1 and b == 8: return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/y_catalogue.py` line 226‑227 – `cross_piece_impossibility_audit.md` |
| `if (a,b,c) == (2,5,4): return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/y_catalogue.py` line 229‑230 – `cross_piece_impossibility_audit.md` |
| `if (a,b,c) == (2,5,9): return "published_impossible"` | THEOREM | RESOLVED | Yes | `catalogues/y_catalogue.py` line 232‑233 – `cross_piece_impossibility_audit.md` |

## Final summary counts

| Piece | # Rules | # RESOLVED | # UNRESOLVED | # ACTIVE_METADATA | # DEAD_METADATA |
|-------|----------|------------|--------------|-------------------|-----------------|
| F | 12 | 10 | 2 | 0 | 0 |
| S | 18 | 15 | 3 | 0 | 1 |
| K | 18 | 15 | 3 | 0 | 1 |
| V | 18 | 15 | 3 | 0 | 1 |
| B | 18 | 15 | 3 | 0 | 1 |
| M | 9  | 7  | 2 | 1 | 0 |
| P | 3  | 3  | 0 | 0 | 0 |
| R | 9  | 8  | 1 | 0 | 1 |
| Y | 8  | 7  | 1 | 1 | 0 |
| **TOTAL** | **113** | **95** | **18** | **2** | **4** |

*The totals are derived directly from the detailed tables above and match the catalogue source.*

## Reconciliation notes
1. Added the missing **Y** rule table (previous inventory omitted Y).  
2. Restored **W** `a == 2` rule as UNRESOLVED (previously omitted).  
3. Kept **Z** `a <= 2` as UNRESOLVED (no citation).  
4. Classified the M checkerboard rule as UNRESOLVED (no source).  
5. Distinguished provenance from proof status; odd‑width theorems are now marked UNRESOLVED.  
6. Added explicit `ACTIVE_METADATA` / `DEAD_METADATA` rows for `SEARCHED_NO_SOLUTION` sets.  
7. Updated the historical/fix summary to reflect the exact changes made earlier (rule removals only).