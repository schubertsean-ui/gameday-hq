#!/usr/bin/env python3
"""apps — the register of every outside app, connector and service (docs/APPS.yaml), held to account like a vendor list.

    python3 tools/apps.py check     exit 1 on a missing field, a paid app with no hard cap, a key that can write held by
                                    an AI session, or a write-capable app allowed where outside text is read
    python3 tools/apps.py due       the reviews that are due (exit 1 when any is); the weekly review does them
    python3 tools/apps.py list      one line per app
    python3 tools/apps.py canary    call each API's cheap canary through tools/api_client.py; exit 1 when a field the
                                    product reads has gone (the API changed under us) or the call failed

Why: every connector an AI holds can spend money or change something, and outside text (a web page, an email, an issue)
can try to give it instructions. So each app is written down once with the most it can do, who holds its key, its hard
spending cap at the provider, where its real usage is read, and what replaces it — and a check refuses the unsafe ones.
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "docs" / "APPS.yaml"
FIELDS = ("name", "kind", "used_for", "access", "key_held_by", "plan", "cap", "unit_cost", "usage_from", "fallback",
          "in_sessions_that_read_outside_text", "last_review", "next_review")
ACCESS = ("read", "write", "deploy", "admin")
KINDS = ("service", "connector", "api")
API_FIELDS = ("auth_scope", "rate_limit", "daily_call_limit", "key_rotation", "terms", "canary_url", "contract_fields")
HOLDERS = ("owner", "code-host-secret", "ai-session-read-only", "none")


def load() -> list[dict]:
    try:
        import yaml
    except ImportError:
        sys.exit("apps: PyYAML is not installed (pip install pyyaml)")
    if not REGISTER.is_file():
        sys.exit(f"apps: {REGISTER.relative_to(ROOT)} is missing — every outside app must be written down")
    return yaml.safe_load(REGISTER.read_text(encoding="utf-8")) or []


def as_date(v) -> dt.date | None:
    if isinstance(v, dt.date):
        return v
    try:
        return dt.date.fromisoformat(str(v))
    except ValueError:
        return None


def problems(apps: list[dict]) -> list[str]:
    out = []
    for a in apps:
        n = a.get("name", "<no name>")
        for f in FIELDS:
            if a.get(f) in (None, ""):
                out.append(f"{n}: `{f}` is empty")
        if a.get("kind") not in KINDS:
            out.append(f"{n}: kind must be one of {', '.join(KINDS)}")
        if a.get("kind") == "api":
            for f in API_FIELDS:
                if a.get(f) in (None, "", []):
                    out.append(f"{n}: an API needs `{f}`")
            if not isinstance(a.get("daily_call_limit"), int):
                out.append(f"{n}: daily_call_limit must be a number (0 when the provider states none)")
            if a.get("key_rotation") is not None and as_date(a.get("key_rotation")) is None:
                out.append(f"{n}: key_rotation must be a date")
        if a.get("access") not in ACCESS:
            out.append(f"{n}: access must be one of {', '.join(ACCESS)}")
        if a.get("key_held_by") not in HOLDERS:
            out.append(f"{n}: key_held_by must be one of {', '.join(HOLDERS)}")
        if a.get("access") in ("write", "deploy", "admin") and a.get("key_held_by") == "ai-session-read-only":
            out.append(f"{n}: a key that can {a['access']} is marked read-only — give the session a read-only key, or hold it elsewhere")
        if a.get("access") in ("deploy", "admin") and a.get("in_sessions_that_read_outside_text") is True:
            out.append(f"{n}: a {a['access']} key must never be in a session that reads outside text (prompt injection)")
        if a.get("key_held_by") == "code-host-secret" and a.get("in_sessions_that_read_outside_text") is True:
            out.append(f"{n}: a code-host secret is for the publishing run only, not for reading sessions")
        plan = str(a.get("plan", "")).lower()
        cap = str(a.get("cap", "")).lower()
        if plan not in ("free", "") and not any(c.isdigit() for c in cap) and "plan's own limit" not in cap:
            out.append(f"{n}: a paid app needs a hard cap with a number, set at the provider")
        if as_date(a.get("next_review")) is None or as_date(a.get("last_review")) is None:
            out.append(f"{n}: last_review and next_review must be dates (YYYY-MM-DD)")
    names = [a.get("name") for a in apps]
    out += [f"{n}: written down twice" for n in set(names) if names.count(n) > 1]
    return out


def pick(obj, path: str):
    """The values at a dotted path; `*` takes every item of a list. An empty list means the field has gone."""
    found = [obj]
    for part in path.split("."):
        nxt = []
        for o in found:
            if part == "*" and isinstance(o, list):
                nxt.extend(o)
            elif isinstance(o, dict) and part in o:
                nxt.append(o[part])
        found = nxt
    return found


def canary(apps: list[dict]) -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from api_client import CircuitOpen, call
    bad = 0
    for a in [x for x in apps if x.get("kind") == "api"]:
        key_env = a.get("key_env")
        try:
            r = call(a["name"], a["canary_url"], key_env=key_env, key_param=a.get("key_param"), retries=1, timeout=20)
        except (CircuitOpen, RuntimeError, OSError) as e:
            print(f"apps canary: {a['name']}: could not call ({e})"); bad += 1; continue
        if r.status != 200:
            print(f"apps canary: {a['name']}: answered {r.status}"); bad += 1; continue
        try:
            body = r.json()
        except ValueError:
            print(f"apps canary: {a['name']}: the answer is not JSON any more"); bad += 1; continue
        gone = [f for f in a.get("contract_fields", []) if not pick(body, f)]
        print(f"apps canary: {a['name']}: " + (f"CHANGED — gone: {', '.join(gone)}" if gone else "every field the product reads is there"))
        bad += bool(gone)
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    cmd = argv[0] if argv else "check"
    apps = load()
    if cmd == "canary":
        return canary(apps)
    if cmd == "list":
        for a in apps:
            print(f"{a.get('name'):<22} {a.get('access'):<6} key:{a.get('key_held_by'):<22} cap: {a.get('cap')}")
        return 0
    if cmd == "due":
        today = dt.date.today()
        due = [a for a in apps if (as_date(a.get("next_review")) or today) <= today]
        for a in due:
            print(f"apps: review due — {a.get('name')} (next_review {a.get('next_review')}): plan, cap, real usage, access, fallback")
        print(f"apps: {len(due)} review(s) due of {len(apps)}")
        return 1 if due else 0
    found = problems(apps)
    for p in found:
        print("apps:", p)
    print(f"apps: {len(apps)} app(s) written down, {len(found)} problem(s)")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
