---
name: session-wrap
description: Records an explicitly requested handoff for the current Claude Code session in the knowledge vault's weekly log and log.md (done, issues, next step, key files), then proposes reusable insights to write back into permanent notes. Use only when the user asks to wrap up, hand off or log the session.
argument-hint: "[topic]"
allowed-tools: Read, Grep, Glob, Bash(date *), Bash(git status*), Bash(git diff --stat*)
---

# Session Wrap

Invoking this skill counts as approval to write the session log. Changes to permanent notes need separate approval.

## Setup

- **Vault root**: `${user_config.vault_path}`. If blank or a literal placeholder, use the current working directory, but only if it contains `20-notes/`. Otherwise ask for the vault path.
- Read `${CLAUDE_PLUGIN_ROOT}/resources/vault-conventions.md` before Part B.
- Now: !`date "+%Y-%m-%d %H:%M (%A)"` · ISO week file: `50-logs/`!`date +%G`/!`date +%G-W%V`.md

## Part A: Session log

1. Summarize from this conversation and the workspace state (`git status`, `git diff --stat` in the working repo):
   - what was completed;
   - what failed, or was tried and abandoned;
   - what's still open;
   - the single most useful next action;
   - the key files.

   Don't invent results or verification you didn't actually see.
2. Open the ISO-week file above. If it doesn't exist, create it from `30-templates/weekly-log.md`. Append under today's day heading, without overwriting:
   ```markdown
   - **Claude session: <topic>** (YYYY-MM-DD HH:MM)
     - Done: <1–3 items>
     - Issues: <blockers or failed attempts, or "none">
     - Next: <one specific next action>
     - Key files: <paths>
     - Knowledge captured: pending review
   ```
   The `Next:` line is read by the SessionStart hook at the start of the next session, so make it specific.
3. Add real blockers under the weekly log's `## Project Blockers / Questions / Status` section, if it has one.
4. Append to `log.md`: `## [YYYY-MM-DD] wrap | <topic>`, with the next step.

## Part B: Knowledge write-back (proposal only)

5. Pull out insights that pass all three tests:
   - **Insight**: explains how, why, or when.
   - **Reuse**: would help in another session, project or customer.
   - **Novel**: Grep `20-notes/` and check `index.md` to see whether the vault already has it.

   Good candidates: root causes, verified limitations, solution patterns, approach comparisons, architecture decisions, performance results with data.

   If nothing qualifies, say "No vault-worthy insights from this session", set `Knowledge captured: none`, and stop.
6. For each insight, read the 2–3 closest notes and decide whether to enhance one of them (preferred) or create a new note.
7. Propose:
   ```
   1. <Insight> → enhance `20-notes/x.md` § <section> — <2-sentence preview>
   2. <Insight> → create `20-notes/<type>-<name>.md` (<type>) — <preview>
   Approve all, some (e.g. "1,3"), or skip?
   ```
8. On approval:
   - Follow the conventions: evidence-based inline links and `last_verified: today`.
   - Set `sources:` to the session (`session: <date> <topic>`) plus any URLs or docs you checked.
   - Use the vault templates for new notes, and add them to `index.md`.
9. Replace `pending review` in the log entry with `[[note]] (enhanced|new)` links.

## Rules

- Never trigger implicitly. The Stop hook only *suggests* this skill to the user.
- Logs are factual and short (3–6 lines). Append only.
- Never write permanent notes without explicit approval. Never commit or push.
