---
name: operating-rules
description: Load at the start of every chat about this project, and whenever the owner asks for a plan, build, review, status, decision list or document for it. Points to the one rulebook (AGENTS.md in the repository), makes the chat name the next step in its first reply, and says where results go.
---

# Operating rules — a pointer, not a copy

The standing rules are one file: `AGENTS.md` on the main branch of the repository schubertsean-ui/gameday-hq. When this skill and
that file disagree, the file wins. Disk is truth; chat memory is not.

## First, in every chat
1. **Find the next step.** Attach the repository if the chat has none, and read `NEXT.md`. If the repository cannot be
   reached, read the newest handoff note in the project space and say that is what you used.
2. **Say it in the first reply, in one line:** what the next step is, and whether this chat is doing it. A chat given
   another task (reading, research, a document) says so, then does its task.
3. **Who gets updates:** only the Coordinating Work Stream talks to the owner about progress. This chat does its one
   task, leaves the result as a branch and draft pull request (green lane: no approval needed), and adds any words of
   the owner's it heard to `OWNER_WORDS.md`. A red-lane item (AGENTS.md, "Who decides") goes in `NEXT.md` under
   "Waiting on owner"; the chat then goes on with green work.

## What to read, and when (whole, not skimmed)
- Always: `AGENTS.md` and `NEXT.md`. For a build step: `STATE.md`, the order in `work/`, and only the files it names.
- The owner's decisions: `OWNER_WORDS.md`. Before asking the owner anything, check the record: never re-ask an open
  item, never ask what the record already answers.

## Kept in every chat
- Only the owner's own quoted, dated words carry the owner's name. Every technical rule, number and process is the AI's
  and is labelled so.
- Do not rule on what another party's terms mean: quote them and add the question to `docs/ASK_THE_LAWYER.md`.
- Plain language, direct links, short enough for a phone. A document comes with a PDF; files are sent one by one,
  never zipped. Lead every message with what the owner can now see.

## Before the chat ends
Leave the work where it outlives the chat, say where, and say what exists only in this chat's workspace.
