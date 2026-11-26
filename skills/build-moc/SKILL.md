---
name: build-moc
description: Builds or updates a Map of Content (MOC) for a topic in the knowledge vault. Groups related notes into curated sections, embeds a live Obsidian Bases view of the notes that link to it, and updates index.md and parent notes. Use when the user asks for a MOC, topic index or overview page, or when a topic has 5 or more notes.
argument-hint: "<topic>"
arguments: [topic]
allowed-tools: Read, Grep, Glob, Bash(uv run *), Bash(date *)
---

# Build or Update a MOC: $topic

## Setup

- **Vault root**: `${user_config.vault_path}`. If blank or a literal placeholder, use the current working directory.
- Read `${CLAUDE_PLUGIN_ROOT}/resources/vault-conventions.md` unless it's already in context. Template: `<root>/30-templates/moc.md`.

## Steps

1. **Collect.** Gather the notes for the topic: the `index.md` sections, tags, filenames, and content (Grep, plus synonyms). Include papers, concepts, guides, code patterns, experiments, and synthesis notes. If `10-mocs/MOC-<Topic>.md` exists, read it and update it rather than replacing it.
2. **Curate.** Sort into sections, removing any that come out empty:
   - Core Concepts (prerequisites first)
   - Key Papers (by influence or date)
   - Guides & Patterns
   - Platform Integration (e.g. Databricks, if relevant)
   - Experiments
   - Open Questions (gaps you noticed)

   Each entry: `- [[note]] — what it contributes`. Curated lists are the value of a MOC, so write real one-liners.
3. **Live view.** Keep or add this Bases block, so new notes that link to the MOC appear automatically:
   ````markdown
   ```base
   filters:
     and:
       - file.hasLink(this.file)
   views:
     - type: table
       name: Notes linking here
       order:
         - file.name
         - note.type
         - note.last_verified
   ```
   ````
   Leave existing Dataview blocks alone unless the user asks to convert them.
4. **Write** `10-mocs/MOC-<Topic-Name>.md` with frontmatter `type: moc`, `domain`, `updated: <today>`. Show the outline first if the MOC is new or the restructure is large.
5. **Integrate.**
   - Add a link to the MOC from 3–5 central notes. Only where it reads naturally.
   - Add or refresh the MOC line in `index.md`.
   - Append `## [<today>] moc | MOC-<Topic>` to `log.md`.
