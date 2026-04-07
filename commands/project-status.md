---
description: Show active project status or rebuild the full workspace index
arguments:
  - name: mode
    description: "--reindex to rebuild full workspace index, or blank for quick status"
    default: ""
---

Show active project status from the workspace index, or rebuild the full index with `--reindex`.

**Index file**: `01-projects/workspace-index.md`

---

## Quick Mode (default: no arguments)

Read the workspace index at `01-projects/workspace-index.md` and show a focused status report.

### Steps

1. Read `01-projects/workspace-index.md`
2. Filter to items with status `active` or `focus`
3. For each active item:
   - Check `~/workspace/{dir}` for git commits in the last 7 days (`git -C {path} log --oneline --since='7 days ago'`)
   - Read CLAUDE.md if it exists for current focus/blockers
4. Also read `50-logs/2026/2026-annual-plan.md` for the Q2 focus project
5. Print a concise status report

### Output Format

```
═══════════════════════════════════════════════
  Workspace Status — {date}
═══════════════════════════════════════════════
  Q2 Focus: {project_name} ({path})
    Last commit: {date} — {message}
    Status: {active/stale}
  ─────────────────────────────────────────────
  Active Projects:
    {name} | {path} | last modified {date} | {commits} commits this week
    ...
  ─────────────────────────────────────────────
  Recently Stale (active → stale since last check):
    {name} | {path} | last touched {date}
  ─────────────────────────────────────────────
  Index: {total} dirs | {active} active | {stale} stale | {archived} archived
  Last reindex: {date}
═══════════════════════════════════════════════
```

Then ask if the user wants to append this to the current weekly log.

---

## Reindex Mode (`--reindex`)

Full scan of `~/workspace/` to rebuild the workspace index.

### Step 1: Scan Workspace

For each directory in `~/workspace/*/`:

```bash
# Get last modified date (most recent file, excluding .git/node_modules/__pycache__)
find "$dir" -maxdepth 3 -type f -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/__pycache__/*' -not -path '*/.venv/*' -printf '%T@\n' 2>/dev/null | sort -rn | head -1

# Check if git repo
[ -d "$dir/.git" ]

# Count files
find "$dir" -maxdepth 3 -type f -not -path '*/.git/*' -not -path '*/node_modules/*' 2>/dev/null | wc -l

# Read README.md or CLAUDE.md for description (first 5 lines)
head -5 "$dir/README.md" 2>/dev/null || head -5 "$dir/CLAUDE.md" 2>/dev/null
```

### Step 2: Auto-Classify

Assign a category based on path patterns and content:

| Pattern | Category |
|---|---|
| `customer_*`, `Fins-*`, `fins-*` | `customer-poc` |
| `reference_repos/*`, `*-examples`, `dbdemos-*`, `*_old` | `reference-repo` |
| `courses_*`, `*_learning` | `learning` |
| `developments/*` (subfolders) | `active-project` |
| `apps_space/*` | `app` |
| `blog_*` | `content` |
| `dotfiles`, `cursor_rules`, `databricks_knowledge_vault` | `tool` |
| `Archieves`, `temp`, `test-*` | `archived` |
| Everything else | `uncategorized` — flag for user review |

### Step 3: Detect Status

| Condition | Status |
|---|---|
| Modified in last 30 days | `active` |
| Modified 30-90 days ago | `stale` |
| Modified 90+ days ago | `obsolete` |
| User manually set to `focus` | `focus` (preserved from previous index) |
| User manually set to `archived` | `archived` (preserved) |

### Step 4: Identify Reusable Assets

For directories classified as `customer-poc` or `active-project`, look for:
- Notebooks (`*.py` with Databricks header or `*.ipynb`)
- Pattern files (names containing `pattern-`, `template-`, `example-`)
- Well-documented code (files with docstrings or README)
- Architecture diagrams (`.mermaid`, `.md` with mermaid blocks)

Note these as `reusable_assets` in the index entry.

### Step 5: Compare with Previous Index

If `01-projects/workspace-index.md` already exists:
- Flag items that changed status (e.g., `active` → `stale`)
- Flag new directories not in the previous index
- Flag directories in index but no longer on disk (deleted)
- Preserve user-set fields (`notes`, `focus` status, manual category overrides)

### Step 6: Suggest Cleanup Actions

Print suggestions:
- Directories with `_old` suffix → "Consider removing or merging with newer version"
- `obsolete` items with <10 files → "Consider archiving to ~/workspace/Archieves/"
- Duplicate-looking dirs (similar names) → "Possible duplicates: X and Y"
- `uncategorized` items → "Please classify: {name}"

### Step 7: Write Index

Write `01-projects/workspace-index.md` with this structure:

```markdown
---
type: index
updated: YYYY-MM-DD
total_dirs: N
active: N
stale: N
obsolete: N
archived: N
---

# Workspace Index

Last reindex: YYYY-MM-DD | Total: N directories

## Focus

| Dir | Category | Last Modified | Reusable Assets | Notes |
|-----|----------|---------------|-----------------|-------|
| ... | ... | ... | ... | Q2 focus project |

## Active

| Dir | Category | Last Modified | Reusable Assets | Notes |
|-----|----------|---------------|-----------------|-------|
| ... | ... | ... | ... | ... |

## Stale (30-90 days)

| Dir | Category | Last Modified | Notes |
|-----|----------|---------------|-------|
| ... | ... | ... | ... |

## Obsolete (90+ days)

| Dir | Category | Last Modified | Notes |
|-----|----------|---------------|-------|
| ... | ... | ... | Consider archiving |

## Archived / Tools

| Dir | Category | Last Modified | Notes |
|-----|----------|---------------|-------|
| ... | ... | ... | ... |
```

### Step 8: Print Summary

```
Workspace reindex complete:
  Total: N directories
  Active: N | Stale: N | Obsolete: N | Archived: N
  New since last index: N
  Status changes: N
  Cleanup suggestions: N

Reusable assets found: N items across M projects
Index written to: 01-projects/workspace-index.md
```
