# Venclexta — franchise context

Business and technical context for the Venclexta franchise. Read this before reasoning
about any script in `franchises/Venclexta/`.

> **Status: scaffold.** Sections marked `TODO` need completion by the franchise owner.
> Do not treat a `TODO` as an absent requirement, and do not fill one in by inferring
> from another franchise — franchise rules differ. If a script's behaviour depends on
> something still marked `TODO`, say so rather than guessing.

---

## Product

| | |
|---|---|
| Brand | Venclexta |
| Generic name | venetoclax |
| Therapy area | Oncology — haematology |
| Mechanism | BCL-2 inhibitor |
| Principal indications | Chronic lymphocytic leukaemia (CLL); acute myeloid leukaemia (AML) |

Commonly used in combination regimens, which matters analytically: attribution between
combination partners is a recurring source of definitional difficulty. Record the
franchise's chosen convention under [Business rules](#business-rules).

## Ownership

| Role | Name | Notes |
|---|---|---|
| Analytics owner | `TODO` | Accountable for everything under `franchises/Venclexta/` |
| Business stakeholder | `TODO` | Owns metric and business-rule definitions |
| Technical contact | `TODO` | Data sources, access, orchestration |

Changes under this directory should be reviewed by the analytics owner.

## Business context

`TODO` — What this franchise's analytics exist to support. Two or three paragraphs:
the commercial questions being answered, who consumes the outputs, and the reporting
cadence that shapes the workloads.

Worth capturing explicitly, because each drives logic that is otherwise hard to
account for:

- Which customer segments matter — community practice, academic centre, IDN, specialty
  pharmacy.
- Which channels the data covers, and any known blind spots.
- Whether analysis is patient-level, HCP-level, account-level, or several of these.
- Indication-level splits, if the franchise reports CLL and AML separately.

## Data sources

`TODO` — Table-level detail belongs in [`docs/data-dictionary.md`](../../docs/data-dictionary.md);
this section is the orientation to which feeds this franchise uses and their character.

| Source | Type | Cadence | Notes |
|---|---|---|---|
| `TODO` | claims / sales / patient / reference | `TODO` | latency, restatement window, caveats |

Record refresh latency and restatement behaviour. Both regularly explain "wrong" numbers
that are in fact correct for the moment they were produced.

## Business rules

`TODO` — the rules that materially shape output. This is the highest-value section of
this file and the one agents rely on most, because these rules are not recoverable from
the code alone.

For each rule state what it is, why it exists, and where it is implemented:

| Rule | Rationale | Where implemented |
|---|---|---|
| `TODO` | `TODO` | `configuration/…` or `scripts/…` |

Candidates specific to this franchise:

- Combination-regimen attribution — how TRx is credited when Venclexta is one component.
- Indication assignment where a patient's indication is not stated directly.
- Any franchise-specific deviation from the shared metric definitions in
  `docs/data-dictionary.md`. **A divergence must be recorded here.** An unrecorded
  divergence is how a franchise's numbers quietly stop reconciling.

## User inputs

Run-time inputs a user supplies. Scripts ship with these deliberately blank; an agent
should surface them, never autofill them.

| Input | Applies to | Notes |
|---|---|---|
| Reporting period | `TODO` | `TODO` |
| Market / product filter | `TODO` | `TODO` |
| `TODO` | `TODO` | `TODO` |

## Configuration

Configuration lives in [`configuration/`](configuration/). Per
[`docs/conventions.md`](../../docs/conventions.md), config files are grouped by business
concern rather than one file per script, and hold no secret values — only secret names
resolved at run time.

| File | Purpose |
|---|---|
| `TODO` | `TODO` |

## Scripts

Registered in [`manifest.yaml`](manifest.yaml) — the authoritative inventory. Consult it
rather than listing `scripts/`; it records each script's declared inputs, outputs and
configuration dependencies.

## Outputs

`TODO` — what this franchise produces and who consumes it.

| Output | Consumer | Cadence |
|---|---|---|
| `TODO` | `TODO` | `TODO` |

Every final output table needs a data dictionary entry in
[`docs/data-dictionary.md`](../../docs/data-dictionary.md).

## Known caveats

`TODO` — the things that surprise people. Data gaps, historical restatements, periods
where a definition changed, indications entering scope mid-series, sources not valid
before a given date.

Recording a caveat here is far cheaper than the downstream investigation caused by
omitting it.
