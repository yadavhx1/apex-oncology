# Conventions

Naming, metadata and authoring rules for `apex-oncology`. Consistency here is what lets
agents navigate the repository from metadata instead of guessing.

---

## Naming

| Thing | Convention | Example |
|---|---|---|
| Franchise directory | `PascalCase`, exact brand name | `franchises/Venclexta/` |
| Script file | `snake_case` + extension | `trx_monthly.sql`, `build_hcp_universe.py` |
| Notebook | `snake_case.ipynb` | `patient_cohort_exploration.ipynb` |
| Configuration file | `snake_case.yaml` | `market_filters.yaml`, `source_tables.yaml` |
| Config key | `snake_case` | `reporting_period_end` |
| Fixed-name files | exactly as specified | `CONTEXT.md`, `manifest.yaml` |
| Docs page | `kebab-case.md` | `agent-workflows.md` |

Prefer YAML over JSON for configuration — it takes comments, which is most of the value.

Name a script for what it produces, not how. `trx_monthly.sql` beats `query1.sql`;
`build_hcp_universe.py` beats `script_v2_final.py`. Never encode status or version in a
filename — `_final`, `_v2`, `_new`, `_old`, `_backup`, `_copy`, dates. Git holds history.

## Placement

```
franchises/<Franchise>/
├── CONTEXT.md          business + technical context (required)
├── manifest.yaml       script inventory (required)
├── configuration/      YAML/JSON consumed by scripts
└── scripts/            .py, .sql, .ipynb
```

- Scripts go in `scripts/`, config in `configuration/`. Not mixed.
- Subdirectories under `scripts/` are fine once the count justifies it. Group by
  business area (`scripts/trx/`, `scripts/patient/`), not by file type — the extension
  already carries that.
- Nothing franchise-specific belongs outside its franchise directory.
- There is deliberately no shared or `common/` franchise. If two franchises need the
  same value, each holds its own copy; divergence between franchises is expected.

## Configuration rules

**Everything configurable lives in configuration.** Parameters, database and schema
names, file paths, secret *names*, thresholds, business-rule values, product and market
code lists. If it might differ between environments or change without a logic change,
it is configuration.

**Never a secret value.** Configuration names a secret; the value resolves from the
environment or a vault at run time:

```yaml
# Correct — a reference
database:
  host: onc-warehouse.internal
  credential_ref: APEX_WAREHOUSE_PWD    # resolved from environment at run time

# Never — a value
database:
  password: hunter2
```

**Comment the business meaning of a value, not its type.** `# TRx floor below which an
account is suppressed from reporting` earns its place; `# integer` does not.

Structure config files by business concern — `market_filters.yaml`,
`source_tables.yaml`, `output_targets.yaml` — rather than one `config.yaml` per script.
See [`templates/config_schema.yaml`](../templates/config_schema.yaml) for the expected
shape.

## Manifest rules

Every script under `scripts/` needs an entry in that franchise's `manifest.yaml`. An
unregistered script is invisible to agents, to MCP and to reviewers.

Each entry records at minimum:

| Field | Meaning |
|---|---|
| `name` | Filename as it appears in `scripts/` |
| `type` | `python` \| `sql` \| `notebook` |
| `purpose` | One line: what it produces and why |
| `owner` | Person or team accountable |
| `configuration` | Config files it consumes — paths relative to the franchise |
| `source_tables` | Tables, views and files it reads |
| `outputs` | Tables, files or reports it writes |
| `user_inputs` | Run-time inputs the user must supply |
| `schedule` | Cadence, or `ad-hoc` |
| `depends_on` | Other scripts that must run first, if any |

Full shape in [`templates/franchise/manifest.yaml`](../templates/franchise/manifest.yaml)
and [`templates/script-metadata.yaml`](../templates/script-metadata.yaml).

Update the manifest **in the same change** as the script. When manifest and script
disagree, the script is authoritative and the manifest is stale — fix the manifest and
report the drift.

## Code annotation

Annotate in place with comments. Do not write a separate markdown document for a script.

Every script opens with a header block — objective, user inputs, source tables, output.
Keep it under ~15 lines. Template:
[`templates/TEMPLATE_SCRIPT.md`](../templates/TEMPLATE_SCRIPT.md).

### Depth scales with business complexity, not line count

| Complexity | Example | Annotation |
|---|---|---|
| Simple | single-table lookup, reference extract | Header, table descriptions, user inputs, important filters. ~3–10 comments. |
| Medium | several joins, derived metrics, multiple filters | Add major business steps and business rules. ~10–20 comments. |
| Complex | nested subqueries, window functions, cohorting, segmentation | Full annotation incl. join purposes and derived-metric explanations. ~20–40 comments. |

### Comment for intent, not syntax

Before adding a comment, ask whether a competent analyst would understand the line
without it. If yes, leave it out. Do not comment `SELECT DISTINCT`, `GROUP BY`,
`ORDER BY`, `UPPER()`, `CAST()`, `COALESCE()`, aliases, basic joins or simple
aggregations unless one carries business meaning.

```sql
/* Latest active factor selected */                    -- good: business intent
/* ROW_NUMBER() ranks records by DATA_MONTH DESC */    -- bad: restates the syntax
```

Length limits: step comment ≤ 10 words; table description, join description and user
input ≤ 1 line; business rule ≤ 15 words. No multi-paragraph comments, no decorative
separators, no repeating a description already given.

When brevity and completeness conflict, choose brevity.

### Table descriptions

Every table, view, CTE or dataset gets a description on first reference — once, not
repeated. Look it up in [`data-dictionary.md`](data-dictionary.md) first and mark the
source:

```sql
/* Repository Description: Oncology syndicated claims */
FROM ALL_CLAIMS_COMBINED_FACT_VW

/* Inferred Description: Product hierarchy mapping */
FROM PRODUCT_XREF
```

Never leave a table undocumented and never write "unknown" or "description
unavailable" — infer from column names, joins and filters if the dictionary has no
entry, and label the inference.

### User inputs are mandatory

Mark every unresolved run-time input where it appears:

```sql
/* USER INPUT REQUIRED */
AND MARKET_CODE = ''
```

Blank dates, empty `IN ()` lists, unset market and product filters, macro variables and
empty config keys are deliberate inputs. Surface them; never autofill.

### Code stays primary

The script must run unchanged with all comments stripped. Do not reformat, restructure
or rewrite code you were asked to annotate or explain.

## Notebooks

- Clear all outputs before committing. Outputs routinely contain real data.
- Every code cell that isn't self-evident gets a preceding markdown cell explaining the
  business step.
- The first cell is a markdown header block matching the script header convention.
- Keep notebooks for exploration and reporting. Promote anything scheduled to a `.py`.

## Language

Use the vocabulary the business audience already uses: patient, HCP, prescriber,
provider, account, product, brand, therapy area, market, claims, TRx, NBRx, specialty
pharmacy, site of care, IDN, academic center, community practice. Translate technical
mechanics into business language.

## Commits and PRs

- Present tense, imperative: `Add Epkinly TRx monthly extract`.
- Name the franchise when a change is franchise-scoped.
- Keep configuration changes separate from logic changes — they carry different risk and
  want different reviewers.
- Work through the [PR checklist](../.github/pull_request_template.md), including the
  AI-context items: manifest updated, `.mcp/context.yaml` updated if structure changed.

## Never commit

Credentials, tokens, connection strings, API keys, passwords. Patient-level or otherwise
identifiable data. Data extracts, result sets, CSVs. Notebook outputs. Local artifacts —
see [`.gitignore`](../.gitignore).
