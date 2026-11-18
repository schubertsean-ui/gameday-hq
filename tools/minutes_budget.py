#!/usr/bin/env python3
"""minutes_budget — how many GitHub Actions minutes this repository has used this month, and whether a run may start.

  python3 tools/minutes_budget.py --kind full|short [--limit N] [--repo owner/name]

Exit 0: the run may start. Exit 1: the run stands down. Exit 3: could not tell (the run goes ahead, so a broken count
never stops the product; the line says so). Under the limit every run may start. At or over it the full run stands
down until the month turns, and the short run starts only when the product is older than kit.json
"minutes.over_limit_short_run_after_hours" — so what people see now stays right.

Why (Happening, 18 Nov 2026): every merge started a full publishing run; one day used about 1,580 minutes and the month
passed the plan's 3,000, so the host billed or refused every job. The publishing workflows now ask this first. The
required check is not gated (merges need it), so the limit leaves it room. Counted from the runs list since the 1st of
the month: each run's minutes rounded up, plus one for its further jobs (a slight overcount). Needs the `gh` command
with a token that can read the repository's Actions (in a workflow: GH_TOKEN: ${{ github.token }} and
permissions: actions: read).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kitconf import CONF  # noqa: E402

M = CONF["minutes"]


def _api(path: str) -> Optional[dict]:
    try:
        r = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=60, env=os.environ.copy())
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except ValueError:
        return None


def _t(s: Optional[str]) -> Optional[dt.datetime]:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def run_minutes(runs: Iterable[dict]) -> int:
    total = 0
    for r in runs:
        a, b = _t(r.get("run_started_at")), _t(r.get("updated_at"))
        if a and b and b > a:
            total += math.ceil((b - a).total_seconds() / 60) + 1
    return total


def month_minutes(repo: str, now: dt.datetime) -> Optional[int]:
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d")
    total, page = 0, 1
    while page <= 20:
        runs = _api(f"repos/{repo}/actions/runs?per_page=100&page={page}&created=>={start}")
        if runs is None:
            return None
        rows = runs.get("workflow_runs") or []
        total += run_minutes(rows)
        if len(rows) < 100:
            return total
        page += 1
    return total


def product_age_hours() -> Optional[float]:
    r = subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "freshness.py"), "--max-hours", "0"],
                       capture_output=True, text=True, check=False)
    if r.returncode == 3:
        return None
    try:
        return float(r.stdout.split(" hours ago")[0].rsplit("— ", 1)[1])
    except (IndexError, ValueError):
        return None


def decide(kind: str, used: Optional[int], limit: int, age: Optional[float]) -> tuple[int, str]:
    if used is None:
        return 3, f"minutes_budget: could not tell how many minutes were used this month — the run goes ahead (limit {limit})"
    head = f"minutes_budget: {used} minutes used this month, limit {limit} (plan {M['plan_minutes']})"
    if used < limit:
        return 0, head + " — the run goes ahead"
    after = M["over_limit_short_run_after_hours"]
    if kind == "short" and (age is None or age >= after):
        return 0, head + (" — over it, but the product's age could not be read: the short run goes ahead" if age is None
                          else f" — over it, but the product is {age:.1f} hours old: the short run keeps it right")
    return 1, head + f" — over it: this {kind} run stands down" + (" until the month turns" if kind == "full" else f" until the product is {after} hours old")


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["short", "full"], required=True)
    ap.add_argument("--limit", type=int, default=int(os.environ.get("KIT_MINUTES_LIMIT") or M["limit"]))
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY") or CONF.get("repo"))
    a = ap.parse_args(argv)
    used = month_minutes(a.repo, dt.datetime.now(dt.timezone.utc)) if a.repo else None
    code, line = decide(a.kind, used, a.limit, product_age_hours() if used is not None and used >= a.limit else None)
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
