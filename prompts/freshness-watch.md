# The freshness watch — a recurring scheduled task on the SMALL model (the product's own clock, outside the code host)

Why: GitHub's own schedules can be delayed or dropped under load (Happening, 17 Nov 2026: 3 of 8 slots fired), and every
scheduled slot costs a billed minute even when it lets nothing through. This watch costs no CI minute when the product
is fresh; it starts the short publishing run only when the product is older than its limit.

**Settings:** every 3 hours at minute 22 (`22 */3 * * *`, UTC) · model: the scout role's model (`kit.json` "roles", the smallest that does it) · notifications off ·
automatic approval on, if the owner allows it. Recorded in `STATE.md` as on only after one run is seen finished.

**Prompt (paste as the scheduled task's prompt; replace the three names):**

{{PROJECT}} ({{LIVE_URL}}) freshness watch. This session's only task is the steps below. Do not start any build step,
do not edit or commit files, do not open pull requests, do not message anyone. Keep it short and cheap: every CI run
costs money, so start one only when these steps say so.

1. If the repository is not in this session, attach schubertsean-ui/gameday-hq and clone it shallow
   (git clone --depth 1 https://github.com/schubertsean-ui/gameday-hq repo). Work in that folder.
2. Run: python3 tools/freshness.py --max-hours 8 ; note its exit code.
3. If the exit code is 0: reply with its one line and stop.
4. Otherwise (1 = older than 8 hours, 3 = could not tell): look for a publishing run already queued or running:
   gh api "repos/schubertsean-ui/gameday-hq/actions/runs?status=in_progress" --jq '[.workflow_runs[].name]' and the same with
   status=queued. If either list holds "publish", reply "a run is already going" and stop.
5. Run here (it costs no CI minute): python3 tools/minutes_budget.py --kind short ; if it exits 1, reply with its line
   and stop. Otherwise start the short run through the REST API:
   gh api -X POST repos/schubertsean-ui/gameday-hq/actions/workflows/publish.yml/dispatches -f ref=main -f inputs[kind]=short
6. Never start the full run: it has its own daily schedule.
7. Reply with one line only: what freshness and minutes_budget printed, and the link of the run you started
   (gh api "repos/schubertsean-ui/gameday-hq/actions/runs?per_page=1" --jq '.workflow_runs[0].html_url'), or "nothing started".

**Without Claude scheduled tasks:** the same job, in this order of preference — an n8n "Schedule Trigger" → "Execute
Command" or "HTTP Request" node calling the dispatch URL; a free external cron service (for example cron-job.org)
calling `POST https://api.github.com/repos/schubertsean-ui/gameday-hq/actions/workflows/publish.yml/dispatches` with a fine-grained
token that can only run this repository's workflows; the database's own scheduler (Supabase pg_cron + pg_net); a
Cloudflare Worker with a Cron Trigger; a computer that is always on (cron or launchd). Without the freshness test in
front, each of these simply starts the short run on its clock — set the clock to the product's limit.
