# Agent workflows

Recommended workflows for AI agents working in `apex-oncology`. These assume you have
read [`AGENTS.md`](../AGENTS.md).

Every workflow below follows the same principle: **narrow before you read.** Establish
the franchise, consult declared metadata, then open only the files that metadata names.

---

## Workflow 1 — Explain a script

The most common request. *"For Venclexta, explain what `trx_monthly.sql` does."*

1. **Establish the franchise.** It is usually named. If not, ask — do not guess and do
   not search all three.
2. **Read `franchises/<F>/CONTEXT.md`.** Business framing first; it determines whether
   the script's logic makes sense.
3. **Look the script up in `franchises/<F>/manifest.yaml`.** This gives declared
   inputs, outputs and config dependencies without reading anything else.
4. **Read the script.**
5. **Read only the config files the manifest named.** Not all of `configuration/`.
6. **Answer in this order:** what it produces → what it reads → which business rules
   shape the output → what the user must supply at run time.

Step 6's last item is the one users value most and agents most often skip. See
Workflow 3.

**Do not** read a second franchise. **Do not** grep the repo for the table names you
found — the manifest already records where they come from.

## Workflow 2 — Find which script does X

*"Which Venclexta script produces the specialty pharmacy view?"*

1. Read `franchises/<F>/manifest.yaml` first. Script entries carry purpose, inputs and
   outputs; matching on that metadata is faster and more accurate than content search.
2. If the manifest doesn't resolve it, search within the franchise only:
   `franchises/<F>/**`. Never repo-wide.
3. If nothing matches, say so. Do not offer the nearest script from another franchise
   as though it were equivalent.

If you find the script by search but it has no manifest entry, that is a finding worth
reporting — an unregistered script is invisible to every other agent.

## Workflow 3 — Identify unresolved user inputs

Often the whole request, and always part of Workflow 1.

Many scripts ship with deliberate blanks that a user fills in per run. Surface them;
never autofill them. Look for:

- Blank or open-ended date bounds — reporting period, data month, snapshot date
- Empty `IN ()` lists — product, market, geography, account
- Unset market or brand filters
- Macro variables and runtime parameters with no default
- Config keys present but empty

Report each as a required input with the business question it answers ("which reporting
month?"), not as a defect. If a blank looks like an actual bug rather than an input,
say which reading you favour and why.

## Workflow 4 — Trace a configuration value

*"Where does the market code filter come from?"*

1. Find the script's entry in `manifest.yaml`; note its declared config dependencies.
2. Read those config files and locate the key.
3. Report the full path: config file → key → where the script consumes it → what it
   affects in the output.
4. If the value is hardcoded in the script instead of read from config, flag it. That
   is a convention violation worth fixing.

## Workflow 5 — Assess blast radius before a config change

Configuration under `franchises/*/configuration/` is production-affecting. Before
changing it:

1. Search within the franchise for every script referencing that config file, and
   cross-check against `manifest.yaml`.
2. List each affected script and what its output feeds.
3. State the blast radius plainly before making the edit — which outputs move, and
   whether any are business-facing.
4. Make the change only after that is on the record.

Never change a config value to make a script produce an expected result. Fix the logic
or raise the discrepancy.

## Workflow 6 — Annotate a script

Annotate **in place**, with comments. Do not produce a standalone markdown document.

1. Add the header block from
   [`templates/TEMPLATE_SCRIPT.md`](../templates/TEMPLATE_SCRIPT.md) — objective, user
   inputs, source tables, output. Keep it under ~15 lines.
2. Describe each source table once, on first reference. Look descriptions up in
   [`data-dictionary.md`](data-dictionary.md) before writing your own; if you must
   infer one, mark it as inferred.
3. Mark every unresolved user input at the line where it appears.
4. Comment the business rules that materially shape the output.
5. Stop.

Scale annotation to business complexity, not line count. A single-table lookup wants a
header and a few comments; a multi-step ETL with window functions and cohort logic
wants full annotation.

Comment for intent, not syntax. Skip `GROUP BY`, `DISTINCT`, `CAST`, `COALESCE`,
aliases, basic joins and simple aggregations unless one carries business meaning.
Prefer `/* Latest active factor selected */` over
`/* ROW_NUMBER() ranks by DATA_MONTH DESC */`.

Preserve the original code exactly. It must still run with all comments stripped.

## Workflow 7 — Add or change a script

1. Confirm the franchise and read its `CONTEXT.md`.
2. Follow [`conventions.md`](conventions.md) for naming and file placement.
3. Put every parameter, path, secret name and business-rule value in `configuration/`.
   Hardcode nothing.
4. Register the script in `manifest.yaml` **in the same change** — inputs, outputs,
   config dependencies, purpose.
5. Add the header block from `TEMPLATE_SCRIPT.md`.
6. Clear notebook outputs before committing.
7. Work through the [PR checklist](../.github/pull_request_template.md).

## Workflow 8 — Onboard a franchise

Copy `templates/`; do not hand-roll. Full steps in
[`templates/TEMPLATE_FRANCHISE.md`](../templates/TEMPLATE_FRANCHISE.md). The step most
often forgotten is registering the franchise in
[`.mcp/context.yaml`](../.mcp/context.yaml) — without it the franchise is invisible to
MCP clients even though the files exist.

## Workflow 9 — Cross-franchise requests

Legitimate occasionally: *"which franchises use the syndicated claims table?"*

1. Say which franchises you are loading, before loading them.
2. Read each franchise's metadata independently. Do not let one franchise's rules
   inform your reading of another.
3. Report per franchise, with differences called out explicitly. Never present a rule
   from one franchise as though it were repository-wide.

If a request looks cross-franchise but is really about one, treat it as one and say so.

---

## Anti-patterns

| Don't | Do |
|---|---|
| Load the whole repository | Scope to one franchise |
| Grep repo-wide for a table name | Read the franchise `manifest.yaml` |
| Read all of `configuration/` | Read only the files the manifest names |
| Autofill a blank filter | Surface it as a required user input |
| Invent a table description | Look it up in `data-dictionary.md`; mark inferences |
| Answer from a similar script in another franchise | Say the target franchise has no match |
| Write a separate documentation file | Annotate the code in place |
| Reformat a script you were asked to explain | Change nothing |
| Trust a stale manifest | Prefer the script; report the drift |
| Run a script against production to check | Reason from code; state what you couldn't confirm |

## Worked example

> For Venclexta, explain the purpose of `<script>`, identify all configuration files it
> consumes, and summarize the business rules that can change its output.

Resolution path: `franchises/Venclexta/CONTEXT.md` → `manifest.yaml` (locate the script,
read its declared dependencies) → the script → only the config files named. Answer with
purpose, config files and their keys, the business rules that shape the output, and the
run-time inputs the user must supply.

`franchises/Epkinly/` and `franchises/Imbruvica/` are never opened.
