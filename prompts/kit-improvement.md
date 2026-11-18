# The kit-improvement review — ONE for the whole account, a recurring scheduled task (mid model), every two weeks

This is how a lesson learned on one project reaches every project. It reads every project's lessons and scorecards,
carries the ones marked `kit: yes` into the kit's home repository as a new version, and proposes the skill update.

**Settings:** every other week (for example `CRON_TZ=America/Chicago 43 7 1-7,15-21 * 2`, the first and third Tuesday) ·
model: the builder role's model (`kit.json` "roles"); the reviewer role's model to judge the final diff · notifications: one push when it finishes.

**Prompt (replace the names):**

Kit-improvement review. The kit's home is the repository schubertsean-ui/owner-run-kit; the projects using it are listed in
`kit-home/PROJECTS.md` (one `owner/repo` a line). One pull request to the kit's home at most. Never merge a change to the
kit's tests, checks or hooks: those wait for the owner's approval (CODEOWNERS).

1. Attach and clone the kit's home and each project in `kit-home/PROJECTS.md` (shallow).
2. In each project: `python3 tools/learnings.py kit` and `docs/SCORECARD.md`. Collect every `kit: yes` lesson not yet
   shipped, with the check that holds it.
3. For each lesson: is it general (true for any product) and is its check product-neutral? If yes, bring the check and
   the rule into the kit's home (generalised: no product names, no project paths). If not, write why in one line.
4. Look across the scorecards: a target missed in two or more projects is a kit problem — propose the change that
   would have prevented it.
5. Keep the kit small: a new rule only after a real failure, and only when a check cannot hold it; `AGENTS.md` stays
   under 100 lines; a rule that no project needed in 60 days is proposed for removal.
6. Bump `KIT_VERSION` (minor for additions, patch for fixes), write the version in `CHANGELOG.md` with each lesson's
   source project and date and the files to bring in, rebuild `install-kit.sh` and `kit-all-files.md`
   (`python3 kit-home/build.py . kit-home`), and run the kit's own tests in a fresh copy.
7. Open the pull request. In each project's lesson, set `kit:` to "yes — shipped in kit X.Y.Z" in that project's next
   step (do not push to the projects from here).
8. If `skills/owner-run-build-kit/SKILL.md` changed, propose the updated account skill to the owner as a review card.
9. Send the owner one message: the new version in one line, what each project gains, and the skill card if any.
