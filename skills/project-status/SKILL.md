---
name: project-status
description: Shows the status of active workspace projects from the vault's workspace index (recent commits, focus project, blockers), or with --reindex rescans the workspace folder and rebuilds 01-projects/workspace-index.md with activity status, categories and reusable assets. Use when the user asks what they are working on, wants a project overview, or wants to reindex their workspace.
argument-hint: "[--reindex]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash(uv run *), Bash(git -C *), Bash(date *)
---

# Project Status

Mode: `$ARGUMENTS` (empty = quick status, `--reindex` = rebuild the index)

## Setup

- **Vault root**: `${user_config.vault_path}`. If blank or a literal placeholder, use the current working directory.
- **Workspace root**: `${user_config.workspace_root}`. If blank or a literal placeholder, use `~/workspace`.
- Index file: `<vault>/01-projects/workspace-index.md`
- Today: !`date +%Y-%m-%d` · Year: !`date +%Y` · Quarter: Q!`echo $(( ($(date +%-m) - 1) / 3 + 1 ))`

## Quick mode (default)

1. Read the index. If it doesn't exist, offer `--reindex`.
2. For each `focus` or `active` entry:
   - run `git -C <workspace>/<dir> log --oneline --since='7 days ago'`;
   - read its `CLAUDE.md` for the current focus or blockers, if it has one.
3. Read `<vault>/50-logs/<year>/<year>-annual-plan.md` (if present) for this quarter's focus project.
4. Print:
   ```
   Workspace Status — <date>
   Q<n> focus: <project> — last commit <date> "<msg>" — active/stale
   Active: <dir> | last modified <date> | <n> commits this week
   Newly stale: <dir> | last touched <date>
   Index: <total> dirs | <active> active | <stale> stale | <archived> archived | last reindex <date>
   ```
5. Offer to append the summary to the current weekly log (`50-logs/<ISO year>/<ISO week>.md`).

## Reindex mode (`--reindex`)

1. **Category rules**: read the "Workspace Categories" section of the vault `CLAUDE.md`. It lists glob → category pairs, plus which container folders hold sub-projects. If there's no such section, use these defaults:
   - `*-examples`, `*_old`, `reference*` → `reference-repo`
   - `*course*`, `*learning*` → `learning`
   - `temp`, `test-*`, `*archive*` → `archived`
   - git repos changed in the last 90 days → `active-project`
   - everything else → `uncategorized`, flagged for the user to classify
2. **Scan** (portable; no GNU find needed). Pass `--expand <dir>` once for each container folder from the category rules:
   ```bash
   uv run --script ${CLAUDE_PLUGIN_ROOT}/scripts/workspace_scan.py --root <workspace> --expand <container>
   ```
   The JSON gives per directory: `last_modified`, `days_since_modified`, `is_git`, `last_commit`, `commits_7d`, `file_count`, `description`, `notebooks`, `candidate_assets`.
3. **Status**: `active` (≤30 days), `stale` (30–90 days), `obsolete` (>90 days). Keep `focus` and `archived` if the user set them in the previous index, along with user notes and manual category overrides.
4. **Diff** against the previous index: status changes, new directories, and directories that no longer exist on disk.
5. **Cleanup suggestions**:
   - `_old` duplicates of newer folders;
   - obsolete folders with fewer than 10 files (suggest archiving);
   - folders with very similar names;
   - uncategorized folders.

   These are suggestions only. Never move or delete anything.
6. **Write** the index: frontmatter `type: index`, `updated`, counts. Then sections Focus / Active / Stale / Obsolete / Archived & Tools, each a table with Dir | Category | Last Modified | Reusable Assets | Notes.
7. **Summary**: totals, new directories, status changes, number of suggestions, reusable assets found.
