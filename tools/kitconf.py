#!/usr/bin/env python3
"""kitconf — reads kit.json, the one settings file for the kit's tools, from the repository root.

Every tool in tools/ imports this so that the project's own values (its live address, its product folders, its test
command, its limits) live in one place. A missing kit.json falls back to the defaults below; a broken one stops with
a plain message, never a silent default.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEFAULTS = {
    "project": "My Project",
    "repo": "",
    "live_url": "",
    "stamp_url": "",
    "max_age_hours": 11,
    "product_dirs": ["src/", "app/", "site/"],
    "test_command": "python3 -m pytest -q -p no:cacheprovider tests",
    "quick_test_command": "python3 -m pytest -q -x -p no:cacheprovider tests",
    "extra_checks": [],
    "protected_dirs": ["tests/", "fixtures/", "tools/checks/", "tools/hooks/"],
    "protected_files": ["kit.json", "tools/check", ".github/workflows/checks.yml", ".github/CODEOWNERS", ".claude/settings.json"],
    "protected_names": ["conftest.py", "pytest.ini", "tox.ini", "setup.cfg"],
    "spec_session_env": "SPEC_SESSION",
    "limits": {"agents_max_lines": 100, "state_max_bytes": 20000, "next_max_chars": 700, "next_max_lines": 3,
               "waiting_max_items": 10, "waiting_item_max_chars": 1200},
    "rules_and_records": ["docs/", ".claude/", "tools/hooks/", "tools/checks/", "tools/check", "prompts/"],
    "where_things_stand": ["NEXT.md", "STATE.md"],
    "minutes": {"plan_minutes": 3000, "limit": 2400, "over_limit_short_run_after_hours": 10},
    "kit_home": "",
    "slos": {"freshness_hours": 11, "orders_pass_rate": 0.99, "lead_time_hours": 24, "change_failure_rate": 0.15, "restore_hours": 24},
    "publish_workflow": "publish",
    "check_workflow": "checks",
    "owner": "",
    "owner_github": "",
    "monthly_cap_usd": 50,
    "spend_warn_at": 0.8,
    "spend": {"ledger": "docs/SPEND_LEDGER.yaml", "bills": "docs/SPEND.yaml"},
    "auto_merge": {"max_changed_lines": 400, "size_exclude": ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "*.lock"],
                   "review_marker": "REVIEW: PASS", "required_check": "checks"},
    "red_lane": {"paths": [".github/**", "tools/check", "tools/checks/**", "tools/hooks/**", ".claude/hooks/**",
                           ".claude/settings.json", "kit.json", "AGENTS.md", "CLAUDE.md", "GEMINI.md", "**/migrations/**", "migrations/**",
                           "**/*.sql", ".env", "**/.env*"],
                 "green_exceptions": ["tools/checks/test_floor.txt"]},
    "roles": {},
}


def load() -> dict:
    data = json.loads(json.dumps(DEFAULTS))
    path = ROOT / "kit.json"
    if path.is_file():
        try:
            mine = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as e:
            sys.exit(f"kit.json could not be read ({e}); fix it before any tool can run")
        for key, value in mine.items():
            if isinstance(value, dict) and isinstance(data.get(key), dict):
                data[key].update(value)
            else:
                data[key] = value
    return data


CONF = load()
