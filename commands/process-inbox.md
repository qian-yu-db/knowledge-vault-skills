Deep-compile all notes in `00-inbox/` into the vault's knowledge graph. This is NOT simple categorization — you are an LLM compiler that synthesizes raw sources into comprehensive, deeply-linked vault notes.

---

## Phase 1: Analyze Each Inbox Note

1. List all files in `00-inbox/`
2. For each note, read the full content and extract:
   - **Core thesis**: What is this source fundamentally about? (1-2 sentences)
   - **Key concepts**: 3-5 distinct ideas or topics covered
   - **Novel claims**: What does this source say that is new or non-obvious?
   - **Practical implications**: How could this be applied — especially in Databricks/AI/ML customer work?
   - **Note type(s)**: Which template type fits? (paper, concept, code-pattern, guide, reading, databricks-feature, etc.)
   - **Multi-topic check**: Does this source cover 3+ distinct topics that belong in separate notes?

---

## Phase 2: Search the Vault for Context

For each key concept extracted in Phase 1:

1. Search `20-notes/` filenames for related notes (e.g., if concept is "retrieval augmented generation", look for `*rag*`, `*retrieval*`, `*vector-search*`)
2. Grep `20-notes/` content for the concept terms
3. Read the top 3-5 matching notes fully — understand what the vault already knows
4. Check `10-mocs/` for MOCs that cover this domain

Build a mental map: "The vault already has X on this topic, but is missing Y and Z."

---

## Phase 3: Triage — Present Plan to User

For each inbox note, recommend ONE of these outcomes:

### CREATE
When no existing note covers the core topic. Output:
> **CREATE** `type-descriptive-name.md` — [1-line description]. No significant overlap found in vault.

### MERGE
When an existing note covers 60%+ of the same concepts. Output:
> **MERGE** into `existing-note.md` — Existing note covers [X, Y] but is missing [Z]. Will weave in [specific new knowledge].

### SPLIT
When the source covers 3+ distinct topics. Output:
> **SPLIT** into N actions:
> 1. MERGE [topic A] into `existing-note-1.md`
> 2. CREATE `type-topic-B.md`
> 3. CREATE `type-topic-C.md`

**Present the full triage plan and WAIT for user confirmation before proceeding.**

---

## Phase 4: Compile

This is the heavy lifting. You are a compiler, not a copy-paste tool.

### For CREATE actions:

1. Load the matching template from `30-templates/`
2. Write **1500-3000 words** of deeply synthesized content following the template structure
3. Fill EVERY section of the template with substance — no empty sections or placeholders
4. Generate proper YAML frontmatter with all required fields per CLAUDE.md

**Compilation quality rules:**
- **Explain, don't summarize**: Write "X works by [mechanism] because [reason]. In Databricks customer work, this means [implication]" — NOT "The article discusses X"
- **Connect to Qian's context**: Include at least one connection to the user's role as Databricks AI Specialist SA, active customers, or learning goals (agentic design, fine-tuning, inference optimization)
- **Inline linking**: Weave `[[links]]` naturally into prose — "This approach is similar to [[concept-context-engineering|context engineering]] strategies" — not just a list at the bottom. Target: **5-10 inline links** per note
- **Worked examples**: Where the source describes a technique, include a concrete code example or scenario
- **Source attribution**: Add the source URL and date at the top of the note
- **Identify gaps**: If the source references a concept that should exist in the vault but doesn't, add it under a `## Suggested Future Notes` section at the bottom

5. Rename the file following naming conventions: `{type}-{descriptive-name}.md`
6. Move to `20-notes/` (or `02-customers/` for customer notes)

### For MERGE actions:

1. Read the existing target note fully
2. **Weave** new knowledge into the appropriate existing sections — do NOT just append at the bottom
3. Add new subsections if the source introduces topics not already in the note
4. Add new inline `[[links]]` where the merged content connects to other vault notes
5. Update `last_verified` date in frontmatter
6. Delete the inbox file after merge

---

## Phase 5: Cross-Link

For each note created or modified:

1. **Backlinks**: Identify 3-5 existing notes that should link TO this note. Open each and add a `[[link]]` in their Related/Connected Concepts section.
2. **MOC updates**: Check each MOC in `10-mocs/` — if this note belongs to a MOC's domain, add it with a brief description under the appropriate section.
3. **Forward links**: Verify all `[[links]]` in the new/modified note point to notes that actually exist.

---

## Phase 6: Report

After all notes are processed, output:

```
## Compilation Report

**Processed**: N inbox notes
**Created**: list of new notes with word counts
**Merged**: list of enhanced notes with what was added
**Cross-links added**: total count
**MOCs updated**: list
**Suggested follow-ups**:
- [topic] now has N notes — consider building a MOC
- [concept] referenced but missing from vault — consider creating
```

---

## Rules

- ALWAYS ask for confirmation after Phase 3 (triage) before writing anything
- Prefer MERGE over CREATE when there is significant overlap — avoid duplicate knowledge
- Every compiled note must have at least 5 outgoing `[[links]]`
- Never leave template sections empty — if a section isn't applicable, remove it rather than leaving a placeholder
- For multi-topic sources, it's OK to create a brief "reading" note linking to the deeper notes created from its topics
- If an inbox note is just a quick personal capture (not a web clipping), compile it at a lighter depth (500-1000 words) — not everything needs 3000 words
