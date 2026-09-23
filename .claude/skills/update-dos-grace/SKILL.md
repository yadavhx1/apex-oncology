---
name: update-dos-grace
description: Update DOS (days of supply) or GRACE period values for AML line-of-therapy validation in the Venclexta franchise. Use when the user wants to change a grace period or DOS value for one product, several products, or all products; add a new product; or remove a product from franchises/Venclexta/configuration/aml_dos_grace.yaml. Triggers on "update grace", "change grace period", "update DOS", "add a product to dos/grace", "grace value for <product>".
---

# Update DOS / GRACE values

Edits to `franchises/Venclexta/configuration/aml_dos_grace.yaml`, which drives the
`GRACE_VALUE` and `DOS_FINAL` CASE expressions in `AML_LOT_VAL.ipynb`.

**These values move reported lines of therapy.** A grace period decides whether two
claims belong to the same treatment episode; DOS decides how long a claim covers.
Changing either changes patient counts and LoT distributions that go to the business.
Treat every edit as production-affecting.

The workflow is: **ask if the request is incomplete → show the change → get
confirmation → edit the YAML → log it → print what changed.**

---

## Ground rules

1. **Ask when the product or the value is missing.** If the user hasn't named the
   product, or hasn't given a number, ask with `AskUserQuestion` before doing anything
   else. Never guess a value — do not infer one from a similar product, another
   franchise, or the product's drug class.
2. **Proceed when both are given.** "Set Mylotarg grace to 10" is complete: go straight
   to step 2 and don't ask a scope question you already have the answer to.
3. **Show the change before writing it** — old → new for every product you're about to
   touch — and get agreement. This is the one confirmation gate; don't skip it even for
   a single-value edit.
4. **Edit the YAML with the Edit tool**, not with a script. This preserves the comments
   and per-product notes, which carry the business reasoning.
5. **Log every change** to `configuration/aml_dos_grace_history.md` (step 4).
6. **Print the result after editing** (step 5), so the user sees the committed state
   without having to open the file.
7. **Preserve the file's structure** — products alphabetical, one blank line between
   entries, inline comments intact.
8. **Do not run the validator or the tests.** No `validate_dos_grace.py`, no
   `test_dos_grace_config.py`, no `MIGRATION_BASELINE_*` edits. This skill updates the
   YAML and the history file only. If the user wants validation, they will ask.

## Step 1 — Read the current state and check the request is complete

`Read` the YAML directly — `franchises/Venclexta/configuration/aml_dos_grace.yaml`. It
holds every product's `grace`, `dos_px` and notes, plus the RX fallback and exclusions.
Do not shell out to the validator to inspect it.

Then check the request against what you need:

| Have | Missing | Do |
|---|---|---|
| Product **and** value | — | Go to step 2 |
| Product only | Value | Ask for the value |
| Value only | Product | Ask which product(s) |
| Neither | Both | Ask for field, products, and value |

When asking, use `AskUserQuestion` and include the current value in the option
descriptions — users often work from a stale spreadsheet, and seeing the live value
catches that before an edit happens.

Fields that can change:

- `products.<NAME>.grace` — grace period in days, per product
- `products.<NAME>.dos_px` — PX (medical-benefit) days of supply, per product
- `dos.rx_fallback_days_supply` — applies to **every** RX claim with a missing or
  non-positive `PRODUCT_DAYS_SUPPLY`. Blunt instrument; confirm intent.
- `product_exclusions` — products dropped before DOS/GRACE assignment

## Step 2 — Show the change and confirm

State the change as a table and wait for agreement:

```
Product      Field    Old    New
MYLOTARG     grace      7     10
VYXEOS       dos_px     1      5
```

Call out anything that makes the change more than a number swap:

- **Value already matches.** Say so and make no edit. Ask whether they meant a
  different product or a different field rather than writing a no-op.
- **Product not in the file.** Say so and offer to add it. Do not silently create it —
  the user may have used a brand name where the file uses the generic (`VIDAZA` vs
  `AZACITIDINE`), or a variant spelling (`HIDAC` vs `HI-DAC`).
- **Setting `dos_px` on one of the 11 orals.** `null` there is deliberate: pharmacy
  dispensed only, no PX claims. Confirm the product genuinely has medical-benefit
  claims before giving it a number.
- **All-products change.** Rare and high-impact. Confirm they mean every product and
  not just the ones they listed, name the distinct values being flattened, and ask
  whether the `null` entries should be set too.
- **Removing a product.** Its `GRACE_VALUE` and PX `DOS_FINAL` become `NULL`; the
  product is *not* excluded from the data. If they want it out of the dataset entirely
  that's `product_exclusions` — a different change. Check which they mean.

