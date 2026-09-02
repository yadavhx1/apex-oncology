# Architecture

How `apex-oncology` is organised, who owns what, and how dependencies flow.

![apex-oncology architecture](assets/apex-oncology-architecture.png)

An interactive version of the structure diagram is at
[`repo-structure.html`](repo-structure.html) — open it in a browser.

---

## Design intent

The repository serves two audiences at once: the analysts and engineers who maintain
oncology workloads, and the AI agents and MCP clients that increasingly read and modify
them. Those audiences want the same thing — to understand one franchise's script
without absorbing the whole repository.

Four decisions follow from that:

**Context is scoped by franchise.** Every franchise directory is self-contained. An
agent answering a Venclexta question reads `franchises/Venclexta/` and nothing else.
This is not merely an efficiency measure: franchises have genuinely different business
rules, data sources and owners, so cross-reading produces answers that are fluent and
wrong.

**Configuration is separated from code.** Scripts express logic; `configuration/` holds
the parameters, paths, secret references and business-rule values that logic operates
on. A business rule change should be a config edit, reviewable on its own.

**Dependencies are declared, not discovered.** Each franchise's `manifest.yaml` records
what every script reads, writes and depends on. Agents consult metadata instead of
grepping, which makes retrieval cheap and precise.

**New franchises are copied, not invented.** `templates/` keeps the fifth franchise
shaped like the first.

## Layout

```
apex-oncology/
├── AGENTS.md                       global operating rules — the entry point
├── CLAUDE.md                       Claude Code entry-point context
├── GEMINI.md                       Gemini entry-point context
├── README.md                       overview and quick start
├── .github/
│   ├── copilot-instructions.md     Copilot repository instructions
│   └── pull_request_template.md    PR checklist, incl. AI-context validation
├── .mcp/
│   └── context.yaml                machine-readable repo map + MCP discovery
├── docs/
│   ├── architecture.md             this file
│   ├── agent-workflows.md          discovery and code-change workflows
│   ├── mcp-integration.md          MCP resources, tools, retrieval strategy
│   ├── conventions.md              naming, metadata, authoring rules
│   ├── data-dictionary.md          authoritative table and field definitions
│   ├── repo-structure.html         interactive structure diagram
│   └── assets/
│       └── apex-oncology-architecture.png
├── franchises/
│   ├── Venclexta/
│   │   ├── CONTEXT.md              business and technical context
│   │   ├── manifest.yaml           script inventory and dependencies
│   │   ├── configuration/          YAML/JSON consumed by scripts
│   │   └── scripts/                .py, .sql, .ipynb workloads
│   ├── Epkinly/                    same structure
│   └── Imbruvica/                  same structure
└── templates/
    ├── TEMPLATE_FRANCHISE.md       how to onboard a franchise
    ├── TEMPLATE_SCRIPT.md          script header / annotation template
    ├── config_schema.yaml          expected shape of a configuration file
    ├── script-metadata.yaml        script-level dependency metadata
    └── franchise/
        ├── CONTEXT.md              starting point for a new CONTEXT.md
        └── manifest.yaml           starting point for a new manifest.yaml
```

## Layers

The architecture diagram shows five layers. Reading top to bottom:

| Layer | Contents | Role |
|---|---|---|
| AI agents / MCP clients | Claude, Gemini, Copilot, custom agents, MCP tools | Query the repository for context; propose and make changes |
| Repository context | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.mcp/context.yaml`, `docs/` | Tell agents how to navigate and what the rules are |
| Franchise assets | `franchises/<F>/` — context, manifest, configuration, scripts | The franchise-scoped source of truth |
| Configuration layer | `franchises/<F>/configuration/` | Structured YAML/JSON supplying parameters, paths, secret names, business-rule values |
| Script execution layer | `franchises/<F>/scripts/` | Python, SQL and notebooks that consume config, process data, emit outputs |

Below the script layer sit the things this repository references but does not contain:
data sources (databases, files, APIs, data lake), scheduling and orchestration (Airflow,
Autosys, ADF, cron), and outputs (tables, reports, files, dashboards).

## Context chain

```
AGENTS.md
  -> .mcp/context.yaml
    -> franchises/<F>/CONTEXT.md
      -> franchises/<F>/manifest.yaml
        -> franchises/<F>/scripts/<script>
          -> franchises/<F>/configuration/*
```

Two flows run along this chain. **Context/query flow** runs downward as an agent
narrows from repository to franchise to script. **Data flow** runs upward at run time
as a script reads its configuration, pulls from data sources and writes outputs.

Enter the chain as far down as the question allows. A question naming a specific script
starts at that franchise's manifest, not at `AGENTS.md`.

## Dependency model

Dependencies point in one direction only:

```
script -> configuration -> (secret names, resolved at run time)
script -> source tables  -> (external data sources)
```

Rules that keep this tractable:

- A script depends on configuration. Configuration never depends on a script.
- A script must not read another franchise's configuration. If two franchises need the
  same value, each holds its own copy — divergence is expected and is the point.
- Cross-franchise sharing is deliberately not supported by a shared directory. If a
  genuine shared asset emerges, raise it rather than reaching across `franchises/`.
- Every dependency a script has must appear in `manifest.yaml`. Undeclared
  dependencies are invisible to agents, to MCP and to reviewers.
- When manifest and script disagree, the script is authoritative and the manifest is
  stale. Fix the manifest; report the drift.

## Ownership

| Area | Owner |
|---|---|
| `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.mcp/`, `.github/` | Repository maintainers |
| `docs/` | Repository maintainers, with franchise input |
| `templates/` | Repository maintainers |
| `franchises/<F>/**` | That franchise's analytics owner |
| `docs/data-dictionary.md` | Shared — franchise owners contribute their tables |

Fill in named owners per franchise in each `CONTEXT.md`. A change under
`franchises/<F>/` should be reviewed by that franchise's owner; a change to the agent
guidance files or `.mcp/context.yaml` affects every franchise and every agent, so it
should be reviewed by maintainers.

## Boundaries — what lives elsewhere

This repository holds **configuration and code**. It does not hold:

- Data of any kind — no extracts, no result sets, no patient-level records, no
  committed notebook outputs.
- Secret values. Configuration names a secret; the value resolves from the environment
  or a vault at run time.
- Orchestration definitions. Schedules live in the scheduler.
- Rendered reports and dashboards. Those are outputs, not sources.

## Scaling to a new franchise

Copy `templates/`, do not hand-roll. The onboarding steps are in
[`templates/TEMPLATE_FRANCHISE.md`](../templates/TEMPLATE_FRANCHISE.md):

1. Copy `templates/franchise/` to `franchises/<NewFranchise>/`, creating
   `configuration/` and `scripts/`.
2. Fill in `CONTEXT.md` — business framing, owner, data sources, key business rules.
3. Fill in `manifest.yaml` — start empty, register scripts as they land.
4. Add configuration files under `configuration/`, following `config_schema.yaml`.
5. Add scripts under `scripts/` and register each one in `manifest.yaml`.
6. Add the franchise to `.mcp/context.yaml` under `franchises:` so agents can discover it.

Step 6 is the one most often missed. A franchise absent from `.mcp/context.yaml` is
invisible to MCP clients even though its files exist.
