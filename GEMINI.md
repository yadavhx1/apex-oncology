# GEMINI.md

Entry-point context for Gemini in `apex-oncology`.

**Read [`AGENTS.md`](AGENTS.md) first — it holds the operating rules and they apply in
full here.** This file is a short orientation only.

---

## Repository shape

Configuration and analytical workloads (Python, SQL, Jupyter notebooks) for three
oncology franchises: `Venclexta`, `Epkinly`, `Imbruvica`.

```
apex-oncology/
├── AGENTS.md CLAUDE.md GEMINI.md    agent entry points
├── .mcp/context.yaml                machine-readable repo map
├── docs/                            architecture, workflows, conventions, data dictionary
├── franchises/<Franchise>/
│   ├── CONTEXT.md                   business + technical context
│   ├── manifest.yaml                script inventory and dependencies
│   ├── configuration/               YAML/JSON consumed by scripts
│   └── scripts/                     .py, .sql, .ipynb
└── templates/                       scaffolding for new franchises and scripts
```

## Context chain

```
AGENTS.md -> .mcp/context.yaml -> franchises/<F>/CONTEXT.md -> manifest.yaml
          -> target script -> configuration/*
```

Enter as far down the chain as the question allows; stop once you have enough.

## The rules that matter most

1. **One franchise at a time.** Answer a Venclexta question from
   `franchises/Venclexta/` only. Franchises have different business rules and owners —
   reading across them produces answers that are confident and wrong. If a request is
   genuinely cross-franchise, name the franchises you are loading first.

2. **Use `manifest.yaml` before searching.** It already records each script's inputs,
   outputs and config dependencies. Prefer it over a repo-wide grep. If the manifest
   and the script disagree, the script is the truth — report the drift.

3. **Surface unresolved user inputs.** Blank dates, empty `IN ()` lists and unset
   market or product filters are deliberate run-time inputs, not defects. Name them
   instead of guessing values.

4. **Separate configuration from code.** Parameters, paths, secret *names* and
   business-rule values live in `configuration/`. Never hardcode them into a script.

5. **Do not invent metadata.** Table descriptions, metric definitions and business
   rules come from `docs/data-dictionary.md` and the franchise `CONTEXT.md`. If
   something isn't recorded, say so rather than filling the gap.

## Safety

No secrets, no patient-level or identifiable data, no committed notebook outputs in
any tracked file. Treat `franchises/*/configuration/` as production-affecting and state
the blast radius before changing it. Do not run scripts against production sources to
verify behaviour. Full detail in `AGENTS.md` §6.

## Output style

Explain in business language — patient, HCP, prescriber, account, product, brand,
market, claims, TRx, NBRx. Annotate code in place with comments rather than producing
standalone documentation files. Keep comments about business intent, not syntax.
