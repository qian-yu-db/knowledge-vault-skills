Actively enhance the vault's knowledge graph — this is the "Lint & Maintain" cycle (Karpathy Phase 4). Unlike `/vault-audit` which only reports problems, this command **fixes them**.

Run this during weekly planning or monthly reflection. It scans for weak spots and enriches them.

---

## Step 1: Scan for Weak Notes

Search `20-notes/` and identify notes that need enrichment. Categorize into:

### Thin Notes (< 500 words, excluding frontmatter)
- Count words in each note (excluding YAML frontmatter)
- Flag notes under 500 words — these are stubs that should be deeper
- Exclude templates, logs, and customer notes from this check

### Poorly Linked Notes (< 3 outgoing `[[links]]`)
- Count `[[` occurrences in each note
- Flag notes with fewer than 3 outgoing links — these are disconnected from the knowledge graph

### Orphan Notes (no incoming links from other notes)
- For each note in `20-notes/`, check if ANY other note links to it
- Flag notes that nothing else references — they're invisible in the graph

### Stale Notes (not verified in 90+ days)
- Check `last_verified` in frontmatter
- Flag Databricks feature notes and code patterns older than 90 days
- Flag all other notes older than 180 days

Combine these into a single list, sorted by severity (thin + orphan + stale = highest priority).

---

## Step 2: Auto-Link Discovery

This is the highest-value, lowest-effort enhancement.

1. For each note in `20-notes/`, extract the main topic from the filename and first heading
2. Search ALL other notes for mentions of that topic (by keyword, not just `[[link]]`)
3. If a note mentions another note's topic but doesn't link to it, flag it as a **missing link**
4. Focus on the top 20 missing links by relevance

Present the link discoveries:
```
## Missing Links Found

1. `guide-model-serving-patterns.md` mentions "feature store" 3 times but doesn't link to [[guide-feature-engineering-and-feature-store]]
2. `concept-rag-architecture.md` discusses "vector search" but doesn't link to [[databricks-feature-vector-search]]
...
```

**After confirmation**, add the `[[links]]` inline where the mentions occur — not just dumped in a Related section.

---

## Step 3: Enrich Weak Notes (pick top 5)

From the weak notes identified in Step 1, select the **top 5 by priority** (prefer notes that are thin AND poorly linked AND in an active domain).

For each:

1. Read the full note
2. Search the web or vault for additional context on the topic
3. **Expand the note** to at least 800 words:
   - Add missing template sections
   - Add explanations, examples, or code snippets
   - Add a "Relevance to My Work" connection if missing
   - Add 3-5 inline `[[links]]` to related vault notes
4. Update `last_verified` date

**Present each enhancement for confirmation before writing.** Show a diff-style preview: "Will expand from 230 words to ~900 words. Adding: [list of new sections/content]."

---

## Step 4: Suggest New Notes & MOCs

Based on the vault scan:

### New Note Candidates
- Concepts mentioned in 3+ notes via `[[broken-link]]` that don't exist yet
- Topics that appear frequently in notes but have no dedicated note

### New MOC Candidates
- Topics with 5+ notes that aren't covered by any MOC in `10-mocs/`
- Check: is there a cluster of notes sharing a domain tag that has no MOC?

### Merge Candidates
- Notes with very similar titles or overlapping content that could be consolidated

Present these as suggestions — don't create automatically:
```
## Suggested New Notes
- [[concept-prompt-caching]] — referenced in 4 notes but doesn't exist
- [[guide-gpu-cluster-sizing]] — frequent topic in customer notes

## Suggested New MOCs
- MOC-Model-Serving — 8 notes about serving patterns, no MOC yet

## Merge Candidates
- `reading-rag-overview.md` and `concept-rag-architecture.md` overlap significantly
```

---

## Step 5: Report

```
## Vault Enhancement Report

**Scanned**: N notes in 20-notes/
**Weak notes found**: X thin, Y poorly linked, Z orphans, W stale

**Links added**: N new cross-links across M notes
**Notes enriched**: list with before/after word counts
**Suggestions**:
- N new note candidates
- N new MOC candidates
- N merge candidates

**Vault health**: overall score or trend (e.g., "Orphan rate dropped from 21% to 15%")
```

---

## Rules

- Always confirm before modifying any note
- Focus on the top 5 weak notes per run — don't try to fix everything at once
- Prefer adding links over rewriting content — linking is highest leverage
- When enriching, weave new content into existing structure — don't just append
- Skip customer notes (02-customers/) — those have their own lifecycle
- Track progress: if the vault has improved since last run, say so
