"""The operating registers are held by tests: the app register is safe, every lesson names a real check, and the
scorecard's measures compute what they say. Added in kit 1.1.0."""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import apps  # noqa: E402
import learnings  # noqa: E402
import scorecard  # noqa: E402


def test_the_app_register_has_no_unsafe_or_empty_entry():
    found = apps.problems(apps.load())
    assert not found, "docs/APPS.yaml: " + "; ".join(found)


def test_the_app_check_refuses_what_it_must():
    base = {"name": "X", "kind": "service", "used_for": "u", "access": "read", "key_held_by": "owner", "plan": "free", "cap": "free tier",
            "unit_cost": "c", "usage_from": "u", "fallback": "f", "in_sessions_that_read_outside_text": False,
            "last_review": "2026-11-18", "next_review": "2026-12-18"}
    assert apps.problems([base]) == []
    assert apps.problems([{**base, "access": "deploy", "in_sessions_that_read_outside_text": True}])
    assert apps.problems([{**base, "access": "write", "key_held_by": "ai-session-read-only"}])
    assert apps.problems([{**base, "plan": "Pro", "cap": "none"}])
    assert apps.problems([{**base, "fallback": ""}])
    assert apps.problems([{**base, "kind": "api"}])                       # an API without its limits, canary and terms
    api = {**base, "kind": "api", "auth_scope": "read", "rate_limit": "5/s", "daily_call_limit": 5000, "key_rotation": "2027-01-01",
           "terms": "t", "canary_url": "https://x", "contract_fields": ["a.b"]}
    assert apps.problems([api]) == []
    assert apps.pick({"a": [{"b": 1}, {"b": 2}]}, "a.*.b") == [1, 2] and apps.pick({"a": {}}, "a.b") == []


def test_every_lesson_names_a_check_that_exists():
    found = learnings.problems(learnings.entries())
    assert not found, "docs/LEARNINGS.md: " + "; ".join(found)


def test_the_scorecard_measures():
    since = dt.datetime(2026, 11, 1, tzinfo=dt.timezone.utc)
    prs = [{"created_at": "2026-11-10T00:00:00Z", "merged_at": "2026-11-10T02:00:00Z"},
           {"created_at": "2026-11-10T00:00:00Z", "merged_at": "2026-11-10T06:00:00Z"},
           {"created_at": "2026-10-01T00:00:00Z", "merged_at": "2026-10-01T09:00:00Z"},   # before the window
           {"created_at": "2026-11-11T00:00:00Z", "merged_at": None}]                      # closed, not merged
    assert scorecard.lead_time_hours(prs, since) == 4.0
    runs = [{"conclusion": "success", "created_at": "2026-11-12T00:00:00Z"}, {"conclusion": "failure", "created_at": "2026-11-12T00:00:00Z"}]
    assert scorecard.deploys(runs, since) == 1
    checks = [{"event": "push", "head_branch": "main", "conclusion": c, "created_at": "2026-11-12T00:00:00Z"} for c in ("success", "success", "success", "failure")]
    checks.append({"event": "pull_request", "head_branch": "x", "conclusion": "failure", "created_at": "2026-11-12T00:00:00Z"})
    assert scorecard.change_failure_rate(checks, since) == 0.25
    orders = [{"id": "A.1", "kind": "fault", "found": "2026-11-10"}, {"id": "A.2", "kind": "build"}]
    seen = {"A.1": {"pass": True, "at": "2026-11-11T06:00Z"}, "A.2": {"pass": False}}
    assert scorecard.restore_hours(orders, seen, since) == 30.0
    assert scorecard.pass_rate(orders, seen) == 0.5
