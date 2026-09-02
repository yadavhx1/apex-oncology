# Data dictionary

Authoritative source for table and field descriptions in `apex-oncology`.

When an agent or author needs to describe a table, view or field, **look here first**.
Only if there is no entry should a description be inferred from the code — and an
inferred description must be labelled as inferred.

> **Status: scaffold.** The structure and rules below are final; the entries are not
> yet populated. Franchise owners contribute their own tables — see
> [Contributing an entry](#contributing-an-entry). Rows marked `TODO` are placeholders
> showing the expected shape, not real metadata. Do not cite them as fact.

---

## How descriptions are sourced

Three tiers, in strict priority order:

1. **Repository description** — recorded in this file. Use verbatim.
2. **Inferred description** — derived from table name, column names, joins, filters and
   business usage in the code. Allowed only when tier 1 has no entry.
3. **Name interpretation** — last resort, when nothing else is available.

A description must always be provided. Never write "unknown table", "description
unavailable", "metadata not found" or "no information available". Never leave a table
undocumented.

Label the tier when annotating code so a reader knows how much to trust it:

```sql
/* Repository Description: Oncology syndicated claims */
FROM ALL_CLAIMS_COMBINED_FACT_VW

/* Inferred Description: Product hierarchy mapping */
FROM PRODUCT_XREF
```

An inferred description that proves correct and useful should be promoted into this file
so the next reader gets it from tier 1.

## Source tables

Database and table are separate columns — deliberately, so entries can be filtered by
database and so a table name appearing in more than one database stays unambiguous.

| Database | Table / View | Type | Grain | Description | Owner | Used by |
|---|---|---|---|---|---|---|
| `TODO` | `TODO` | Fact / Dim / View | one row per … | *TODO — one line, business language* | `TODO` | `TODO` |

Fill one row per table referenced by any script in the repository. Keep `Description`
to a single line in business language; put detail in the per-table sections below.

### Column reference

Detailed field definitions for individual tables. Add a subsection per table that needs
more than the one-liner above.

<!--
### `DATABASE.TABLE_NAME`

Business purpose in one or two sentences. Grain. Refresh cadence. Known caveats —
late-arriving data, restatement windows, franchises for which it is not valid.

| Column | Type | Description | Notes |
|---|---|---|---|
| | | | |
-->

## Output tables

Every script that writes an output registers that output's data dictionary here. This is
required, not optional — a final output table without a dictionary entry cannot be
consumed safely by anyone downstream.

Intermediate and staging tables do **not** need entries. Document final outputs only.

| Database | Table | Produced by | Franchise | Grain | Description |
|---|---|---|---|---|---|
| `TODO` | `TODO` | `franchises/<F>/scripts/<script>` | `TODO` | one row per … | *TODO* |

### Output column definitions

<!--
### `DATABASE.OUTPUT_TABLE_NAME`

Produced by: `franchises/<Franchise>/scripts/<script>`
Franchise: `<Franchise>`
Grain: one row per …
Refresh: <cadence>

| Column | Type | Description | Derivation | Nullable |
|---|---|---|---|---|
| | | | | |
-->

Include `Derivation` for any calculated or derived column — the business rule that
produces it, not the expression that implements it. "Latest active factor for the
reporting month" is useful; "`ROW_NUMBER()` partitioned by HCP" is not.

## Metric definitions

Shared metric vocabulary. A metric defined differently by a franchise must say so in
that franchise's `CONTEXT.md` rather than silently diverging from this table.

| Metric | Definition | Notes |
|---|---|---|
| TRx | Total prescriptions — new plus refill — in the period | *TODO: confirm the repository's exact source and period convention* |
| NBRx | New-to-brand prescriptions in the period | *TODO: confirm the new-to-brand rule applied* |
| `TODO` | *TODO* | |

The two rows above are placeholders carrying the industry-standard reading. Replace them
with this repository's exact definitions — period convention, source feed and the
new-to-brand rule are all things that vary in practice, and the precise version is what
makes the table worth having.

## Conventions for this file

- **Database and table stay in separate columns.** Do not collapse to `DB.TABLE`.
- One line per description in the summary tables; detail goes in the per-table sections.
- Business language, not implementation language. Use the shared vocabulary — patient,
  HCP, prescriber, provider, account, product, brand, therapy area, market, claims, TRx,
  NBRx, specialty pharmacy, site of care, IDN.
- State the grain explicitly ("one row per HCP per month"). Ambiguous grain is the most
  common cause of misuse.
- Record known caveats — late-arriving data, restatement windows, franchises for which a
  table is not valid. A caveat omitted here becomes a defect downstream.
- **No data values.** Descriptions and definitions only: no sample rows, no extracts, no
  patient-level or otherwise identifiable values.

## Contributing an entry

1. Add the table to **Source tables** or **Output tables**, whichever applies.
2. Add a per-table subsection with column definitions if the one-liner is not enough.
3. For a script output, complete the output column definitions including derivations —
   this is required for every final output table.
4. Cross-check the table is also declared in that franchise's `manifest.yaml` under
   `source_tables` or `outputs`. The two must agree.
5. If you are promoting a previously inferred description, drop the "Inferred" label
   from the code comment in the same change.
