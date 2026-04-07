# Obsidian Knowledge Base - Claude Code Context

This is an LLM-powered personal knowledge base using the Karpathy-style compilation pipeline.

---

## About Me

<!-- Personalize this section — it helps Claude tailor notes to your context -->

### Role & Context
- **Position**: [Your role]
- **Focus**: [Your focus areas]
- **Goal**: [Your current professional goal]

### My Expertise

| Domain | Level | Notes |
|--------|-------|-------|
| [Domain 1] | [Learning/Solid/Expert] | |
| [Domain 2] | [Learning/Solid/Expert] | |
| [Domain 3] | [Learning/Solid/Expert] | |

### How I Work
- **Decision style**: [e.g., data-driven, intuition-first, collaborative]
- **Communication**: [e.g., concise, detailed, visual]
- **When stuck**: [e.g., research first, ask for help, prototype]

### My Principles
- [Principle 1]
- [Principle 2]
- [Principle 3]

---

## Vault Structure

```
00-inbox/        # Quick capture, unsorted — raw sources land here
01-projects/     # Active work with deadlines
02-customers/    # Customer/client engagement notes
10-mocs/         # Maps of Content (entry points to topic clusters)
20-notes/        # All atomic notes (flat directory)
30-templates/    # Note templates
40-archive/      # Completed/deprecated content
50-logs/         # Weekly logs and reflections
assets/          # Images, PDFs, attachments
  └── papers/    # PDF papers for summarization
```

## Note Types & Required Frontmatter

| Type | Required Fields | Location |
|------|-----------------|----------|
| paper | type, status, arxiv, year, authors, tags | 20-notes/ |
| model-card | type, model_name, task, framework, status | 20-notes/ |
| experiment | type, project, status, date | 20-notes/ |
| code-pattern | type, language, domain | 20-notes/ |
| concept | type, domain, confidence | 20-notes/ |
| reading | type, domain, source, author | 20-notes/ |
| guide | type, domain | 20-notes/ |
| customer | type, customer_name, industry, status | 02-customers/ |
| log | type, week | 50-logs/ |
| reflection | type, period | 50-logs/reflections/ |
| quarterly-review | type, year, quarter | 50-logs/YYYY/ |
| annual-plan | type, year, status | 50-logs/YYYY/ |
| assessment | type, skill, date, score | 50-logs/YYYY/assessments/ |
| moc | type, domain, updated | 10-mocs/ |

## Tag Taxonomy

```
# Content Type
type/paper, type/model, type/code, type/concept, type/experiment, type/decision

# Domain (2 levels max — customize to your fields)
domain/ml, domain/ml/nlp, domain/ml/cv, domain/ml/rl
domain/data-eng, domain/data-eng/spark, domain/data-eng/streaming
domain/devops, domain/devops/ci-cd, domain/devops/infra

# Status
status/inbox, status/active, status/review-needed, status/outdated, status/archived

# Confidence
confidence/verified, confidence/needs-review, confidence/outdated
```

## Naming Conventions

- Use lowercase with hyphens: `concept-attention-mechanism.md`
- Prefix with type: `paper-qlora-2023.md`, `model-card-llama3.md`, `pattern-spark-udf.md`
- MOCs: `MOC-Topic-Name.md`

## Key Workflows

### Processing Inbox Notes (LLM Compilation)
The `/process-inbox` command deep-compiles raw inbox notes into the vault's knowledge graph using a 5-phase approach:

1. **Analyze**: Extract core thesis, key concepts, novel claims, and practical implications from each inbox note
2. **Search**: Scan `20-notes/` and `10-mocs/` for related existing content to understand what the vault already knows
3. **Triage**: For each note, decide CREATE (new note), MERGE (enhance existing), or SPLIT (multi-topic source) — present plan and wait for confirmation
4. **Compile**: Synthesize 1500-3000 words per note following the matching template, with 5-10 inline `[[links]]`, source attribution, and "Relevance to My Work" connections
5. **Cross-link**: Add backlinks in 3-5 existing notes that should reference the new content; update relevant MOCs

Quality targets: explain don't summarize, connect to your professional context, inline linking in prose, identify vault gaps.

### Session Knowledge Write-Back
The `/session-wrap` skill (in addition to writing the weekly log) extracts vault-worthy knowledge from the session:

1. **Extract**: Identify technical insights using 3-part filter (Technical Insight + Reusability + Novelty tests)
2. **Search**: Find related existing notes in the vault
3. **Propose**: Present write-back proposals (enhance existing note or create new note) — wait for confirmation
4. **Execute**: Write 500-1500 words per insight, with cross-links. Update the log entry with references to captured knowledge.

Vault-worthy: root cause analyses, solution patterns, undocumented behaviors, approach comparisons, customer insights.
NOT vault-worthy: routine edits, scheduling, simple lookups.

### Vault Enhancement (Lint & Maintain Cycle)
The `/vault-enhance` command actively improves the knowledge graph — Karpathy's Phase 4:

1. **Scan**: Find weak notes (thin content, few links, orphans, stale dates)
2. **Auto-link**: Discover notes that mention each other's topics but don't link — add the links
3. **Enrich**: Expand the top 5 weakest notes with deeper content, examples, and cross-links
4. **Suggest**: Identify new note candidates, MOC candidates, and merge candidates

Baked into rhythms: weekly log has a "Vault Health" checklist, monthly reflection has a "Deep Clean" section.

### Marking Notes as Outdated
1. Add `status/outdated` tag
2. Add warning callout at top: `> [!warning] Outdated: See [[newer-note]]`
3. Keep the note - don't delete
4. Add link to superseding content

### Creating MOCs
Trigger: when a topic has 5+ related notes
Structure: concepts → papers → implementations → experiments → open questions

## Version-Sensitive Content

For library-dependent code or API documentation:
- Always include `last_verified: YYYY-MM-DD` in frontmatter
- Flag with `confidence/needs-review` if older than 90 days
- Check official docs before major updates

## Templates Location

Templates are in `30-templates/` - use these when creating new notes.

## Slash Commands

Commands provided by the knowledge-vault plugin:

| Command | Description |
|---------|-------------|
| `/setup-vault <path>` | Bootstrap a new vault from scratch |
| `/process-inbox` | Deep-compile inbox notes into vault knowledge graph |
| `/build-moc <topic>` | Create or update a MOC for a topic |
| `/new-paper <url-or-title>` | Create a paper note from URL or title |
| `/new-customer <name>` | Create a new customer note in 02-customers/ |
| `/review-outdated` | Find notes needing review (>90 days old) |
| `/vault-audit` | Full health check: broken links, orphans, metadata |
| `/vault-enhance` | Actively enrich weak notes, auto-link, discover gaps |
| `/weekly-quiz [skill]` | Generate 5-question quiz for skill reinforcement |
| `/project-status` | Aggregate status from active projects |

### Recommended Schedule

- **Weekly** (planning session): `/process-inbox` + `/vault-enhance` + `/weekly-quiz`
- **Monthly** (reflection): `/vault-audit` + `/vault-enhance` + `/review-outdated`
- **End of session** (auto-prompted): `/session-wrap` — Stop hook reminds you when the session was substantive
- **As needed**: `/new-paper`, `/build-moc`
