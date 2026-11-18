#!/usr/bin/env python3
"""session_start — a SessionStart hook: remember the commit this session began from.

Writes it to .git/kit_session_base. tools/hooks/protect_tests.py treats every test, fixture and check that exists at
that commit as protected for the rest of the session. Also clears the Stop hook's counters. Runs on startup only (not
on resume, clear or compact), so the base does not move mid-session.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def git_dir() -> Path | None:
    r = subprocess.run(["git", "rev-parse", "--absolute-git-dir"], cwd=ROOT, capture_output=True, text=True, check=False)
    return Path(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else None


def main() -> int:
    git = git_dir()
    if git is None:
        return 0
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False).stdout.strip()
    if head:
        (git / "kit_session_base").write_text(head)
    for name in ("kit_stop_blocks", "kit_check_green"):
        (git / name).unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
