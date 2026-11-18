# LEARNINGS.md — what went wrong or right, and the check that now holds it (newest first)

One entry per lesson, written the day it happens, blameless: what happened, not who. `python3 tools/learnings.py check`
refuses an entry with a missing line, or one that names a check file that does not exist. An entry marked `kit: yes`
would help every project: the kit-improvement review carries it to the kit's home repository, so the next project
starts with it. Keep entries short; the git history and the linked pull request hold the detail.

## 2026-11-18 — Python's cache folders counted as a product change
- **What happened:** the rule "a product change must update STATE.md" fired on `__pycache__/` folders the tests had written.
- **Why:** generated files were not ignored by git.
- **Now held by:** `tests/test_working_rules.py` (with `.gitignore`)
- **kit:** yes — shipped in kit 1.0.0

## 2026-11-18 — a same-second edit was judged from stale compiled code
- **What happened:** a test passed after a product file was broken and restored within one second.
- **Why:** Python reused compiled code whose source time and size had not changed.
- **Now held by:** `tools/checks/check.py` (writes no compiled files during the check)
- **kit:** yes — shipped in kit 1.0.0
