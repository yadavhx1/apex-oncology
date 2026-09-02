# GitHub Copilot instructions — apex-oncology

Repository-wide instructions for Copilot. These complement
[`AGENTS.md`](../AGENTS.md), which is the authoritative operating guide.

## Context

`apex-oncology` holds configuration and analytical workloads for three oncology
franchises — `Venclexta`, `Epkinly`, `Imbruvica`. Workloads are Python, SQL and
Jupyter notebooks. Each franchise is self-contained under
`franchises/<Franchise>/` with `CONTEXT.md`, `manifest.yaml`, `configuration/`
and `scripts/`.

## Suggestion rules

- **Stay inside the current franchise.** When editing a file under
  `franchises/Venclexta/`, draw on that franchise's context and configuration only.
  Do not pull identifiers, table names, filters or business rules from another
  franchise — they differ per franchise and cross-contamination is a correctness bug,
  not a style issue.

- **Never hardcode configurable values.** Reporting periods, market codes, product
  lists, database and schema names, file paths and secret names belong in that
  franchise's `configuration/`. Suggest reading from config, not a literal.

- **Never suggest a literal secret.** No credentials, tokens, connection strings, API
  keys or passwords — not even placeholder-looking ones. Reference a secret by name and
  resolve it from the environment or vault at run time.

- **Never suggest committing data.** No CSV extracts, no result sets, no patient-level
  or otherwise identifiable values in tracked files or notebook outputs.

- **Leave deliberate blanks alone.** An empty `IN ()` list, a blank date bound or an
  unset market filter is usually a required run-time user input. Do not autofill a
  plausible value; if anything, flag it as user input.

- **Register new scripts.** A new or renamed script under `scripts/` needs a
  corresponding entry in that franchise's `manifest.yaml`, recording its inputs,
  outputs and config dependencies.

## Comment and documentation style

Comment for business intent, not syntax. Skip comments a competent analyst wouldn't
need — `GROUP BY`, `DISTINCT`, aliases, basic joins and simple aggregations are
self-explanatory.

Prefer business framing:

```sql
/* Latest active factor selected */
```

over mechanics:

```sql
/* ROW_NUMBER() ranks records by DATA_MONTH DESC */
```

Use the pharma vocabulary already in use across the repo: patient, HCP, prescriber,
provider, account, product, brand, therapy area, market, claims, TRx, NBRx, specialty
pharmacy, site of care, IDN.

New script files should open with the header block from
[`templates/TEMPLATE_SCRIPT.md`](../templates/TEMPLATE_SCRIPT.md) — objective, user
inputs, source tables, output.

## Conventions

Follow [`docs/conventions.md`](../docs/conventions.md) for file naming, manifest fields
and metadata. Franchise directories are `PascalCase` brand names; scripts and config
files are `snake_case`.
