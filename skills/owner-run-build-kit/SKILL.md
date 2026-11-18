---
name: owner-run-build-kit
description: Use at the start of any build, product, app, site or venture work for the owner, in any project or chat, and when the owner says "use the kit", "set up the brain", "harness", "loops", or asks how a project is run, managed, measured or improved.
---

# The Owner-Run AI Build Kit — how every project is run

The owner's projects all run on one kit: a Brain on disk, a Harness of gates the AI cannot get around, five Loops,
and a management layer run the way Google's and Cursor's engineering leads run theirs. The kit's home is the GitHub
repository schubertsean-ui/owner-run-kit (`KIT_VERSION`, `CHANGELOG.md`, `install-kit.sh`, `kit-all-files.md`, the guide).
The guide: `GUIDE.md` in the kit's home (first published at https://claude.ai/artifact/HhoG4CSkSEshCACYMeKD9R).

## At the start of any project work
1. **Is the kit installed?** Look for `AGENTS.md`, `NEXT.md` and `kit.json` in the project's repository.
   - Yes: `AGENTS.md` is the rulebook from here on; say the step in `NEXT.md` in the first reply and whether this chat
     is doing it; run `tools/freshness.py`, `tools/stranded.py`, `tools/orders.py faults` and give their lines.
   - No repository yet: propose installing the kit (attach the kit's home, run `bash install-kit.sh` in the new
     repository), then follow `prompts/start-any-ai.md` from the kit.
   - No way to reach GitHub here: ask the owner to attach `kit-all-files.md`, or work at Level C (one document called
     "The brain", re-posted when it changes) and say which level is in use.
2. `python3 tools/kit_drift.py`: if BEHIND, bring the newer kit in with the next step (protected files in a spec session).

## Always
- Two lanes (AGENTS.md, "Who decides"). Green: the AI builds, tests and merges its own pull request once the check is
  green, another model's review passed and `tools/checks/lane.py --pr` says MERGE OK — no approval, day or night. Red
  (spend past the monthly cap or a new paid service, database changes, anything touching money (payments,
  Stripe, billing, pricing), deploy config, secrets, repo settings, the
  harness, legal, public posts, messages to people, force-push): written in `NEXT.md` under "Waiting on owner", and
  other green work goes on. A morning summary in `STATE.md` says what got done, what waits, and spend against the cap.
- Proof the owner can open, or "not checked". One check fails when the product is wrong; never weakened. No key that
  can delete live data. Wait on the thing itself, not a guess.
- The cheapest thing that gets it right: a script first, then each role's model in `kit.json` "roles" (any vendor; the
  reviewer differs from the builder). Every paid run is logged before and after (`tools/spend.py`); paid work halts at
  the cap. One step per session. Every app is in `docs/APPS.yaml` with a hard cap and a fallback.
- Only the owner's quoted, dated words carry the owner's name; every technical choice is the AI's and says so.
- Files one by one, never zipped; a document comes as a link and a PDF.

## The learning loop — every chat feeds it
- A correction, a failure or a surprise becomes a check first, then an entry in `docs/LEARNINGS.md` naming that check.
  Mark it `kit: yes` when it would help any project.
- A chat that cannot write to a repository puts the lesson in its handoff note or the project space, in the same form,
  so the next session can file it.
- Each project's weekly review (`prompts/weekly-review.md`) and the account's kit-improvement review
  (`prompts/kit-improvement.md`) carry lessons into the kit's home as a new version; this skill is updated by a review
  card the owner saves.
