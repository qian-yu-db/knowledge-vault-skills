---
name: process-inbox
description: Compiles raw captures in the vault's 00-inbox/ into interlinked knowledge notes. Archives each source immutably in raw/, records provenance, merges into existing notes where possible, and updates index.md, log.md, MOCs and backlinks. Use when the user asks to process, compile, ingest or triage the inbox or newly clipped articles.
argument-hint: "[inbox-file ...]"
allowed-tools: Read, Grep, Glob, Bash(ls *), Bash(mkdir *), Bash(mv *), Bash(date *), Bash(uv run *), Bash(git status*), Bash(git add *), Bash(git commit *)
---

# Process Inbox (Ingest → Compile → Cross-link)

You are a compiler. You synthesize sources into the vault's knowledge graph; you don't copy-paste or narrate them.

## Setup

- **Vault root**: `${user_config.vault_path}`. If blank or a literal placeholder, use the current working directory. It must contain `20-notes/`; if not, stop and suggest `/knowledge-vault:setup-vault`.
- Read `${CLAUDE_PLUGIN_ROOT}/resources/vault-conventions.md` and the vault `CLAUDE.md` (for About Me and the schema) unless they're already in context.
- Lint command: `uv run --script ${CLAUDE_PLUGIN_ROOT}/scripts/vault_lint.py --vault <root>`
- Today: !`date +%Y-%m-%d` · Raw folder: `raw/`!`date +%Y-%m`

Scope: `$ARGUMENTS` if given (specific inbox files). Otherwise every file in `00-inbox/`.

## Phase 1: Analyze (read-only)

For each inbox item, record:
- **Thesis** (1–2 sentences) and **3–5 key concepts**.
- **Novel claims**: what's new or non-obvious, with short quotes.
- **Type(s)**, from the vault CLAUDE.md note types.
- **Capture kind**: a web clip or paper gets a full compile; a quick personal note gets a light compile.

## Phase 2: What does the vault already know?

Follow the search ladder in the conventions (index.md first, then qmd, the Obsidian CLI, or Grep). For each key concept, read the top 3–5 matching notes. Write down "the vault has X, is missing Y".

## Phase 3: Triage plan, then wait for approval

One outcome per item:
- **CREATE** `type-name.md`: no existing note covers the core topic.
- **MERGE** into `existing.md`: an existing note covers most of it. Say exactly what new knowledge gets woven in.
- **SPLIT**: the source covers 3+ distinct topics. Give a list of CREATE/MERGE actions.
- **SKIP**: duplicate or low value. The source still moves to `raw/` so it isn't lost.

The plan also shows:
- Where each source will be archived (`raw/YYYY-MM/<slug>.md`).
- The MOCs that will be touched.
- Whether a local git commit per item will be made (only if the vault is a git repo).

**Stop and wait for the user to approve or edit the plan.**

## Phase 4: Compile

**Parallelism.** With 2 or more approved items, dispatch one `knowledge-vault:source-compiler` subagent per item, all in a single message so they run concurrently. Two items that MERGE into the *same* target must run one after the other, never in parallel. With a single item, do the work inline using the same instructions.

Give each subagent a self-contained brief (it can't see this conversation):
- the absolute vault root;
- the inbox file path, and the raw path it will have;
- the approved actions (CREATE/MERGE/SPLIT and target filenames);
- the template path for each CREATE (`<root>/30-templates/<type>.md`);
- the conventions path (`${CLAUDE_PLUGIN_ROOT}/resources/vault-conventions.md`);
- the "About Me" and "Learning Goals" text from the vault CLAUDE.md;
- the related notes found in Phase 2.

The subagent writes **only** its target notes. It returns a report listing: files written, word counts, outgoing links, suggested backlinks, the index line, and suggested future notes.

## Phase 5: Integrate (main thread only)

Shared files are edited only here, to avoid conflicting writes.
1. **Archive the source**: `mkdir -p raw/YYYY-MM && mv 00-inbox/<file> raw/YYYY-MM/<slug>.md`. Check that the notes' `sources:` entries match this path.
2. **Backlinks**: add each suggested backlink as an inline sentence in the named note, where the relationship makes sense.
3. **MOCs**: add new notes under the right section of each relevant `10-mocs/MOC-*.md`.
4. **index.md**: add or update one line per created or merged note.
5. **log.md**: append `## [<today>] ingest | <source title>` with raw path, created, merged.
6. **Verify**: run the lint command and fix any *new* broken links or missing fields in the touched notes.
7. **Commit** (if approved): `git add -A <touched paths> && git commit -m "vault: ingest <title>"`.

## Phase 6: Report

```
## Compilation Report
Processed: N  |  Created: list (words)  |  Merged: list (what was added)
Archived to raw/: N  |  Backlinks added: N  |  MOCs updated: list
Lint: broken links before → after
Suggested follow-ups: MOC candidates, missing concepts referenced 2+ times
```

## Rules

- Never write permanent notes before the Phase 3 approval.
- Prefer MERGE over CREATE. Duplicated knowledge is the most expensive kind of vault debt.
- Never delete a source. It moves to `raw/` and is never edited there.
- Follow the linking and sizing rules in the conventions. There is no word-count target.
