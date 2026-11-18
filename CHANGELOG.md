# Kit changelog — newest first

Each version says what changed, why (the lesson behind it, from a project's `docs/LEARNINGS.md`), and which files a
project must bring in. Protected files (tests, checks, hooks, `kit.json`) come in through a spec session the owner starts.

## 1.1.1 — 18 Nov 2026
- **Changed — who decides (the owner's words of 18 Nov 2026, in `OWNER_WORDS.md`):** the AI no longer decides
  everything, and the owner does not approve every step. Two lanes in `AGENTS.md`: green (branches, commits, draft
  pull requests, tests, docs, refactors, features, fixes; the AI merges its own pull request when the check is green,
  a reviewer of another model passed it, and `tools/checks/lane.py --pr` says MERGE OK) and red (spend past the cap or a
  new paid service, production data and deploy settings, secrets, repo settings, the harness, legal, public posts,
  messages to people, force-push): it waits in `NEXT.md` under "Waiting on owner" while green work goes on. A morning
  summary in `STATE.md`. `.github/CODEOWNERS` now owns exactly the red-lane paths, so new tests no longer wait for the
  owner.
- **Added:** `tools/checks/lane.py` (the red-lane paths, existing tests changed, the floor lowered, a new paid app, the
  size limit; with `--pr` also the required check and the reviewer's pass), shown in `bash tools/check`;
  `tools/checks/floor.py` (the installer sets the test floor to the tests collected at install; `floor.py raise` after
  adding tests; it never lowers); `tools/spend.py` and `docs/SPEND_LEDGER.yaml` (every paid run logged before and after;
  exit 2 at the cap, a warning from 80%); `.claude/agents/reviewer.md`, `prompts/reviewer-brief.md`, `GEMINI.md`;
  `tests/test_lanes_and_spend.py`.
- **Changed:** `kit.json` gains `owner`, `owner_github`, `monthly_cap_usd` (50), `spend_warn_at`, `spend`,
  `auto_merge`, `red_lane` and `roles` (a model and vendor per role, defaults to revisit); `AGENTS.md` is the
  vendor-neutral rulebook and `CLAUDE.md`, `GEMINI.md` and `.claude/agents/` point at it; raising the test floor is no
  longer a spec change in `tools/checks/tests_untouched.py`; `NEXT.md` gains "Waiting on owner" (its own limits).
- **Why:** on a fresh 1.1.0 install the floor was 0, so deleting a test file left the check GREEN; the rules said the
  AI merges anything on green, including the harness; nothing counted money against a cap.
- **Bring in:** every file above; protected files (`kit.json`, `tests/`, `tools/checks/`, `.github/`) through a
  red-lane pull request the owner merges.

## 1.1.0 — 18 Nov 2026
- **Added — running it like Google and Cursor:** `docs/APPS.yaml` and `tools/apps.py` (every outside app with its most
  powerful access, who holds the key, a hard cap at the provider, where real usage is read, a fallback, review dates;
  unsafe entries refused); `tools/scorecard.py` (the four delivery measures, quality, freshness and cost against targets
  in `kit.json` "slos"); `docs/SPEND.yaml` (bills, copied from the bill); `.github/workflows/revert-on-red.yml` (a red
  post-merge check opens a revert pull request at once).
- **Added — APIs to other apps:** `tools/api_client.py` (the one way the product calls an API: timeout, retries only on
  429 and 5xx honouring `Retry-After`, a circuit breaker per provider, a cache, one usage line per call, keys only from
  the secret store and never logged); `tools/api_usage.py` (real calls against each provider's daily limit);
  `apps.py canary` (one cheap live call per API, failing when a field the product reads has gone); API entries in
  `docs/APPS.yaml` carry key scope, rate limit, key-rotation date, terms, canary and contract fields;
  `tests/test_api_client.py`.
- **Added — the learning loop:** `docs/LEARNINGS.md` and `tools/learnings.py` (every lesson names the check that now
  holds it; `kit: yes` lessons travel to the kit); `KIT_VERSION`, `CHANGELOG.md` and `tools/kit_drift.py` (is this
  project on the newest kit); `prompts/weekly-review.md` (each project) and `prompts/kit-improvement.md` (across all
  projects); the account skill `skills/owner-run-build-kit/SKILL.md`.
- **Changed:** `AGENTS.md` gains "Apps and connectors" and "Learning"; `kit.json` gains `kit_home`, `slos`,
  `publish_workflow`, `check_workflow`; `tests/test_ops.py` holds the new registers.
- **Bring in:** every file above; `kit.json` and `tests/` through a spec session.

## 1.0.0 — 18 Nov 2026
- The Brain, the six-layer Harness, the five Loops and the project-management roles, taken from Happening / 1Live.
- Lessons shipped: `.gitignore` for generated files; the check writes no compiled Python files.
