# Project instructions — paste into the project space every chat in the project reads
# (Claude: Project → Instructions · ChatGPT: Project → Instructions · Gemini: a Gem's instructions · Notion AI: a pinned page)

{{PROJECT}}.

Charter: "{{owner's words}}"
Vision: "{{owner's words}}"
Goals: "{{owner's words}}" · "{{…}}"

How work runs here:
- The rulebook is AGENTS.md in the repository schubertsean-ui/gameday-hq (or the document "The brain" if there is no repository).
  When this text and that file disagree, the file wins. Disk is truth; chat memory is not.
- The next step is in NEXT.md. Say it in your first reply, and whether this chat is doing it.
- One place gets every update for the owner: the Coordinating Work Stream ({{link}}). Any other chat does its one task,
  leaves its result on the code host as a branch and draft pull request, puts any words of the owner's it heard into
  OWNER_WORDS.md, and sends the owner no separate status.
- Two lanes (AGENTS.md, "Who decides"): green work goes ahead and merges itself through the gate, with no approval;
  red-lane items (spend past the $50 monthly cap or a new paid service, database changes, anything touching money
  (payments, Stripe, billing, pricing), deploy settings, secrets,
  repo settings, the harness, legal, public posts, messages to people) go in NEXT.md under "Waiting on owner", as one
  plain paragraph with a recommendation, while other green work goes on.
- Files are sent one by one, never zipped. A document comes as a link and as a PDF.
