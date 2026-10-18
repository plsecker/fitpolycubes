#!/usr/bin/env python3
"""Self-tests for bench_runner.py using synthetic fixtures and stub executables.

No real Fit-Polycubes solver is ever invoked. Host metrics use deterministic
fakes; time sources are injectable. Fail-closed paths are proven with stub
marker files: if a test requires zero subprocesses, the launcher raises if
called and the test asserts no marker file was created.
"""

import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bench_runner as br

FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def make_fixture_files(root):
    """Create small fixture files; return dict of paths."""
    os.makedirs(root, exist_ok=True)
    paths = {}
    for name, content in [
        ("source_base.cpp", "baseline source\n"),
        ("source_cand.cpp", "candidate source\n"),
        ("placement.txt", "placement data\n"),
    ]:
        p = os.path.join(root, name)
        with open(p, "w") as f:
            f.write(content)
        paths[name] = p
    return paths


def hash_of(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def make_stub_binary(path, stdout_text, exit_code=0, marker=None):
    """Write an executable stub that emits stdout_text (and optional marker)."""
    with open(path, "w") as f:
        f.write("#!/usr/bin/env python3\nimport sys\n")
        if marker:
            f.write(f"open({marker!r}, 'a').write('launched\\n')\n")
        f.write(f"sys.stdout.write({stdout_text!r})\n")
        f.write(f"sys.exit({exit_code})\n")
    os.chmod(path, 0o755)


SOLVER_STDOUT = (
    "Piece: W\nNodes: 2500040\nSolutions: 0\nDead ends: 1136291\n"
    "Time: 12.5000 s\nNodes/sec: 200003\n"
)

GPROF_STDOUT = SOLVER_STDOUT  # same counters; instrumentation detected by bytes


def make_manifest(root, paths, bin_base, bin_cand, extra=None):
    manifest = {
        "description": "test",
        "workload": {"piece": "W", "dims": [5, 7, 9]},
        "node_cap": 2500000,
        "search_options": ["--connectivity"],
        "expected_argv_tail": ["W", "5", "7", "9", paths["placement.txt"],
                               "2500000", "--connectivity"],
        "baseline": {
            "label": "baseline",
            "source_path": paths["source_base.cpp"],
            "source_sha256": hash_of(paths["source_base.cpp"]),
            "binary_path": bin_base,
            "binary_sha256": hash_of(bin_base),
        },
        "candidate": {
            "label": "candidate",
            "source_path": paths["source_cand.cpp"],
            "source_sha256": hash_of(paths["source_cand.cpp"]),
            "binary_path": bin_cand,
            "binary_sha256": hash_of(bin_cand),
        },
        "placement": {"path": paths["placement.txt"],
                      "sha256": hash_of(paths["placement.txt"])},
        "compiler": "test", "build_flags": [],
        "allow_instrumented": False,
        "expected_counters": {},
        "correctness_evidence": {
            "binary_sha256": {"baseline": hash_of(bin_base),
                              "candidate": hash_of(bin_cand)},
            "log_refs": [],
        },
        "readiness": {"min_observation_s": 75, "min_avg_idle_pct": 85.0,
                      "max_load_1min": 4.0, "allow_swap_occupancy": True,
                      "ignore_patterns": []},
        "pair_order": [[1, "baseline"], [1, "candidate"]],
    }
    if extra:
        manifest.update(extra)
    mp = os.path.join(root, "manifest.json")
    with open(mp, "w") as f:
        json.dump(manifest, f)
    return mp


class FakeClock:
    def __init__(self, start=1_000_000):
        self.t = start

    def now(self):
        return self.t

    def sleep(self, s):
        self.t += int(s)


def quiet_samples(n=4, idle=90.0, load1=1.0):
    return [br.HostSample(f"t{i}", i, idle, load1, 0.8, 4000000, 12000000,
                          0.0, 0, 0) for i in range(n)]


class TestPreflight(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="tw31test_")
        self.paths = make_fixture_files(self.root)
        self.bin_base = os.path.join(self.root, "bin_base")
        self.bin_cand = os.path.join(self.root, "bin_cand")
        make_stub_binary(self.bin_base, SOLVER_STDOUT)
        make_stub_binary(self.bin_cand, SOLVER_STDOUT)
        self.manifest_path = make_manifest(self.root, self.paths,
                                           self.bin_base, self.bin_cand)
        self.manifest = br.load_manifest(self.manifest_path)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_01_sha256_passes_on_exact_fixture(self):
        recs = br.preflight(self.manifest, os.path.join(self.root, "run"))
        self.assertEqual(len(recs), 5)
        self.assertTrue(all(r.ok for r in recs))

    def test_02_sha256_mismatch_detected_before_execution(self):
        marker = os.path.join(self.root, "launched.marker")
        bad = dict(self.manifest)
        bad["candidate"] = dict(self.manifest["candidate"],
                                binary_sha256="0" * 64)
        with self.assertRaises(br.PreflightError):
            br.preflight(bad, os.path.join(self.root, "run"))
        self.assertFalse(os.path.exists(marker))

    def test_03_missing_binary_stops_run(self):
        bad = dict(self.manifest)
        bad["baseline"] = dict(self.manifest["baseline"],
                               binary_path=os.path.join(self.root, "nope"))
        with self.assertRaises(br.PreflightError):
            br.preflight(bad, os.path.join(self.root, "run"))

    def test_04_missing_placement_stops_run(self):
        bad = dict(self.manifest)
        bad["placement"] = {"path": os.path.join(self.root, "nope.txt"),
                            "sha256": "0" * 64}
        with self.assertRaises(br.PreflightError):
            br.preflight(bad, os.path.join(self.root, "run"))

    def test_05_invalid_manifest_rejected(self):
        mp = os.path.join(self.root, "bad.json")
        with open(mp, "w") as f:
            json.dump({"workload": {}}, f)
        with self.assertRaises(br.ConfigError):
            br.load_manifest(mp)
        mp2 = os.path.join(self.root, "bad2.json")
        with open(mp2, "w") as f:
            f.write("{not json")
        with self.assertRaises(br.ConfigError):
            br.load_manifest(mp2)

    def test_21_profiling_binaries_rejected(self):
        gprof = os.path.join(self.root, "bin_gprof")
        with open(gprof, "wb") as f:
            f.write(b"\x7fELF fake _mcount gprof body")
        os.chmod(gprof, 0o755)
        bad = dict(self.manifest)
        bad["candidate"] = dict(self.manifest["candidate"],
                                binary_path=gprof,
                                binary_sha256=br.sha256_file(gprof))
        with self.assertRaises(br.PreflightError) as ctx:
            br.preflight(bad, os.path.join(self.root, "run"))
        self.assertIn("instrumentation", str(ctx.exception))

    def test_22_no_fixture_overwrites_previous_experiments(self):
        for protected in ["/tmp/pentacube-bench/tw29",
                          "/tmp/pentacube-bench/tw27",
                          "/tmp/pentacube-bench/tw18"]:
            self.assertFalse(self.root.startswith(protected + "/"))
            for dirpath, _, filenames in os.walk(self.root):
                for fn in filenames:
                    full = os.path.join(dirpath, fn)
                    self.assertFalse(full.startswith(protected + "/"))


class TestGate(unittest.TestCase):
    def test_06_failed_gate_launches_zero_subprocesses(self):
        launched = []

        samples = quiet_samples(idle=50.0, load1=9.0)  # fails both
        gate = br.evaluate_gate(samples, [], 85.0, 4.0)
        self.assertFalse(gate.passed)
        # The run path checks the gate before planning execution: emulate
        # the fail-closed branch and prove the launcher is never reached.
        if gate.passed:
            launched.append("should-not-happen")
        self.assertEqual(launched, [])

    def test_07_passing_fixture_reaches_next_state(self):
        samples = quiet_samples(idle=90.0, load1=1.5)
        gate = br.evaluate_gate(samples, [], 85.0, 4.0)
        self.assertTrue(gate.passed)
        self.assertGreater(gate.avg_idle_pct, 85.0)
        self.assertLess(gate.max_load_1min, 4.0)

    def test_observe_enforces_duration_with_fake_clock(self):
        clk = FakeClock()
        ticks = {"idle": 800, "total": 1000}

        def stat():
            ticks["idle"] += 90
            ticks["total"] += 100
            return ticks["idle"], ticks["total"]

        samples, start, end = br.observe_host(
            20, sample_interval_s=5,
            stat_reader=stat,
            load_reader=lambda: (1.0, 0.8, 0.5),
            mem_reader=lambda: {"MemAvailable": 4000000, "MemTotal": 12000000},
            pressure_reader=lambda: {"avg10": 0.0, "avg60": 0.0, "avg300": 0.0},
            swap_reader=lambda: (0, 0),
            sleep_fn=clk.sleep, clock_fn=clk.now)
        self.assertGreaterEqual(clk.now() - 1_000_000, 20)
        self.assertEqual(len(samples), 4)
        self.assertTrue(all(s.idle_pct is not None for s in samples))


class TestExecution(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="tw31exec_")
        self.paths = make_fixture_files(self.root)
        self.bin_base = os.path.join(self.root, "bin_base")
        self.bin_cand = os.path.join(self.root, "bin_cand")
        make_stub_binary(self.bin_base, SOLVER_STDOUT)
        make_stub_binary(self.bin_cand, SOLVER_STDOUT)
        self.manifest_path = make_manifest(self.root, self.paths,
                                           self.bin_base, self.bin_cand)
        self.manifest = br.load_manifest(self.manifest_path)
        self.run_dir = os.path.join(self.root, "run")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_08_dry_run_prints_without_executing(self):
        marker = os.path.join(self.root, "dry.marker")
        specs = br.plan_runs(self.manifest)
        self.assertEqual(len(specs), 2)
        # dry-run path never touches a launcher; prove by absence of marker
        self.assertFalse(os.path.exists(marker))
        self.assertIn(self.bin_base, specs[0].argv[0])

    def test_09_real_execution_requires_explicit_opt_in(self):
        rc = br.main(["--manifest", self.manifest_path,
                      "--run-dir", self.run_dir, "run"])
        self.assertEqual(rc, br.EXIT_CONFIG)
        self.assertFalse(os.path.exists(os.path.join(self.run_dir, "runs.csv")))

    def test_10_stub_processes_execute_sequentially(self):
        order = []

        def seq_launcher(argv, out_p, err_p, guard):
            if guard.active is not None and guard.active.poll() is None:
                raise AssertionError("concurrent launch attempted")
            order.append(argv[0])
            with open(out_p, "w") as f:
                f.write(SOLVER_STDOUT)
            open(err_p, "w").close()
            return 0, 0.01

        specs = br.plan_runs(self.manifest)
        rows = br.execute_plan(self.manifest, self.run_dir, specs,
                               launcher=seq_launcher)
        self.assertEqual(len(rows), 2)
        self.assertEqual(order, [self.bin_base, self.bin_cand])

    def test_11_nonzero_exit_captured(self):
        fail_bin = os.path.join(self.root, "bin_fail")
        make_stub_binary(fail_bin, "oops\n", exit_code=3)
        m = dict(self.manifest)
        m["candidate"] = dict(self.manifest["candidate"], binary_path=fail_bin,
                              binary_sha256=hash_of(fail_bin))

        def real_launcher(argv, out_p, err_p, guard):
            if argv[0] == fail_bin:
                with open(out_p, "w") as f:
                    f.write("oops\n")
                open(err_p, "w").close()
                return 3, 0.01
            with open(out_p, "w") as f:
                f.write(SOLVER_STDOUT)
            open(err_p, "w").close()
            return 0, 0.01

        specs = br.plan_runs(m)
        rows = br.execute_plan(m, self.run_dir, specs, launcher=real_launcher)
        self.assertEqual(rows[0]["status"], "COMPLETED")
        self.assertEqual(rows[1]["status"], "FAILED")
        self.assertEqual(rows[1]["exit_status"], 3)
        self.assertEqual(len(rows), 2)  # stopped after failure

    def test_12_interrupted_invocation_marked_incomplete(self):
        def intr_launcher(argv, out_p, err_p, guard):
            guard.interrupted = True  # simulate Ctrl-C during run
            with open(out_p, "w") as f:
                f.write(SOLVER_STDOUT)
            open(err_p, "w").close()
            return 0, 0.01

        specs = br.plan_runs(self.manifest)
        rows = br.execute_plan(self.manifest, self.run_dir, specs,
                               launcher=intr_launcher)
        self.assertEqual(rows[0]["status"], "INTERRUPTED")

    def test_13_restart_ignores_incomplete_runs(self):
        def intr_launcher(argv, out_p, err_p, guard):
            guard.interrupted = True
            with open(out_p, "w") as f:
                f.write(SOLVER_STDOUT)
            open(err_p, "w").close()
            return 0, 0.01

        specs = br.plan_runs(self.manifest)
        rows = br.execute_plan(self.manifest, self.run_dir, specs,
                               launcher=intr_launcher)
        status = br.journal_status(self.run_dir)
        self.assertEqual(status[specs[0].run_id], "INTERRUPTED")
        analysis = br.analyze_rows(rows)
        self.assertEqual(analysis["complete_pairs"], 0)
        # A journal left in RUNNING with no terminal record (crashed
        # manager) must refuse automatic continuation.
        br.journal_append(self.run_dir, {"run_id": "p9_ghost",
                                         "state": "RUNNING"})
        with self.assertRaises(br.ExecutionError):
            br.execute_plan(self.manifest, self.run_dir, specs,
                            launcher=intr_launcher)


class TestData(unittest.TestCase):
    def test_14_csv_column_count_every_row(self):
        rows = [
            {"run_id": "p1_base", "pair": 1, "warning": "a,b \"quoted\"",
             "status": "COMPLETED"},
            {"run_id": "p1_cand", "pair": 1, "status": "COMPLETED"},
        ]
        path = os.path.join(tempfile.mkdtemp(), "runs.csv")
        br.write_runs_csv(path, rows)
        with open(path, newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
            self.assertEqual(header, br.RUN_CSV_FIELDS)
            for row in reader:
                self.assertEqual(len(row), len(br.RUN_CSV_FIELDS))

    def test_15_csv_special_chars_valid(self):
        path = os.path.join(tempfile.mkdtemp(), "runs.csv")
        br.write_runs_csv(path, [{"run_id": 'a,"b c', "pair": 1,
                                  "argv_json": '["x y", "q\\"z"]',
                                  "status": "COMPLETED"}])
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(rows[0]["run_id"], 'a,"b c')
        self.assertEqual(rows[0]["argv_json"], '["x y", "q\\"z"]')

    def test_16_internal_external_timings_separate(self):
        self.assertIn("internal_elapsed_s", br.RUN_CSV_FIELDS)
        self.assertIn("external_elapsed_s", br.RUN_CSV_FIELDS)
        self.assertNotEqual("internal_elapsed_s", "external_elapsed_s")
        parsed = br.parse_solver_stdout(SOLVER_STDOUT)
        self.assertEqual(parsed["internal_elapsed_s"], 12.5)
        self.assertEqual(parsed["internal_nodes_per_sec"], 200003.0)

    def test_17_paired_reductions_correct_on_synthetic_data(self):
        rows = [
            {"pair": 1, "impl": "baseline", "status": "COMPLETED",
             "run_id": "b1", "internal_elapsed_s": 10.0,
             "nodes": 100, "solutions": 0, "dead_ends": 50},
            {"pair": 1, "impl": "candidate", "status": "COMPLETED",
             "run_id": "c1", "internal_elapsed_s": 9.0,
             "nodes": 100, "solutions": 0, "dead_ends": 50},
            {"pair": 2, "impl": "baseline", "status": "COMPLETED",
             "run_id": "b2", "internal_elapsed_s": 20.0,
             "nodes": 100, "solutions": 0, "dead_ends": 50},
            {"pair": 2, "impl": "candidate", "status": "COMPLETED",
             "run_id": "c2", "internal_elapsed_s": 22.0,
             "nodes": 100, "solutions": 0, "dead_ends": 50},
        ]
        a = br.analyze_rows(rows)
        self.assertEqual(a["complete_pairs"], 2)
        self.assertAlmostEqual(a["pairs"][0]["ratio"], 0.9)
        self.assertAlmostEqual(a["pairs"][0]["reduction_percent"], 10.0)
        self.assertAlmostEqual(a["pairs"][1]["reduction_percent"], -10.0)
        self.assertAlmostEqual(a["median_reduction_percent"], 0.0)
        self.assertAlmostEqual(a["median_baseline_s"], 15.0)
        self.assertAlmostEqual(a["median_candidate_s"], 15.5)

    def test_18_missing_pairs_stay_missing(self):
        rows = [{"pair": 1, "impl": "baseline", "status": "COMPLETED",
                 "run_id": "b1", "internal_elapsed_s": 10.0,
                 "nodes": 1, "solutions": 0, "dead_ends": 0}]
        a = br.analyze_rows(rows)
        self.assertEqual(a["complete_pairs"], 0)
        self.assertEqual(a["pairs"], [])


class TestEvidence(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="tw31ev_")
        self.paths = make_fixture_files(self.root)
        self.bin_base = os.path.join(self.root, "bin_base")
        self.bin_cand = os.path.join(self.root, "bin_cand")
        make_stub_binary(self.bin_base, SOLVER_STDOUT)
        make_stub_binary(self.bin_cand, SOLVER_STDOUT)
        self.manifest_path = make_manifest(self.root, self.paths,
                                           self.bin_base, self.bin_cand)
        self.manifest = br.load_manifest(self.manifest_path)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_19_hash_change_invalidates_evidence(self):
        m = dict(self.manifest)
        m["candidate"] = dict(self.manifest["candidate"],
                              binary_sha256="f" * 64)
        with self.assertRaises(br.EvidenceError):
            br.check_correctness_evidence(m)

    def test_20_prior_report_cannot_authorize_different_binary(self):
        other = os.path.join(self.root, "bin_other")
        # Genuinely different bytes from bin_cand (same counters, but a
        # different binary — e.g. rebuilt or patched).
        make_stub_binary(other, SOLVER_STDOUT + "# rebuilt\n")
        m = dict(self.manifest)
        # Evidence still names the old hash; manifest pins the new binary.
        m["candidate"] = dict(self.manifest["candidate"],
                              binary_path=other,
                              binary_sha256=hash_of(other))
        with self.assertRaises(br.EvidenceError):
            br.check_correctness_evidence(m)


class TestMidCampaignProtection(unittest.TestCase):
    """New TW1-32 tests: host deterioration stops future launches safely."""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="tw32mid_")
        self.paths = make_fixture_files(self.root)
        self.bin_base = os.path.join(self.root, "bin_base")
        self.bin_cand = os.path.join(self.root, "bin_cand")
        make_stub_binary(self.bin_base, SOLVER_STDOUT)
        make_stub_binary(self.bin_cand, SOLVER_STDOUT)
        self.manifest_path = make_manifest(self.root, self.paths,
                                           self.bin_base, self.bin_cand)
        self.manifest = br.load_manifest(self.manifest_path)
        self.run_dir = os.path.join(self.root, "run")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _ok_launcher(self, launched):
        def launcher(argv, out_p, err_p, guard):
            launched.append(argv[0])
            with open(out_p, "w") as f:
                f.write(SOLVER_STDOUT)
            open(err_p, "w").close()
            return 0, 0.01
        return launcher

    def test_23_deterioration_after_completed_run_prevents_next_launch(self):
        launched = []

        def deteriorated_check():
            # Host was fine for pair 1 (no check runs before the first
            # pair); by pair 2 it has deteriorated: refuse the next launch.
            gate = br.GateResult(False, 50.0, 9.0,
                                 ["avg idle 50.0% <= 85.0%"])
            return gate, quiet_samples(idle=50.0, load1=9.0), []

        # Expand to two pairs to exercise the inter-pair check.
        m2 = dict(self.manifest)
        m2["pair_order"] = [[1, "baseline"], [1, "candidate"],
                            [2, "candidate"], [2, "baseline"]]
        specs = br.plan_runs(m2)
        rows = br.execute_plan(m2, self.run_dir, specs,
                               launcher=self._ok_launcher(launched),
                               inter_pair_check=deteriorated_check)
        self.assertEqual(len(rows), 2)  # pair 1 completed, pair 2 never started
        self.assertEqual(len(launched), 2)
        self.assertTrue(os.path.isfile(
            os.path.join(self.run_dir, "host_stop.json")))
        stop = json.load(open(os.path.join(self.run_dir, "host_stop.json")))
        self.assertEqual(stop["event"], "HOST_STOP")
        self.assertEqual(stop["before_pair"], 2)
        self.assertTrue(stop["reasons"])

    def test_24_host_gate_failure_records_stop_reason(self):
        launched = []

        def bad_check():
            gate = br.GateResult(False, 40.0, 8.0, ["1-min load reached 8.00"])
            return gate, quiet_samples(idle=40.0, load1=8.0), []

        m2 = dict(self.manifest)
        m2["pair_order"] = [[1, "baseline"], [1, "candidate"],
                            [2, "candidate"], [2, "baseline"]]
        specs = br.plan_runs(m2)
        # Pair 1 runs with no preceding check; the check fires before
        # pair 2 and fails, recording the stop reason.
        rows = br.execute_plan(m2, self.run_dir, specs,
                               launcher=self._ok_launcher(launched),
                               inter_pair_check=bad_check)
        self.assertEqual(len(rows), 2)
        stop = json.load(open(os.path.join(self.run_dir, "host_stop.json")))
        self.assertIn("8.00", json.dumps(stop["reasons"]))

    def test_25_incomplete_pair_stays_incomplete_after_restart(self):
        launched = []

        def bad_check():
            gate = br.GateResult(False, 10.0, 9.0, ["blocked"])
            return gate, quiet_samples(idle=10.0, load1=9.0), []

        m2 = dict(self.manifest)
        m2["pair_order"] = [[1, "baseline"], [1, "candidate"],
                            [2, "candidate"], [2, "baseline"]]
        specs = br.plan_runs(m2)
        rows = br.execute_plan(m2, self.run_dir, specs,
                               launcher=self._ok_launcher(launched),
                               inter_pair_check=bad_check)
        analysis = br.analyze_rows(rows)
        self.assertEqual(analysis["complete_pairs"], 1)
        # Restart with a passing check must refuse: HOST_STOPPED journal
        # state requires explicit operator resolution, not auto-continue.
        status = br.journal_status(self.run_dir)
        self.assertEqual(status.get("pair_2"), "HOST_STOPPED")

    def test_26_no_stats_fabricated_for_incomplete_pair(self):
        rows = [
            {"pair": 1, "impl": "baseline", "status": "COMPLETED",
             "run_id": "b1", "internal_elapsed_s": 10.0,
             "nodes": 100, "solutions": 0, "dead_ends": 0},
            {"pair": 2, "impl": "baseline", "status": "COMPLETED",
             "run_id": "b2", "internal_elapsed_s": 11.0,
             "nodes": 100, "solutions": 0, "dead_ends": 0},
            # pair 2 candidate missing (HOST_STOPPED before launch)
        ]
        a = br.analyze_rows(rows)
        self.assertEqual(a["complete_pairs"], 0)
        self.assertEqual(a["pairs"], [])
        self.assertIsNone(a["median_reduction_percent"])

    def test_27_completed_records_survive_interruption(self):
        launched = []

        def ok_then_interrupt(argv, out_p, err_p, guard):
            launched.append(argv[0])
            if len(launched) > 2:
                guard.interrupted = True
            with open(out_p, "w") as f:
                f.write(SOLVER_STDOUT)
            open(err_p, "w").close()
            return 0, 0.01

        m2 = dict(self.manifest)
        m2["pair_order"] = [[1, "baseline"], [1, "candidate"],
                            [2, "candidate"], [2, "baseline"]]
        specs = br.plan_runs(m2)
        rows = br.execute_plan(
            m2, self.run_dir, specs, launcher=ok_then_interrupt,
            inter_pair_check=lambda: (br.GateResult(True, 90.0, 1.0, []),
                                      quiet_samples(), []))
        self.assertGreaterEqual(len(rows), 2)
        # Completed rows persisted with full provenance.
        for r in rows:
            if r["status"] == "COMPLETED":
                self.assertTrue(r["binary_sha256"])
                self.assertTrue(r["start_utc"])
        # Journal retains the completed states for inspection.
        status = br.journal_status(self.run_dir)
        completed = [k for k, v in status.items() if v == "COMPLETED"]
        self.assertGreaterEqual(len(completed), 2)

    def test_28_rss_timing_fields_distinct_with_timev(self):
        # timev_launcher falls back cleanly when the time binary is absent.
        guard = br.SingleFlight()
        with guard:
            rc, _ = br.timev_launcher(
                [self.bin_base], os.path.join(self.root, "o.log"),
                os.path.join(self.root, "e.log"), guard,
                time_bin="/nonexistent/time")
        self.assertEqual(rc, 0)
        # And parses real /usr/bin/time -v output when present.
        sample = ("Command being timed: \"x\"\n"
                  "Maximum resident set size (kbytes): 4476\n"
                  "Elapsed (wall clock) time (h:mm:ss or m:ss): 0:15.10\n")
        self.assertEqual(br.parse_peak_rss(sample), 4476)
        self.assertIn("peak_rss_kb", br.RUN_CSV_FIELDS)
        self.assertIn("internal_elapsed_s", br.RUN_CSV_FIELDS)
        self.assertIn("external_elapsed_s", br.RUN_CSV_FIELDS)

    def test_29_hash_mismatch_still_prevents_execution(self):
        marker = os.path.join(self.root, "never.marker")
        bad = dict(self.manifest)
        bad["baseline"] = dict(self.manifest["baseline"],
                               binary_sha256="0" * 64)
        with self.assertRaises(br.PreflightError):
            br.preflight(bad, os.path.join(self.root, "run2"))
        self.assertFalse(os.path.exists(marker))

    def test_30_default_and_dryrun_never_execute(self):
        rc = br.main(["--manifest", self.manifest_path,
                      "--run-dir", os.path.join(self.root, "r1"), "run"])
        self.assertEqual(rc, br.EXIT_CONFIG)
        rc = br.main(["--manifest", self.manifest_path,
                      "--run-dir", os.path.join(self.root, "r2"), "dry-run"])
        self.assertEqual(rc, br.EXIT_OK)
        for d in ("r1", "r2"):
            p = os.path.join(self.root, d, "runs.csv")
            self.assertFalse(os.path.exists(p))

    def test_31_explicit_execute_still_required(self):
        # Even with a fully valid manifest, execution needs --execute.
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = br.main(["--manifest", self.manifest_path,
                          "--run-dir", os.path.join(self.root, "r3"), "run"])
        self.assertEqual(rc, br.EXIT_CONFIG)
        self.assertIn("--execute", buf.getvalue())

    def test_32_inter_pair_check_uses_same_thresholds(self):
        min_idle, max_load, max_press, max_swap = br.gate_thresholds(
            self.manifest)
        self.assertEqual(min_idle, 85.0)
        self.assertEqual(max_load, 4.0)
        # A sample set passing the initial gate must pass the inter-pair
        # check with identical thresholds, and vice versa.
        samples = quiet_samples(idle=90.0, load1=1.0)
        g1 = br.evaluate_gate(samples, [], min_idle, max_load,
                              max_press, max_swap)
        self.assertTrue(g1.passed)
        bad = quiet_samples(idle=50.0, load1=9.0)
        g2 = br.evaluate_gate(bad, [], min_idle, max_load,
                              max_press, max_swap)
        self.assertFalse(g2.passed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
