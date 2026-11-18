# work/ — the work orders (the paint-by-numbers plan)

One file per screen of the approved picture (`work/<Screen>.yaml`) and one per part of the machine (`Data`, `Reading`,
`Running`). Each file is a list of **orders**. An order is one thing a customer can see or press, or one thing the
machine must do, written so that a worker who has never seen the project can build it and a machine can say whether it
is done. `python3 tools/orders.py --help` lists the commands. Every number and method here is the AI's choice.

## The three roles — never the same session for one order
- **Planner** writes the order from the picture and the code. Changes `pass` and `test` only with the reason written in the order.
- **Builder** does one order: follows `how`, runs the order's test on a built copy (`--site <folder>`), stops when it passes. Never edits `pass` or `test`.
- **Judge** has no memory of the build. Runs `python3 tools/orders.py run --record` after a publishing run and looks at the page. Only the judge's run moves the count.

## The slots — all must be filled; `python3 tools/orders.py plan` refuses an empty one
```yaml
- id: Main.03                  # the file's name, a dot, a number. Never reused.
  kind: build                  # build = on the picture and to be made right · fault = something is wrong (see "Failures")
  what: "Each row shows the item's photo, under its time"      # what the customer sees, in the picture's own words
  from: "The item's own page at its source"                     # where the value comes from in the world
  kept: "`schema/items.sql` (new), items.image_url"             # where it is stored: real paths in backticks; (new) for one this order creates
  shown: "`site/templates/list.html`, `img.photo` in `li.item`" # the code that puts it on the page, and its mark on the page
  pass: "A photo on at least 99% of rows — 1,151 of 1,163 sources carry one (count of 16 Nov)"   # the pass mark, with the evidence for the number
  test: {type: share, page: "/list.html", of: "//li[@class='item']", with: ".//img", at_least: 0.99}  # the same, for the machine
  how:                         # the steps, in order, naming files and functions; a step a small model can do without asking
    - "In `site/build.py` keep pictures on every day shown, not only the first"
  if_it_fails:                 # at least two lines: what is seen, then what is DONE about it. Never "report it".
    - "The source shows a photo and none was read: a reader fault — fix the reader, add the page to its test"
    - "The page passes its byte limit: move later days to their own file; do not raise the limit"
  needs: []                    # orders that must pass first
  owner: "no"                  # "no", or the one thing only the owner can supply (money, an account, a credential, publishing)
```
A fault also carries: `found:` (the day), `seen_how:` (the command and its output, or the link, that shows it), `next:` (the exact next action).
After two failed tries the builder adds `tried:` (what was done, what was seen) and the method changes.

## The pass mark
- A value every item has by nature (a name, a date, a link): 100%.
- A value the source carries for some items: the share a complete reading would reach, with the count that shows it. Never set at today's measured value just so that it passes.
- A value the picture shows on every row and sources rarely carry: a second source must fill it; the order names it.
- Something a customer presses: a test that presses it (add a browser test to your check if your product needs one).
- Where no machine can tell (a real voice, the lawyer's answer, the owner's eye on a side-by-side): `type: person`, which never passes without proof.

## The tests — each reads the live product (or a built folder with `--site <folder>`)
| type | keys | passes when |
|---|---|---|
| `answers` | `page` or `pages` | every page answers 200 |
| `text` | `page`, `has: [regex]`, `lacks: [regex]` | the visible words do, and do not, say them |
| `count` | `page`, `css` or `xpath`, `at_least` / `at_most` / `exactly` | that many elements match |
| `share` | `page`, `of` (the rows), `with` (inside a row), `at_least` (default 0.99) | that share of rows has it |
| `bytes` | `page`, `at_most` | the page is no larger |
| `command` | `run` | the command exits 0 (for the database, the reader, the runs) |
| `person` | `proof`: a file under `evidence/`, or `words: …` found in `OWNER_WORDS.md` | the proof exists |
A selector that starts with `/`, `./` or `(` is XPath; anything else is CSS and needs the `cssselect` package.

## Failures — reported is not enough; only reported and fixed is acceptable
1. **A failure is written down as a failing test first.** Whoever sees something wrong adds an order of `kind: fault` whose test fails for that reason. That is the report.
2. **The session that finds it fixes it.** When the fix needs a publishing run, the session watches the run and looks at the product. When it needs something only the owner can supply, `owner` names it, the owner gets the steps, and `if_it_fails` says what is done meanwhile so the product stays right.
3. **Fixed means its test passes on the live product,** written by `run --record`. Nothing else closes a fault.
4. **A fixed fault's test runs for ever.** Anything that passed once and fails now is a fault again, first in line.
5. **Faults come before building.** `python3 tools/orders.py faults` exits 1 while one is open; a session starts there.
6. **A second failed try changes the method,** and the order says what was tried. A third goes to the largest model for the cause.

The ladder every `if_it_fails` follows — find the first rung that is true, and do what it says:
1. *It is not at the source.* Name a second source and read it; only when nothing in the world carries it is the picture itself a question for the owner.
2. *It is at the source and was not read.* A reader fault: fix the reader, add the page to its test.
3. *It was read and refused on the way in.* Read the run's log; fix the rule or the reading.
4. *It is stored and not on the page.* A template or build fault.
5. *It is on the page and wrong.* Find which of 1–4 made it wrong; add a test with that page.
6. *It passes on a built copy and fails live.* The run did not publish: read the run, start it again, watch it.
7. *It needs money, an account, a credential or the lawyer.* Send the owner the steps; do the stand-in until then.
