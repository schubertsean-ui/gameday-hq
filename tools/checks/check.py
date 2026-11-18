#!/usr/bin/env python3
"""check.py — the body of `bash tools/check`. Read tools/check for how it is called.

Sections, in order:
  1. product tests        kit.json "test_command" (quick: "quick_test_command"). Its exit code decides. When the output is
                          pytest's, also: no deselected tests; no skipped tests on the code host (CI=true); and, in a full
                          run, at least as many tests as tools/checks/test_floor.txt (tests cannot quietly disappear).
  2. tests untouched      tools/checks/tests_untouched.py: a change may alter existing tests/checks OR other files, never both.
  3. extra checks         each {"name", "run"} in kit.json "extra_checks" (a page-size budget, a screenshot audit, a linter):
                          its command's exit code decides.
  4. lane (shown, never blocking)  tools/checks/lane.py: GREEN (the AI may merge it, after review) or RED (it waits for
                          the owner). It does not turn the check red, so a red-lane change the owner approves can still pass.
  5. spend (shown, never blocking) tools/spend.py status: this month's spend against kit.json "monthly_cap_usd".
Sections 2 to 5 run only in a full check.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from kitconf import CONF  # noqa: E402


def section(title: str) -> None:
    print(f"\n== {title}", flush=True)


def count(word: str, text: str) -> int:
    found = re.findall(rf"(\d+) {word}", text)
    return int(found[-1]) if found else 0


def run_tests(quick: bool) -> bool:
    section("product tests")
    cmd = CONF["quick_test_command" if quick else "test_command"]
    if not cmd:
        print("   NOT RUN: kit.json has no test command")
        return False
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")  # no stale bytecode after a same-second edit (kit test, 18 Nov 2026)
    r = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, env=env)
    out = r.stdout + r.stderr
    print("\n".join(out.strip().splitlines()[-25:]))
    if r.returncode == 127 or "No module named pytest" in out:
        print(f"   NOT RUN: the test command could not start (`{cmd}`)")
        return False
    ok = r.returncode == 0
    print(f"   {'ok' if ok else 'FAIL'} (exit {r.returncode})")
    if re.search(r"\d+ (passed|failed|skipped|error)", out):  # pytest's summary line: hold the extra rules
        passed, skipped, deselected = count("passed", out), count("skipped", out), count("deselected", out)
        if deselected:
            print(f"   FAIL: {deselected} test(s) were deselected — every test must run")
            ok = False
        if skipped:
            if os.environ.get("CI") == "true":
                print(f"   FAIL: {skipped} test(s) skipped on the code host — nothing may skip there")
                ok = False
            else:
                print(f"   NOTE: {skipped} skipped here — they were NOT verified in this run")
        floor_file = ROOT / "tools" / "checks" / "test_floor.txt"
        floor = int(re.sub(r"\D", "", floor_file.read_text()) or 0) if floor_file.is_file() else 0
        if not quick and passed + skipped < floor:
            print(f"   FAIL: {passed + skipped} tests ran; the floor is {floor} (tools/checks/test_floor.txt) — tests have gone missing")
            ok = False
    return ok


def tests_untouched(base: str) -> bool:
    section("existing tests, fixtures and checks were not altered alongside other files")
    r = subprocess.run([sys.executable, "tools/checks/tests_untouched.py", "--base", base], cwd=ROOT, text=True)
    if r.returncode == 3:
        print("   NOT RUN (no base to compare with)")
        return False
    return r.returncode == 0


def extra_checks() -> bool:
    ok = True
    for item in CONF.get("extra_checks") or []:
        section(item.get("name", item.get("run", "extra check")))
        r = subprocess.run(item["run"], shell=True, cwd=ROOT, text=True)
        print(f"   {'ok' if r.returncode == 0 else 'FAIL'} (exit {r.returncode})")
        ok = ok and r.returncode == 0
    return ok


def shown(title: str, cmd: list[str]) -> None:
    section(title)
    r = subprocess.run([sys.executable, *cmd], cwd=ROOT, text=True, capture_output=True)
    print("\n".join((r.stdout + r.stderr).strip().splitlines()[-12:]))
    print("   (shown only; this section never decides the check)")


def main(argv: list[str]) -> int:
    quick = "--quick" in argv
    base = argv[argv.index("--base") + 1] if "--base" in argv and argv.index("--base") + 1 < len(argv) else "origin/main"
    ok = run_tests(quick)
    if not quick:
        ok = tests_untouched(base) and ok
        ok = extra_checks() and ok
        shown("lane: who decides this change (tools/checks/lane.py)", ["tools/checks/lane.py", "--base", base])
        shown("spend this month against the cap (tools/spend.py)", ["tools/spend.py", "status"])
    print(f"\n== check: {'GREEN' if ok else 'RED'}")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
