"""The session guards themselves are under test. Every case is a fault that really happened, or its direct opposite:
  - a hook started by a path relative to the working directory refused EVERY tool call after one `cd`
    (python3 exits 2 for a file it cannot open; Claude Code reads exit 2 as "block"), and the session died;
  - hook messages pointed at rules that no longer existed;
  - the guard on tests must still block from a subfolder.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = json.loads((ROOT / ".claude" / "settings.json").read_text())
SPEC_ENV = json.loads((ROOT / "kit.json").read_text()).get("spec_session_env", "SPEC_SESSION")


def _hook_commands() -> list[tuple[str, str]]:
    return [(event, hook["command"]) for event, groups in SETTINGS["hooks"].items() for g in groups for hook in g["hooks"]]


def _run(command: str, cwd: Path, payload: dict, project_dir: str | None) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PROJECT_DIR", SPEC_ENV)}
    if project_dir is not None:
        env["CLAUDE_PROJECT_DIR"] = project_dir
    return subprocess.run(["sh", "-c", command], cwd=cwd, input=json.dumps(payload), capture_output=True, text=True, env=env, check=False)


HARMLESS = {"tool_name": "Bash", "tool_input": {"command": "ls"}}
PRE_TOOL = [c for e, c in _hook_commands() if e == "PreToolUse"]


def test_there_are_hooks_to_test():
    assert len(PRE_TOOL) >= 1 and len(_hook_commands()) >= 3


@pytest.mark.parametrize("command", PRE_TOOL)
@pytest.mark.parametrize("where", ["root", "subfolder"])
@pytest.mark.parametrize("with_project_dir", [True, False])
def test_a_harmless_call_passes_from_any_folder(command, where, with_project_dir):
    cwd = {"root": ROOT, "subfolder": ROOT / "tools"}[where]
    r = _run(command, cwd, HARMLESS, str(ROOT) if with_project_dir else None)
    assert r.returncode == 0, f"{command!r} from {cwd}: exit {r.returncode}: {r.stderr}"


@pytest.mark.parametrize("command", [c for _, c in _hook_commands()])
def test_no_hook_blocks_when_it_cannot_be_found(command, tmp_path):
    r = _run(command, tmp_path, HARMLESS, None)
    assert r.returncode != 2, f"{command!r} blocks when it cannot find itself: {r.stderr}"
    r = _run(command, tmp_path, HARMLESS, str(tmp_path / "not-a-repository"))
    assert r.returncode != 2, f"{command!r} blocks when CLAUDE_PROJECT_DIR is wrong: {r.stderr}"


def test_every_hook_command_goes_through_the_launcher_and_names_a_real_file():
    for _, command in _hook_commands():
        assert "tools/hooks/run" in command, f"{command!r} does not use tools/hooks/run"
        name = command.split()[-1].strip("\"'")
        assert (ROOT / "tools" / "hooks" / name).is_file(), f"{command!r} names a hook that does not exist"


def test_the_test_guard_still_blocks_from_a_subfolder():
    command = next(c for c in PRE_TOOL if "protect_tests" in c)
    payload = {"tool_name": "Edit", "tool_input": {"file_path": str(ROOT / "tools" / "check")}}
    r = _run(command, ROOT / "tools", payload, None)
    assert r.returncode == 2 and "tools/check" in r.stderr


def test_hook_messages_name_a_rule_that_exists():
    agents = (ROOT / "AGENTS.md").read_text()
    assert "rule 2" in (ROOT / "tools" / "hooks" / "protect_tests.py").read_text()
    assert "2. One check fails" in agents, "the hooks cite AGENTS.md rule 2; it must still be rule 2"
