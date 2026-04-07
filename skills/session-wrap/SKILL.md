---
name: session-wrap
description: Capture the current Claude Code session state — what was done, what's broken, and what to do next — as a log entry in the Obsidian vault, then extract vault-worthy knowledge and write it back into permanent notes. Prevents broken state and lost insights from carrying across sessions. Use at the end of any non-trivial session.
---

# Session Wrap

Capture session state and compound knowledge before ending. This prevents context loss between sessions AND ensures research explorations enrich the permanent vault.

---

## Part A: Session Log

1. **Review the conversation** — summarize what was accomplished, what failed, and what's unfinished

2. **Determine the current weekly log file**:
   - Calculate the current ISO week: run `date +%Y-W%W`
   - The log lives at `50-logs/YYYY/YYYY-WXX.md`
   - Read the weekly log to find the right day section

3. **Append to today's section** under the matching day (Monday-Sunday) in the weekly log:

   ```markdown
   - **Claude Session: [brief topic]** (YYYY-MM-DD HH:MM)
     - Done: [1-3 bullet points of what was completed]
     - Issues: [anything broken or partially done, if any]
     - Next: [what to do in the next session, if any]
     - Key files: [list of main files created/modified]
     - Knowledge captured: [will be filled in Part B]
   ```

4. **If there are open issues or blockers**, add them under `## Project Blockers / Questions / Status`

5. **If the weekly log file doesn't exist yet**, create it using the template structure from `30-templates/weekly-log.md`

---

## Part B: Knowledge Write-Back

After the log entry is written, extract vault-worthy knowledge from this session.

### Step 6 — Knowledge Extraction

Scan the full conversation and apply a 3-part filter:

**1. Technical Insight Test**: Does this explain HOW something works, WHY it behaves a certain way, or WHEN to use one approach over another?

**2. Reusability Test**: Would this knowledge help in a different session, for a different customer, or on a different project?

**3. Novelty Test**: Does the vault already have this knowledge? (Search `20-notes/`)

**Vault-worthy**: root cause analyses, solution patterns, undocumented behaviors, approach comparisons, customer-derived insights, architecture decisions, performance observations with data.

**NOT vault-worthy**: routine edits, formatting, scheduling, simple lookups, code-only artifacts without transferable knowledge.

If there are NO vault-worthy insights, say "No vault-worthy insights from this session" and stop here.

### Step 7 — Vault Search

For each extracted insight:
1. Search `20-notes/` filenames and content for related notes
2. Read the most relevant 2-3 matching notes
3. Decide: **enhance existing note** vs. **create new note** — prefer enhancing

### Step 8 — Proposal

Present write-back proposals. Do NOT execute without confirmation.

```markdown
## Vault Write-Back Proposals

1. **[Insight title]** → Enhance `existing-note.md`
   - Section: [which section to add to]
   - Preview: [2-3 sentence summary]

2. **[Insight title]** → Create new `type-name.md`
   - Type: [concept/guide/code-pattern/databricks-feature]
   - Preview: [2-3 sentence summary]

Approve all? Select specific items (e.g., "1,3")? Or skip?
```

### Step 9 — Execute (only after user confirms)

**For enhancements**: weave into appropriate section, add 3+ cross-links, update `last_verified`.
**For new notes**: load template from `30-templates/`, write 500-1500 words, add frontmatter and 3+ cross-links, check MOCs.

### Step 10 — Update Log Entry

Append to the session entry: `- Knowledge captured: [[note-1]] (enhanced), [[note-2]] (new)`

---

## Rules

- Keep log entries concise — 3-5 lines max per session
- Always include the "Next" line so future sessions have a starting point
- Reference specific file paths so the next session can pick up immediately
- Do NOT overwrite existing content in the weekly log — only append
- Never auto-execute write-backs without user confirmation
- Prefer enhancing existing notes over creating new ones
- If the session was purely operational, skip Part B entirely
