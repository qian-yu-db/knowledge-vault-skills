# Vault Conventions (shared by all knowledge-vault skills)

The vault's own `CLAUDE.md` is the schema and wins on any conflict: note types, tags,
"About Me", learning goals, workspace categories. This file holds the plugin-level
rules that keep an LLM-maintained vault trustworthy.

## Contents
1. Layout
2. Provenance: raw sources are immutable
3. Notes: size, atomicity, voice
4. Linking rules
5. index.md and log.md
6. Search ladder
7. Lint script
8. Dates, git, approvals

---

## 1. Layout

```
00-inbox/      queue of unprocessed captures (web clips, quick notes)
01-projects/   active work
02-customers/  engagement notes (own lifecycle; skip in enrichment)
10-mocs/       Maps of Content (MOC-Topic-Name.md) and .base dashboards
20-notes/      compiled knowledge notes, flat, `{type}-{kebab-name}.md`
30-templates/  note templates
40-archive/    retired notes (soft delete, never hard delete)
50-logs/       weekly logs `50-logs/YYYY/YYYY-WNN.md`, reflections
raw/           IMMUTABLE source material `raw/YYYY-MM/{slug}.md` (+ raw/assets/)
assets/        images and PDFs referenced by notes
index.md       catalog of every compiled note (read first when answering)
log.md         append-only operations log
CLAUDE.md      the vault schema (user-editable)
```

## 2. Provenance: raw sources are immutable

- Processing an inbox item **moves** it to `raw/YYYY-MM/{slug}.md`. Do not delete it. Never edit files under `raw/` after that.
- Every compiled note records where its claims came from in frontmatter:
  ```yaml
  sources:
    - raw/2026-11/karpathy-llm-wiki.md
    - https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
  ```
- A compiled note is a regenerable cache over `raw/`. It is never the origin of a fact. Do not cite another compiled note as evidence for a claim; cite the raw source or URL.
- Keep source claims separate from your own synthesis. Put interpretation, opinions, and "how this applies to my work" under clearly named headings (e.g. `## Relevance to My Work`, `## My Take`), or in a `> [!note] Interpretation` callout.

## 3. Notes: size, atomicity, voice

- Size each note to its content. There is no word target. Most atomic notes are 300–1200 words. If a source covers 3+ distinct ideas, split it into several notes rather than writing one long one.
- Explain mechanisms ("X works by … because …"). Don't narrate the source ("the article discusses …").
- Remove template sections that don't apply. Never leave placeholders.
- Personalization comes from the vault `CLAUDE.md` "About Me" and "Learning Goals" sections. Never invent the user's projects, customers, or goals.

## 4. Linking rules

- Link only to notes that exist, or that you are creating in this same run. Check before linking. The PostToolUse lint hook reports broken links.
- Add a link only when there is a real relationship you could state in one sentence (prerequisite, example of, contrasts with, implements, contradicts). Don't add links just to raise link counts. Speculative links make the graph look more coherent than the evidence is.
- Put links inline in prose where the relationship is explained: `this mirrors [[concept-context-engineering|context engineering]]`. A `## Related` list is fine as a supplement.
- Use the existing filename exactly; aliases go after `|`.

## 5. index.md and log.md

**index.md**: a catalog grouped by category. One line per compiled note:
```markdown
## Agents
- [[concept-agent-memory]] — how agents persist state across turns; episodic vs semantic stores
```
Update it whenever a note is created, renamed, merged, or archived.

**log.md**: append-only, newest at the bottom, with prefixes that are easy to parse:
```markdown
## [2026-11-26] ingest | Karpathy LLM Wiki gist
- raw: raw/2026-11/karpathy-llm-wiki.md
- created: [[concept-llm-wiki]]; merged: [[guide-obsidian-workflow]]
```
Operations: `ingest`, `query`, `enhance`, `audit`, `review`, `moc`, `wrap`, `setup`.

## 6. Search ladder

Use the cheapest method that works:
1. Read `index.md`. It's often enough to pick candidate notes.
2. `qmd query --json -n 10 "<question>"` if `qmd` is on PATH (hybrid BM25 + vector + rerank). Worth adopting past a few hundred notes.
3. `obsidian search query="<text>"` and `obsidian backlinks file=<name>` if the Obsidian CLI is on PATH. It needs the Obsidian app running.
4. Grep/Glob over `20-notes/` and `10-mocs/` (filename patterns plus content terms, including synonyms).

## 7. Lint script

`scripts/vault_lint.py` in the plugin (each skill gives its full path). It computes the deterministic checks: broken links, orphans, thin or poorly linked notes, stale `last_verified` dates, missing frontmatter or required fields, missing `sources`, naming problems, and notes missing from `index.md`. Use its JSON output instead of counting words or links by hand.

## 8. Dates, git, approvals

- ISO week: `date +%G-W%V` (never `%Y-W%W`). Year of the week: `date +%G`.
- Set `last_verified: YYYY-MM-DD` whenever you check a note's content against a current source.
- Every skill that changes permanent notes presents a plan first and waits for approval. Logs and index updates that are part of an approved plan don't need separate approval.
- If the vault is a git repo, the approved plan may include one local commit per completed operation (`vault: ingest <title>`), so a bad compile can be reverted. Never push.
