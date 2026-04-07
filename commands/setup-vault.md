---
description: Bootstrap a new LLM knowledge vault from scratch — creates folder structure, templates, and CLAUDE.md
arguments:
  - name: path
    description: "Path where the vault should be created (e.g., ~/my-knowledge-vault)"
    required: true
---

Set up a complete LLM-powered knowledge base from scratch at the specified path.

This creates everything needed to start using the Karpathy-style compilation pipeline with Obsidian + Claude Code.

---

## Step 1: Create Vault Directory Structure

Create the following folder structure at `$ARGUMENTS`:

```
{vault_root}/
├── 00-inbox/          # Quick capture, unsorted — raw sources land here
├── 01-projects/       # Active work with deadlines
├── 02-customers/      # Customer engagement notes (optional)
├── 10-mocs/           # Maps of Content (entry points to topic clusters)
├── 20-notes/          # All atomic notes (flat directory)
├── 30-templates/      # Note templates
├── 40-archive/        # Completed/deprecated content
├── 50-logs/           # Weekly logs and reflections
│   └── {current_year}/
├── assets/            # Images, PDFs, attachments
│   └── papers/        # PDF papers for summarization
└── .claude/
    └── commands/      # Project-specific command overrides (optional)
```

Run `mkdir -p` for all directories.

## Step 2: Write Templates

Read ALL template files from `${CLAUDE_PLUGIN_ROOT}/resources/templates/` and write each one to `{vault_root}/30-templates/`.

The templates include: annual-plan, code-pattern, concept, customer-note, databricks-feature, experiment, moc, model-card, monthly-reflection, paper, project, quarterly-review, reading, skill-assessment, weekly-log.

## Step 3: Generate CLAUDE.md

Read the CLAUDE.md template from `${CLAUDE_PLUGIN_ROOT}/resources/claude-md-template.md` and write it to `{vault_root}/CLAUDE.md`.

## Step 4: Create Initial Weekly Log

1. Get the current ISO week: `date +%Y-W%W`
2. Read the weekly-log template from `{vault_root}/30-templates/weekly-log.md`
3. Create the first log file at `{vault_root}/50-logs/{year}/{year}-W{week}.md`
4. Replace template variables with actual values

## Step 5: Initialize Git

```bash
cd {vault_root}
git init
echo ".DS_Store" > .gitignore
echo ".obsidian/workspace.json" >> .gitignore
echo ".trash/" >> .gitignore
git add -A
git commit -m "Initialize knowledge vault"
```

## Step 6: Print Setup Summary

```
═══════════════════════════════════════════════
  Knowledge Vault Created
═══════════════════════════════════════════════
  Location: {vault_root}
  Templates: 15 note templates in 30-templates/
  First log: 50-logs/{year}/{year}-W{week}.md
  
  Next steps:
  1. Open {vault_root} in Obsidian
  2. Install Obsidian Web Clipper for article ingestion
  3. Clip articles → they land in 00-inbox/
  4. Run /process-inbox to compile them into knowledge
  
  Key commands:
  /process-inbox     — Compile inbox → deep notes
  /vault-enhance     — Enrich weak notes, fix links
  /session-wrap      — Capture session knowledge
  /vault-audit       — Full health check
  /build-moc <topic> — Create topic index
  /new-paper <url>   — Add a paper note
  
  Recommended rhythm:
  Weekly (Sunday):  /process-inbox + /vault-enhance
  End of session:   /session-wrap (auto-prompted)
  Monthly:          /vault-audit + /review-outdated
═══════════════════════════════════════════════
```
