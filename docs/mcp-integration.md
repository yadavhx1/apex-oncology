# MCP integration

How to expose `apex-oncology` to AI agents over the Model Context Protocol.

The machine-readable source of truth is [`.mcp/context.yaml`](../.mcp/context.yaml).
This document explains the reasoning behind that file and how a server over this
repository should behave.

---

## Why not just give agents filesystem access?

A generic filesystem MCP server pointed at this repository technically works, and
behaves badly in practice:

- **Cross-franchise contamination.** Nothing stops a search from returning Epkinly
  business rules while answering a Venclexta question. Because franchise rules genuinely
  differ, the resulting answer is fluent and wrong — the worst failure mode.
- **Context exhaustion.** Whole-repo reads crowd out the specific config file that
  actually answers the question.
- **Metadata bypassed.** `manifest.yaml` already records every script's inputs, outputs
  and dependencies. Raw file access invites grepping instead of reading the answer.
- **No guardrails.** Filesystem access has no notion of "this path is production-affecting."

So the design goal is **narrow resources, franchise-scoped by default**. Expose intent
("give me this franchise's manifest"), not mechanism ("read this path").

## Suggested MCP surface

| Tool | Resource URI | Parameters | Returns |
|---|---|---|---|
| `get_repo_context()` | `apex://repo/context` | — | Global rules and repository map: `AGENTS.md` + `.mcp/context.yaml` |
| `get_franchise_context(franchise)` | `apex://franchise/{franchise}/context` | `franchise` | That franchise's `CONTEXT.md` |
| `get_franchise_manifest(franchise)` | `apex://franchise/{franchise}/manifest` | `franchise` | That franchise's `manifest.yaml` |
| `get_script_dependencies(franchise, script)` | `apex://franchise/{franchise}/script/{script}/dependencies` | `franchise`, `script` | Resolved config files, source tables and outputs for one script |
| `search_context(query, franchise?)` | `apex://search` | `query`, optional `franchise` | Matches from context and documentation |

### Notes per tool

**`get_repo_context()`** — the cheap first call. An agent that starts here learns the
franchise list and the context chain without touching franchise files.

**`get_franchise_context(franchise)`** — business framing. Should be called before
reasoning about any script in that franchise, because the logic only makes sense against
the business rules.

**`get_franchise_manifest(franchise)`** — the workhorse. Most "which script does X" and
"what does this script read" questions resolve entirely from the manifest, with no
script or config file opened at all.

**`get_script_dependencies(franchise, script)`** — resolves one script's declared
dependencies from the manifest so the agent can request exactly the right config files.
Prefer this over returning the whole manifest when the script is already known.

**`search_context(query, franchise?)`** — `franchise` should be treated as
near-mandatory. Omit it only for genuinely cross-franchise questions, and have the server
label such results with their franchise so the agent cannot conflate them.

## Retrieval strategy

Rules a server should enforce, not merely document:

1. **Franchise-scope by default.** When `franchise` is supplied, never return content
   from another franchise. When it is omitted, label every result with its franchise.
2. **Prefer metadata over traversal.** Answer from `manifest.yaml` where possible.
   Reserve file reads for cases metadata cannot resolve.
3. **Return the narrowest useful unit.** One config file, not the directory. One script
   entry, not the whole manifest.
4. **Read only what the manifest names.** A script's config dependencies are declared;
   returning all of `configuration/` defeats the design.
5. **Never return secrets or data.** The repository should contain neither. A server
   that finds either should refuse and surface it as a problem, not pass it through.
6. **Report manifest drift.** If a script references a config file the manifest doesn't
   declare, the script is authoritative — return the truth and flag the inconsistency.

## Typical call sequences

**Explain a script**

```
get_franchise_context("Venclexta")
get_script_dependencies("Venclexta", "trx_monthly.sql")
-> read the script and only the config files returned
```

**Find which script does X**

```
get_franchise_manifest("Venclexta")
-> match on purpose / outputs; often no further calls needed
search_context("specialty pharmacy", franchise="Venclexta")   # only if unresolved
```

**First contact with the repository**

```
get_repo_context()
-> franchise list, context chain, safety rules
```

A well-behaved agent's first call is `get_repo_context()` and its second is
franchise-scoped. An agent whose first call is an unscoped `search_context` is a signal
that the surface is under-documented in its client config.

## Server implementation guidance

- **Read-only by default.** Writes should go through normal Git review, not an MCP tool.
  If write tools are added, exclude `.mcp/context.yaml`, the agent guidance files and
  anything under `configuration/` from unattended modification.
- **Resolve `franchise` case-insensitively** but return the canonical `PascalCase` name
  from `.mcp/context.yaml`.
- **Reject unknown franchises explicitly.** Return the valid list rather than empty
  results, so the agent corrects itself instead of concluding nothing exists.
- **Cache `.mcp/context.yaml` and the manifests**; invalidate on file change. They are
  read constantly and change rarely.
- **Enforce the size of returns.** A single config file or script entry is the unit. Cap
  responses and paginate rather than dumping directories.
- **Redact defensively.** Scan returns for credential-shaped strings and refuse rather
  than pass them through, even though tracked files should never contain them.
- **Keep `.mcp/context.yaml` in sync.** Structural changes — a new franchise, a new docs
  page, a changed context chain — must be reflected there or MCP clients will not see
  them. This is the most common integration failure.

## Client configuration

Whatever client you use, point it at the entry-point file so scoping rules load before
any franchise content:

- Claude Code reads [`CLAUDE.md`](../CLAUDE.md) automatically.
- Gemini reads [`GEMINI.md`](../GEMINI.md).
- Copilot reads [`.github/copilot-instructions.md`](../.github/copilot-instructions.md).
- Custom agents and MCP tools should call `get_repo_context()` first, which returns
  [`AGENTS.md`](../AGENTS.md).

All four defer to `AGENTS.md`. Update it there, not in four places.
