# Knowledge Vault — Claude Code Plugin

An Obsidian knowledge base that Claude maintains for you, based on Karpathy's ["LLM Wiki"](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern:

- **immutable raw sources**;
- a **compiled, interlinked wiki** that the model keeps up to date;
- a **schema** (`CLAUDE.md`) that you and the model evolve together.

Every ingest, query and session leaves the vault better than before.

## Install

```bash
# From a local clone
claude plugin marketplace add /path/to/knowledge-vault
claude plugin install knowledge-vault@knowledge-vault

# Then, inside Claude Code
/knowledge-vault:setup-vault ~/my-knowledge-vault      # new vault, or upgrade an existing one
/plugin   # → knowledge-vault → configure → set vault_path (lets skills and hooks work from any directory)
```

Requirements:
- `uv` (runs the lint scripts; falls back to `python3`);
- `jq` (hooks);
- Obsidian 1.12+ with Bases enabled.

Optional extras:
- the [Obsidian CLI](https://obsidian.md/help/cli);
- [qmd](https://github.com/tobi/qmd), for local hybrid search once the vault passes a few hundred notes;
- the official [obsidian-skills](https://github.com/obsidianmd/obsidian-skills).

## Operations

| Operation | Skill | What it does |
|-----------|-------|-------------|
| **Ingest** | `/knowledge-vault:process-inbox` | Triage plan (CREATE / MERGE / SPLIT / SKIP), which you approve first. Then one `source-compiler` subagent per source, the source archived to `raw/`, `sources:` provenance, backlinks, MOCs, `index.md` and `log.md` |
| **Query** | `/knowledge-vault:vault-query <q>` | Reads `index.md`, then searches (qmd, Obsidian CLI or grep). Answers with `[[citations]]` and gaps, and can file the answer back as a `synthesis` note |
| **Lint** | `/knowledge-vault:vault-audit [--deep]` | Deterministic report from `scripts/vault_lint.py`. `--deep` adds `claim-checker` subagents that look for contradictions, unsupported claims, stale claims and provenance laundering |
| **Enhance** | `/knowledge-vault:vault-enhance` | Adds missing inline links, enriches weak notes, fixes index drift, suggests MOCs and merges |
| **Refresh** | `/knowledge-vault:review-outdated` | Re-checks stale notes against current docs, then updates or deprecates them |
| **Write-back** | `/knowledge-vault:session-wrap` | Session handoff in the weekly log and `log.md`, then proposed insights for permanent notes |
| Other | `setup-vault`, `build-moc`, `new-paper`, `new-customer`, `weekly-quiz`, `project-status` | |

Every skill that changes permanent notes shows a plan and waits for your approval.

## Hooks

| Event | Behavior |
|-------|----------|
| `SessionStart` | When the session runs inside the vault, Claude gets the inbox count, a lint summary, and the last session's `Next:` step |
| `PostToolUse` (Write/Edit) | Lints the note Claude just wrote (frontmatter, required fields, broken links) and reports errors back to Claude |
| `Stop` | Once per session, after 25+ tool calls, shows *you* a reminder to run session-wrap. Set `KNOWLEDGE_VAULT_WRAP_MIN_TOOL_CALLS` to change the threshold |

## Vault layout

```
00-inbox/   queue of captures       raw/          immutable processed sources (raw/YYYY-MM/)
01-projects/ 02-customers/          index.md      catalog Claude reads first
10-mocs/    MOCs + .base dashboards  log.md        append-only ops log
20-notes/   compiled notes (flat)    CLAUDE.md     schema: types, About Me, Learning Goals
30-templates/ 40-archive/ 50-logs/ assets/
```

## Development

```bash
uv run --with pytest pytest -q tests                  # lint/scan script tests
claude plugin validate . --strict                     # manifest and structure
uv run --script evals/run_smoke.py --baseline         # behavior evals, headless (works with gateway/apiKeyHelper auth)
claude plugin eval . --scaffold --no-publish --runs 1 \
  --allow-tools "Bash(uv run *)" "Bash(date *)" "Bash(ls *)"   # same cases via the official runner (needs direct API auth)
uv run --script scripts/vault_lint.py --vault ~/my-vault --format text   # lint a real vault
```

Plugin structure:

```
.claude-plugin/   plugin.json (userConfig: vault_path, workspace_root), marketplace.json
skills/           12 skills (SKILL.md with frontmatter)
agents/           source-compiler, claim-checker
hooks/            hooks.json + session-start / validate-note / stop-wrap-reminder
scripts/          vault_lint.py, workspace_scan.py (stdlib only, PEP 723)
resources/        vault-conventions.md, claude-md-template.md, templates/, bases/
evals/            behavior eval cases + fixture vault
tests/            pytest for the scripts
```

## Upgrading from 1.x

- Commands are now skills with the same names (`/knowledge-vault:process-inbox`, …).
- Run `/knowledge-vault:setup-vault <your-vault>`. It detects the existing vault and adds `raw/`, `index.md`, `log.md`, the new templates and a Bases dashboard, without overwriting anything.
- Move anything personal (role, learning goals, workspace category patterns) into your vault's `CLAUDE.md`: "About Me", "Learning Goals", "Workspace Categories".
