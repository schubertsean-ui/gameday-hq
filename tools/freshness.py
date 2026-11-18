#!/usr/bin/env python3
"""freshness — how long ago was the live product last published? Fails when it is older than it should be.

    python3 tools/freshness.py                    one line; exit 0 when fresh, 1 when older than the limit
    python3 tools/freshness.py --max-hours 8      another limit (default: kit.json "max_age_hours")
    python3 tools/freshness.py --url https://...  another address (default: kit.json "live_url")

Why (Happening, 16 Nov 2026): a scheduled run was recorded as "switched on" and had never run; nobody looked. This asks
the product itself, so it does not depend on any run having reported anything.

How it tells: the `Last-Modified` time of the address (GitHub Pages, Netlify and most static hosts set it at each
publish). Where a host does not, publish a small file holding the publish time in ISO form (for example
/published.txt containing 2026-11-18T04:10:27Z) and name it in kit.json "stamp_url"; it is read when Last-Modified is
missing. Exit 3: could not tell — never "fresh".
"""
from __future__ import annotations

import argparse
import sys
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kitconf import CONF  # noqa: E402


def parse_time(text: Optional[str]) -> Optional[datetime]:
    if not text:
        return None
    text = text.strip()
    for parse in (parsedate_to_datetime, lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))):
        try:
            t = parse(text)
        except (TypeError, ValueError, IndexError):
            continue
        return t if t.tzinfo else t.replace(tzinfo=timezone.utc)
    return None


def verdict(published: Optional[datetime], shown: str, now: datetime, max_hours: float) -> tuple[int, str]:
    if published is None:
        return 3, "could not tell when it was last published (no usable Last-Modified time or stamp)"
    age = (now - published).total_seconds() / 3600
    line = f"last published {shown} — {age:.1f} hours ago (limit {max_hours:g})"
    return (0, "fresh: " + line) if age <= max_hours else (1, "STALE: " + line)


def fetch(url: str, method: str) -> tuple[Optional[str], str]:
    req = urllib.request.Request(url, method=method, headers={"User-Agent": "own-site-freshness-check"})
    with urllib.request.urlopen(req, timeout=20) as r:
        body = r.read(200).decode("utf-8", "replace") if method == "GET" else ""
        return r.headers.get("Last-Modified"), body


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=CONF.get("live_url"))
    ap.add_argument("--stamp", default=CONF.get("stamp_url"))
    ap.add_argument("--max-hours", type=float, default=float(CONF.get("max_age_hours") or 11))
    a = ap.parse_args()
    if not a.url:
        print("freshness: no address to ask (kit.json live_url is empty) — could not tell")
        return 3
    try:
        shown, _ = fetch(a.url, "HEAD")
        when = parse_time(shown)
        if when is None and a.stamp:
            _, body = fetch(a.stamp, "GET")
            shown, when = body.strip(), parse_time(body)
    except Exception as e:  # the site not answering is a result to report, not a crash
        print(f"freshness: {a.url} did not answer ({type(e).__name__}: {e})")
        return 3
    code, line = verdict(when, shown or "", datetime.now(timezone.utc), a.max_hours)
    print(f"freshness: {a.url} {line}")
    return code


if __name__ == "__main__":
    sys.exit(main())
