# AGENTS.md

Global operating rules for AI agents and MCP clients working in `apex-oncology`.

This file is the **entry point**. Read it first, then follow the context chain below.
Every other agent-facing file (`CLAUDE.md`, `.github/copilot-instructions.md`) defers to
this one.

---

## 1. What this repository is

`apex-oncology` holds configuration and analytical workloads for multiple oncology
franchises. Each franchise is **self-contained**: its own business context, its own
script inventory, its own configuration.

Franchises: `Venclexta`, `Epkinly`, `Imbruvica`.

Supported workloads: Python (`.py`), SQL (`.sql`), Jupyter notebooks (`.ipynb`),
and YAML/JSON configuration.

## 2. Context chain — read in this order

```
AGENTS.md                          <- you are here
  -> .mcp/context.yaml             machine-readable repo map
    -> franchises/<F>/CONTEXT.md   business + technical context for one franchise
      -> franchises/<F>/manifest.yaml   script inventory and dependencies
        -> the target script
          -> franchises/<F>/configuration/*   configs that script consumes
```

Stop as soon as you have what you need. Do not walk the whole chain out of habit.

## 3. Franchise scoping — the most important rule

**Load exactly one franchise unless the request is explicitly cross-franchise.**

A question about a Venclexta script is answered from `franchises/Venclexta/` alone.
Do not read `franchises/Epkinly/` or `franchises/Imbruvica/` to answer it. Franchises
have different business rules, different data sources and different owners; mixing
them produces confidently wrong answers.

If a request genuinely spans franchises, say so and name the franchises you are
loading before you load them.

## 4. Resolving a script

When asked about a specific script:

1. Read `franchises/<F>/CONTEXT.md` for business framing.
2. Look the script up in `franchises/<F>/manifest.yaml` to get its declared inputs,
   outputs and config dependencies.
3. Read the script.
4. Read only the config files the manifest names.

If the manifest and the script disagree, **the script is the truth** and the manifest
is stale. Report the drift; do not silently trust either one.

## 5. Making changes

- Configuration and code stay separate. Parameters, paths, credentials references and
  business-rule values belong in `configuration/`, never hardcoded in a script.
- Adding or renaming a script means updating that franchise's `manifest.yaml` in the
  same change. An unregistered script is invisible to agents and to MCP.
- Adding a franchise means copying `templates/` — see `templates/TEMPLATE_FRANCHISE.md`.
- Follow `docs/conventions.md` for naming and metadata.
- Annotate code in place rather than writing separate documentation files. See
  `templates/TEMPLATE_SCRIPT.md` for the expected header block.

## 6. Safety

- **Never commit secrets.** No credentials, tokens, connection strings, API keys or
  passwords in any tracked file, including notebook outputs. Configuration references
  a secret by *name*; the value comes from the runtime environment or a vault.
- **Never commit patient-level or otherwise identifiable data.** This repository holds
  configuration and code, not data. No extracts, no CSV samples, no result sets.
- **Clear notebook outputs before committing.** Outputs frequently contain real data.
- Treat anything under `franchises/*/configuration/` as production-affecting. Flag the
  blast radius of a change before making it.
- Do not run scripts against production data sources to "check" something.

## 7. Unresolved inputs

Many scripts intentionally ship with blank filters — reporting periods, market codes,
product lists — that a user fills in at run time. When you read a script, **surface
these rather than guessing values for them**. An empty `IN ()` list or a blank date is
a required user input, not a bug.

## 8. What not to do

- Do not load the entire repository into context. Scope to a franchise.
- Do not invent table descriptions, business rules or metric definitions. Look them up
  in `docs/data-dictionary.md` and the franchise `CONTEXT.md`. If it genuinely isn't
  recorded, say it isn't recorded.
- Do not generate standalone architecture or documentation files unless asked.
- Do not reformat or rewrite a script you were only asked to explain.
