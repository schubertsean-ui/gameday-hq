# STATE.md — where things stand (a test keeps it under 20,000 bytes: a new line replaces an old one; the history is in git)

## Morning summary — {{DATE}} (the coordinator replaces this at the end of each work session, and at least once a day)
- **Done:** {{what got done, one line each, with its pull request link}}
- **Works / doesn't:** {{what the owner can now see working; what is broken or not yet checked}}
- **What it means for you:** {{one or two plain sentences}}
- **Waiting on you:** {{the red-lane items in NEXT.md, one line each, or "nothing"}}
- **Spend this month:** {{the line from `python3 tools/spend.py status`, e.g. "$12.40 of $50.00 (25%)"}}
- **The one decision needed:** {{one question, or "none"}}

## Where things stand
- **{{DATE}} — the kit is installed.** Brain: `AGENTS.md`, `NEXT.md`, `STATE.md`, `OWNER_WORDS.md`, `work/`. Harness: hooks in `.claude/settings.json`, git hooks (`tools/hooks/install_git_hooks.sh`), `bash tools/check`, the lane gate `tools/checks/lane.py`, the required check `checks` on the code host — merged, never run until one run is seen green and one seen red. Loops: `publish.yml` merged, never run; the freshness watch not yet created.
- **Live product:** {{LIVE_URL}} — not yet published.
- **Scheduled tasks:** none yet. Each one is listed here with its name, when it runs, its model, and the link of its first finished run.
