---
name: vault-query
description: Answers a question from the user's Obsidian knowledge vault with citations to vault notes and raw sources, says what the vault does not know, and offers to file the answer back as a synthesis note. Use when the user asks what their vault or notes say about a topic, asks to search or consult their knowledge base, or wants an answer grounded in their own notes.
argument-hint: "<question>"
arguments: [question]
allowed-tools: Read, Grep, Glob, Bash(qmd *), Bash(obsidian search*), Bash(obsidian backlinks*), Bash(date *), Bash(uv run *)
---

# Query the Vault

Question: $question

## Setup

- **Vault root**: `${user_config.vault_path}`. If blank or a literal placeholder, use the current working directory. It must contain `20-notes/`.
- Read `${CLAUDE_PLUGIN_ROOT}/resources/vault-conventions.md` (search ladder, provenance) unless it's already in context.

## Steps

1. **Retrieve** with the search ladder:
   - Read `index.md`.
   - Then use `qmd query --json -n 10 "<question>"` if `qmd` exists, or `obsidian search query="…"` if the Obsidian CLI exists. Otherwise Grep `20-notes/` and `10-mocs/` with several phrasings and synonyms.
   - Read the 3–8 most relevant notes in full. Follow one level of `[[links]]` when they look relevant.
2. **Check against sources**. For each claim you plan to use, open the `raw/` file or note in that note's `sources:` if the claim is load-bearing or surprising.
3. **Answer**:
   - Lead with the direct answer. Every factual sentence cites `[[note]]`, and the raw source where you checked one.
   - Keep what the vault says apart from your own general knowledge. Label the latter "Outside the vault:".
   - Add a **Gaps** line: what the vault doesn't cover, or where notes disagree.
   - Use whatever format suits the question: prose, a comparison table, a checklist, or Mermaid.
4. **Offer to file it back**. If the answer is a reusable synthesis (a comparison, decision, or explanation that spans several notes), ask:
   > File this as `20-notes/synthesis-<slug>.md`? (yes / no / merge into [[existing-note]])

   On yes:
   - Use the `synthesis` template. Frontmatter: `question`, `sources:` (the notes and raw files used), `date_added`, `last_verified`.
   - Add the note to `index.md` and link it from the 1–3 notes it draws on most.
   - Append `## [<today>] query | <question>` to `log.md`.
5. If you found contradictions or stale notes, list them. Suggest `/knowledge-vault:review-outdated` or `/knowledge-vault:vault-audit --deep`.

## Rules

- Never present general model knowledge as if the vault says it.
- Don't write anything without the user's yes in step 4.
