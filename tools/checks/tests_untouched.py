#!/usr/bin/env python3
"""tests_untouched — a change may alter existing tests/checks OR other files, never both.

Compares this copy's commits (and uncommitted files) with a base ref. Protected files are the same set as
tools/hooks/protect_tests.py (kit.json). A protected file that already exists on the base and is modified, renamed or
deleted here is a "spec change".
  - no spec changes                      -> pass
  - only spec changes                    -> pass, with a notice (it needs a second look, and the owner's yes, before merge)
  - spec changes mixed with other files  -> FAIL (exit 2)
New test files never count: adding tests alongside code is the normal test-first path. A new test-runner config file
does count, because it can switch tests off. Raising the test floor (tools/checks/floor.py raise) never counts: the
floor may go up with the tests that raised it; lowering it does count. Exit 3: no base to compare with (never a pass).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "hooks"))
from protect_tests import MIX_EXEMPT, PROTECTED_NAMES, is_protected  # noqa: E402

FLOOR = "tools/checks/test_floor.txt"


def _floor(text: str) -> int:
    digits = "".join(ch for ch in text if ch.isdigit())
    return int(digits) if digits else 0


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="origin/main")
    a = ap.parse_args()
    if git("rev-parse", "--verify", "--quiet", a.base).returncode != 0:
        print(f"tests_untouched: base ref {a.base} not found — NOT RUN")
        return 3
    lines = git("diff", "--name-status", "-M", f"{a.base}...HEAD").stdout.splitlines()
    for line in git("status", "--porcelain").stdout.splitlines():  # uncommitted work counts too
        code, name = line[:2].strip() or "M", line[3:].split(" -> ")[-1].strip()
        lines.append(f"{'A' if code == '??' else code[0]}\t{name}")
    base_has_tests = git("cat-file", "-e", f"{a.base}:tests").returncode == 0
    spec, other = [], []
    for line in lines:
        parts = line.split("\t")
        status, old, new = parts[0][0], parts[1], parts[-1]
        if old in MIX_EXEMPT or new in MIX_EXEMPT:
            continue
        if status == "M" and old == FLOOR:
            was = git("show", f"{a.base}:{FLOOR}")
            now = (ROOT / FLOOR).read_text(encoding="utf-8") if (ROOT / FLOOR).is_file() else "0"
            if was.returncode == 0 and _floor(now) >= _floor(was.stdout):
                continue  # the floor went up (or stayed): never a spec change
        existed = git("cat-file", "-e", f"{a.base}:{old}").returncode == 0
        new_runner_config = base_has_tests and status == "A" and new.rsplit("/", 1)[-1] in PROTECTED_NAMES
        if (status in "MDR" and existed and is_protected(old)) or new_runner_config:
            spec.append(f"{status} {new}")
        elif not (status == "A" and is_protected(new)):
            other.append(new)
    spec, other = sorted(set(spec)), sorted(set(other))
    if spec and other:
        print("tests_untouched: FAIL — this change alters existing tests, fixtures or checks AND other files:")
        for s in spec:
            print("   ", s)
        print(f"   ...together with {len(other)} other file(s). Split it: the spec change goes first, on its own.")
        return 2
    if spec:
        print(f"tests_untouched: spec-only change ({len(spec)} protected file(s)) — needs a second look and the owner's yes before merge")
    else:
        print("tests_untouched: ok — no existing test, fixture or check was altered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
