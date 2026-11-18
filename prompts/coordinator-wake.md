# The coordinator's wake — a ONE-TIME scheduled message back into the Coordinating Work Stream

Used when the coordinator starts something that finishes later (a publishing run at about 14:10 UTC, say) and no
watcher can wake it on the thing itself. Set it for just after the expected finish. It is written down in `STATE.md`.
In Claude: a one-shot "send later" into this same session. Elsewhere: a calendar reminder to the owner to type "go on".

**Message (replace the names):**

Coordinator wake ({{PROJECT}}). In the repository folder: git fetch, reset to origin/main. Run tools/freshness.py,
tools/stranded.py, tools/orders.py faults. Check that {{THE THING AWAITED, e.g. the short publishing run started about
14:10 UTC}} finished (gh api repos/schubertsean-ui/gameday-hq/actions/runs). If it did, run
`python3 tools/orders.py run {{ORDER}} --record`, record the run link in STATE.md, and update NEXT.md. If it did not,
find out why first (AGENTS.md). Then, for each open helper pull request: have the reviewer read it
(prompts/reviewer-brief.md), run `python3 tools/checks/lane.py --pr <n>`, and merge only on MERGE OK; a RED one goes in
NEXT.md under "Waiting on owner". Hand the next step in NEXT.md to a fresh helper (kit.json "roles"."builder"). Replace
the morning summary in STATE.md, and send the owner one short update in this chat, leading with what they can now see.
