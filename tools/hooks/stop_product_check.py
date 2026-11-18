#!/usr/bin/env python3
"""stop_product_check — a Stop hook: a session that changed the product ends on a green product check.

If product files changed in this working tree (uncommitted, or committed ahead of the base branch), run
`bash tools/check --quick`. Green: the session may end. Red: exit 2 with the tail of the output, which sends the agent
back to work. After MAX_BLOCKS consecutive red stops the hook lets the session end and writes CHECK_FAILED.txt at the
repository root (a tracked path, so it shows in the change). It never waits or loops itself.

This hook is a reminder for an honest agent, not a lock: a shell command can get around it. The judge is the same
check running on the code host, which the agent cannot reach.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from kitconf import CONF  # noqa: E402

PRODUCT = tuple(CONF["product_dirs"]) + tuple(CONF["protected_dirs"][:1])  # the product, and the tests that judge it
MAX_BLOCKS = 3


def git_dir() -> Path | None:
    r = subprocess.run(["git", "rev-parse", "--absolute-git-dir"], cwd=ROOT, capture_output=True, text=True, check=False)
    return Path(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else None


def sh(*cmd: str) -> str:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False).stdout


def base_ref() -> str:
    for ref in ("origin/main", "main"):
        if subprocess.run(["git", "rev-parse", "--verify", "--quiet", ref], cwd=ROOT, capture_output=True, check=False).returncode == 0:
            return ref
    return "HEAD"


def changed_product_files() -> list[str]:
    names = set(sh("git", "diff", "--name-only", f"{base_ref()}...HEAD").split())
    for line in sh("git", "status", "--porcelain").splitlines():
        names.add(line[3:].split(" -> ")[-1].strip())
    return sorted(n for n in names if n.startswith(PRODUCT) or n in PRODUCT)


def tree_fingerprint() -> str:
    h = hashlib.sha256()
    h.update(sh("git", "rev-parse", "HEAD").encode())
    h.update(sh("git", "diff", "HEAD").encode())
    h.update(sh("git", "status", "--porcelain").encode())
    for name in sh("git", "ls-files", "--others", "--exclude-standard").splitlines():
        f = ROOT / name
        if f.is_file():
            h.update(name.encode() + f.read_bytes())
    return h.hexdigest()


def main() -> int:
    try:
        json.load(sys.stdin)
    except Exception:  # noqa: BLE001
        pass
    git = git_dir()
    if git is None or not changed_product_files():
        return 0
    green, blocks, failed = git / "kit_check_green", git / "kit_stop_blocks", ROOT / "CHECK_FAILED.txt"
    fp = tree_fingerprint()
    if green.exists() and green.read_text().strip() == fp:
        return 0
    r = subprocess.run(["bash", "tools/check", "--quick"], cwd=ROOT, capture_output=True, text=True, check=False)
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        green.write_text(fp)
        blocks.unlink(missing_ok=True)
        failed.unlink(missing_ok=True)
        return 0
    try:
        n = int(blocks.read_text().strip() or 0) + 1 if blocks.exists() else 1
    except ValueError:
        n = 1
    blocks.write_text(str(n))
    tail = "\n".join(out.splitlines()[-40:])
    if n > MAX_BLOCKS:
        failed.write_text(f"The session ended with the product check RED after {MAX_BLOCKS} attempts.\n\n{tail}\n")
        blocks.unlink(missing_ok=True)
        print("stop_product_check: still RED after the block limit — ending the session with CHECK_FAILED.txt written. "
              "Say plainly in the final message that the check is failing.", file=sys.stderr)
        return 0
    print(f"stop_product_check: `bash tools/check --quick` is RED (attempt {n} of {MAX_BLOCKS}). Fix the product, not "
          f"the tests or the check (AGENTS.md rule 2).\n\n{tail}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        code = main()
    except Exception as e:  # noqa: BLE001 — a crash must not read as "the check passed"
        print(f"stop_product_check: the hook itself failed ({e!r}); run `bash tools/check --quick` by hand and report "
              f"its output.", file=sys.stderr)
        code = 2
    sys.exit(code)
