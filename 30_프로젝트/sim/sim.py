"""
Phase 1 simulator: generate 5 CSV test cases.

Columns: t_ms, ax, ay, az, gx, gy, gz
- ax/ay/az: raw int16, gravity baseline az=16384 (1g)
- gx/gy/gz: raw int16
- Sample rate: 100 Hz (10 ms step)
"""

import os
import csv

SAMPLE_MS = 10
GRAVITY = 16384


def write_case(name, rows):
    os.makedirs("cases", exist_ok=True)
    path = os.path.join("cases", f"{name}.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        for r in rows:
            w.writerow(r)
    print(f"wrote {path} ({len(rows)} rows)")


def idle(duration_ms):
    rows = []
    t = 0
    while t < duration_ms:
        rows.append([t, 0, 0, GRAVITY, 0, 0, 0])
        t += SAMPLE_MS
    return rows


def case_idle():
    return idle(5000)


def case_hard_accel():
    rows = idle(2000)
    t = rows[-1][0] + SAMPLE_MS
    # ax ramp from 0 to 8000 over 100ms (fast)
    for i in range(10):
        ax = (i + 1) * 800
        rows.append([t, ax, 0, GRAVITY, 0, 0, 0])
        t += SAMPLE_MS
    # hold high for 200ms
    for _ in range(20):
        rows.append([t, 8000, 0, GRAVITY, 0, 0, 0])
        t += SAMPLE_MS
    # back to idle
    while t < 5000:
        rows.append([t, 0, 0, GRAVITY, 0, 0, 0])
        t += SAMPLE_MS
    return rows


def case_hard_brake():
    rows = []
    t = 0
    # cruising at ax=3000 for 2s
    while t < 2000:
        rows.append([t, 3000, 0, GRAVITY, 0, 0, 0])
        t += SAMPLE_MS
    # sharp brake: ax drops to -7000 over 100ms
    for i in range(10):
        ax = 3000 - (i + 1) * 1000
        rows.append([t, ax, 0, GRAVITY, 0, 0, 0])
        t += SAMPLE_MS
    # hold low 200ms
    for _ in range(20):
        rows.append([t, -7000, 0, GRAVITY, 0, 0, 0])
        t += SAMPLE_MS
    # back to 0
    while t < 5000:
        rows.append([t, 0, 0, GRAVITY, 0, 0, 0])
        t += SAMPLE_MS
    return rows


def case_sharp_turn():
    rows = idle(2000)
    t = rows[-1][0] + SAMPLE_MS
    # gz ramp up to 18000
    for i in range(10):
        gz = (i + 1) * 1800
        rows.append([t, 0, 0, GRAVITY, 0, 0, gz])
        t += SAMPLE_MS
    # hold 200ms
    for _ in range(20):
        rows.append([t, 0, 0, GRAVITY, 0, 0, 18000])
        t += SAMPLE_MS
    # back to idle
    while t < 5000:
        rows.append([t, 0, 0, GRAVITY, 0, 0, 0])
        t += SAMPLE_MS
    return rows


def case_noise():
    """Small random spikes that must NOT trigger events."""
    rows = []
    t = 0
    pattern = [0, 500, -300, 200, -100, 400, -500, 100, 0, -200]
    i = 0
    while t < 5000:
        ax = pattern[i % len(pattern)]
        gz = pattern[(i + 3) % len(pattern)] * 4
        rows.append([t, ax, 0, GRAVITY, 0, 0, gz])
        t += SAMPLE_MS
        i += 1
    return rows


CASES = {
    "idle":        case_idle,
    "hard_accel":  case_hard_accel,
    "hard_brake":  case_hard_brake,
    "sharp_turn":  case_sharp_turn,
    "noise":       case_noise,
}


def main():
    for name, fn in CASES.items():
        write_case(name, fn())


if __name__ == "__main__":
    main()
