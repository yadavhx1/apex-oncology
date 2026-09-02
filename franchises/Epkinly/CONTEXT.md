# Epkinly — franchise context

Business and technical context for the Epkinly franchise. Read this before reasoning
about any script in `franchises/Epkinly/`.

> **Status: scaffold.** Sections marked `TODO` need completion by the franchise owner.
> Do not treat a `TODO` as an absent requirement, and do not fill one in by inferring
> from another franchise — franchise rules differ. If a script's behaviour depends on
> something still marked `TODO`, say so rather than guessing.

---

## Product

| | |
|---|---|
| Brand | Epkinly |
| Generic name | epcoritamab |
| Therapy area | Oncology — haematology |
| Mechanism | CD3xCD20 bispecific T-cell engaging antibody |
| Principal indications | Diffuse large B-cell lymphoma (DLBCL); follicular lymphoma |

Two characteristics shape this franchise's analytics more than anything else:

**It is administered, not dispensed.** As an injectable given in a care setting, volume
is visible through medical-benefit channels rather than retail pharmacy. Metrics built
on retail prescription feeds do not transfer from an oral franchise without redefinition.

**It uses step-up dosing.** Treatment begins with a defined ramp-up schedule before full
dosing. Counting administrations without accounting for the step-up schedule
systematically misstates patient counts and persistence. Record the convention adopted
under [Business rules](#business-rules).

**It is the newest of the three franchises.** Series are shorter, launch dynamics still
dominate, and year-over-year comparisons may not be meaningful yet. Note the first
period with reliable data under [Known caveats](#known-caveats).

## Ownership

| Role | Name | Notes |
|---|---|---|
| Analytics owner | `TODO` | Accountable for everything under `franchises/Epkinly/` |
| Business stakeholder | `TODO` | Owns metric and business-rule definitions |
| Technical contact | `TODO` | Data sources, access, orchestration |

Changes under this directory should be reviewed by the analytics owner.

## Business context

`TODO` — What this franchise's analytics exist to support. Two or three paragraphs:
the commercial questions being answered, who consumes the outputs, and the reporting
cadence that shapes the workloads.

Worth capturing explicitly for an administered launch product:

- Site of care mix — academic centre, community practice, hospital outpatient — and how
  it is determined.
- Which channels the data covers, and known blind spots. Medical-benefit visibility is
  usually less complete and slower than retail.
- Whether analysis is patient-level, HCP-level, account-level, or several of these.
- Launch-phase measures in use — depth and breadth of prescribing, account activation —
  which differ from steady-state measures.

## Data sources

`TODO` — Table-level detail belongs in [`docs/data-dictionary.md`](../../docs/data-dictionary.md);
this section is the orientation to which feeds this franchise uses and their character.

| Source | Type | Cadence | Notes |
|---|---|---|---|
| `TODO` | medical claims / specialty distribution / patient services / reference | `TODO` | latency, restatement window, caveats |

Record refresh latency and restatement behaviour. For a medical-benefit product both are
typically worse than for retail, and both regularly explain "wrong" numbers that are in
fact correct for the moment they were produced.

## Business rules

`TODO` — the rules that materially shape output. This is the highest-value section of
this file and the one agents rely on most, because these rules are not recoverable from
the code alone.

For each rule state what it is, why it exists, and where it is implemented:

| Rule | Rationale | Where implemented |
|---|---|---|
| `TODO` | `TODO` | `configuration/…` or `scripts/…` |

Candidates specific to this franchise:

- Step-up dosing treatment — whether ramp-up administrations count toward volume, and
  how a patient's treatment start is dated.
- Administration-to-patient attribution, and the deduplication rule when the same
  administration appears in more than one feed.
- Site-of-care assignment where the administering account differs from the prescriber's
  affiliation.
- Indication assignment between DLBCL and follicular lymphoma where not stated directly.
- Any franchise-specific deviation from the shared metric definitions in
  `docs/data-dictionary.md`. **A divergence must be recorded here** — and for an
  administered product, divergence from prescription-based definitions is likely rather
  than exceptional.

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

`TODO` — the things that surprise people. Specifically for this franchise: the first
period with reliable data, any indication that entered scope mid-series, periods where
channel coverage changed, and the point at which launch-phase measures stop being the
right lens.

Recording a caveat here is far cheaper than the downstream investigation caused by
omitting it.
