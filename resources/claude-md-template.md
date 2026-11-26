# Obsidian Knowledge Base - Claude Code Context

This is an LLM-maintained personal knowledge base (Karpathy-style "LLM wiki"). Three layers:
**raw/** holds immutable sources, **20-notes/** holds the compiled, interlinked notes (Claude maintains them), and **this file** is the schema that you and Claude evolve together.

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

### Learning Goals
<!-- /weekly-quiz rotates through this list; notes link "Relevance to My Work" to it -->
- [Goal 1]
- [Goal 2]
- [Goal 3]

### Workspace Categories (optional, used by /project-status --reindex)
<!-- glob → category; list container folders whose subfolders are separate projects -->
- Containers: `developments`
- `customer_*` → customer-poc
- `*-examples`, `*_old` → reference-repo

---

## Vault Structure

```
00-inbox/        # Queue of unprocessed captures (web clips, quick notes)
01-projects/     # Active work with deadlines
02-customers/    # Customer/client engagement notes
10-mocs/         # Maps of Content (entry points to topic clusters)
20-notes/        # All atomic notes (flat directory)
30-templates/    # Note templates
40-archive/      # Completed/deprecated content
50-logs/         # Weekly logs and reflections
raw/             # IMMUTABLE processed sources: raw/YYYY-MM/<slug>.md (never edited)
assets/          # Images, PDFs, attachments
  └── papers/    # PDF papers for summarization
index.md         # Catalog of every compiled note (read first when answering)
log.md           # Append-only operations log: ## [YYYY-MM-DD] <op> | <title>
```

## Provenance Rules

- Processed inbox items move to `raw/YYYY-MM/`. They are never deleted or edited.
- Every compiled note has a `sources:` frontmatter list (raw paths and/or URLs). Cite sources, not other compiled notes.
- Keep source claims apart from interpretation (`## My Take`, `## Relevance to My Work`).
- Size notes to their content (most are 300–1200 words). Split multi-topic sources instead of writing long notes.
- Link only to notes that exist, and only where the relationship is stated in the text.

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
| synthesis | type, question, sources | 20-notes/ |
| databricks-feature | type, product_area, last_verified | 20-notes/ |
| customer | type, customer_name, industry, status | 02-customers/ |
| log | type, week | 50-logs/ |
| reflection | type, period | 50-logs/reflections/ |
| quarterly-review | type, year, quarter | 50-logs/YYYY/ |
| annual-plan | type, year, status | 50-logs/YYYY/ |
| assessment | type, skill, date, score | 50-logs/YYYY/assessments/ |
| moc | type, domain, updated | 10-mocs/ |

Compiled types (paper, concept, reading, guide, code-pattern, databricks-feature, synthesis) should also have `sources:` and `last_verified:`.

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

The plugin's skills handle the workflows (`/knowledge-vault:<skill>`). Their shared rules are in the plugin's `resources/vault-conventions.md`.

- **Ingest** (`process-inbox`): analyze → search the vault → triage plan (CREATE / MERGE / SPLIT / SKIP, needs approval) → compile (one subagent per source) → archive the source to `raw/` → backlinks, MOCs, `index.md`, `log.md` → lint.
- **Query** (`vault-query`): `index.md` → search → answer with `[[citations]]` and gaps → optionally file the answer as a `synthesis` note.
- **Lint** (`vault-audit`, `vault-enhance`, `review-outdated`): the deterministic lint script, plus optional semantic checks (contradictions, unsupported or stale claims), then confirmed fixes.
- **Write-back** (`session-wrap`): weekly log entry and `log.md`, then proposed insights for permanent notes (needs approval).

### Marking Notes as Outdated
1. Add `status/outdated` tag
2. Add warning callout at top: `> [!warning] Outdated: See [[newer-note]]`
3. Keep the note - don't delete
4. Add link to superseding content

### Creating MOCs
Trigger: when a topic has 5+ related notes
Structure: concepts → papers → guides/patterns → experiments → open questions, plus an embedded ```base``` view of notes linking to the MOC (Obsidian Bases, a core plugin)

## Version-Sensitive Content

For library-dependent code or API documentation:
- Always include `last_verified: YYYY-MM-DD` in frontmatter
- Flag with `confidence/needs-review` if older than 90 days
- Check official docs before major updates

## Templates Location

Templates are in `30-templates/` - use these when creating new notes.

## Skills (knowledge-vault plugin)

| Skill | Description |
|-------|-------------|
| `/knowledge-vault:setup-vault <path>` | Create a vault, or upgrade an existing one in place |
| `/knowledge-vault:process-inbox` | Ingest and compile inbox sources (provenance, index, log) |
| `/knowledge-vault:vault-query <question>` | Answer from the vault with citations; file the answer back |
| `/knowledge-vault:vault-audit [--deep]` | Health report; `--deep` adds contradiction and claim checks |
| `/knowledge-vault:vault-enhance` | Add missing links, enrich weak notes, fix index drift |
| `/knowledge-vault:review-outdated` | Re-verify stale notes against current sources |
| `/knowledge-vault:build-moc <topic>` | Create or update a MOC with a live Bases view |
| `/knowledge-vault:new-paper <url>` | Paper note with raw abstract and context |
| `/knowledge-vault:new-customer <name> [id]` | Customer or engagement note |
| `/knowledge-vault:weekly-quiz [area]` | Interactive quiz over Learning Goals |
| `/knowledge-vault:project-status [--reindex]` | Workspace project overview |
| `/knowledge-vault:session-wrap` | Session handoff log plus knowledge write-back |

Hooks: when a session starts inside the vault, Claude gets an inbox and lint summary plus the last "Next:" step. Every note Claude writes is linted, and errors go back to Claude. A substantive session triggers a one-time reminder to wrap it up.

### Recommended Schedule

- **Weekly**: `process-inbox` + `vault-enhance` + `weekly-quiz`
- **Monthly**: `vault-audit --deep` + `review-outdated`
- **End of a substantive session**: `session-wrap`
- **Any time**: `vault-query`, `new-paper`, `build-moc`
