# Script header and annotation template

Every script in `apex-oncology` opens with a header block. Annotation goes **in the
code**, as comments — not in a separate markdown file.

Rules in [`docs/conventions.md`](../docs/conventions.md); workflow in
[`docs/agent-workflows.md`](../docs/agent-workflows.md).

---

## The header block

Keep it under ~15 lines. Four sections, always in this order.

### SQL

```sql
/*******************************************************************
OBJECTIVE:
  Monthly TRx by HCP and account for franchise reporting.

USER INPUTS:
  reporting_period_end  -- blank below; supply the reporting month
  market_code           -- blank below; supply the market

SOURCE TABLES:
  ALL_CLAIMS_COMBINED_FACT_VW  -- oncology syndicated claims
  PRODUCT_XREF                 -- product hierarchy mapping

OUTPUT:
  VENCLEXTA_TRX_MONTHLY  -- one row per HCP per account per month
*******************************************************************/
```

### Python

```python
"""
OBJECTIVE:
  Build the HCP universe for franchise reporting.

USER INPUTS:
  reporting_period_end  -- read from configuration/market_filters.yaml; unset by default

SOURCE TABLES:
  HCP_MASTER_VW  -- prescriber reference with affiliations
  ACCOUNT_XREF   -- account hierarchy mapping

OUTPUT:
  VENCLEXTA_HCP_UNIVERSE  -- one row per HCP
"""
```

### Notebook

The first cell is a markdown cell carrying the same four sections.

## Annotating the body

### Table descriptions — once, on first reference

Look the description up in [`docs/data-dictionary.md`](../docs/data-dictionary.md)
first and label the tier so a reader knows how much to trust it:

```sql
/* Repository Description: Oncology syndicated claims */
FROM ALL_CLAIMS_COMBINED_FACT_VW

/* Inferred Description: Product hierarchy mapping */
FROM PRODUCT_XREF
```

Never leave a table undocumented; never write "unknown" or "description unavailable".
If the dictionary has no entry, infer from column names, joins and filters — and mark
it `Inferred`.

### User inputs — mandatory, at the line

```sql
/* USER INPUT REQUIRED */
AND MARKET_CODE = ''

/* USER INPUT REQUIRED */
AND DATA_MONTH BETWEEN '' AND ''
```

Blank dates, empty `IN ()` lists, unset market and product filters, macro variables and
empty config keys are deliberate run-time inputs. Mark them; never autofill.

### Business rules — only the ones that shape output

```sql
/* Active records only */
/* Latest version only */
/* Oncology market only */
```

Fifteen words maximum.

### Step comments — medium and complex logic only

```sql
/* Step 1: Extract claims */
/* Step 2: Apply market filters */
/* Step 3: Calculate TRx */
```

Ten words maximum. Not this:

```sql
/* Step 1:
   Extract oncology claims data for the selected products and reporting periods,
   joining to the product hierarchy to resolve brand.
*/
```

## Depth scales with business complexity, not line count

| Complexity | Example | Include | Target |
|---|---|---|---|
| Simple | single-table lookup, reference extract | Header, table descriptions, user inputs, important business filters. No step or join comments. | 3–10 comments |
| Medium | several joins, derived metrics, multiple filters | Add major business steps and business rules. | 10–20 comments |
| Complex | nested subqueries, window functions, cohorting, segmentation | Full annotation incl. join purposes and derived-metric explanations. | 20–40 comments |

## Comment for intent, not syntax

Before adding a comment, ask: *would a competent analyst understand this line without
it?* If yes, leave it out.

```sql
/* Latest active factor selected */                    -- good: business intent
/* ROW_NUMBER() ranks records by DATA_MONTH DESC */    -- bad: restates the syntax
```

Do not comment `SELECT DISTINCT`, `GROUP BY`, `ORDER BY`, `UPPER()`, `LOWER()`,
`CAST()`, `COALESCE()`, `NVL()`, aliases, basic joins or simple aggregations unless one
carries business meaning.

Avoid multi-paragraph comments, decorative separators, large comment blocks, and
repeating a description already given.

## Length limits

| Comment type | Maximum |
|---|---|
| Step comment | 10 words |
| Table description | 1 line |
| Join description | 1 line |
| Business rule | 15 words |
| User input | 1 line |

## Code stays primary

The script must run unchanged with every comment stripped. Preserve the original
formatting. Do not reformat, restructure or rewrite code you were asked to annotate or
explain.

When brevity and completeness conflict, choose brevity.

## Notebooks

- Clear all outputs before committing — they routinely contain real data.
- Precede every non-obvious code cell with a markdown cell naming the business step.
- First cell is the header block.
- Promote anything scheduled from `.ipynb` to `.py`.

## Before you finish

```
[ ] Header block present: objective, user inputs, source tables, output
[ ] Every table described once, tier labelled (Repository / Inferred)
[ ] Every unresolved user input marked at its line
[ ] Business rules that shape output are documented
[ ] Comments carry business context, not syntax
[ ] Annotation proportional to business complexity
[ ] Original code unchanged; still runs with comments stripped
[ ] No secrets, no data values, no hardcoded configurable values
[ ] Notebook outputs cleared
[ ] Script registered in the franchise manifest.yaml
[ ] Final output table added to docs/data-dictionary.md
```

The test: someone should understand the purpose, inputs, outputs, source tables and key
business logic in under 60 seconds by reading the comments and code together.
