# Imbruvica — franchise context

Business and technical context for the Imbruvica franchise. Read this before reasoning
about any script in `franchises/Imbruvica/`.

> **Status: scaffold.** Sections marked `TODO` need completion by the franchise owner.
> Do not treat a `TODO` as an absent requirement, and do not fill one in by inferring
> from another franchise — franchise rules differ. If a script's behaviour depends on
> something still marked `TODO`, say so rather than guessing.

---

## Product

| | |
|---|---|
| Brand | Imbruvica |
| Generic name | ibrutinib |
| Therapy area | Oncology — haematology |
| Mechanism | Bruton's tyrosine kinase (BTK) inhibitor |
| Principal indications | Chronic lymphocytic leukaemia (CLL); mantle cell lymphoma (MCL); Waldenström's macroglobulinaemia (WM); chronic graft-versus-host disease |

Two characteristics shape this franchise's analytics:

**It is an oral product with a long history.** Volume is visible through retail and
specialty pharmacy prescription feeds, and the series is long enough for trend and
persistence analysis to be meaningful — which also means it spans definitional changes.
Record where those breaks fall under [Known caveats](#known-caveats).

**It is a mature franchise in a competitive class.** Analytics here typically concern
share, persistence and switching within the BTK-inhibitor class rather than launch
dynamics. Indication mix has shifted over time, and some indications have been withdrawn
or narrowed in various markets — so a filter that was correct historically may not be
correct now. Note the applicable period for any indication-dependent logic.

## Ownership

| Role | Name | Notes |
|---|---|---|
| Analytics owner | `TODO` | Accountable for everything under `franchises/Imbruvica/` |
| Business stakeholder | `TODO` | Owns metric and business-rule definitions |
| Technical contact | `TODO` | Data sources, access, orchestration |

Changes under this directory should be reviewed by the analytics owner.

## Business context

`TODO` — What this franchise's analytics exist to support. Two or three paragraphs:
the commercial questions being answered, who consumes the outputs, and the reporting
cadence that shapes the workloads.

Worth capturing explicitly for a mature oral franchise:

- The competitive set used for share calculations, and the market definition that bounds
  it. This is a definitional choice, not a fact, and it must be written down.
- Which customer segments matter — community practice, academic centre, IDN, specialty
  pharmacy.
- Which channels the data covers, and known blind spots.
- Whether analysis is patient-level, HCP-level, account-level, or several of these.
- Persistence, adherence and switching measures in use, and the windows they assume.

## Data sources

`TODO` — Table-level detail belongs in [`docs/data-dictionary.md`](../../docs/data-dictionary.md);
this section is the orientation to which feeds this franchise uses and their character.

| Source | Type | Cadence | Notes |
|---|---|---|---|
| `TODO` | retail claims / specialty pharmacy / sales / patient / reference | `TODO` | latency, restatement window, caveats |

Record refresh latency and restatement behaviour, and for a long-running franchise also
record when a feed changed or was replaced. Both regularly explain "wrong" numbers that
are in fact correct for the moment they were produced.

## Business rules

`TODO` — the rules that materially shape output. This is the highest-value section of
this file and the one agents rely on most, because these rules are not recoverable from
the code alone.

For each rule state what it is, why it exists, and where it is implemented:

| Rule | Rationale | Where implemented |
|---|---|---|
| `TODO` | `TODO` | `configuration/…` or `scripts/…` |

Candidates specific to this franchise:

- Market definition for share calculations — which competitors are in class, and from
  when. Changes to this rule break comparability and must be dated.
- Persistence and adherence windows, and the gap that ends a treatment episode.
- Switching logic — what qualifies as a switch versus a temporary interruption.
- Indication assignment across CLL, MCL and WM where not stated directly, including
  periods where an indication was withdrawn or narrowed.
- Any franchise-specific deviation from the shared metric definitions in
  `docs/data-dictionary.md`. **A divergence must be recorded here.** For a franchise
  this old, historical divergences are likely and are exactly what a reader needs.

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

Market and competitor code lists are strong candidates for configuration here, since
they change without any change in logic.

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

`TODO` — the things that surprise people. For a long-running franchise the most valuable
entries are dated definitional breaks: when the market definition changed, when an
indication entered or left scope, when a data feed was replaced, and the earliest period
for which the current definitions hold.

Recording a caveat here is far cheaper than the downstream investigation caused by
omitting it.
