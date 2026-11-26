---
name: vault-enhance
description: Improves the knowledge vault's graph (lint-and-maintain cycle). Adds missing cross-links where notes mention each other's topics, enriches the weakest notes, fixes index drift, and proposes new notes, MOCs and merges, with a confirmation before each change. Use when the user asks to enhance, enrich, link up or maintain the vault.
argument-hint: "[max-notes-to-enrich, default 5]"
allowed-tools: Read, Grep, Glob, Bash(uv run *), Bash(date *), WebSearch, WebFetch
---

# Vault Enhance (fix, don't just report)

Enrichment budget: `$ARGUMENTS` notes (default 5).

## Setup

- **Vault root**: `${user_config.vault_path}`. If blank or a literal placeholder, use the current working directory.
- Read `${CLAUDE_PLUGIN_ROOT}/resources/vault-conventions.md` and the vault `CLAUDE.md` unless they're already in context.
- Lint: `uv run --script ${CLAUDE_PLUGIN_ROOT}/scripts/vault_lint.py --vault <root>`

## Step 1: Scan

Run lint. Build a priority list from `orphans`, `thin`, `poorly_linked`, `stale` and `missing_sources`. Notes that appear in several lists rank higher, as do notes in domains with recent `log.md` activity. Skip `02-customers/`.

## Step 2: Missing-link discovery (highest value)

1. For each note in `20-notes/`, take its topic terms: words from the filename, the H1, and any aliases.
2. Grep other notes for those terms where they don't already link to that note.
3. Keep only mentions where the link adds meaning (the sentence actually discusses that topic). Show the top ~20:
   ```
   1. guide-model-serving.md: "…feature store lookups…" → [[guide-feature-store]]
   ```
4. After the user confirms, turn the mention into an inline link. Never append bare link lists.

## Step 3: Index drift

For each path in `not_in_index`, propose an `index.md` line. Write them after confirmation.

## Step 4: Enrich the top N weak notes

For each note:
1. Read it, its sources, and its neighbors.
2. Research gaps in this order: `raw/` sources first, then the vault, then the web (official docs preferred). Record new URLs in `sources:`.
3. Show a preview: "230 → ~700 words; adds: mechanism section, example, 3 links ([[a]], [[b]], [[c]])".
4. After confirmation, weave the new content into the existing structure and update `last_verified`.

## Step 5: Suggestions (don't create anything)

- **New notes**: link targets that are broken in 2 or more notes, and frequent topics with no note.
- **New MOCs**: tag or domain clusters of 5 or more notes with no MOC.
- **Merges**: overlapping notes. Name the one to keep.

## Step 6: Report and log

Report links added, notes enriched (words before → after), index lines added, and the suggestions. Run lint again and show before → after for broken links and orphan rate. Append to `log.md`:
`## [<today>] enhance | +N links, N notes enriched, orphan rate x% → y%`.

## Rules

- Confirm before every write. At most N notes enriched per run.
- Prefer adding links over rewriting text. Only add links that are backed by evidence (see conventions §4).