## Step 3 — Apply the change

Edit each product entry in place, alphabetical order and structure intact. Keep the
entry's `notes` unless the new value makes them wrong — if it does, update them rather
than leaving a note that contradicts the value.

For multiple products taking one value, edit each entry individually. The SQL groups
them into a shared `IN (...)` branch automatically; don't hand-group the YAML.

Adding a new product — insert alphabetically, name uppercase matching
`FINAL_PRODUCT_NAME` (letters, digits, underscore, hyphen only):

```yaml
  PRODUCT_NAME:
    grace: <days>
    dos_px: <days or null>
    notes: <why, one line — optional but wanted>
```

A product in `product_exclusions` must not also appear in `products`.

## Step 4 — Log it to the history file

Append one row per changed value to
`franchises/Venclexta/configuration/aml_dos_grace_history.md`, newest first:

```
| Date | Product | Field | Old | New | Reason |
|---|---|---|---|---|---|
| 2026-09-23 | MYLOTARG | grace | 7 | 10 | Cycle length correction |
```

- **Date** — today's date, `YYYY-MM-DD`, from the session context.
- **Product** — the `FINAL_PRODUCT_NAME` as written in the YAML. Use `—` for
  file-level changes like the RX fallback.
- **Field** — `grace`, `dos_px`, `rx_fallback_days_supply`, or `product_exclusions`.
- **Old / New** — the literal values. `null` for null, `—` for an added or removed
  entry's absent side.
- **Reason** — what the user gave. If they gave none, write `Not stated` rather than
  inventing one, and flag it in step 6 as a follow-up.

An added product gets a row per field; a removed product gets rows showing its values
going to `—`.

## Step 5 — Print the result

Show the post-edit state of every product you touched, read back from the file:

```
MYLOTARG
  grace   10 days
  dos_px   1 day
  notes   (unchanged)
```

Then confirm both files were written: the YAML and the history file.

## Step 6 — Report and follow up

Tell the user:

- **What changed** — the table of product, field, old → new
- **Blast radius** — `AML_LOT_VAL.ipynb` regenerates `GRACE_VALUE` / `DOS_FINAL` on next
  run, moving treatment episodes and therefore reported lines of therapy for the
  affected products
- **Not validated** — state plainly that the validator and tests were not run, so the
  edit is unverified. If the change was structural (a product added or removed, a value
  moving between groups), say that `MIGRATION_BASELINE_*` in
  `scripts/test_dos_grace_config.py` is now out of sync and those tests will fail for
  anyone who runs them.

Then flag the follow-ups the user owns:

- [ ] Record the business reason in `franchises/Venclexta/CONTEXT.md` under business
      rules. A value with no recorded rationale is the thing that causes the next
      argument about why numbers moved.
- [ ] Get business-stakeholder sign-off if the change alters a definition rather than
      correcting an error.
- [ ] Note the change in the PR, per `.github/pull_request_template.md` — the
      configuration-change section asks for the blast radius explicitly.
- [ ] Re-run the notebook. Editing config changes nothing until it runs.

Do not commit unless the user asks.

## Notes and edge cases

- **`L-DAC` is 60 while `S-DAC` and `HI-DAC` are 7.** Carried over from the original
  SQL and flagged in the YAML. If a user asks to "fix the DAC grace values", confirm
  which way they want it aligned and whether the business has agreed — don't assume
  L-DAC is the typo.
- **Product name mismatches** are the most common failure. The file uses
  `FINAL_PRODUCT_NAME` values, which are uppercase and sometimes generic
  (`AZACITIDINE`) rather than brand (`VIDAZA`). Check before adding a duplicate under
  another name.
- **`grace: null` vs absent** — both yield `NULL`. Prefer an explicit `null` entry with
  a note, so the product is visibly accounted for.
- **`dos_px: null` is normal**, not an omission: 11 of the 28 products are orals with
  no PX claims.
- **Do not run the notebook against production** to preview a change.

## Files

| Path | Role |
|---|---|
| `franchises/Venclexta/configuration/aml_dos_grace.yaml` | The values — what you edit |
| `franchises/Venclexta/configuration/aml_dos_grace_history.md` | Change log — append every edit |
| `franchises/Venclexta/CONTEXT.md` | Where the business reason belongs |
| `franchises/Venclexta/scripts/AML_LOT_VAL.ipynb` | Consumer — builds the final Tx table |
| `franchises/Venclexta/scripts/dos_grace_config.py` | Loader and SQL generation — not run by this skill |
| `franchises/Venclexta/scripts/validate_dos_grace.py` | Validator CLI — not run by this skill |
| `franchises/Venclexta/scripts/test_dos_grace_config.py` | Tests + migration baseline — not run by this skill |
