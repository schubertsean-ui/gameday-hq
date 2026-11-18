#!/usr/bin/env python3
"""kit_drift — is this project on the newest version of the kit?

    python3 tools/kit_drift.py      exit 0 when current, 1 when the kit's home has a newer version, 3 when it could not tell

Reads KIT_VERSION here and KIT_VERSION on the main branch of the kit's home repository (kit.json "kit_home",
owner/name). When behind, read the home's CHANGELOG.md and bring the changes in: ordinary files in the next step's pull
request; protected files (tests, checks, hooks, kit.json) in a spec session the owner starts.
"""
from __future__ import annotations

import base64
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kitconf import CONF, ROOT  # noqa: E402


def version_tuple(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.strip().split(".") if x.isdigit())


def home_version(home: str) -> str | None:
    try:
        r = subprocess.run(["gh", "api", f"repos/{home}/contents/KIT_VERSION?ref=main"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    try:
        return base64.b64decode(json.loads(r.stdout)["content"]).decode().strip()
    except (ValueError, KeyError):
        return None


def main() -> int:
    here_file = ROOT / "KIT_VERSION"
    here = here_file.read_text().strip() if here_file.is_file() else ""
    home = CONF.get("kit_home") or ""
    if not here or not home or home.startswith("your-"):
        print(f"kit_drift: could not tell (KIT_VERSION here: {here or 'missing'}; kit_home in kit.json: {home or 'missing'})")
        return 3
    there = home_version(home)
    if there is None:
        print(f"kit_drift: could not read KIT_VERSION from {home} — could not tell")
        return 3
    if version_tuple(there) > version_tuple(here):
        print(f"kit_drift: BEHIND — this project runs kit {here}, {home} has {there}: read its CHANGELOG.md and bring the changes in")
        return 1
    print(f"kit_drift: current — kit {here} ({home} has {there})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
