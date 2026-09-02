---
name: update-dos-grace
description: Update DOS (days of supply) or GRACE period values for AML line-of-therapy validation in the Venclexta franchise. Use when the user wants to change a grace period or DOS value for one product, several products, or all products; add a new product; or remove a product from franchises/Venclexta/configuration/aml_dos_grace.yaml. Triggers on "update grace", "change grace period", "update DOS", "add a product to dos/grace", "grace value for <product>".
---

# Update DOS / GRACE values

Guided, validated edits to
`franchises/Venclexta/configuration/aml_dos_grace.yaml`, which drives the
`GRACE_VALUE` and `DOS_FINAL` CASE expressions in `AML_LOT_VAL.ipynb`.

**These values move reported lines of therapy.** A grace period decides whether two
claims belong to the same treatment episode; DOS decides how long a claim covers.
Changing either changes patient counts and LoT distributions that go to the business.
Treat every edit as production-affecting.

---

## Ground rules

1. **Never guess a value.** If the user hasn't given a number, ask. Do not infer one
   from a similar product, another franchise, or the product's class.
2. **Show current values before changing them.** The user is often working from a
   stale spreadsheet; seeing the current state catches that.
3. **Confirm before writing.** State old → new for every product you're about to touch
   and get agreement. For an all-products change, list them all.
4. **Edit the YAML with the Edit tool**, not with a script. This preserves the comments
   and per-product notes, which carry the business reasoning.
5. **Always validate after editing** (step 5). Never end the task on an unvalidated file.
6. **Preserve the file's structure** — products alphabetical, one blank line between
   entries, inline comments intact.

## Step 1 — Read the current state

```
python franchises/Venclexta/scripts/validate_dos_grace.py
```

That prints every product, grouped by value, plus the RX fallback and exclusions. Read
`franchises/Venclexta/configuration/aml_dos_grace.yaml` too so you can see the notes.

For a single product:

```
python franchises/Venclexta/scripts/validate_dos_grace.py --product MYLOTARG
```

## Step 2 — Establish the scope

If the user's request already makes the scope unambiguous ("set Mylotarg grace to 10"),
skip the question and proceed. Otherwise ask with `AskUserQuestion`:

- **Which field?** — grace, DOS (PX), the RX fallback, or exclusions
- **Which products?** — all, a named subset, or a new product
- **What value?** — if not already given

Suggested options for the scope question:

| Option | Meaning |
|---|---|
| Selected products | Change the value for specific named products (most common) |
| Add a new product | New entry with grace and dos_px |
| All products | Same value for every product — rare, ask for confirmation of intent |
| Remove a product | Delete an entry entirely |

## Step 3 — Apply the change

### Selected products

For each named product, edit its `grace` or `dos_px` in place. Keep the entry's `notes`
unless the change makes them wrong — if it does, update them rather than leaving a note
that contradicts the value.

If a named product isn't in the file, say so and offer to add it (see below). Do not
silently create it — the user may have used a different name, e.g. a brand name where
the file uses the generic, or `HI-DAC` vs `HIDAC`.

### All products

Rare and high-impact. Before editing:

- Confirm the user means *every* product, not every product in a group. "Update grace
  for all products" often means "all the products I just listed".
- Point out that products currently at different values will be flattened to one, and
  name the distinct values being collapsed.
- Ask whether products with `grace: null` should also be set.

Then apply, keeping alphabetical order and structure intact.

### Add a new product

Insert alphabetically. Required:

```yaml
  PRODUCT_NAME:
    grace: <days>
    dos_px: <days or null>
    notes: <why, one line — optional but wanted>
```

Ask for both values. `dos_px: null` is correct for an oral product dispensed only
through pharmacy (no PX claims) — confirm which it is rather than assuming. Name must
be uppercase, matching `FINAL_PRODUCT_NAME` in the source data: letters, digits,
underscore, hyphen only.

Check the name isn't already present under a variant spelling before adding.

### Remove a product

Confirm first, and say what happens: with the entry gone, `GRACE_VALUE` and PX
`DOS_FINAL` for that product become `NULL` — the product is not excluded from the data,
it just loses its values. If the user wants it out of the dataset entirely, that's
`product_exclusions`, which is a different change. Check which they mean.

### RX fallback / exclusions

`dos.rx_fallback_days_supply` applies to every RX claim with a missing or non-positive
`PRODUCT_DAYS_SUPPLY` — it's a blunt instrument, so confirm intent.

A product in `product_exclusions` must not also appear in `products` — the validator
rejects that.

## Step 4 — Handle the migration baseline

`franchises/Venclexta/scripts/test_dos_grace_config.py` holds
`MIGRATION_BASELINE_GRACE` and `MIGRATION_BASELINE_DOS_PX` — a frozen snapshot of the
values that were hardcoded in the notebook before the config existed.

**Any intentional value change will fail those tests. That is the design.** The
baseline exists so a shift in reported LoT can't happen silently.

So after editing the YAML:

1. Run the tests (step 5). Expect a baseline failure.
2. Update the corresponding entries in `MIGRATION_BASELINE_*` to the new values.
3. Re-run — everything should pass.
4. Make sure the commit message says which product moved, from what to what, and why.

Do **not** delete the baseline, weaken the assertion, or skip the test to make it pass.
If the user asks you to, explain what the baseline is for and offer step 2 instead.

Adding a *new* product also needs a baseline entry. Removing one needs its entry removed.

## Step 5 — Validate

```
python franchises/Venclexta/scripts/validate_dos_grace.py
python franchises/Venclexta/scripts/test_dos_grace_config.py
```

Run both from `franchises/Venclexta/scripts/` (the test imports its module by name).

The validator catches: missing or unknown keys, non-positive or non-integer values, a
non-null `grace.default`, malformed product names, and a product both excluded and
assigned values. The tests additionally confirm the generated SQL still assigns exactly
what the config says, with no product dropped or double-matched.

If validation fails, fix it and re-run. Do not report success on a failing file.

Inspect the SQL when the change was structural — a value moving between groups, a
product added or removed:

```
python franchises/Venclexta/scripts/validate_dos_grace.py --sql
```

## Step 6 — Report and follow up

Tell the user:

- **What changed** — a table of product, field, old → new
- **Blast radius** — `AML_LOT_VAL.ipynb` regenerates `GRACE_VALUE` / `DOS_FINAL` on next
  run, moving treatment episodes and therefore reported lines of therapy for the
  affected products
- **Validation result** — validator and test output, stated plainly
- **Baseline** — whether `MIGRATION_BASELINE_*` was updated

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
- **Multiple products, one value** — apply to each entry individually. The SQL groups
  them into a shared `IN (...)` branch automatically; don't try to hand-group the YAML.
- **If the user wants to see the effect before committing to it**, `--sql` output plus
  the group summary is the closest you can get without running against data. Do not run
  the notebook against production to preview a change.

## Files

| Path | Role |
|---|---|
| `franchises/Venclexta/configuration/aml_dos_grace.yaml` | The values — what you edit |
| `franchises/Venclexta/scripts/dos_grace_config.py` | Loader, validation, SQL generation |
| `franchises/Venclexta/scripts/validate_dos_grace.py` | Validator / inspector CLI |
| `franchises/Venclexta/scripts/test_dos_grace_config.py` | Round-trip tests + migration baseline |
| `franchises/Venclexta/scripts/AML_LOT_VAL.ipynb` | Consumer — builds the final Tx table |
| `franchises/Venclexta/CONTEXT.md` | Where the business reason belongs |
