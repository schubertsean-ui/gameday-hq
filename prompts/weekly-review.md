# The weekly review — one per project, a recurring scheduled task (mid model), the engineering lead's Monday hour

**Settings:** weekly, a weekday early morning in the owner's time zone, away from the hour (for example `CRON_TZ=America/Chicago 37 6 * * 1`) ·
model: the builder role's model (`kit.json` "roles") · notifications: one push when it finishes · automatic approval on, if the owner allows it.
Recorded in `STATE.md` as on only after one run is seen finished.

**Prompt (replace the names):**

{{PROJECT}} weekly review. Work in the repository schubertsean-ui/gameday-hq (attach and clone it if it is not here). One pull
request at most; never merge a change to tests, checks or kit.json; no money, accounts or publishing.

1. Run and keep each line: `python3 tools/scorecard.py --write docs/SCORECARD.md`, `python3 tools/apps.py check`,
   `python3 tools/apps.py due`, `python3 tools/apps.py canary`, `python3 tools/learnings.py check`, `python3 tools/learnings.py kit`,
   `python3 tools/kit_drift.py`, `python3 tools/orders.py faults`, `python3 tools/stranded.py`.
2. Download the last week's API usage artifacts (`gh run download --pattern 'api-usage-*'`), join them, and run
   `python3 tools/api_usage.py --days 7 --file <joined file>`. A provider over 80% of its limit or failing more than 5%:
   raise the cache time, batch calls, or ask the owner for a higher tier (numbered steps, with the price page).
   A canary that says CHANGED is a fault with a failing test before anything else. A `key_rotation` date that has
   passed: write the owner's numbered steps to replace the key in the secret store.
3. For each app review due: open the provider's usage page named in its `usage_from`, compare plan, cap and real usage;
   if the cap is wrong or missing, write the owner a numbered-steps ask; set `last_review` and `next_review` (+1 month).
   Copy any new bill figures into `docs/SPEND.yaml` with their source.
4. Each target the scorecard marks NO is an error budget spent: write it as an order of kind `fault` with a failing
   test, unless one already exists.
5. For each lesson this week that is not yet in `docs/LEARNINGS.md` (read the merged pull requests, the faults closed,
   and the owner's words added to `OWNER_WORDS.md`), add an entry naming the check that now holds it; mark `kit: yes`
   when it would help any project.
6. If `kit_drift.py` says BEHIND: bring in the ordinary files from the kit's home now; list the protected ones for a
   spec session.
7. Write five actions ranked by result per cost (what each will change on the scorecard, and what it costs) into
   `NEXT.md`'s queue, the first one first.
8. Open one pull request with the scorecard, the registers and the entries; merge it through the green-lane gate
   (`python3 tools/checks/lane.py --pr <n>`, after the reviewer's pass). Check `kit.json` "roles" against current
   independent rankings; a better model or price is a proposed change in the pull request, never a new paid service
   without the owner (red lane). Run `python3 tools/spend.py status` and put its line in the morning summary.
9. Send the owner one message in the Coordinating Work Stream: the scorecard's missed targets in a line each, the five
   actions, spend against the cap, and anything waiting on the owner.
