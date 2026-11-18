# The written brief the coordinator gives each helper (one step, one branch, one model)

Helpers start with no memory. Everything they need is in the brief or in files the brief names.

```
Task: {{order id}} — {{what the customer will see, in the picture's words}}
Role: builder (work/ROLES.md, "Builder"). Model: {{kit.json roles: builder for code · reader or scout for reading}}.
Branch: {{short-name}} from origin/main. One draft pull request; its body says `builder-model: <model>`. Do not merge.
Read: AGENTS.md, NEXT.md, the order in work/{{File}}.yaml, and only the files its `from`, `kept`, `shown` and `how` name.
Inputs: {{the data, pages or pictures it needs, with paths}}
Limits: do not edit existing tests, checks, kit.json, or the order's pass and test. No red-lane path (kit.json
"red_lane"). No money past the cap (`python3 tools/spend.py before ...` first), accounts, keys, messages or publishing.
Done means: `python3 tools/orders.py run {{id}} --site {{built folder}}` PASSES and `bash tools/check --base origin/main`
is GREEN; NEXT.md and STATE.md updated in the same change; the pull request open.
Stop and say why when: the test looks wrong; a step is red lane (AGENTS.md, "Who decides"); two tries have failed
(write them under `tried:` in the order first).
End with: what changed, the check's last lines and where it ran, the pull request link, what you assumed, what you did not verify.
```
