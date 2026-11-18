#!/usr/bin/env python3
"""lane — which lane a change is in, and the merge gate the AI must pass before it merges its own pull request.

  python3 tools/checks/lane.py [--base origin/main]   this copy's change (commits and uncommitted files) against the base
  python3 tools/checks/lane.py --pr N                 the gate for pull request N on the code host (needs gh)

GREEN lane: the AI may merge by itself. RED lane: it never merges; the item waits for the owner in NEXT.md under
"Waiting on owner", and other green work goes on. A change is RED when it:
  - touches a path in kit.json "red_lane"."paths" (the harness, CI, settings, deploy config, secrets, migrations ...);
  - changes or deletes an existing test, fixture or check, or adds a test-runner config (tools/checks/tests_untouched.py);
  - lowers the test floor (raising it is green: python3 tools/checks/floor.py raise);
  - adds an app to docs/APPS.yaml, or changes an app's plan or cap (a new paid service or a new cost).
A green change can still be NOT YET: more changed lines than kit.json "auto_merge"."max_changed_lines" (split it). With
--pr it is also NOT YET until the required check ("checks") is green on the head commit and a reviewer that is not the
builder has commented (or reviewed) "REVIEW: PASS <head sha>" with a "reviewer-model:" line naming a model other than the PR body's
"builder-model:".
Exit 0: GREEN (with --pr: MERGE OK) · 4: RED, waits for the owner · 5: NOT YET · 3: NOT RUN (no base, no gh, no PR).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "hooks"))
sys.path.insert(0, str(ROOT / "tools" / "checks"))
from kitconf import CONF  # noqa: E402
from protect_tests import PROTECTED_NAMES, is_protected  # noqa: E402
from floor import read_floor  # noqa: E402

FLOOR_PATH = "tools/checks/test_floor.txt"
APPS_PATH = "docs/APPS.yaml"
GREEN, RED, NOT_YET, NOT_RUN = 0, 4, 5, 3


def glob_match(pattern: str, path: str) -> bool:
    """`**` = any folders (or none), `*` = anything but `/`, `?` = one character. A pattern without `/` matches a name anywhere."""
    if "/" not in pattern:
        pattern = "**/" + pattern
    rx, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            rx, i = rx + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            rx, i = rx + ".*", i + 2
        elif pattern[i] == "*":
            rx, i = rx + "[^/]*", i + 1
        elif pattern[i] == "?":
            rx, i = rx + "[^/]", i + 1
        else:
            rx, i = rx + re.escape(pattern[i]), i + 1
    return re.fullmatch(rx, path) is not None


def _apps(text: str | None) -> dict[str, tuple[str, str]]:
    try:
        data = yaml.safe_load(text or "") or []
    except yaml.YAMLError:
        return {"<unreadable docs/APPS.yaml>": ("", "")}
    return {str(a.get("name")): (str(a.get("plan", "")), str(a.get("cap", ""))) for a in data if isinstance(a, dict)}


def classify(changes: list[tuple[str, str, str]], base_text, head_text, changed_lines: int, conf: dict = CONF,
             exists_on_base=lambda p: True) -> tuple[int, list[str]]:
    """changes: (status A/M/D/R, old path, new path). base_text/head_text(path) -> file text or None."""
    red_paths = conf["red_lane"]["paths"]
    green_exc = set(conf["red_lane"].get("green_exceptions") or [])
    reasons: list[str] = []
    base_has_tests = exists_on_base("tests")
    for status, old, new in changes:
        for path in {old, new}:
            if path in green_exc:
                continue
            hit = next((p for p in red_paths if glob_match(p, path)), None)
            if hit:
                reasons.append(f"RED: {path} is a red-lane path ({hit})")
        if status in "MDR" and is_protected(old) and old not in green_exc and exists_on_base(old):
            reasons.append(f"RED: {old} is an existing test, fixture or check and this change {'deletes' if status == 'D' else 'alters'} it")
        if status == "A" and base_has_tests and new.rsplit("/", 1)[-1] in PROTECTED_NAMES:
            reasons.append(f"RED: {new} is a new test-runner config (it can switch tests off)")
    touched = {p for c in changes for p in c[1:]}
    if FLOOR_PATH in touched:
        before, after = read_floor(base_text(FLOOR_PATH) or "0"), read_floor(head_text(FLOOR_PATH) or "0")
        if after < before:
            reasons.append(f"RED: the test floor goes down ({before} -> {after}); only the owner lowers it")
    if APPS_PATH in touched:
        b, h = _apps(base_text(APPS_PATH)), _apps(head_text(APPS_PATH))
        for name in sorted(set(h) - set(b)):
            reasons.append(f"RED: {APPS_PATH} adds the app '{name}' (a new service needs the owner's yes)")
        for name in sorted(set(h) & set(b)):
            if h[name] != b[name]:
                reasons.append(f"RED: {APPS_PATH} changes the plan or cap of '{name}'")
    reasons = sorted(set(reasons))
    if reasons:
        return RED, reasons
    limit = int(conf["auto_merge"]["max_changed_lines"])
    if changed_lines > limit:
        return NOT_YET, [f"NOT YET: {changed_lines} changed lines; the green-lane limit is {limit} — split it"]
    return GREEN, [f"GREEN: {changed_lines} changed lines (limit {limit}); no red-lane path"]


def review_passed(comments: list[dict], head_sha: str, body: str, conf: dict = CONF) -> tuple[bool, str]:
    marker = conf["auto_merge"]["review_marker"]
    m = re.search(r"builder-model:\s*(\S+)", body or "", re.I)
    if not m:
        return False, "the pull request body does not say 'builder-model: <model>'"
    builder = m.group(1).lower()
    for c in comments:
        text = c.get("body") or ""
        r = re.search(r"reviewer-model:\s*(\S+)", text, re.I)
        sha = re.search(re.escape(marker) + r"\s+([0-9a-f]{7,40})", text)
        if sha and head_sha.startswith(sha.group(1)) and r and r.group(1).lower() != builder:
            return True, f"reviewed by {r.group(1)} at {sha.group(1)}"
    return False, f"no '{marker} <head sha>' comment from a reviewer-model other than {builder} for {head_sha[:7]}"


def checks_green(rollup: list[dict], name: str) -> tuple[bool, str]:
    mine = [c for c in rollup or [] if (c.get("name") or c.get("context")) == name]
    if not mine:
        return False, f"the required check '{name}' has not reported on the head commit"
    states = {(c.get("conclusion") or c.get("state") or "").upper() for c in mine}
    if states == {"SUCCESS"}:
        return True, f"'{name}' is green"
    return False, f"'{name}' is {', '.join(sorted(s or 'PENDING' for s in states))}"


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False)


def _excluded(path: str) -> bool:
    return any(glob_match(p, path) for p in CONF["auto_merge"].get("size_exclude") or [])


def local_change(base: str, head: str | None):
    rng = f"{base}...{head or 'HEAD'}"
    changes = []
    for line in git("diff", "--name-status", "-M", rng).stdout.splitlines():
        parts = line.split("\t")
        changes.append((parts[0][0], parts[1], parts[-1]))
    lines = 0
    numstats = [git("diff", "--numstat", "-M", rng).stdout]
    if head is None:  # uncommitted work counts too
        numstats.append(git("diff", "--numstat", "HEAD").stdout)
        for line in git("status", "--porcelain").stdout.splitlines():
            code, name = line[:2].strip() or "M", line[3:].split(" -> ")[-1].strip()
            changes.append(("A" if code == "??" else code[0], name, name))
            if code == "??" and (ROOT / name).is_file() and not _excluded(name):
                try:
                    lines += len((ROOT / name).read_text(encoding="utf-8").splitlines())
                except UnicodeDecodeError:
                    pass
    for out in numstats:
        for line in out.splitlines():
            a, d, path = line.split("\t", 2)
            if a != "-" and not _excluded(path.split(" => ")[-1].strip("{}")):
                lines += int(a) + int(d)

    def base_text(p: str):
        r = git("show", f"{base}:{p}")
        return r.stdout if r.returncode == 0 else None

    def head_text(p: str):
        if head is None:
            f = ROOT / p
            return f.read_text(encoding="utf-8") if f.is_file() else None
        r = git("show", f"{head}:{p}")
        return r.stdout if r.returncode == 0 else None

    def exists(p: str) -> bool:
        return git("cat-file", "-e", f"{base}:{p}").returncode == 0

    return sorted(set(changes)), base_text, head_text, lines, exists


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--pr", type=int)
    a = ap.parse_args(argv)
    head = None
    pr = None
    if a.pr is not None:
        fields = "number,url,headRefOid,baseRefName,statusCheckRollup,comments,reviews,body"
        r = subprocess.run(["gh", "pr", "view", str(a.pr), "--json", fields], cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"lane: could not read pull request {a.pr} with gh ({r.stderr.strip()[:200]}) — NOT RUN")
            return NOT_RUN
        pr = json.loads(r.stdout)
        f = git("fetch", "-q", "origin", f"+refs/heads/{pr['baseRefName']}:refs/kit/base", f"+refs/pull/{a.pr}/head:refs/kit/pr")
        if f.returncode != 0 or git("rev-parse", "refs/kit/pr").stdout.strip() != pr["headRefOid"]:
            print(f"lane: could not fetch pull request {a.pr} at its head {pr['headRefOid'][:7]} — NOT RUN")
            return NOT_RUN
        a.base, head = "refs/kit/base", "refs/kit/pr"
    if git("rev-parse", "--verify", "--quiet", a.base).returncode != 0:
        print(f"lane: base ref {a.base} not found — NOT RUN")
        return NOT_RUN
    changes, base_text, head_text, lines, exists = local_change(a.base, head)
    code, reasons = classify(changes, base_text, head_text, lines, CONF, exists)
    if pr is not None and code == GREEN:
        for ok, why in (checks_green(pr.get("statusCheckRollup"), CONF["auto_merge"]["required_check"]),
                        review_passed((pr.get("comments") or []) + (pr.get("reviews") or []), pr["headRefOid"], pr.get("body") or "")):
            reasons.append(("ok: " if ok else "NOT YET: ") + why)
            if not ok:
                code = NOT_YET
    for line in reasons:
        print("  ", line)
    word = {GREEN: "MERGE OK" if pr else "GREEN lane", RED: "RED lane — waits for the owner (NEXT.md, 'Waiting on owner')",
            NOT_YET: "NOT YET"}[code]
    print(f"lane: {word}" + (f" — {pr['url']} at {pr['headRefOid'][:7]}" if pr else ""))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
