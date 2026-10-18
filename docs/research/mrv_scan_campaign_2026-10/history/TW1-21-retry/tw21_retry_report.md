# TW1-21 RETRY — Quiet-Host Search: BLOCKED (no suitable host available)

**Date:** 2026-10-16 (Pacific/Auckland)
**Status:** BLOCKED — no accessible Linux compute host passes (or can even reach) the quietness gate. No benchmarks run. No solver code modified. No commits, merges, or deploys. No prior artifacts modified.

---

## 1. Input verification (done before host search)

Reports read:
- `/tmp/pentacube-bench/tw20/debug/debug_report.md`
- `/tmp/pentacube-bench/tw20/perf/tw20_perf_report.md` (+ `perf/progress.txt`)

Verified source paths and hashes (actual, this session):

| Item | Path | SHA256 | Match |
|---|---|---|---|
| Baseline source | `/tmp/pentacube-bench/tw18/solver_coalesced.cpp` | `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278` | ✓ |
| ActiveX source | `/tmp/pentacube-bench/tw20/solver_active_x.cpp` | `42fad94bb9cabeafc379e50b58f8e6816c0aa545a48ed178145febb15ef7bed9` | ✓ |
| W placements | `/home/philip/Work/fitpolycubes/placements_W_5x7x9.txt` | `a7a421cde69049fcfa7fd7ee8aa71a82a4ad4c7bfc9631c04ab035d663f8b045` | ✓ |
| V placements | `/home/philip/Work/fitpolycubes/placements_V_5x5x6.txt` | `dc22870d591d5c5789f4b7df8f546a36682e325474dbcb938b723afc46c100fe` | ✓ |
| KSSref placements | `/home/philip/Work/fitpolycubes/placements_KSSref_5x5x5.txt` | `9786dd438861f4668cc4b7f8f179d2b2e844426681d17c44d7375e901b1de291` | ✓ |

CLI/flags per TW1-20: `solver PIECE X Y Z placements_file [max_nodes] --connectivity --symmetry --region-prune=propagate`; caps V exhaustive / KSSref 10000000 / W 2500000; single-threaded, never `--parallel` with propagation.

---

## 2. Host search — nz-vdi-psecker and alternatives

### nz-vdi-psecker: UNREACHABLE
- `~/.ssh/config` contains only GitHub hosts — no entry for nz-vdi-psecker, no credentials or key configured for it.
- DNS: `getent hosts nz-vdi-psecker` empty; `nslookup` → SERVFAIL. FQDN variants (`*.local`, `*.lan`, short names) all unresolvable.
- `ssh -o ConnectTimeout=5 nz-vdi-psecker` → "Could not resolve hostname". No address to even attempt a gate check.

### Tailscale peers: no Linux compute host
- `tailscale status`: only `philip-virtualbox` (this VM, 100.98.115.115), `desktop-acumqap` (Windows, 100.126.127.78, reachable via relay, ping OK), `nz-psecker-l` (Windows, offline 1 day).
- SSH to the online Windows peer times out (no SSH server). No Linux peer exists to benchmark on.

### Local network / other routes: no compute host
- No docker / lxc / virsh available. No aws/gcloud/az CLIs.
- SSH-open endpoints found (10.0.2.2 = VirtualBox NAT gateway, key-auth required, not a login host; 192.168.1.1 = appliance offering only diffie-hellman-group1-sha1) — network appliances, not benchmark hosts.
- `visualsvn.4rf.local` (192.168.0.173, from /etc/hosts): SSH times out.

### Local VM itself: already gate-failed
- Current load at search time: 4.30 (1-min) on 8 CPUs — still above the <4.0 gate, and TW1-21 already documented swap 67% full + idle 65–71%. Re-running here under the same conditions is explicitly out of scope.

---

## 3.–5. Build / correctness / benchmark

Not reached — no host satisfied (or could reach) the gate, so nothing was transferred, built, or timed. Per instructions, no results are invented.

---

## 6. Decision

**BLOCKED — no suitable quiet host available.** TW1-20's standing result is unchanged: correctness established, performance **RETAIN AS EXPERIMENTAL**.

To unblock, provide one of:
1. A reachable hostname/IP + SSH credentials (or Tailscale peer running Linux with OpenSSH) for nz-vdi-psecker or equivalent, with g++ available;
2. Or a later quiet window on this VM with desktop load closed and swap freed (re-run the TW1-21 gate first);
3. Or a cloud VM (needs credentials + CLI, none configured here).

With a staged host, the protocol is ready: verify hashes post-transfer → build both with `-Ofast -march=native -flto -std=c++17 -pthread` → V/KSSref/W correctness gate → five alternating W 2.5M pairs.

---

## Artifacts

| File | SHA256 |
|---|---|
| `/tmp/pentacube-bench/tw21-retry/tw21_retry_report.md` | (see verification command below) |
| `/tmp/pentacube-bench/tw21-retry/progress.txt` | (see verification command below) |
| `/tmp/pentacube-bench/tw21-retry/benchmark_results.csv` | (see verification command below) |

No raw benchmark logs exist (nothing was run). Prior artifacts untouched.
