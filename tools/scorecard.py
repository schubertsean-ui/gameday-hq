#!/usr/bin/env python3
"""scorecard — the weekly numbers a Google or Cursor engineering lead would read, measured, never estimated.

    python3 tools/scorecard.py [--days 7] [--write docs/SCORECARD.md] [--offline]

Delivery (the four DORA measures): how often the product was published; how long a change took from pull request to
merge; what share of changes broke `main` (the post-merge check failed); how long a fault took from found to fixed on
the live product. Quality: orders passing on the live product, faults open, freshness. Cost: CI minutes this month and
the providers' own bills (docs/SPEND.yaml, one line per provider per month, copied from the bill). Each is compared with
its target in kit.json "slos": a missed target is an error budget spent, and reliability work comes first.
--offline skips the code host (useful in a test or without a token); those lines then say "not measured".
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kitconf import CONF, ROOT  # noqa: E402


def t(s: Optional[str]) -> Optional[dt.datetime]:
    if not s:
        return None
    s = str(s)
    if len(s) == 10:
        s += "T00:00:00Z"
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def gh(path: str) -> Optional[dict | list]:
    try:
        r = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except ValueError:
        return None


# ---------------------------------------------------------------- the measures (pure, so they can be tested)

def lead_time_hours(prs: list[dict], since: dt.datetime) -> Optional[float]:
    hours = [(t(p["merged_at"]) - t(p["created_at"])).total_seconds() / 3600
             for p in prs if p.get("merged_at") and t(p["merged_at"]) >= since]
    return statistics.median(hours) if hours else None


def deploys(runs: list[dict], since: dt.datetime) -> int:
    return sum(1 for r in runs if r.get("conclusion") == "success" and t(r.get("created_at")) >= since)


def change_failure_rate(check_runs: list[dict], since: dt.datetime) -> Optional[float]:
    on_main = [r for r in check_runs if r.get("event") == "push" and r.get("head_branch") == "main"
               and r.get("conclusion") in ("success", "failure") and t(r.get("created_at")) >= since]
    return sum(r["conclusion"] == "failure" for r in on_main) / len(on_main) if on_main else None


def restore_hours(orders: list[dict], seen: dict, since: dt.datetime) -> Optional[float]:
    hours = []
    for o in orders:
        s = seen.get(o.get("id"), {})
        if o.get("kind") == "fault" and s.get("pass") and o.get("found") and t(s.get("at")) and t(s["at"]) >= since:
            hours.append((t(s["at"]) - t(o["found"])).total_seconds() / 3600)
    return statistics.median(hours) if hours else None


def pass_rate(orders: list[dict], seen: dict) -> Optional[float]:
    return sum(bool(seen.get(o.get("id"), {}).get("pass")) for o in orders) / len(orders) if orders else None


def spend(month: str) -> tuple[float, list[str]]:
    path = ROOT / "docs" / "SPEND.yaml"
    if not path.is_file():
        return 0.0, []
    import yaml
    rows = [r for r in (yaml.safe_load(path.read_text(encoding="utf-8")) or []) if str(r.get("month")) == month]
    return sum(float(r.get("amount", 0)) for r in rows), [f"{r.get('provider')} {r.get('amount')} ({r.get('source')})" for r in rows]


# ---------------------------------------------------------------- the card

def fmt(v, unit="", pct=False) -> str:
    if v is None:
        return "not measured"
    return f"{v:.0%}" if pct else f"{v:.1f}{unit}" if isinstance(v, float) else f"{v}{unit}"


def met(v, target, lower_is_better=True) -> str:
    if v is None:
        return "—"
    return "yes" if (v <= target if lower_is_better else v >= target) else "NO"


def card(days: int, offline: bool) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    since = now - dt.timedelta(days=days)
    slo, repo = CONF["slos"], CONF.get("repo") or ""
    prs = runs = checks = []
    if not offline and repo:
        prs = gh(f"repos/{repo}/pulls?state=closed&per_page=100&sort=updated&direction=desc") or []
        runs = (gh(f"repos/{repo}/actions/workflows/{CONF['publish_workflow']}.yml/runs?per_page=100") or {}).get("workflow_runs", [])
        checks = (gh(f"repos/{repo}/actions/workflows/{CONF['check_workflow']}.yml/runs?per_page=100") or {}).get("workflow_runs", [])
    import orders as orders_tool  # the kit's own work orders
    orders, seen = orders_tool.load_orders(), orders_tool.seen()
    open_faults = sum(orders_tool.is_open(o, seen) for o in orders)
    lt = lead_time_hours(prs, since) if prs else None
    dep = deploys(runs, since) if runs else None
    cfr = change_failure_rate(checks, since) if checks else None
    rt = restore_hours(orders, seen, since)
    pr_ = pass_rate(orders, seen)
    fresh = subprocess.run([sys.executable, str(ROOT / "tools" / "freshness.py")], capture_output=True, text=True).stdout.strip()
    total, lines = spend(now.strftime("%Y-%m"))
    minutes = None
    if not offline and repo:
        import minutes_budget
        minutes = minutes_budget.month_minutes(repo, now)
    rows = [
        ("Delivery", "Published to the live product", fmt(dep, " runs"), "—", "—"),
        ("Delivery", "Lead time, pull request to merge (median)", fmt(lt, " h"), f"≤ {slo['lead_time_hours']} h", met(lt, slo["lead_time_hours"])),
        ("Delivery", "Changes that broke main (post-merge check)", fmt(cfr, pct=True), f"≤ {slo['change_failure_rate']:.0%}", met(cfr, slo["change_failure_rate"])),
        ("Delivery", "Fault found to fixed on the live product (median)", fmt(rt, " h"), f"≤ {slo['restore_hours']} h", met(rt, slo["restore_hours"])),
        ("Quality", "Orders passing on the live product", fmt(pr_, pct=True), f"≥ {slo['orders_pass_rate']:.0%}", met(pr_, slo["orders_pass_rate"], False)),
        ("Quality", "Faults open", str(open_faults), "0", "yes" if open_faults == 0 else "NO"),
        ("Quality", "Freshness", fresh or "not measured", f"≤ {slo['freshness_hours']} h", "yes" if fresh.startswith("freshness:") and "fresh:" in fresh else "NO"),
        ("Cost", "CI minutes this month", fmt(minutes, " min"), f"≤ {CONF['minutes']['limit']}", met(minutes, CONF["minutes"]["limit"])),
        ("Cost", "Provider bills this month (docs/SPEND.yaml)", f"${total:,.2f}" if lines else "not entered", "—", "—"),
    ]
    out = [f"# Scorecard — {CONF.get('project')} — {now:%Y-%m-%d} (last {days} days)", "",
           "| Area | Measure | Value | Target | Met |", "| --- | --- | --- | --- | --- |"]
    out += [f"| {a} | {m} | {v} | {tg} | {ok} |" for a, m, v, tg, ok in rows]
    missed = [m for _, m, _, _, ok in rows if ok == "NO"]
    out += ["", f"**Targets missed:** {', '.join(missed) if missed else 'none'}. A missed target comes before new work.",
            "", "**Bills:** " + ("; ".join(lines) if lines else "none entered for this month (copy each provider's figure into docs/SPEND.yaml)")]
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--write")
    ap.add_argument("--offline", action="store_true")
    a = ap.parse_args()
    text = card(a.days, a.offline)
    if a.write:
        (ROOT / a.write).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
