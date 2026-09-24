# Pull request

## What and why

<!-- What changes, and the business reason. One or two paragraphs. -->

**Franchise:** <!-- Venclexta | Epkinly | Imbruvica | repository-wide -->

**Type:** <!-- new script | script change | configuration change | context/docs | agent guidance | franchise onboarding -->

## Impact

<!--
Which outputs move as a result of this change, and does anything business-facing
consume them? For a configuration change, state the blast radius: every script that
reads the changed file. "None" is a valid answer — say it explicitly.
-->

---

## Checklist

Delete sections that don't apply. Don't tick a box you haven't actually checked.

### Safety — every PR

- [ ] No credentials, tokens, connection strings, API keys or passwords in any file
- [ ] Secrets referenced by name only; values resolve from environment or vault at run time
- [ ] No patient-level or otherwise identifiable data
- [ ] No data extracts, result sets or CSVs
- [ ] Notebook outputs cleared
- [ ] I have reviewed the full diff, not just the files I meant to change

### AI context validation — every PR

The point of this section: an agent must be able to answer questions about this change
from metadata alone. Stale metadata is worse than missing metadata, because agents are
told to trust it.

- [ ] Franchise `manifest.yaml` updated if a script was added, renamed or re-pointed
- [ ] Manifest entry is complete — purpose, owner, schedule, configuration, source tables, outputs, user inputs, depends_on
- [ ] Manifest matches the script's actual dependencies (no drift)
- [ ] `configuration:` list in the manifest updated if a config file was added or removed
- [ ] Franchise `CONTEXT.md` updated if business rules, data sources, owners or caveats changed
- [ ] Business rules implemented in configuration are traceable to `CONTEXT.md`
- [ ] `.mcp/context.yaml` updated if repository structure changed — new franchise, new docs page, changed context chain
- [ ] `docs/data-dictionary.md` updated for new source tables and for every new final output table, including column derivations
- [ ] No franchise-specific content placed outside its franchise directory
- [ ] No script reads another franchise's configuration

### Scripts

- [ ] Header block present — objective, user inputs, source tables, output ([`TEMPLATE_SCRIPT.md`](../templates/TEMPLATE_SCRIPT.md))
- [ ] Every table described once on first reference, tier labelled (Repository / Inferred)
- [ ] Every unresolved user input marked at its line with `USER INPUT REQUIRED`
- [ ] Business rules that shape output are documented
- [ ] Comments carry business context, not syntax; annotation proportional to business complexity
- [ ] No configurable value hardcoded — parameters, paths, table names, thresholds and code lists read from `configuration/`
- [ ] Naming follows [`conventions.md`](../docs/conventions.md); no `_final`, `_v2`, `_new`, `_old` or dates in filenames
- [ ] Script runs unchanged with all comments stripped

### Configuration changes

- [ ] Blast radius stated above — every script reading this file is listed
- [ ] Change is business-approved if it alters a business rule
- [ ] No value changed merely to make a script produce an expected result
- [ ] Deliberately blank user inputs left blank
- [ ] Comments explain business meaning, not type
- [ ] Config change is separated from logic changes where practical (different risk, different reviewers)

### Franchise onboarding

- [ ] Full checklist in [`TEMPLATE_FRANCHISE.md`](../templates/TEMPLATE_FRANCHISE.md) worked through
- [ ] Franchise registered in `.mcp/context.yaml`
- [ ] `CONTEXT.md` business rules and known caveats genuinely completed, not left as `TODO`
- [ ] Named owners recorded
- [ ] `docs/architecture.md` layout tree and ownership table updated

### Agent guidance changes

Changes to `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` or
`.mcp/context.yaml` affect every franchise and every agent.

- [ ] Rule changed in `AGENTS.md` first; client files defer to it rather than restating
- [ ] Client-specific files still consistent with `AGENTS.md`
- [ ] `.mcp/context.yaml` consistent with the human-readable docs
- [ ] Reviewed by a repository maintainer

---

## Testing / verification

<!--
How you know this is right. Reasoning from the code is acceptable — say so, and say
what you could not confirm. Do NOT run scripts against production data sources to
verify behaviour.
-->

## Reviewers

<!--
Franchise-scoped changes: that franchise's analytics owner (see CONTEXT.md).
Agent guidance, .mcp/, templates/ or docs/: a repository maintainer.
-->
