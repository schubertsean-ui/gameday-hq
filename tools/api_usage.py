#!/usr/bin/env python3
"""api_usage — what the product's API calls really did, provider by provider, against each provider's limit.

    python3 tools/api_usage.py [--days 1] [--file data/api_usage.jsonl]

Reads the usage lines that tools/api_client.py writes for every call, and the limits in docs/APPS.yaml
(`daily_call_limit`). Prints, per provider: calls, share answered from cache, errors (429 and 5xx counted apart),
median and 95th-percentile time, and the day's calls against the limit. Exit 1 when a provider used more than 80% of
its daily limit or more than 5% of its calls failed — the weekly review turns that into a fault. Exit 3: no usage
recorded (could not tell). The publishing run prints this in its log and keeps the usage file as an artifact.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def limits() -> dict:
    path = ROOT / "docs" / "APPS.yaml"
    if not path.is_file():
        return {}
    import yaml
    return {a.get("name"): a.get("daily_call_limit") for a in (yaml.safe_load(path.read_text()) or []) if a.get("kind") == "api"}


def summarise(lines: list[dict], caps: dict, days: int) -> tuple[int, list[str]]:
    by: dict[str, list[dict]] = {}
    for line in lines:
        by.setdefault(line["provider"], []).append(line)
    code, out = 0, []
    for name, rows in sorted(by.items()):
        live = [r for r in rows if not r.get("cached")]
        cached = len(rows) - len(live)
        errors = [r for r in live if r["status"] == 0 or r["status"] >= 500]
        limited = [r for r in live if r["status"] == 429]
        ms = sorted(r["ms"] for r in live) or [0]
        p95 = ms[min(len(ms) - 1, int(0.95 * len(ms)))]
        per_day = len(live) / max(days, 1)
        cap = caps.get(name)
        share_failed = (len(errors) + len(limited)) / len(live) if live else 0
        flag = ""
        if cap and per_day > 0.8 * cap:
            flag, code = f"  OVER 80% of the daily limit ({cap})", 1
        if share_failed > 0.05:
            flag, code = flag + f"  {share_failed:.0%} FAILED", 1
        out.append(f"api_usage: {name}: {len(live)} calls ({cached} from cache, {cached / len(rows):.0%}), "
                   f"{len(limited)} rate-limited, {len(errors)} errors, median {statistics.median(ms):.0f} ms, "
                   f"p95 {p95} ms, {per_day:.0f}/day" + (f" of {cap}" if cap else "") + flag)
    return code, out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=1)
    ap.add_argument("--file", default=str(ROOT / "data" / "api_usage.jsonl"))
    a = ap.parse_args()
    path = Path(a.file)
    if not path.is_file():
        print("api_usage: no usage recorded (data/api_usage.jsonl is missing) — could not tell")
        return 3
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=a.days)
    lines = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    lines = [x for x in lines if dt.datetime.fromisoformat(x["t"]) >= since]
    code, out = summarise(lines, limits(), a.days)
    print("\n".join(out) if out else "api_usage: no calls in the window")
    return code


if __name__ == "__main__":
    sys.exit(main())
