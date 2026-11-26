---
name: weekly-quiz
description: Generates and runs an interactive 5-question quiz drawn from the user's vault notes plus the latest developments, rotating through the learning goals listed in the vault CLAUDE.md, then scores it and logs gaps in the weekly log. Use when the user asks for a quiz, flashcards or a knowledge check.
argument-hint: "[skill-area]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, WebSearch, Bash(date *)
---

# Weekly Knowledge Quiz

Override skill area: `$ARGUMENTS`

## Setup

- **Vault root**: `${user_config.vault_path}`. If blank or a literal placeholder, use the current working directory.
- ISO week: !`date +%G-W%V` (week number !`date +%V`)

## Step 1: Pick the skill area

- If an area was passed, use it.
- Otherwise read the "Learning Goals" list in the vault `CLAUDE.md` and rotate through it: area = goals[(ISO week number − 1) mod len(goals)].
- If there's no Learning Goals section, ask the user for 3–5 areas and suggest adding them to `CLAUDE.md`.

## Step 2: Gather material

- Read the vault notes for that area: the `index.md` section, filename globs, a content Grep. Prefer notes added or verified recently.
- Do one web search for notable developments from the last ~3 months in that area.

## Step 3: Quiz, one question at a time

Ask 5 questions:
- 2 conceptual (definitions, comparisons);
- 2 applied (scenarios, design decisions grounded in the user's work context);
- 1 cutting-edge (from the web search).

Ask one question, wait for the answer, then give feedback with the correct answer, why it matters, and a `[[note]]` link if the vault covers it. Then ask the next.

## Step 4: Score and log

- Give a score out of 5, 1–2 gap areas, and specific resources for each (a vault note, or an external link).
- Append to the current weekly log `50-logs/<ISO year>/<ISO week>.md`: `- Quiz (<area>): <score>/5 — gaps: …`. Create the log from the template if it doesn't exist.
- If a question exposed a missing or wrong vault note, suggest `/knowledge-vault:vault-enhance`, or a new note for that topic.
