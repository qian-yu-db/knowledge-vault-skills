---
name: setup-vault
description: Creates a new LLM-maintained Obsidian knowledge vault (folders, templates, CLAUDE.md schema, index.md, log.md, Bases dashboard, git), or upgrades an existing vault to the current layout without overwriting anything. Use when the user wants to start a knowledge vault or bring an older vault up to date.
argument-hint: "<vault-path>"
arguments: [path]
disable-model-invocation: true
allowed-tools: Read, Glob, Bash(mkdir *), Bash(cp -n *), Bash(ls *), Bash(date *), Bash(git init*), Bash(git status*), Bash(uv run *)
---

# Set Up or Upgrade a Knowledge Vault

Target path: `$path`. If empty, use `${user_config.vault_path}`. If that is also blank or a literal placeholder, ask for a path.

Plugin resources live in `${CLAUDE_PLUGIN_ROOT}/resources/`. Read `${CLAUDE_PLUGIN_ROOT}/resources/vault-conventions.md` first. It defines the layout created here.

Today: !`date +%Y-%m-%d` · ISO week: !`date +%G-W%V`

## Step 1: Detect mode

- **New**: the path doesn't exist or is empty.
- **Upgrade**: the path already contains `20-notes/`. Never overwrite or move existing user content in this mode.
- Anything else (a non-empty folder that isn't a vault): ask before continuing.

Tell the user which mode applies and what will be created, then wait for confirmation.

## Step 2: Folders

`mkdir -p` the layout from the conventions file. Only missing folders are created:
`00-inbox 01-projects 02-customers 10-mocs 20-notes 30-templates 40-archive 50-logs/<ISO year> raw/assets assets/papers`

## Step 3: Templates and dashboard

- Copy each template without clobbering: `cp -n ${CLAUDE_PLUGIN_ROOT}/resources/templates/*.md <vault>/30-templates/`. Skip `index.md` and `log.md`, which go to the vault root (Step 4).
- In upgrade mode, list templates that exist in both places but differ, so the user can merge them by hand. Don't overwrite them.
- Copy `${CLAUDE_PLUGIN_ROOT}/resources/bases/Vault-Health.base` to `10-mocs/` if missing.

## Step 4: index.md and log.md

- If `index.md` is missing, create it from `${CLAUDE_PLUGIN_ROOT}/resources/templates/index.md`. In upgrade mode, populate it:
  1. Run `uv run --script ${CLAUDE_PLUGIN_ROOT}/scripts/vault_lint.py --vault <vault>` to get the note list and types.
  2. Group the notes by domain or MOC.
  3. Write one line per note, with a one-line summary taken from its first paragraph.
  4. For more than ~150 notes, first ask whether to populate all of them or start with headings only.
- If `log.md` is missing, create it from the template and append `## [<today>] setup | <new vault or upgrade>`.

## Step 5: CLAUDE.md schema

- **New**: copy `${CLAUDE_PLUGIN_ROOT}/resources/claude-md-template.md` to `<vault>/CLAUDE.md`. Ask the user for their role, focus areas, and learning goals, and fill in "About Me".
- **Upgrade**: compare the existing `CLAUDE.md` with the template. Propose *additions only* (missing sections such as Provenance, index/log, Learning Goals, Workspace Categories), shown as a diff, and apply only what the user approves.

## Step 6: Weekly log (new mode)

Create `50-logs/<ISO year>/<ISO week>.md` from `30-templates/weekly-log.md`, filling in the dates.

## Step 7: Git

- **New**: `git init`. Write a `.gitignore` containing `.DS_Store`, `.obsidian/workspace*.json`, `.trash/`. Make an initial commit ("Initialize knowledge vault").
- **Upgrade**: if the vault is a git repo, offer one commit: `vault: upgrade layout`.

## Step 8: Summary

Print what was created or skipped, then the next steps:
1. Set the vault path so skills and hooks work from any directory: `/plugin` → knowledge-vault → configure → `vault_path`.
2. Open the vault in Obsidian. Enable Bases (core plugin) and, optionally, Settings → General → Command line interface.
3. Install Obsidian Web Clipper and point it at `00-inbox/`.
4. Optional: install the official Obsidian skills (`claude plugin marketplace add obsidianmd/obsidian-skills`), and `qmd` for search once the vault passes a few hundred notes.
5. Rhythm: `/knowledge-vault:process-inbox` weekly, `/knowledge-vault:vault-query` any time, `/knowledge-vault:vault-audit` monthly.
