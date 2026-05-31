"""
SIL test runner.

For each case in cases/*.csv, run ./algo_test and check that the emitted
event names match expected/<case>.txt (one event name per line, ignoring t_ms).
"""

import os
import sys
import subprocess

BIN = "./algo_test"
CASES_DIR = "cases"
EXPECTED_DIR = "expected"


def load_expected(name):
    path = os.path.join(EXPECTED_DIR, f"{name}.txt")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]


def run_case(csv_path):
    proc = subprocess.run([BIN, csv_path], capture_output=True, text=True)
    if proc.returncode != 0:
        return None, f"binary failed: {proc.stderr.strip()}"
    events = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(",")
        if len(parts) >= 2:
            events.append(parts[1])
    return events, None


def main():
    if not os.path.exists(BIN):
        print(f"binary {BIN} not found. run `make` first.")
        sys.exit(2)

    csvs = sorted(f for f in os.listdir(CASES_DIR) if f.endswith(".csv"))
    if not csvs:
        print(f"no CSV in {CASES_DIR}/. run `make gen` first.")
        sys.exit(2)

    fails = 0
    for csv_name in csvs:
        name = os.path.splitext(csv_name)[0]
        csv_path = os.path.join(CASES_DIR, csv_name)
        events, err = run_case(csv_path)
        if err:
            print(f"[ERROR] {name}: {err}")
            fails += 1
            continue

        expected = load_expected(name)
        if expected is None:
            print(f"[SKIP]  {name}: no expected/{name}.txt — emitted: {events}")
            continue

        if events == expected:
            print(f"[PASS]  {name}: {events}")
        else:
            print(f"[FAIL]  {name}")
            print(f"        expected: {expected}")
            print(f"        got:      {events}")
            fails += 1

    print()
    if fails:
        print(f"FAIL: {fails} case(s)")
        sys.exit(1)
    print("OK: all cases pass")


if __name__ == "__main__":
    main()
