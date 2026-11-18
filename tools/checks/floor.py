#!/usr/bin/env python3
"""floor — the test floor: the fewest tests a full check accepts (tools/checks/test_floor.txt). It only goes up.

  python3 tools/checks/floor.py            show the floor and how many tests are collected now
  python3 tools/checks/floor.py raise      set the floor to the number collected now, if that is higher (the one-line
                                           command to run after adding tests; green lane, no approval needed)
  python3 tools/checks/floor.py --install  the same, run by install-kit.sh so a fresh install is guarded at once

It never lowers the floor: lowering is the owner's call (red lane), made by hand in a pull request the owner merges.
Counting: kit.json "test_command" with --collect-only when it is pytest; otherwise (or when pytest cannot start) a
count of the test functions in tests/ read from the source, which is never more than pytest would collect.
Exit 0: done or shown · 2: refused (would lower) · 3: could not count.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True  # the installer runs this: it leaves no compiled files behind
sys.path.insert(0, str(ROOT / "tools"))
from kitconf import CONF  # noqa: E402

FLOOR_FILE = ROOT / "tools" / "checks" / "test_floor.txt"


def read_floor(text: str | None = None) -> int:
    if text is None:
        text = FLOOR_FILE.read_text(encoding="utf-8") if FLOOR_FILE.is_file() else "0"
    digits = re.sub(r"\D", "", text)
    return int(digits) if digits else 0


def static_count(folder: Path) -> int:
    """Test functions and methods in test_*.py / *_test.py, read from the source (parametrized cases count once)."""
    n = 0
    for path in sorted(list(folder.rglob("test_*.py")) + list(folder.rglob("*_test.py"))):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
                n += 1
            elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                n += sum(1 for f in node.body if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and f.name.startswith("test"))
    return n


def parse_collected(out: str) -> int | None:
    """The number from pytest's collect-only summary; None when collection had errors or there is no summary."""
    m = re.search(r"(\d+) tests? collected([^\n]*)", out) or re.search(r"collected (\d+) items?([^\n]*)", out)
    if m:
        return None if "error" in m.group(2) else int(m.group(1))
    if "no tests collected" in out and "error" not in out:
        return 0
    return None


def count() -> tuple[int | None, str]:
    cmd = CONF.get("test_command") or ""
    if "pytest" in cmd:
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        r = subprocess.run(cmd + " --collect-only", shell=True, cwd=ROOT, capture_output=True, text=True, env=env)
        n = parse_collected(r.stdout + r.stderr)
        if r.returncode in (0, 5) and n is not None:
            return n, "pytest --collect-only"
    tests = ROOT / "tests"
    if tests.is_dir():
        return static_count(tests), "test functions read from tests/ (pytest did not run)"
    return None, "no test command and no tests/ folder"


def main(argv: list[str]) -> int:
    floor = read_floor()
    n, how = count()
    if not argv or argv[0] in ("show", "--show"):
        print(f"floor: {floor} · collected now: {n if n is not None else 'could not count'} ({how})")
        return 0 if n is not None else 3
    if argv[0] not in ("raise", "--install"):
        print(__doc__)
        return 2
    if n is None:
        print(f"floor: could not count the tests ({how}); the floor stays {floor}. Run `python3 tools/checks/floor.py raise` once the tests run.")
        return 3
    if n > floor:
        FLOOR_FILE.parent.mkdir(parents=True, exist_ok=True)
        FLOOR_FILE.write_text(f"{n}\n", encoding="utf-8")
        print(f"floor: raised {floor} -> {n} ({how})")
    elif n < floor:
        print(f"floor: {n} tests now, below the floor of {floor}. Not lowered: tests have gone missing, or the owner "
              f"lowers it by hand (red lane).")
        return 2 if argv[0] == "raise" else 0
    else:
        print(f"floor: stays {floor} ({how})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
