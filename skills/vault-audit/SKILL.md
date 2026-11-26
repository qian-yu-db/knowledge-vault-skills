---
name: vault-audit
description: Reports on the health of the knowledge vault — broken links, orphans, missing frontmatter or required fields, stale notes, missing provenance, naming, index drift — and with --deep checks note clusters for contradictions and unsupported claims. Report only; makes no changes. Use for a monthly vault health check or when the user asks about vault quality.
argument-hint: "[--deep] [topic-or-MOC]"
allowed-tools: Read, Grep, Glob, Bash(uv run *), Bash(date *)
---

# Vault Audit (read-only)

Arguments: `$ARGUMENTS`

## Setup

- **Vault root**: `${user_config.vault_path}`. If blank or a literal placeholder, use the current working directory.
- Read `${CLAUDE_PLUGIN_ROOT}/resources/vault-conventions.md` unless it's already in context.

## Step 1: Deterministic checks

Run:
```bash
uv run --script ${CLAUDE_PLUGIN_ROOT}/scripts/vault_lint.py --vault <root>
```
Use its JSON as the source of truth for every count. Don't recount by hand.

## Step 2: Judgment checks (cheap)

Using the JSON plus filenames and titles:
- **Duplicates or merge candidates**: titles or topics that nearly match.
- **MOC coverage**: domains or tags with 5 or more notes and no MOC.
- **Misfiled notes**: for example, a non-MOC in `10-mocs/`, or compiled knowledge in `01-projects/`.
- **Inbox backlog**: items older than 2 weeks.

## Step 3: Semantic checks (only with `--deep`)

1. Pick up to 4 clusters to check: the topic or MOC given in the arguments, otherwise the MOCs with the most stale or missing-source notes. A cluster is a MOC plus the notes it links to, at most ~12 notes.
2. Dispatch one `knowledge-vault:claim-checker` subagent per cluster, all in one message. Brief each with the absolute vault root and the note paths.
3. Merge their findings. Drop anything that isn't backed by a quote.

## Step 4: Report

```
## Vault Audit — <date>
Stats: notes by type, inbox size, orphan rate, broken links, % with sources, index coverage
Trend: compare with the last `audit` entry in log.md, if there is one

### Critical (fix soon)
broken links, missing frontmatter or required fields, contradictions (deep)
### Warnings
orphans, stale (Databricks or code notes >90d, others >180d), missing sources, not in index, naming
### Suggestions
MOC candidates, merge candidates, notes to enrich (→ /knowledge-vault:vault-enhance), stale notes to review (→ /knowledge-vault:review-outdated)
```

Finally, append to `log.md` (an append-only operations log; ask once if it doesn't exist):
`## [<today>] audit | <N> notes, <broken> broken links, orphan rate <x%>`.
