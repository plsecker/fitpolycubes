#!/usr/bin/env python3
"""Five sequential, interleaved V complete-search repetitions per solver."""
import pathlib
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parent
PLACEMENTS = pathlib.Path("/home/philip/Work/fitpolycubes/placements_V_5x5x6.txt")
COMMANDS = {
    "reference": [str(ROOT / "solver_reference"), "V", "5", "5", "6", str(PLACEMENTS), "0"],
    "tw13": [str(ROOT / "solver_tw13"), "V", "5", "5", "6", str(PLACEMENTS), "0"],
    "coalesced": [str(ROOT / "solver_coalesced"), "V", "5", "5", "6", str(PLACEMENTS), "0"],
}
SOURCE_HASHES = {
    "reference": "65e9e2c42c7b58a2ba7cd6501132e9ef300bbabcdc93fe4d1aadbe4512f6738e",
    "tw13": "9289644a9c968182f14c734fa96ac83a4612ffd93bc822cacea376e24130443c",
    "coalesced": "a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278",
}
BINARY_HASHES = {
    "reference": "61647ab64deb5be29e9e44336fe9c9e800bce2891f19e8151b1e8367b90035a8",
    "tw13": "4e2ff001cd69e6a7bfdebde86b90d0ec1a8dc9bc7115cad6a28ba4018e6e310d",
    "coalesced": "214b4de314f63dd5240ef178be7b4851ccd2e2b43137c29e4ea0dedf23df3180",
}
ORDERS = [
    ("reference", "tw13", "coalesced"),
    ("tw13", "coalesced", "reference"),
    ("coalesced", "reference", "tw13"),
    ("reference", "coalesced", "tw13"),
    ("coalesced", "tw13", "reference"),
]

for round_no, order in enumerate(ORDERS, start=11):
    for variant in order:
        command = COMMANDS[variant]
        load_before = time.strftime("%Y-%m-%dT%H:%M:%S%z") + f" load={subprocess.getoutput('uptime').split('load average:')[-1].strip()}"
        start_ns = time.perf_counter_ns()
        result = subprocess.run(command, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True,
                                check=False)
        external_s = (time.perf_counter_ns() - start_ns) / 1_000_000_000
        load_after = time.strftime("%Y-%m-%dT%H:%M:%S%z") + f" load={subprocess.getoutput('uptime').split('load average:')[-1].strip()}"
        log = ROOT / f"V_precise_r{round_no}_{variant}.log"
        with log.open("w") as f:
            f.write(f"RUN={round_no} variant={variant}\n")
            f.write("COMMAND=" + " ".join(command) + "\n")
            f.write(f"SOURCE_SHA256={SOURCE_HASHES[variant]}\n")
            f.write(f"BINARY_SHA256={BINARY_HASHES[variant]}\n")
            f.write(f"PLACEMENT_SHA256=dc22870d591d5c5789f4b7df8f546a36682e325474dbcb938b723afc46c100fe\n")
            f.write(f"LOAD_BEFORE={load_before}\n")
            f.write(result.stdout)
            if result.stdout and not result.stdout.endswith("\n"):
                f.write("\n")
            f.write(f"EXTERNAL_WALL_S={external_s:.9f}\n")
            f.write(f"EXIT_STATUS={result.returncode}\n")
            f.write(f"LOAD_AFTER={load_after}\n")
        print(f"round={round_no} variant={variant} external_s={external_s:.9f} "
              f"exit={result.returncode} log={log.name}")
        if result.returncode != 0:
            raise SystemExit(result.returncode)
