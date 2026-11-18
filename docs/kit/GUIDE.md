# The Owner-Run AI Build Kit — Brain, Harness, Loops and Project Management

Nov 18, 2026 · @Sean Schubert · Version 1.1.1, taken from the working setup of Happening / 1Live; first installed in `schubertsean-ui/gameday-hq`

## How to use this kit

This kit sets up an AI-built, owner-run project so that the work does not rest on the AI's word. It has three parts: a **Brain** kept on disk, a **Harness** of gates that fire on every change, and **Loops** that keep the work and the live product moving. It is the setup running Happening / 1Live on 18 November 2026, with the product taken out so it fits any project.

**Pick the level you can reach.** Each level is a complete way of working; a higher one adds gates the AI cannot get around.

| Level | What you need | What you get |
| --- | --- | --- |
| A — Full | A coding agent working on a repository (Claude Code, or Codex, Cursor, GitHub Copilot's agent) and a code host that can block a merge until a check is green | All six harness layers and all five loops |
| B — Partial | Files and commands, but no required check on the code host (for example a private repository on GitHub Free) | The Brain, the hooks, the product check and git's own gates; the owner looks at the check's output before each merge |
| C — Chat only | Any chat AI, no lasting files | The Brain as one document re-posted when it changes, one written check, and the owner's eye as the gate |

**The files that come with this guide** (sent one by one, never zipped):

- `install-kit.sh` — one command, run at the top of a repository, writes all 70 kit files and sets the test floor to the tests it counts. It never overwrites a file that exists unless told `--force`.
- `kit-all-files.md` — the same 70 files as one readable document (named `KIT.md` in the kit's home), each under the path it goes to. Copy them by hand, or hand the document to any AI that can write files.
- `HAPPENING-reference-setup-2026-11-18` — the exact Happening setup this kit was taken from: every file, setting, schedule and connector, with its real values.

**To hand the whole thing to an AI,** paste the prompt in the section "Ready prompts" (`prompts/start-any-ai.md`). It makes the AI say what it can do, pick a level, install the kit at that level, prove the gates fire, and start the loops.

**The split of work is fixed, in two lanes.** The owner does not approve every step: work goes on while the owner sleeps. The **green lane** is the AI's alone: branches, commits, draft pull requests, tests, docs, refactors, features and fixes, and merging its own pull request once the check is green, a reviewer of another model has passed it, and the gate (`tools/checks/lane.py --pr`) says MERGE OK. The **red lane** waits for the owner: spend past the monthly cap ($50 in this install) or a new paid service, production data and deploy settings, secrets, domains, billing, repo settings and the harness, legal matters, public announcements, messages to people, force-push. The AI writes each red item in `NEXT.md` under "Waiting on owner" with a recommendation, and goes on with green work. The owner also marks the picture of the finished product right.

## The idea on one page

The owner says what the finished product looks like; the AI builds exactly that, and every claim of "done" is checked by something other than the AI. Four parts make that hold.

- **The Brain** is what is known, kept in files on disk, never in a chat's memory: the standing rules, the one next step, where things stand, the owner's own words, and a numbered work order for every value and button on the finished product. What is not in the Brain is not known. Every session reads it first.
- **The Harness** turns each rule that matters into a gate that fires on every change: hooks inside the AI session, git's own hooks, one product check, a required check on the code host that the AI cannot reach, and judges that read the live product itself.
- **The Loops** keep things moving without the owner pushing: the build loop (one step, the check, merge, judge it live), the run loop (the product's own timetable keeps it fresh), the wake loop (the AI wakes on the thing it is waiting for), the owner loop (one channel; a morning summary; only red-lane items wait for the owner) and the failure loop (every failure becomes a failing test, closed only when it passes on the live product).
- **Project management** is one coordinator the owner talks to, fresh helpers on the model each role is given in `kit.json` "roles" (any vendor), roles that never mark their own work (planner, builder, reviewer, judge), a cost ladder (a script before a model, a small model before a large one), and a monthly cap every paid run is counted against.

```text
The owner talks to one coordinator; gates and the live product judge the work

  Owner  <-- one channel -->  Coordinator  <------------------------+
  (marks the end right;       (only contact; plans,                 |
   red-lane items only)        merges through the gate; summary)    | results
   the word to publish)              |                              |
                                     | brief                        |
  Brain, on disk  --read first-->  Helpers                        Judges
  AGENTS.md  the rules             (fresh each step, own branch,  (orders run live,
  NEXT.md    the one step           cheapest model for the job)    faults reopen if broken,
  STATE.md   where things are            |                         freshness, stranded)
  OWNER_WORDS.md  quotes                 | pull request                 ^
  work/  an order per field          Harness                            |
                                     (session and git hooks,            |
                                      one product check,                |
                                      required check on main)           |
                                         | merge on green, publish      |
                                     Live product  ---------------------+
                                     (where customers see it; never published empty)
                                         ^ keeps it fresh
  Run loop: a full run each day on the product's own schedule, and a short run when it is 8 hours old
```

Work flows down the middle column; the results come back up the right from the live product, never from the AI's own report.

**The five standing rules.** Everything else may be improved; these hold.

1. Nothing is called done without proof the owner can open: a command and its real output, a picture made by a tool, or a link. "Couldn't verify" is never "passed".
2. One check fails when the product is wrong. It is never weakened to make something pass; if it is wrong, the AI says why.
3. Ask before money, an account, a credential, sending or publishing. Silence is never a yes.
4. Never hold a key that can delete live data.
5. Wait on the thing itself. The AI watches the runs it starts and wakes when they finish, not on a guess; every schedule is written down where the owner can see and stop it. (An owner who wants every run started by them uses the stricter form: no timers the AI sets for itself.)

A new standing rule is written only after a real failure, and only when a check cannot catch it. Every correction becomes a check, not another paragraph.

## Who decides — the two lanes (new in 1.1.1)

The owner's words, 18 Nov 2026: "I do not want to have to approve every single thing since I expect work to be done while I sleep or am away", and "Set your spending cap at $50." Everything below is the AI's design to serve them.

| Lane | What is in it | What the AI does |
| --- | --- | --- |
| Green | Branches, commits, draft pull requests, tests, docs, refactors, features, fixes; paid runs while the month is under the cap | Does it, day or night. Merges its own pull request only when all hold: the required check `checks` is green; a reviewer that did not write it (another model, another vendor where possible) commented `REVIEW: PASS <head sha>`; no existing test changed; the test floor not lowered; under 400 changed lines (`kit.json` "auto_merge"); no red-lane path. `python3 tools/checks/lane.py --pr <n>` checks all of these and says MERGE OK, RED or NOT YET |
| Red | Spend that would pass the cap, a new paid service or subscription; production migrations, data writes or deletes; production deploy config, secrets, env vars, domains, billing; repo settings, branch protection, CODEOWNERS, CI workflows and harness files (`tools/checks/**`, `tools/hooks/**`, `.github/**`, `.claude/settings.json`, `kit.json`, `AGENTS.md`, lowering the test floor); deleting a repo or a branch with unmerged work; anything legal, public announcements, messages or emails to people; force-push or rewriting history | Stops that item, writes it in `NEXT.md` under "Waiting on owner" (one plain paragraph: what, why, the recommendation, what happens without an answer), and keeps going on green work. It may open a draft pull request for the owner; it never merges it |

**Machine-checked, twice.** The red-lane paths live in `kit.json` "red_lane"; `tools/checks/lane.py` flags any change touching them (and `bash tools/check` shows its verdict). `.github/CODEOWNERS` lists the same paths with the owner as code owner, so with "Require review from Code Owners" switched on, the code host refuses a red-lane merge without the owner even if an AI ignored the rule. A test keeps the two lists the same.

**The morning summary.** At the end of each work session, and at least once a day, the coordinator replaces the top of `STATE.md`: what got done with pull request links, what works and what doesn't, what it means for the owner, what waits on the owner, spend this month against the cap, and the one decision needed.

**The cap.** `kit.json` "monthly_cap_usd": 50, all AI providers and paid services together. Before any paid run, `python3 tools/spend.py before --provider P --what W --estimate E` logs it in `docs/SPEND_LEDGER.yaml`, or refuses (exit 2) when the month would reach the cap; after it, `spend.py after <id> --actual A`. `spend.py status` exits 2 at or over the cap and warns from 80%. At the cap paid work halts and unpaid work goes on. This is the AI's own brake; **the hard backstop is the cap the owner sets on each provider's billing page**, because no file in a repository can stop a provider charging.

**A model per role.** `kit.json` "roles" names a model and vendor for the coordinator, builder, reviewer, reader and scout. Each is chosen by current independent rankings, mixing vendors freely; the reviewer is a different model, and a different vendor where possible, from the builder. The values shipped are defaults to revisit (picked 18 Nov 2026 from the vendors' release notes, not from a ranking); the weekly review checks them. `AGENTS.md` is the vendor-neutral rulebook; `CLAUDE.md`, `GEMINI.md` and `.claude/agents/` only point at it.

## The Brain

The Brain is eight kinds of file in the repository, kept small by tests, plus a few shelves outside it. Every session starts from the files, never from what a chat remembers.

| File | What it holds | Kept small by | Who writes it | When it is read |
| --- | --- | --- | --- | --- |
| `CLAUDE.md` | Two import lines: `@AGENTS.md` and `@NEXT.md` | A test fails if either line goes | Set once | Loaded by Claude Code at the start of every session |
| `AGENTS.md` | The standing rules: start of session, who decides, cost, the directive, the five rules, whose words are whose, what customers see, commands, where things are | At most 100 lines (Happening: 97) | The AI, each rule traceable to the owner's dated words | Every session. Codex, Cursor, Copilot's agent, Windsurf, Jules and others read it by name; Gemini CLI and Aider with one setting |
| `NEXT.md` | The one next step, in one short line | At most 700 characters and 3 lines | The coordinator, at the end of every step, replacing what was there | Every session, before anything else |
| `STATE.md` | Where things stand, what runs by itself (with the link of a finished run), what waits on the owner | At most 20,000 bytes; a new line replaces an old one | The AI, in the same change as the product | When the step needs it |
| `OWNER_WORDS.md` | The owner's words, quoted exactly and dated; the only file that names the owner | Never reworded | The AI copies; never edits | Before asking the owner anything |
| `work/` | One work order per value and button on the finished product, and `seen.json`, what the judge saw on the live product | `orders.py plan` refuses an empty slot | Planner writes orders; only the judge writes `seen.json` | For each step |
| `docs/ASK_THE_LAWYER.md`, `docs/IDEAS.md` | The running lawyer list; every idea from the owner, unranked | — | The AI | When a question or idea comes up |
| `kit.json`, `prompts/` | The tools' settings; the prompts for scheduled tasks, helpers and handoffs | `kit.json` is protected | A session the owner starts for changing checks | By the tools; by the coordinator |

**How the Brain stays true**

- Disk is truth. A chat's memory, the AI's own idea of the product, and what today's tools make easy are not the brief.
- The newest dated word wins. Where an older document and a newer decision differ, the AI says so once and follows the newer.
- The owner's words and the AI's choices stay apart. Every technical rule, number and process is the AI's, and says so; an interpretation is written "I assumed …" where it is made.
- Read only what the step needs, once, and whole. A partial read is no read.
- A correction becomes a check. The files cannot grow, so a new rule must replace an old line or become a test.

**Shelves outside the repository**

| Shelf | Happening uses | What lives there |
| --- | --- | --- |
| Project space | The claude.ai Project "Happening" | The charter, vision and goals as the Project's instructions; pointer documents (which chat coordinates, where things are); handoff notes; reviews |
| AI memory | Claude's memory, account and project | Standing preferences that apply everywhere, such as "files one by one, never zipped" and "step-by-step asks" |
| Account skills | `happening-operating-rules` (a pointer), `build-the-end` (the blueprint), `marketing` | A short pointer every chat loads, so chats that the code host never sees start from the same rulebook |
| The owner's drive | Google Drive | The owner's source documents: the brief, the master specification |
| The picture of the finished product | A design canvas of 18 boards, with a checksum per board in the repository | The approved end, which is the brief; a revision on the canvas is the new approved picture |

## The Harness

Six layers of gates, from the AI's own session out to the live product. The inner layers are reminders an honest agent cannot miss; the outer layers are where the AI cannot reach, so they are the real judges.

| # | Layer | Where it runs | What it stops | Can the AI get around it? |
| --- | --- | --- | --- | --- |
| 1 | Session hooks (`.claude/settings.json`) | Inside the AI tool, at fixed moments | **Start:** records the commit the session began from. **Before an edit:** blocks any edit to an existing test, fixture, check, hook, workflow-that-runs-the-check or `kit.json` (new tests are fine). **Before stopping:** if the product changed, runs the quick check; while it is red the AI is sent back, up to 3 times, then the session ends with `CHECK_FAILED.txt` written for all to see | Yes, through a shell command. Layers 3 to 5 catch that |
| 2 | Git hooks (`tools/hooks/install_git_hooks.sh`) | In every copy of the repository, for any AI tool or person | A commit while the quick check is red; a push while the full check is red | Yes, with `--no-verify`. Layer 5 catches that |
| 3 | The one product check (`bash tools/check`) | Anywhere; no model is used | Failing tests; deselected tests; any skipped test on the code host; fewer tests than the floor (set at install, so a deleted test file is RED from the first day); an existing test changed in the same change as other files; any extra check named in `kit.json` (a page-size budget, a screenshot audit). It also shows, without deciding, the change's lane and the month's spend | Only by changing the check, which layers 1, 4 and 5 stop |
| 4 | Working rules held as tests (`tests/test_working_rules.py`, `tests/test_harness.py`) | Inside the product check | `NEXT.md` longer than one short line, or not loaded; `AGENTS.md` or `STATE.md` growing; a change that is only rules and records with no product in it (unless the owner's dated words asked for it); a product change that does not update where things stand; a hook that blocks when it cannot find itself | No: they are tests, and tests are protected |
| 5 | The code host (ruleset on `main`, `.github/workflows/checks.yml`, `.github/CODEOWNERS`) | On the code host, out of the AI's reach | Any change reaching `main` except by a pull request whose `checks` job is green; a second run after each merge catches two merges that conflict; with "Require review from Code Owners", the owner's own approval for any red-lane path | No. Only the owner can change the ruleset |
| 6 | Live judges (`tools/orders.py`, `freshness.py`, `stranded.py`, `minutes_budget.py`, the publishing workflow's own guards) | Against the live product and the code host | An order marked done that fails on the live product; a fixed fault that breaks again; a stale product; work pushed but never merged; a month's CI minutes overrun; publishing an empty product | No. They read the product itself, not a report about it |

**What the AI never holds.** A key that can delete live data. The database and model keys live only in the code host's secret store and are read only by the publishing run. A session that reads outside pages holds no key that can publish or change live data, because outside text can try to give instructions.

**Each gate is proven by making it fire.** Before the kit was sent, every gate was run red and green in a scratch repository (18 Nov 2026):

- A broken product function: `bash tools/check --quick` exit 2, RED; restored: exit 0, GREEN.
- `NEXT.md` made 800 characters long: RED on the next-step test.
- A test loosened by a shell edit alongside product code: `tests_untouched: FAIL`, RED.
- The before-edit hook, called from a subfolder on an existing test: exit 2, blocked. A new test: allowed. Product code: allowed. The same test with `SPEC_SESSION=1`: allowed. `kit.json`: blocked.
- The stop hook with the product broken: exit 2, sent back to work.
- A commit with the check red: refused by git. A push mixing a protected file with other files: refused by git.
- A branch pushed and never merged: `stranded.py` exit 1; settled: exit 0.

Not proven in this session: the code host's ruleset (it needs the owner's account; Happening's own ruleset has been active since 13 Nov 2026).

## The Loops

Five loops run at once. The build loop changes the product; the run loop keeps it right between changes; the wake, owner and failure loops keep the other two honest and moving. Times below are Happening's, as an example.

**1. Build loop — one step at a time, judged on the live product**

1. The coordinator reads its in-tray: `freshness.py`, `stranded.py`, `orders.py faults`, the open pull requests and the project space. Anything red comes first.
2. It picks the step: the oldest open fault, else the line in `NEXT.md`.
3. It hands the step to a fresh helper with a written brief (`prompts/helper-brief.md`): the builder role's model for code, the reader or scout for reading, its own branch. A paid helper is logged first (`tools/spend.py before`).
4. The helper sees the order fail, writes a test that fails for the same reason, builds until it passes on a built copy, runs `bash tools/check` green, updates `NEXT.md` and `STATE.md`, and opens a draft pull request naming its model.
5. The code host's `checks` job runs (about 3 minutes in Happening). Green: a reviewer of another model reads the diff (`prompts/reviewer-brief.md`); on MERGE OK from `tools/checks/lane.py --pr` the coordinator merges. Red: back to the helper. A red-lane change waits for the owner.
6. If the merge changes what customers see, the coordinator starts the publishing run and watches the live product's publish time, not a guess at the run's length.
7. The judge runs `orders.py run --record` on the live product: every order, not only the one built, so anything that broke elsewhere is found.
8. The coordinator writes the morning summary in `STATE.md` and sends the owner one message that leads with what they can now see.

Two failed tries change the method, and the order records what was tried. A third goes to the largest model for the cause before anything else is tried.

**2. Run loop — the product's own timetable**

- A full run once a day on the code host's schedule (Happening: 03:47 UTC, stopped at 75 minutes).
- A short run that refreshes only what changes often, started when the product is 8 hours old. The starter is a scheduled task on the smallest model every 3 hours at minute 22, which costs no CI minute when the product is fresh (`prompts/freshness-watch.md`). The code host's own schedule runs twice a day as a backup, because its slots can be delayed or dropped (Happening, 17 Nov 2026: 3 of 8 fired).
- No full run on a merge. On 16–17 Nov 2026 merges started 34 full runs in two days; the month passed the plan's 3,000 minutes and every job was refused until a budget was set.
- A minutes guard in front of each publishing run: past 2,400 of the plan's 3,000 minutes the full run stands down, and the short run runs only when the product is 10 hours old.
- The two publishing runs share one lane, so they never publish at the same time; each keeps what it read for the next; neither publishes an empty product.
- A freshness limit every session checks: 11 hours in Happening.

**3. Wake loop — the AI waits on the thing itself**

- A session that starts a run watches that run, or the publish time of the live product, and goes on building in between. It does not end with "awaiting your next message" while its run is still going.
- When nothing can watch, the coordinator sets a one-time wake back into its own session just after the expected finish (`prompts/coordinator-wake.md`). Happening example: "close Running.32 after the 14:10 publish", set for 14:35 UTC.
- Anything that runs by itself is written down as on only after one of its runs has been seen finished, with the link. Until then the record says "merged, never run". This rule exists because a six-hour run was recorded as switched on and had never run.

**4. Owner loop — one channel, few asks**

- Every update goes to one place, the Coordinating Work Stream. Any other chat or session does its one task, leaves the result on the code host, and sends the owner nothing of its own.
- Each message leads with what the owner can now see, in a few lines. Assumptions and gaps go in the files, with one line saying where.
- Only red-lane items wait for the owner, in `NEXT.md` under "Waiting on owner"; the morning summary in `STATE.md` lists them with spend against the cap. Each ask says in one sentence what it is for, then gives numbered steps: one action a step, the page to open and the button as it is written on the screen, and what the owner will see when it has worked.
- The owner can redirect at any time in any words. Their words go into `OWNER_WORDS.md` the same day.

**5. Failure loop — only a reported and fixed failure is acceptable**

1. A failure seen anywhere is written down first as a work order of kind `fault`, with a test that fails for that reason. That is the report.
2. The session that finds it fixes it.
3. It is closed only when its test passes on the live product, recorded by the judge.
4. Its test runs for ever. Anything that passed once and fails now is a fault again, first in line.
5. Faults come before building: `orders.py faults` exits 1 while one is open, and every session starts there.

## Managing the project

One coordinator, many short-lived helpers, and a plan the machine can check. The owner talks to one session; the work is spread across cheap, fresh ones.

**The coordinator** is one long-running AI session and the owner's only point of contact. It plans, hands out steps, merges through the green-lane gate, writes the morning summary, judges on the live product, and notices every other chat or tool working on the project (Happening's owner, 18 Nov 2026: "I may start separate chats but it's your job to notice them and integrate every chat content"). At each of the owner's messages it reads its in-tray: stranded work, open pull requests, and the project space.

**Helpers** start with no memory and get a written brief: the goal, the inputs, the limits, what done is, and when to stop and ask. One step, one branch, one pull request each. A chat, a different coding agent or a second session works the same way: it leaves a branch and a pull request, and puts any words of the owner's it heard into `OWNER_WORDS.md`.

**Four roles, never the same session for one order** (`work/ROLES.md`)

| Role | Does | Never |
| --- | --- | --- |
| Planner | Writes the work orders from the picture of the finished product and the code: one per value and button, every slot filled, a pass mark with its evidence | Fixes the product |
| Builder | Makes one order pass: sees it fail, writes the test first, builds, check green, draft pull request | Edits an order's pass mark or test, weakens a check, ends at "reported" |
| Reviewer | Reads a finished pull request it did not write, on another model, and comments `REVIEW: PASS` or `FAIL` at the head commit | Edits, pushes or merges |
| Judge | Runs every order against the live product after a publishing run and records what it saw | Judges something it built |

**Work orders.** Each value and button on the finished product has an order with twelve slots: what the customer sees, where the value comes from, where it is kept, what shows it, the pass mark with its evidence, a machine test, the steps, what is done when it fails (at least two lines, each ending in an action), what it needs first, and anything only the owner can supply. `orders.py plan` refuses a gap. Happening numbered 916 values and buttons on 18 boards and wrote 620 orders; its owner set the floor for every share at 99% ("Anything less than 99% is a fail").

**Which model does which job** — the cheapest that gets it right (since 1.1.1 the role's model is set in `kit.json` "roles", any vendor; the Happening column is the Claude-only setup it came from)

| Work | Who does it | In Happening |
| --- | --- | --- |
| Anything a command can check or do | A script, no model | `tools/check`, the judges, the publishing runs |
| Reading files, pages and documents | The small model, several items per helper | Agents `scout` and `page-reader` on Haiku; the freshness watch on Haiku |
| Writing code | The mid model | Helpers on Sonnet; `opusplan` writes with Sonnet |
| Plans, design decisions, judging finished work | The large model | Opus, which `opusplan` uses for planning |
| A root cause that two tries did not find | The largest model, for that question only | Fable |

**Keeping cost down**

- One step per session, then stop: a long session pays again for everything said before.
- Batch: one helper reads several pages, because each helper costs a fixed amount to start.
- Never spend a model on what a command can check.
- As few pull requests as possible: each one costs a check run.
- The monthly cap in `kit.json` ($50 here), every paid run logged before and after with `tools/spend.py`, paid work halted at the cap. Behind it, hard spending limits at every provider, set by the owner (Happening: a $5 Actions budget on GitHub; Supabase approved up to $35 a month), plus the minutes guard in front of the publishing runs. One spend line a week, taken from the providers' own bills.

**What the owner looks at, and when**

| When | What |
| --- | --- |
| When a step finishes | The live product or a picture of it, the check's result and where it ran, and any ask |
| When a screen is complete | A picture of the live screen beside its approved picture: the owner's eye is the last test |
| Weekly | Orders passing on the live product, faults open, spend |
| Each morning | The morning summary at the top of `STATE.md`: done, waiting on you, spend against the cap, the one decision |
| Always, personally | The red lane: spend past the cap, new paid services, production data and deploy settings, secrets, repo settings and the harness, legal, public posts, messages to people |
| Not at all | Code, status files, ledgers |

**Records that stay.** The ask-the-lawyer list (each item framed in detail, with the other party's own words, a real example and the exact question) does not hold up the work unless the owner says so. The ideas register keeps every idea from the owner's documents, with where it was written, unranked: the owner sorts. Before moving to a new chat or another AI, a handoff note (`prompts/handoff-note.md`) is written first.

## Running it like Google and Cursor

Google's and Cursor's engineering teams keep quality, speed and cost in line with a handful of habits. Version 1.1.0 turns each one into a file or a check, so nothing depends on anyone remembering it.

| Habit | How the kit does it | Where |
| --- | --- | --- |
| Small changes, a fast check before merge, one main branch | One step per helper, one pull request, a check of about 3 minutes | `checks.yml`, the ruleset on `main` |
| A broken main branch is undone in minutes, then fixed calmly | When the check after a merge goes red, a pull request that reverts the merge opens at once | `.github/workflows/revert-on-red.yml` |
| Targets with an error budget | Targets for freshness, orders passing, lead time, breakage and time to fix; a missed target becomes a fault and comes before new work | `kit.json` "slos", `tools/scorecard.py` |
| The four delivery measures | How often the product was published, pull request to merge, share of merges that broke `main`, fault found to fixed live, every week | `tools/scorecard.py` |
| Helpers working in parallel, each attaching its evidence | Fresh helpers on their own branches; each pull request carries the check's output and a picture or link | `prompts/helper-brief.md`, agent `builder` |
| Every correction becomes a test | The failure loop, and a lessons register in which every lesson names the check that now holds it | `work/ORDERS_FORMAT.md`, `docs/LEARNINGS.md` |
| Routine changes merge on green; changes to the referee need a person | Green lane merges on a green check and another model's review; code owners on every red-lane path | `.github/CODEOWNERS`, `tools/checks/lane.py` |
| Design reviewed against the approved picture | The judge puts a picture of each live screen beside its approved picture; visual comparisons plug in as extra checks | `work/ROLES.md`, `kit.json` "extra\_checks" |
| Every vendor written down, capped and reviewed | Each outside app with its most powerful access, who holds its key, a hard cap at the provider, where real usage is read, a fallback and a monthly review; unsafe entries refused | `docs/APPS.yaml`, `tools/apps.py` |
| Least privilege, and defence against instructions hidden in outside text | A session that reads pages, emails or issues holds no key that can write, deploy or publish | `tools/apps.py check` |
| Real spend, never estimates | Bills copied from each provider; CI minutes counted from the code host | `docs/SPEND.yaml`, `tools/minutes_budget.py` |

**APIs to other apps.** Every call the product makes to another app's API goes through one client, `tools/api_client.py`, which gives every call:

- a timeout, so no call hangs a run;
- retries only where a retry can help (rate-limited or server errors, a dropped connection), waiting as long as the provider asks or backing off, never more than 30 seconds;
- a circuit breaker: after 5 failures in a row the provider is left alone for 10 minutes;
- a cache, so the same answer is not paid for twice;
- one usage line per call, with the key never written anywhere.

Each API's register entry adds its key scope, its stated rate limit and daily limit, the date its key is next replaced, its terms, a cheap "canary" call and the fields the product reads. Each week `tools/apps.py canary` calls every canary and fails when a field has gone (the API changed under the product), and `tools/api_usage.py` flags a provider above 80% of its daily limit or failing more than 5% of calls.

**Managing Claude itself.** A script before a model; the small model for reading, the mid model for code, the large model for design and judging; one step per session; helpers batched; the rulebook kept under 100 lines because it is paid for on every turn; scheduled tasks on the smallest model with notifications off unless they matter. Plan usage is read from the account's usage page, and in Claude Code from `/usage`.

**What the first scorecard showed.** Run read-only against Happening's GitHub history on 18 Nov 2026: 45 publishing runs in 7 days; a median of about 6 minutes from pull request to merge; no merge broke `main`; and 4,051 Actions minutes used this month against the plan's 3,000, which is a missed target.

## Saving it to Claude for every project

Four layers, from the one that reaches everywhere to the one that serves a single project. The kit itself lives in one place, a GitHub repository; everything else points to it, so there is never a second copy to drift.

| Layer | What it holds | Reaches | Set up by |
| --- | --- | --- | --- |
| Account skill `owner-run-build-kit` | Short instructions: check the kit is installed, follow `AGENTS.md`, feed the learning loop; points to the kit's home | Every chat and Project on the account, and Claude Code signed in with the same account (synced about every 10 minutes, one way) | The owner, by saving the review card in this chat |
| The kit's home: a private repository `owner-run-kit`, marked as a template | The 70 files, `KIT_VERSION`, `CHANGELOG.md`, the installer, the list of projects | Every coding agent (Claude Code, Codex, Cursor, Copilot) | The owner creates it (steps below); the AI fills it |
| Account instructions | One line: "For any build, product or venture work, use the owner-run-build-kit skill and follow AGENTS.md in the project's repository." | All conversations on the account | The owner (steps below) |
| Project instructions | `prompts/project-instructions.md`, filled in for that project | Chats inside that Project only | The AI drafts; the owner pastes |

Claude's memory is not where the kit lives: it carries preferences stated in chats, and a Project's memory can be kept apart from the account's.

**The owner's steps** (from Anthropic's help pages; not seen on screen in this session)

1. **Save the skill.** In this chat, open the review card for `owner-run-build-kit` and press Save. You should see it under Customize → Skills, switched on.
2. **Create the kit's home.** On GitHub: the + menu → New repository. Owner: your own account. Name: `owner-run-kit`. Private. Press Create repository. Then Settings → General → tick "Template repository". You should see an empty repository marked Template.
3. **Let the AI in.** Tell Claude "kit repo ready" in any Claude Code session; it attaches the repository, pushes the kit, and creates the kit-improvement review. You should see a pull request with 70 files and a green check.
4. **Account instructions.** Your initials (lower left) → Settings → Your Claude → Instructions. Add the one line from the table. You should see it saved; it applies to every conversation.
5. **Each new project:** on GitHub, open `owner-run-kit` → Use this template → Create a new repository. For an existing project, the AI runs the installer instead.

**Outside Claude.** Codex, Cursor, Copilot's agent and the others read `AGENTS.md` in each repository by themselves. For ChatGPT or Gemini, paste the skill's text into the custom instructions or the Gem.

## Keeping it improving

Claude does not learn between chats by itself, so lessons are written to files and carried by two scheduled reviews. A lesson moves in four steps, and a change to any check still needs the owner.

1. **In the moment, in every chat and session.** A correction, a failure or a surprise becomes a check first, then an entry in `docs/LEARNINGS.md` naming that check (`tools/learnings.py check` refuses an entry whose check does not exist). One that would help any project is marked `kit: yes`. A chat that cannot write to the repository puts the lesson in its handoff note in the same form, for the next session to file.
2. **Every week, in each project** (`prompts/weekly-review.md`, a scheduled task on the mid model): the scorecard against the targets, app reviews due, the API canaries and usage, the week's lessons filed, and `tools/kit_drift.py`. A missed target becomes a fault before new work; five actions ranked by result per cost go into `NEXT.md`.
3. **Every two weeks, across all projects** (`prompts/kit-improvement.md`, one scheduled task for the account): every `kit: yes` lesson and every target missed in two or more projects is made product-neutral and brought into the kit's home. It then bumps `KIT_VERSION`, writes `CHANGELOG.md`, rebuilds the installer, runs the kit's own tests and opens one pull request. If the skill changed, it puts a review card in front of the owner.
4. **Back into every project.** Each project's `tools/kit_drift.py` says BEHIND; the next step brings the ordinary files in. Protected files (tests, checks, hooks, `kit.json`) come in through a spec session the owner starts.

**What keeps the loop honest**

- The owner approves every change to the kit's tests, checks and hooks (code owners), and every skill update (the review card).
- A rule is added only after a real failure, and only when a check cannot hold it. A rule no project needed in 60 days is proposed for removal, and `AGENTS.md` stays under 100 lines.
- Every version says what changed, why, and which project's lesson it came from.
- Claude's memory keeps preferences stated in chats on its own; the kit keeps lessons. Neither replaces the other.

## Setup in order

About an hour of the owner's clicks, spread over the first day, and the rest is the AI's. The owner's steps are the ones that need an account, money or a credential. The button names below are from GitHub's documentation and Happening's record; they were not seen on screen in this session, so the AI walks the owner through each screen as it appears.

**The owner's steps**

1. **A home for the code.** Create an organisation or account on the code host and a private repository. For a private repository to block merges until the check is green, GitHub needs the Pro, Team or Enterprise plan; GitHub Free allows it on public repositories only. You should see an empty repository page.
2. **Give the AI access.** In Claude: connect GitHub and allow the repository. In another agent: its own GitHub connection. You should see the AI clone the repository.
3. **Let the AI install the kit** (its steps are below). You should see a pull request whose `checks` job is green, and a second one the AI made red on purpose.
4. **Switch on the judge.** Repository → Settings → Rules → Rulesets → New ruleset → New branch ruleset. Name: "main is judged". Enforcement status: Active. Target branches: Include default branch. Tick "Require a pull request before merging" (approvals 0) and "Require review from Code Owners", so red-lane changes wait for you and everything else does not. Tick "Require status checks to pass" and add the check named `checks`. Leave the bypass list empty. Press Create. You should see the AI's red pull request unable to merge.
5. **Spending limits.** On the code host: Billing → Budgets, an Actions budget (Happening: $5). At each model provider and paid service: a hard monthly cap, together no more than the kit's cap (`kit.json` "monthly_cap_usd", $50 here). This is the hard backstop; the kit's own count stops the AI first. You should see each limit on its provider's page.
6. **Secrets.** Repository → Settings → Secrets and variables → Actions → New repository secret: the database address and any model key the publishing run needs. Type them there, never in a chat.
7. **Hosting.** Repository → Settings → Pages → Source: GitHub Actions, and your custom domain. You should see the live address after the first publishing run.
8. **The project space.** Create a Project (or its equivalent), paste `prompts/project-instructions.md` as its instructions, and upload `.claude/skills/operating-rules/SKILL.md` as an account skill so every chat starts from the rulebook.
9. **Approve the scheduled task** the AI proposes for the freshness watch (and allow automatic approval if offered), so the short run starts without you.

**The AI's steps**

1. Run `bash install-kit.sh` at the top of the repository (or create each file from `kit-all-files.md`).
2. Fill every `{{…}}`: `grep -rn '{{' .` lists them. Fill `kit.json`: the live address, the product folders, the test command, the limits.
3. `pip install -r requirements-kit.txt`, then `bash tools/hooks/install_git_hooks.sh` once in each copy.
4. `bash tools/check`: GREEN. Break one test on purpose: RED. Restore: GREEN. Delete a test file: RED (the floor). Paste the outputs. After adding tests later: `python3 tools/checks/floor.py raise`.
5. Push on a branch and open a pull request; see `checks` go green on the code host. Open a second, deliberately broken one; see it red. After the owner's step 4, see that the red one cannot merge. Close it.
6. Write the first work orders from the approved picture (`work/ROLES.md`, Planner) until `orders.py plan` shows 0 gaps.
7. Set the build commands in `.github/workflows/publish.yml`; start it by hand once and watch it finish. Only then write it in `STATE.md` as on, with the run's link.
8. Create the freshness watch from `prompts/freshness-watch.md` on the smallest model; record it as on only after one of its runs is seen finished.
9. Write the pointer to the Coordinating Work Stream (`prompts/coordinating-stream-pointer.md`) into the project space, and put the first real step in `NEXT.md`.

## Alternatives when a program or connector is not available

Every part has a stand-in, down to a version that needs no tool at all. Use the left-most column you have; each step to the right keeps the same rule with a weaker gate, so say which one is in use in `STATE.md`.

| Part | Happening uses | If that is not available | With no tool at all |
| --- | --- | --- | --- |
| Coding agent | Claude Code cloud sessions on the repository | Codex, Cursor's agent, GitHub Copilot's coding agent, Windsurf, Jules, Devin, Gemini CLI, Aider: all read `AGENTS.md` ([agents.md](https://agents.md)) | A chat AI writes each change; the owner or a helper runs it and pastes the output back (Level C) |
| Rules loaded every session | `CLAUDE.md` imports `@AGENTS.md` and `@NEXT.md` | Most agents read `AGENTS.md` by name; Gemini CLI: `.gemini/settings.json` with `"context": {"fileName": "AGENTS.md"}`; Aider: `read: AGENTS.md` in `.aider.conf.yml`. `AGENTS.md`'s first line tells any tool to read `NEXT.md` | Paste `AGENTS.md` and `NEXT.md` at the start of each chat |
| Session hooks | `.claude/settings.json`: start, before-edit, stop | Cursor's hooks (`.cursor/hooks.json`, events such as `afterFileEdit` and `stop`) can call the same three scripts; any other agent: the git hooks | `bash tools/hooks/install_git_hooks.sh`: git runs the check before every commit and push, for every tool and person |
| Required check before merge | GitHub ruleset "main is judged" on the Team plan | GitHub Free: make the repository public, or move to Pro; GitLab: protected `main` plus "Pipelines must succeed" under Settings → Merge requests → Merge checks; Bitbucket merge checks; Gitea or Forgejo branch protection | The owner merges by hand, and only after the check's green output is pasted on the pull request |
| CI runner | GitHub Actions (`checks.yml`) | GitLab CI, Bitbucket Pipelines, CircleCI, Buildkite, or a self-hosted runner: each runs `bash tools/check` | Run `bash tools/check` in the AI's workspace and paste the output; say where it ran |
| Scheduler | A Claude scheduled task on Haiku every 3 hours; one-time wakes into the coordinator; GitHub's cron as backup | n8n's Schedule Trigger; a free external cron service (such as cron-job.org) calling the workflow's dispatch address with a token that can only run this repository's workflows; Supabase `pg_cron` with `pg_net`; a Cloudflare Worker with a Cron Trigger; GitLab scheduled pipelines | An always-on computer's cron or launchd; or the owner's next message restarts the work, and the AI says exactly what it is waiting for |
| Hosting | GitHub Pages, built by the publishing run | Cloudflare Pages, Netlify, Vercel. If the host sets no `Last-Modified`, the run writes `published.txt` and `kit.json` names it as `stamp_url` | A private preview, or pictures of each screen sent as files |
| Database | Supabase PostgreSQL, its address only in the code host's secrets | Neon or any PostgreSQL; with none set, each run rebuilds a throwaway database from the readings kept in git (Happening's own fallback) | Files in the repository |
| Secrets | GitHub Actions secrets | GitLab masked and protected variables; Doppler; 1Password | The owner holds every key; the AI never sees one |
| Project space | The claude.ai Project, its instructions and documents | A ChatGPT Project, a Gemini Gem, a Notion page, a Google Drive folder, or `docs/` in the repository | One pinned document |
| AI memory | Claude's account and project memory | `OWNER_WORDS.md` plus a short preferences block in `AGENTS.md`; another AI's own memory | The Brain document, re-posted when it changes |
| Skills | Account skill `happening-operating-rules` (a pointer) and repository skills | Cursor or Codex rules files; ChatGPT custom instructions; the pointer text pasted into the project's instructions | Paste the pointer at the start of a chat |
| One update channel | One persistent Claude Code session, the Coordinating Work Stream | One pinned chat; a GitHub issue called "Coordinator" whose comments are the updates; a Slack channel; a weekly email draft the owner reads | One document called "Updates", newest first |
| Cheap helpers | The roles in `kit.json` "roles"; in Claude Code, `scout` and `reader` on Haiku, builders on Sonnet, the reviewer fallback on Opus | The model picker in Codex or Cursor; a separate chat on a small model; a batch call to a model's API | Scripts first; one chat per step |
| Reading other sites | Direct reading with a real browser (Playwright); Firecrawl once per place to find where its calendar lives; Common Crawl's index; Overture Maps places | Web search tools, plain downloads, the source's own feeds or keys | The owner's screenshots, read by the AI |
| The picture of the finished product | A design canvas of 18 boards, a checksum per board in the repository | Figma, Penpot, Excalidraw, or a slide deck of screenshots | Dated photos of sketches |
| Documents and PDFs | Claude Docs, exported as PDF | Google Docs, Notion, or Markdown in the repository printed to PDF | Markdown files |
| Visitor counts | PostHog (on hold until launch) | Plausible, GoatCounter, Cloudflare Web Analytics | Totals from the host's logs |
| Spend control | GitHub Budgets ($5 for Actions) and `tools/minutes_budget.py` (2,400 of 3,000 minutes) | GitLab compute quotas; hard caps at each provider | A weekly spend line from each provider's bill |

**Three things that have no stand-in:** proof the owner can open; one check that fails when the product is wrong; and no key that can delete live data. If a level cannot give these, it reports "not checked", never "passed".

## Ready prompts

Nine prompts come in `prompts/`, each written so a fresh AI with no memory can act on it. The first is the one to hand anyone.

| Prompt | Use it for | Where it goes |
| --- | --- | --- |
| `start-any-ai.md` | Installing the kit with any AI, at whatever level it can reach | Pasted as the first message |
| `project-instructions.md` | Charter, vision, goals and the four working lines every chat in the project reads | The project space's instructions |
| `coordinating-stream-pointer.md` | Naming the one session that gets all updates, and what every other chat does | A document in the project space |
| `helper-brief.md` | The brief the coordinator gives each helper: task, role, model, branch, limits, done, stop | Written by the coordinator for each step |
| `freshness-watch.md` | The recurring small-model task that starts the short publishing run when the product is stale, with five non-Claude ways to run it | A scheduled task, every 3 hours |
| `coordinator-wake.md` | A one-time wake back into the coordinator after a run it cannot watch | A one-time scheduled message |
| `handoff-note.md` | Moving to a new chat, session or AI without losing anything | Written before the move; named in the new session's first message |

Two more came in version 1.1.0: `weekly-review.md`, the weekly scheduled review of each project, and `kit-improvement.md`, the review every two weeks that carries lessons into the kit across all projects (see "Keeping it improving").

**The prompt to hand any AI** (`prompts/start-any-ai.md`, in full):

```markdown
You are setting up and then running the work for one owner, using the Owner-Run AI Build Kit. The owner does not read
code, reads on a phone, and judges by what they can see. Do the following, in order, and keep every message short
enough for one phone screen.

1. Say what you can do here, in one list: run commands, read and write files that last, reach a code host
   (GitHub, GitLab), open web pages, take screenshots, schedule a task, start helper sessions on smaller models,
   publish. Then name the install level you can reach:
   - Level A, full: a coding agent on a repository with a code host that can require a check before merge.
   - Level B, partial: files and commands, but no required check on a code host (or no hooks).
   - Level C, chat only: no files that last, no commands.
2. Install the Brain at that level. A and B: create the kit's files in the repository (AGENTS.md, CLAUDE.md,
   NEXT.md, STATE.md, OWNER_WORDS.md, kit.json, work/, docs/, prompts/), filling every {{...}} from what the owner
   has already given you and asking only for what is missing. C: keep one document called "The brain" holding the
   same sections, and re-post it in full whenever it changes.
3. Install the Harness at that level. A: the hooks (.claude/settings.json, or your tool's own hooks file), the git
   hooks (bash tools/hooks/install_git_hooks.sh), bash tools/check, and the required check on the code host; the
   owner switches the last one on, from your numbered steps. B: the git hooks and bash tools/check. C: one written
   check you will run on the owner's real result each time, with the owner's eye as the last test.
4. Prove it fires. Break one test on purpose, show the check go RED, restore it, show GREEN. Paste both outputs.
   "Couldn't verify" is never "passed".
5. Start the Loops. Build: one small step, the check, a result the owner can see. Run: the product's own timetable
   (a scheduled workflow) plus a freshness watch where scheduling is available. Owner: one place for every update
   (the Coordinating Work Stream). Failure: every failure becomes a failing test first.
6. Work in two lanes (AGENTS.md, "Who decides"): green work goes ahead with no approval and merges itself through
   `tools/checks/lane.py --pr`; red-lane items (spend past the monthly cap, a new paid service, production data or
   deploy settings, secrets, repo settings, the harness, legal, public posts, messages to people) go in NEXT.md under
   "Waiting on owner" with a recommendation, while other work goes on. Asks are numbered steps, one action a step,
   naming the button as written on the screen. Each role's model is in kit.json "roles", any vendor.

Then read NEXT.md (or "The brain") and do the one next step. From here on, AGENTS.md is your standing instruction.
```

Attach `kit-all-files.md` (or `install-kit.sh`) with it, so the AI has the files to install.

## File map

70 files. "Fill" means replace each `{{…}}` (find them with `grep -rn '{{' . | grep -v '\${{'`; GitHub's own `${{ … }}` expressions stay). "Set" means put your project's values in. "As is" means leave it.

| Path | Part | What it is | Change it? |
| --- | --- | --- | --- |
| `CLAUDE.md` | Brain | Loads `AGENTS.md` and `NEXT.md` into every Claude Code session | As is |
| `GEMINI.md` | Brain | Loads `AGENTS.md` and `NEXT.md` into Gemini CLI | As is |
| `AGENTS.md` | Brain | The standing rules; read by most coding agents | Fill |
| `NEXT.md` | Brain | The one next step | As is; the AI replaces it at each step |
| `STATE.md` | Brain | Where things stand, what runs by itself, what waits on the owner | Fill |
| `OWNER_WORDS.md` | Brain | The owner's words, quoted and dated | Fill with the owner's own words |
| `kit.json` | Harness | The settings every kit tool reads: live address, product folders, test command, limits, protected files | Set |
| `.gitignore` | Harness | Generated files never count as a change | As is; add your own |
| `requirements-kit.txt` | Harness | What the kit's tools need: pytest, pyyaml, lxml, cssselect | As is |
| `.claude/settings.json` | Harness | Claude Code's three hooks and the `opusplan` model setting | As is |
| `.claude/agents/scout.md` | Management | Small-model, read-only reader | As is |
| `.claude/agents/reader.md` | Management | Small-model batch reader of saved pages or documents | Name your reader's instruction file |
| `.claude/agents/builder.md` | Management | Mid-model builder of one work order | As is |
| `.claude/skills/operating-rules/SKILL.md` | Brain | Pointer skill for chats; upload it as an account skill too | Fill |
| `.github/CODEOWNERS` | Harness | The red-lane paths, owned by the owner | As is (set to @schubertsean-ui) |
| `.github/workflows/checks.yml` | Harness | The required check on every pull request, and again after each merge | As is; add your language's setup step |
| `.github/workflows/publish.yml` | Loops | The product's own timetable: minutes guard, build, never-empty guard, publish | Set the build commands and folder |
| `docs/ASK_THE_LAWYER.md` | Brain | The running lawyer list, one framed question per item | Fill as questions come up |
| `docs/IDEAS.md` | Brain | Every idea, with where it was written, unranked | Fill as ideas come up |
| `prompts/start-any-ai.md` | Management | Paste into any AI to install the kit | As is |
| `prompts/project-instructions.md` | Brain | Instructions for the project space | Fill |
| `prompts/coordinating-stream-pointer.md` | Loops | Names the one update channel | Fill |
| `prompts/helper-brief.md` | Management | The written brief a helper gets | As is; the coordinator fills one per step |
| `prompts/freshness-watch.md` | Loops | The recurring small-model task, with five non-Claude ways to run it | Fill the three names |
| `prompts/coordinator-wake.md` | Loops | One-time wake back into the coordinator | Fill per use |
| `prompts/handoff-note.md` | Management | The note written before moving to a new session | Fill per use |
| `tools/check` | Harness | The one product check | As is |
| `tools/checks/check.py` | Harness | The body of the product check | As is |
| `tools/checks/tests_untouched.py` | Harness | An existing test may not change in the same change as other files | As is |
| `tools/checks/test_floor.txt` | Harness | The fewest tests a full check accepts; the installer sets it | Raise it with `python3 tools/checks/floor.py raise`; only the owner lowers it |
| `tools/hooks/run` | Harness | Starts a hook from any folder; a missing hook reports, never blocks | As is |
| `tools/hooks/session_start.py` | Harness | Records the commit the session began from | As is |
| `tools/hooks/protect_tests.py` | Harness | Blocks edits to existing tests and checks | As is |
| `tools/hooks/stop_product_check.py` | Harness | Sends the AI back while the check is red | As is |
| `tools/hooks/install_git_hooks.sh` | Harness | Git's own gates, for any tool or person | Run once per copy |
| `tools/kitconf.py` | Harness | Reads `kit.json` for every tool | As is |
| `tools/orders.py` | Management | Work orders: `plan`, `run`, `faults`, `count` | As is |
| `tools/freshness.py` | Loops | Is the live product as fresh as it should be? | As is |
| `tools/stranded.py` | Loops | Which branches hold work that never reached `main` | As is |
| `tools/stranded_settled.txt` | Loops | Branches looked at and settled | Add a line per settled branch |
| `tools/minutes_budget.py` | Loops | Stops publishing runs past the month's CI minutes | Set the limits in `kit.json` |
| `tests/test_working_rules.py` | Harness | The working rules held as tests | As is |
| `tests/test_harness.py` | Harness | Tests that the hooks themselves work | As is |
| `work/ORDERS_FORMAT.md` | Management | The work-order format, the tests, and the rule on failures | As is |
| `work/ROLES.md` | Management | Coordinator, planner, builder and judge, step by step | As is |
| `work/Example.yaml` | Management | Three example orders, one of each common shape | Replace with your own |

**Added in version 1.1.1** (8 files)

| Path | Part | What it is | Change it? |
| --- | --- | --- | --- |
| `tools/checks/lane.py` | Harness | Green or red lane for a change; with `--pr`, the whole merge gate | As is; the paths are in `kit.json` "red_lane" |
| `tools/checks/floor.py` | Harness | Sets and raises the test floor; never lowers it | As is |
| `tools/spend.py`, `docs/SPEND_LEDGER.yaml` | Management | Every paid run logged before and after; exit 2 at the cap, a warning from 80% | Set `monthly_cap_usd` in `kit.json` |
| `.claude/agents/reviewer.md`, `prompts/reviewer-brief.md` | Management | The reviewer of another model, and its brief | As is |
| `GEMINI.md` | Brain | Points Gemini CLI at `AGENTS.md` | As is |
| `tests/test_lanes_and_spend.py` | Harness | Tests for the lanes, the floor, CODEOWNERS and the cap | As is |

**Added in version 1.1.0** (17 files)

| Path | Part | What it is | Change it? |
| --- | --- | --- | --- |
| `KIT_VERSION`, `CHANGELOG.md` | Learning | The kit version this project runs; what changed in each version and why | As is |
| `docs/APPS.yaml` | Management | Every outside app and API: access, key holder, hard cap, usage source, fallback, review dates; for APIs also key scope, limits, key rotation, terms, canary | Replace the examples with your own |
| `docs/LEARNINGS.md` | Learning | Lessons, each naming the check that now holds it | Add as lessons happen |
| `docs/SPEND.yaml` | Management | Each provider's bill, copied from the bill | Add each month |
| `.github/workflows/revert-on-red.yml` | Harness | A red check after a merge opens a revert pull request | Allow Actions to open pull requests |
| `prompts/weekly-review.md` | Loops | The weekly review of each project | Fill the names |
| `prompts/kit-improvement.md` | Learning | The review that carries lessons into the kit, across projects | Fill the names |
| `skills/owner-run-build-kit/SKILL.md` | Brain | The account skill that makes every project use the kit | Fill the kit's home |
| `tools/apps.py` | Management | Checks the app register; reviews due; API canaries | As is |
| `tools/api_client.py` | Management | The one way the product calls another app's API | As is |
| `tools/api_usage.py` | Management | Real API calls against each provider's limit | As is |
| `tools/scorecard.py` | Management | Delivery, quality and cost against the targets | Set the targets in `kit.json` |
| `tools/learnings.py` | Learning | Checks the lessons; lists the ones for the kit | As is |
| `tools/kit_drift.py` | Learning | Is this project on the newest kit? | Set `kit_home` in `kit.json` |
| `tests/test_ops.py`, `tests/test_api_client.py` | Harness | Tests for the registers, the scorecard and the API client | As is |

## Honest status

The kit's gates were run red and green in a scratch repository before it was sent; the code host's side and the publishing run were not, because they need the owner's accounts.

**Tested on 18 Nov 2026, in a scratch repository with a local remote**

- The installer wrote all 45 files, byte for byte identical to the source; run a second time without `--force` it kept every file.
- The kit's own 15 tests pass in a fresh copy; with one product test added, 16 pass and `bash tools/check` is GREEN.
- Every gate listed under "The Harness" went RED on a deliberate break and GREEN when restored.
- `orders.py`: `plan` found 4 deliberate gaps; `run` passed and failed `answers`, `text`, `share` and `command` tests against a locally served site; `faults` exited 1 on an open fault, 0 once the judge recorded it fixed, and 1 again when a passing order was broken on purpose.
- `freshness.py`: fresh (exit 0), stale (exit 1), no answer (exit 3); both date forms read.
- `minutes_budget.py`: with no GitHub token it says "could not tell" (exit 3) and lets the run go ahead; its decision rule gave the expected answer in six cases.
- Two faults in the kit itself were found by these runs and fixed before sending: Python's cache folders counted as a product change (a `.gitignore` now comes with the kit), and a same-second edit could be judged from stale compiled code (the check now writes none).

**Tested for version 1.1.1, 18 Nov 2026** (a fresh repository, `git init`, the installer, `origin/main` set locally because pushing was not used)

| Scenario | 1.1.0 | 1.1.1 |
| --- | --- | --- |
| Kit tests pass | 24 passed | 39 passed |
| `bash tools/check` on a fresh install | GREEN | GREEN |
| Break a test | RED | RED |
| Edit an existing test and product in one change | RED | RED |
| Delete a test file | **GREEN** (floor was 0) | RED (floor set to 39 at install) |
| Touch a red-lane path | nothing flags it | flagged, exit 4 |
| Lower the test floor | nothing flags it | flagged, exit 4 |
| Spend over the cap | nothing counts it | exit 2; a run that would pass the cap is refused; WARN at 82% |
| Add a test and raise the floor with product code | — | GREEN, green lane |
| The files in `KIT.md` against the installer | — | 0 differences (70 files) |
| The `checks` job on GitHub (gameday-hq pull request 1) | — | first run failed in 3 s (pip cache wanted a requirements.txt); fixed in 1.1.1 and held by a test |

Not tested in 1.1.1: `lane.py --pr` against a real pull request on GitHub (its parts are tested with recorded answers), and the ruleset with code owners on.

**Tested for version 1.1.0, the same day**

- All 62 files reinstalled byte for byte; the kit's 24 tests pass in a fresh copy; `bash tools/check --quick` GREEN.
- The API client against a local server: a rate-limited answer retried as told, then answered; the circuit opened after 5 failures and made no further call; a repeat answered from the cache; the key absent from the usage log and the cache; a missing secret named plainly.
- `apps.py check` refused each unsafe entry it is written to refuse; `learnings.py check` passed the two real lessons.
- `scorecard.py` and `minutes_budget.py` read Happening's real GitHub history (read-only): the numbers under "What the first scorecard showed".

**Not tested**

- The ruleset on a real code host, `checks.yml` and `publish.yml` running on GitHub, and the freshness watch as a scheduled task with this kit's file names. The Happening originals of all four are running.
- The hooks inside a live Claude Code session with the kit's copies; they were tested by calling them as Claude Code does. Cursor's hooks were not tried.
- The GitHub button names in "Setup in order" were not seen on screen.
- `orders.py` is a smaller, general version of Happening's `done.py`: it has no browser test that presses buttons and no screen-by-screen picture comparison. Add those as `extra_checks` in `kit.json` where a product needs them.
- The method comes from one product that has not publicly launched. No company run wholly by AI has been shown to work; what this supports is a business the owner runs, with a short list of decisions the owner holds.

* Version 1.1.0: `revert-on-red.yml` and the two scheduled reviews have not run; `apps.py canary` has not called a real API (the example entry is a placeholder); the kit's home repository does not exist yet.

**Where it came from:** the Happening repository's main branch at commit `d0d9ac2` (18 Nov 2026, 07:28 UTC), its Project documents, and the owner's dated words in `OWNER_WORDS.md`. Every rule, number and process in the kit is the AI's choice, labelled as such, except the owner's quoted words (1.1.0 was written by Claude; 1.1.1's changes by Grok Bot).

**Sources**

- [AGENTS.md](https://agents.md) — the agents that read `AGENTS.md`, and the Gemini CLI and Aider settings.
- [GitHub Docs: About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) — rulesets on private repositories need Pro, Team or Enterprise Cloud.
- [GitLab Docs: Auto-merge](https://docs.gitlab.com/user/project/merge_requests/auto_merge/) — "Pipelines must succeed", available on the Free tier.
- [InfoQ: Cursor 1.7 adds hooks](https://www.infoq.com/news/2025/10/cursor-hooks/) — Cursor's hook events, including `afterFileEdit` and `stop`.

* [Claude Help Center: Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude) — custom skills in Customize → Skills; enabled skills load in Claude Code signed in with the same account, synced about every 10 minutes, one way.
* [Claude Help Center: Understanding Claude's personalization features](https://support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features) — account Instructions apply to all conversations; project instructions only inside that project.
