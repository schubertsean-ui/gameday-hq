#!/usr/bin/env python3
"""protect_tests — a PreToolUse hook for Edit/Write/MultiEdit/NotebookEdit: the builder may not edit its own examiner.

Blocks (exit 2) a direct edit to a protected file that already existed when the session began: existing tests and
fixtures, the checks themselves, the hooks, the workflow that runs the check, kit.json and the test-runner config
(the lists are in kit.json). New test files may be created freely: that is how test-first work happens.

A session that is meant to change tests or checks (a "spec session") is started by a person with SPEC_SESSION=1 (the
name is kit.json's "spec_session_env") in the environment of the AI tool itself. An agent cannot set that from inside
a session, because hooks read the environment of the tool's process, not of its shell commands.

This hook is a reminder for an honest agent, not a lock: it cannot see edits made through shell commands.
tools/checks/tests_untouched.py catches those when the check runs on the code host, where the agent cannot reach.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from kitconf import CONF  # noqa: E402

PROTECTED_DIRS = tuple(CONF["protected_dirs"])
PROTECTED_FILES = tuple(CONF["protected_files"])
PROTECTED_NAMES = tuple(CONF["protected_names"])  # test-runner config is protected wherever it sits
MIX_EXEMPT: tuple[str, ...] = ()                   # files a tool rewrites alongside product work (Happening: screens.json)


def git_dir() -> Path | None:
    r = subprocess.run(["git", "rev-parse", "--absolute-git-dir"], cwd=ROOT, capture_output=True, text=True, check=False)
    return Path(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else None


def is_protected(rel: str) -> bool:
    return (rel in PROTECTED_FILES or any(rel.startswith(d) for d in PROTECTED_DIRS)
            or rel.rsplit("/", 1)[-1] in PROTECTED_NAMES)


def base_ref() -> str:
    g = git_dir()
    marker = (g / "kit_session_base") if g else None
    if marker is not None and marker.is_file() and marker.read_text().strip():
        return marker.read_text().strip()
    return "HEAD"


def exists_on_base(rel: str) -> bool:
    r = subprocess.run(["git", "cat-file", "-e", f"{base_ref()}:{rel}"], cwd=ROOT, capture_output=True, check=False)
    return r.returncode == 0


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception as e:  # noqa: BLE001
        print(f"protect_tests: unreadable payload ({e}); blocking to be safe", file=sys.stderr)
        return 2
    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not path:
        return 0
    try:
        rel = str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return 0  # outside the repository
    name = rel.rsplit("/", 1)[-1]
    creates_runner_config = name in PROTECTED_NAMES and not exists_on_base(rel)
    if not is_protected(rel) or (not exists_on_base(rel) and not creates_runner_config):
        return 0
    if os.environ.get(CONF["spec_session_env"]) == "1":
        return 0
    print(f"protect_tests: {rel} is an existing test, fixture or check. A build session may not change it "
          f"(AGENTS.md rule 2). If the test is wrong, stop and say why; changing it is a separate spec session "
          f"that a person starts with {CONF['spec_session_env']}=1.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
