#!/usr/bin/env python3
"""stranded — which branches on the code host hold work that never reached `main`.

Why (Happening, 16 Nov 2026): six branches were found holding work that had been pushed and never merged, among them
the owner's own words and the lawyer list. A session's work is saved only when it is on `main`.

For every branch on the remote it counts the changes `main` does not have (a change `main` holds under another commit
does not count). A branch tip listed in tools/stranded_settled.txt has been looked at and settled; a new push to that
branch moves its tip, and it is counted again.

Exit 0: nothing stranded. Exit 1: something is. Exit 3: could not tell (never a pass).
    python3 tools/stranded.py            asks the remote first
    python3 tools/stranded.py --no-fetch uses what is already here
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SETTLED = ROOT / "tools" / "stranded_settled.txt"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def settled() -> dict[str, str]:
    out = {}
    if SETTLED.exists():
        for line in SETTLED.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                sha, _, why = line.partition(" ")
                out[sha] = why.strip()
    return out


def deepen() -> None:
    """A shallow copy hides where a branch left main, and every old branch then looks stranded."""
    if git("rev-parse", "--is-shallow-repository").strip() != "true":
        return
    try:
        git("fetch", "-q", "--unshallow", "origin")
    except subprocess.CalledProcessError:  # some hosts refuse --unshallow; a bounded fetch is usually allowed
        git("fetch", "-q", "--depth=1000", "origin")


def main() -> int:
    try:
        if "--no-fetch" not in sys.argv:
            deepen()
            git("fetch", "-q", "--prune", "origin", "+refs/heads/*:refs/remotes/origin/*")
        refs = git("for-each-ref", "--format=%(refname:short) %(objectname)", "refs/remotes/origin").splitlines()
        done = settled()
        found = []
        for ref in refs:
            name, _, sha = ref.partition(" ")
            if name in ("origin", "origin/HEAD", "origin/main") or sha in done:
                continue
            missing = [line for line in git("cherry", "origin/main", name).splitlines() if line.startswith("+")]
            if missing:
                when = git("log", "-1", "--format=%cd", "--date=format:%d %b %H:%M", name).strip()
                found.append((name.removeprefix("origin/"), len(missing), when, sha[:7]))
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"stranded: could not tell — {getattr(e, 'stderr', '') or e}".strip())
        return 3
    if not found:
        print("stranded: none — every pushed change is on main or settled")
        return 0
    print(f"stranded: {len(found)} branch(es) hold work that is not on main")
    for name, n, when, sha in sorted(found):
        print(f"  {n:>3} change(s) · last push {when} · {name} ({sha})")
    return 1


if __name__ == "__main__":
    sys.exit(main())
