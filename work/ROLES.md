# work/ROLES.md — what each role does, step by step

`work/ORDERS_FORMAT.md` is the format of an order and the rule on failures. This file is the procedure. One session
takes one role for one order (or one screen); it never judges what it built.

## Coordinator — the one session the owner talks to
1. At each of the owner's messages: `python3 tools/freshness.py`, `python3 tools/stranded.py`, `python3 tools/orders.py faults`, the open pull requests, and the project space. Anything red comes first.
2. Pick the step: the oldest open fault, else the next line of `NEXT.md`.
3. Hand it to a fresh helper with a written brief (`prompts/helper-brief.md`): the model of its role in `kit.json` "roles", its own branch. A paid helper first passes `python3 tools/spend.py before ...`; at the cap, paid work halts and unpaid work goes on.
4. When its pull request is green on the code host: the reviewer (another model) reads it (`prompts/reviewer-brief.md`). `python3 tools/checks/lane.py --pr <n>` says MERGE OK: mark it ready and merge (`gh pr ready <n>`, `gh pr merge <n> --squash`; never `--admin`, never force-push). RED: it waits in `NEXT.md` under "Waiting on owner"; go on with green work. NOT YET: split it or wait for the review. If the merge starts no publishing run and the product must change, start one by hand.
5. Watch the run on the thing itself (the live product's publish time, `tools/freshness.py`), not a guess at its length. Then judge: `python3 tools/orders.py run --record`.
6. Update `NEXT.md` and `STATE.md`, with the morning summary (AGENTS.md, "Who decides"); send the owner one message that leads with what they can now see.

## Planner — writes a screen's orders (`work/<Screen>.yaml`)
1. Read `work/ORDERS_FORMAT.md`.
2. List every value and button on the screen of the approved picture, numbered. Every number must end up in an order.
3. Read the code that builds the page, far enough to name the real file and the real mark on the page for each value.
4. Fetch the live page into a scratch folder and find each value's mark in it.
5. Write one order per distinct value or button. Rows that repeat share one order. Fill every slot: real paths in backticks; a pass mark with its evidence; `how` steps a builder can do without asking; `if_it_fails` with at least two rungs of the ladder, each ending in an action.
6. Everything wrong goes in as `kind: fault` with `found`, `seen_how`, `next`. Its test must fail for that reason today.
7. Check: `python3 tools/orders.py plan` prints no line for your file; `python3 tools/orders.py run <Screen>` — every test RUNS (a "test itself broke" is your error, fixed now).
8. Read every PASS again: passing for the right reason, or is the selector too wide? Read every FAIL again: product or test?
9. Write only your own file. Do not fix the product: that is a builder's order.

## Builder — makes one order pass
1. `python3 tools/orders.py faults`. Take the oldest open fault, or the order you were given. One order.
2. Read the order. See it fail: `python3 tools/orders.py run <id>`.
3. Have real data to build from (the project's own command, in `AGENTS.md`, "Commands").
4. Follow `how`. Write or extend a test in `tests/` that fails before the change and passes after it.
5. See the order pass on the built copy: `python3 tools/orders.py run <id> --site <built folder>`.
6. `bash tools/check --base origin/main` must be green, with nothing skipped for want of a database or a browser.
7. Commit on your branch, push, open a draft pull request whose body says `builder-model: <model>`. The coordinator merges through the gate.
8. Two tries that do not pass: write under `tried:` what was done and what was seen, and change the method. A third: the largest model looks for the cause first.
9. Never: edit `pass` or `test`, weaken a check, or end at "reported".

## Reviewer — passes or fails one pull request it did not write
1. Follow `prompts/reviewer-brief.md`: the whole diff, `bash tools/check --base origin/main`, `python3 tools/checks/lane.py`.
2. One comment: `REVIEW: PASS <head sha>` or `REVIEW: FAIL <head sha>`, then `reviewer-model: <model>`. Never edit, push or merge.

## Judge — says whether it is done
1. After the publishing run: `python3 tools/orders.py run --record`. All orders, not only the one built: this is how something that broke elsewhere is found.
2. `python3 tools/orders.py faults`. Anything open goes back to a builder.
3. A screen whose every order passes: a picture of the live screen beside its approved picture goes to the owner — their eye is the last test of a screen.
4. Commit `work/seen.json`.
