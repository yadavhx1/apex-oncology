# CLAUDE.md

Entry-point context for Claude Code in `apex-oncology`.

**Read [`AGENTS.md`](AGENTS.md) first — it holds the operating rules and they apply in
full here.** This file adds only what is specific to working through Claude Code.

---

## Repository in one paragraph

Configuration and analytical workloads (Python, SQL, notebooks) for three oncology
franchises — `Venclexta`, `Epkinly`, `Imbruvica`. Each franchise directory is
self-contained: `CONTEXT.md` for business framing, `manifest.yaml` for the script
inventory and its dependencies, `configuration/` for the YAML/JSON a script consumes,
`scripts/` for the workloads themselves.

## Navigating efficiently

The context chain is `AGENTS.md` → `.mcp/context.yaml` → `franchises/<F>/CONTEXT.md`
→ `manifest.yaml` → script → `configuration/*`. Enter as far down that chain as the
question allows.

- **Scope to one franchise.** This is the rule that matters most. Reading a second
  franchise to answer a single-franchise question yields wrong answers, because the
  business rules differ. Glob and Grep with a franchise-scoped path
  (`franchises/Venclexta/**`), not a repo-wide one.
- **Start from the manifest, not from a filesystem sweep.** `manifest.yaml` already
  records what each script reads and writes. Use it instead of grepping for table
  names across the repo.
- Use `Read` on the specific config files the manifest names. Do not read all of
  `configuration/`.

## When explaining a script

Answer in this order: what it produces, what it reads, which business rules shape the
output, and what the user must supply at run time. That last one is easy to miss and
the most useful — blank dates, empty `IN ()` lists, unset market or product filters
are deliberate user inputs. Name them explicitly.

Use pharma vocabulary the business audience already uses — patient, HCP, prescriber,
account, product, brand, market, claims, TRx, NBRx, specialty pharmacy, site of care.
Prefer "latest active factor selected" over "`ROW_NUMBER()` ranks by `DATA_MONTH DESC`".

## When changing a script

- Annotate in place with comments; do not produce a separate markdown write-up.
  `templates/TEMPLATE_SCRIPT.md` has the expected header block.
- Comment for business context, not for syntax. If a competent analyst would
  understand a line by reading it, leave it alone.
- Update the franchise `manifest.yaml` in the same change if you added, renamed or
  re-pointed a script.
- Never hardcode a value that belongs in `configuration/`.

## Hard limits

No secrets, no patient-level data, no committed notebook outputs — see `AGENTS.md` §6.
Do not execute scripts against production sources to verify behaviour; reason from the
code and say what you could not confirm.

## Where things are

| Need | Path |
|---|---|
| Operating rules | `AGENTS.md` |
| Machine-readable repo map | `.mcp/context.yaml` |
| Architecture and ownership | `docs/architecture.md` |
| Agent workflows | `docs/agent-workflows.md` |
| MCP resources and tools | `docs/mcp-integration.md` |
| Naming and metadata rules | `docs/conventions.md` |
| Table and field definitions | `docs/data-dictionary.md` |
| Adding a franchise | `templates/TEMPLATE_FRANCHISE.md` |
