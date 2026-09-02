# Onboarding a new franchise

Steps to add a franchise to `apex-oncology`. Copy from `templates/`; do not hand-roll —
consistency is what lets agents navigate every franchise the same way.

Throughout, `<Franchise>` is the brand name in `PascalCase`, e.g. `Venclexta`.

---

## 1. Create the directory

```
franchises/<Franchise>/
├── CONTEXT.md
├── manifest.yaml
├── configuration/
└── scripts/
```

Copy `templates/franchise/CONTEXT.md` and `templates/franchise/manifest.yaml` into
place, then create the two empty directories. Add a `.gitkeep` to each until real files
land — Git does not track empty directories.

## 2. Fill in `CONTEXT.md`

The scaffold marks every required section with `TODO`. The two that matter most:

**Business rules.** The rules that shape output, why each exists, and where it is
implemented. This is not recoverable from the code, which is exactly why it belongs
here. Record any deviation from the shared metric definitions in
`docs/data-dictionary.md` — an unrecorded divergence is how a franchise's numbers
quietly stop reconciling.

**Known caveats.** Data gaps, restatement windows, dated definitional breaks, the
earliest period for which current definitions hold. Cheaper to write than the
investigation caused by omitting it.

Also complete: product details, named owners, business context, data sources, user
inputs, outputs.

Delete `TODO` markers as you complete them, and remove the scaffold status note at the
top once the file is real. Leaving stale `TODO`s is worse than leaving the section out —
agents are told to treat them as unknown and will refuse to answer from them.

## 3. Fill in `manifest.yaml`

Set `franchise.name`, `generic_name` and `owner`. Leave `scripts: []` and
`configuration: []` empty at first — they grow as workloads land.

## 4. Add configuration

Config files go in `configuration/`, grouped by business concern
(`market_filters.yaml`, `source_tables.yaml`, `output_targets.yaml`) rather than one
file per script. Follow `templates/config_schema.yaml`.

Everything configurable belongs here: parameters, database and schema names, paths,
thresholds, business-rule values, product and market code lists.

**Never a secret value** — configuration names a secret, and the value resolves from
the environment or a vault at run time. See `docs/conventions.md`.

Register each file in `manifest.yaml` under `configuration:` with its purpose.

## 5. Add scripts

Scripts go in `scripts/` as `snake_case` files named for what they produce. Each one:

- Opens with the header block from `templates/TEMPLATE_SCRIPT.md` — objective, user
  inputs, source tables, output.
- Reads configuration rather than hardcoding values.
- Is registered in `manifest.yaml` in the same change, with inputs, outputs, config
  dependencies, purpose, owner, schedule and user inputs.
- Has notebook outputs cleared before commit.

## 6. Register the franchise in `.mcp/context.yaml`

Add an entry under `franchises:`:

```yaml
  - name: <Franchise>
    path: franchises/<Franchise>
    generic_name: <generic>
    context: franchises/<Franchise>/CONTEXT.md
    manifest: franchises/<Franchise>/manifest.yaml
    configuration: franchises/<Franchise>/configuration
    scripts: franchises/<Franchise>/scripts
```

**This is the step most often missed.** A franchise absent from `.mcp/context.yaml` is
invisible to MCP clients even though every file exists on disk. The symptom is an agent
insisting the franchise isn't in the repository.

## 7. Add data dictionary entries

Add the franchise's source tables and every final output table to
`docs/data-dictionary.md`, including output column definitions with derivations.
Intermediate and staging tables do not need entries.

Cross-check that each table also appears in `manifest.yaml` under `source_tables` or
`outputs` — the two must agree.

## 8. Update `docs/architecture.md`

Add the franchise to the layout tree and the ownership table.

---

## Checklist

```
[ ] franchises/<Franchise>/ created with CONTEXT.md, manifest.yaml, configuration/, scripts/
[ ] CONTEXT.md complete — business rules and known caveats genuinely filled in
[ ] All TODO markers resolved or deliberately retained; scaffold note removed
[ ] manifest.yaml has franchise name, generic name, owner
[ ] Config files follow config_schema.yaml and contain no secret values
[ ] Every script registered in manifest.yaml
[ ] Every script has the TEMPLATE_SCRIPT.md header block
[ ] Notebook outputs cleared
[ ] Franchise registered in .mcp/context.yaml
[ ] Source and output tables added to docs/data-dictionary.md
[ ] docs/architecture.md layout tree and ownership table updated
[ ] Named owners recorded, not left as TODO
```

## Verifying it worked

Ask an agent a question scoped to the new franchise — *"For `<Franchise>`, what scripts
exist and what do they produce?"* A correctly onboarded franchise is answered from
`CONTEXT.md` and `manifest.yaml` alone, without the agent reading another franchise or
sweeping the filesystem. If the agent cannot find the franchise at all, revisit step 6.

## Related

| | |
|---|---|
| Operating rules | `AGENTS.md` |
| Naming and metadata | `docs/conventions.md` |
| Architecture and ownership | `docs/architecture.md` |
| MCP surface | `docs/mcp-integration.md` |
| Context template | `templates/franchise/CONTEXT.md` |
| Manifest template | `templates/franchise/manifest.yaml` |
| Script header template | `templates/TEMPLATE_SCRIPT.md` |
| Config shape | `templates/config_schema.yaml` |
