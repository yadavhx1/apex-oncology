# DOS / GRACE change history

Change log for `aml_dos_grace.yaml`, the DOS and GRACE values behind AML
line-of-therapy validation.

Every edit to a `grace`, `dos_px`, `rx_fallback_days_supply` or `product_exclusions`
value gets a row here — appended by the `/update-dos-grace` skill, newest first. These
values move reported lines of therapy, so the point of this file is to answer "when did
this number change, and why" without archaeology through git.

Conventions:

- **Date** — `YYYY-MM-DD`, the day the edit was made.
- **Product** — the `FINAL_PRODUCT_NAME` as written in the YAML. `—` for file-level
  changes such as the RX fallback.
- **Field** — `grace`, `dos_px`, `rx_fallback_days_supply`, or `product_exclusions`.
- **Old / New** — literal values. `null` where the value is null; `—` for the absent
  side of an added or removed entry.
- **Reason** — the business reason as given. `Not stated` when none was supplied; that
  is a gap to close in `CONTEXT.md`, not a value judgement about the change.

A row here records the edit, not its verification. Rows are not proof the validator or
the migration-baseline tests were run.

| Date | Product | Field | Old | New | Reason |
|---|---|---|---|---|---|
| 2026-09-23 | MYLOTARG | dos_px | 1 | 7 | Not stated |
