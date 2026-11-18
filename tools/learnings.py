#!/usr/bin/env python3
"""learnings — the lessons register (docs/LEARNINGS.md): every correction becomes a check, and the useful ones travel.

    python3 tools/learnings.py check   exit 1 when an entry lacks a line, or names a check file that does not exist
    python3 tools/learnings.py kit     the entries marked `kit: yes` that are not yet shipped in the kit (exit 0)

An entry is a `## YYYY-MM-DD — title` heading followed by four lines: What happened, Why, Now held by (a path in
backticks, or `none: <why no check can hold it>`), and kit (yes or no; "shipped in kit X" once it is in the kit).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "docs" / "LEARNINGS.md"
LINES = ("What happened", "Why", "Now held by", "kit")


def entries() -> list[dict]:
    if not FILE.is_file():
        return []
    out, cur = [], None
    for line in FILE.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## (\d{4}-\d{2}-\d{2}) — (.+)$", line)
        if m:
            cur = {"date": m.group(1), "title": m.group(2)}
            out.append(cur)
            continue
        m = re.match(r"^- \*\*(What happened|Why|Now held by|kit):\*\* ?(.*)$", line)
        if m and cur is not None:
            cur[m.group(1)] = m.group(2).strip()
    return out


def problems(items: list[dict]) -> list[str]:
    out = []
    for e in items:
        head = f"{e['date']} {e['title'][:50]}"
        for k in LINES:
            if not e.get(k):
                out.append(f"{head}: the line `{k}` is missing or empty")
        held = e.get("Now held by", "")
        if held and not held.startswith("none:"):
            paths = re.findall(r"`([^`]+)`", held)
            if not paths:
                out.append(f"{head}: `Now held by` names no file in backticks (or say `none: <why>`)")
            for p in paths:
                if not (ROOT / p).exists():
                    out.append(f"{head}: the check `{p}` does not exist — the lesson is not held by anything")
        if e.get("kit") and not re.match(r"^(yes|no)\b", e["kit"]):
            out.append(f"{head}: `kit` must start with yes or no")
    return out


def main(argv: list[str]) -> int:
    items = entries()
    if (argv[0] if argv else "check") == "kit":
        todo = [e for e in items if e.get("kit", "").startswith("yes") and "shipped in kit" not in e.get("kit", "")]
        for e in todo:
            print(f"kit candidate: {e['date']} — {e['title']} (held by {e.get('Now held by')})")
        print(f"learnings: {len(todo)} kit candidate(s) not yet shipped")
        return 0
    found = problems(items)
    for p in found:
        print("learnings:", p)
    print(f"learnings: {len(items)} entr(ies), {len(found)} problem(s)")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
