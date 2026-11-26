---
name: review-outdated
description: Finds stale or version-sensitive vault notes (old last_verified dates, review-needed tags, Databricks feature and code-pattern notes), checks the chosen ones against current official sources, and updates or deprecates them. Use when the user wants to refresh outdated notes or run the monthly freshness review.
argument-hint: "[type-or-topic filter]"
allowed-tools: Read, Grep, Glob, Bash(uv run *), Bash(date *), WebSearch, WebFetch
---

# Review Outdated Notes

Filter: `$ARGUMENTS` (optional type or topic).

## Setup

- **Vault root**: `${user_config.vault_path}`. If blank or a literal placeholder, use the current working directory.
- Read `${CLAUDE_PLUGIN_ROOT}/resources/vault-conventions.md` unless it's already in context.

## Steps

1. **Find candidates.**
   - Run `uv run --script ${CLAUDE_PLUGIN_ROOT}/scripts/vault_lint.py --vault <root>` and take `stale`. It applies 90 days for `databricks-feature` and `code-pattern` notes and 180 days for everything else.
   - Add notes tagged `status/review-needed` or `confidence/needs-review` (Grep).
   - Apply the filter, if one was given.
2. **Prioritize.**
   - **High**: Databricks features and code patterns, especially ones linked from active `01-projects/` or recent `log.md` entries.
   - **Medium**: papers with implementations, model cards, guides.
   - **Low**: concepts, archived experiments.
3. **Show the table** (path, type, last_verified or age, why flagged, priority). Ask which notes to review; suggest the top 5.
4. **Review each selected note:**
   - Read the note and its `sources:`. Check each version-sensitive claim against current official docs or release notes. Note the URLs.
   - Propose specific edits, each with old claim → new claim and the citing URL.
   - After approval:
     - Apply the edits and add the new URLs to `sources:`.
     - Set `last_verified: <today>`.
     - Add a row to "Version Notes" if the note has that section.
   - If the note is obsolete, don't delete it.
     - Add the `status/outdated` tag and a top callout: `> [!warning] Outdated (<today>): superseded by [[newer-note]]`.
     - Move it to `40-archive/` only if the user asks.
5. **Log**: append `## [<today>] review | N notes verified, N updated, N deprecated` to `log.md`.
