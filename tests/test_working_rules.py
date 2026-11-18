"""Working rules held as checks, not as paragraphs to be remembered ("every correction becomes a check").

  - the next step is one short line in NEXT.md, loaded into every session by CLAUDE.md; below it, "Waiting on owner"
    holds the red-lane items, each one short paragraph, never so many that the owner cannot read them in a minute
  - AGENTS.md and STATE.md cannot grow: a new line replaces an old one (git history holds the old one)
  - a change is never rules and records alone, unless the owner's dated words asked for it (OWNER_WORDS.md)
  - a change to the product moves the record of where things stand
The limits live in kit.json; each was the file's size on the day the check was added (Happening, 16–17 Nov 2026).
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from kitconf import CONF  # noqa: E402

LIM = CONF["limits"]
RULES_AND_RECORDS = tuple(CONF["rules_and_records"])
PRODUCT = tuple(CONF["product_dirs"])
WHERE_THINGS_STAND = tuple(CONF["where_things_stand"])


def _changed() -> list[str] | None:
    """Files this change touches against the code host's main; None when there is no main to compare with."""
    def git(*a: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, check=False)
    if git("rev-parse", "--verify", "--quiet", "origin/main").returncode != 0:
        assert os.environ.get("CI") != "true", "origin/main is missing on the code host, so this rule could not be checked"
        return None
    names = set(git("diff", "--name-only", "origin/main...HEAD").stdout.split())
    names |= {line[3:].split(" -> ")[-1].strip() for line in git("status", "--porcelain").stdout.splitlines()}
    return sorted(n for n in names if n)


def _is_rule_or_record(name: str) -> bool:
    return name.startswith(RULES_AND_RECORDS) or ("/" not in name and name.endswith(".md"))


def test_the_next_step_is_one_short_line_every_session_is_given():
    whole = (ROOT / "NEXT.md").read_text(encoding="utf-8")
    text, _, waiting = whole.partition("## Waiting on owner")
    text = text.strip()
    assert text and len(text) <= LIM["next_max_chars"], f"NEXT.md's next step is {len(text)} characters; the limit is {LIM['next_max_chars']}"
    assert len(text.splitlines()) <= LIM["next_max_lines"]
    items = [i.strip() for i in ("\n" + waiting).split("\n- ")[1:] if i.strip()]
    assert len(items) <= LIM["waiting_max_items"], f"{len(items)} items wait on the owner; the limit is {LIM['waiting_max_items']}"
    for item in items:
        assert len(item) <= LIM["waiting_item_max_chars"], f"a waiting item is {len(item)} characters: one plain paragraph"
    assert "@NEXT.md" in (ROOT / "CLAUDE.md").read_text(encoding="utf-8"), "CLAUDE.md no longer loads NEXT.md into the session"
    assert "@AGENTS.md" in (ROOT / "CLAUDE.md").read_text(encoding="utf-8"), "CLAUDE.md no longer loads AGENTS.md into the session"


def test_agents_md_and_state_md_do_not_grow():
    lines = (ROOT / "AGENTS.md").read_text(encoding="utf-8").splitlines()
    assert len(lines) <= LIM["agents_max_lines"], (
        f"AGENTS.md is {len(lines)} lines; the limit is {LIM['agents_max_lines']}. A correction becomes a check, or replaces a line")
    size = len((ROOT / "STATE.md").read_bytes())
    assert size <= LIM["state_max_bytes"], (
        f"STATE.md is {size} bytes; the limit is {LIM['state_max_bytes']}. A new line replaces an old one: the old one is in git")
    assert "Next step (" not in (ROOT / "STATE.md").read_text(encoding="utf-8"), "the next step lives in NEXT.md only"


def test_a_change_is_not_rules_and_records_alone():
    changed = _changed()
    if not changed:
        return
    if all(_is_rule_or_record(n) for n in changed):
        assert "OWNER_WORDS.md" in changed, (
            "this change is rules and records only, with no product, test or tool in it and no words of the owner's asking "
            "for it: " + ", ".join(changed[:8]))


def test_a_change_to_the_product_moves_the_record():
    changed = _changed()
    if not changed or not any(n.startswith(PRODUCT) for n in changed):
        return
    assert any(n in WHERE_THINGS_STAND for n in changed), (
        "the product changed but none of " + ", ".join(WHERE_THINGS_STAND) + " did: say where things now stand")
