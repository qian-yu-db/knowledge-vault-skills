---
name: new-paper
description: Creates a research-paper note in the knowledge vault from an arXiv/paper URL or a title. Fetches metadata and code links, archives the abstract as a raw source, connects the paper to existing notes, projects and the user's learning goals, and updates index.md and MOCs. Use when the user shares a paper link or asks to add or summarize a paper.
argument-hint: "<arxiv-url | paper-url | title>"
allowed-tools: Read, Grep, Glob, WebFetch, WebSearch, Bash(mkdir *), Bash(date *), Bash(uv run *)
---

# New Paper Note

Input: `$ARGUMENTS`

## Setup

- **Vault root**: `${user_config.vault_path}`. If blank or a literal placeholder, use the current working directory.
- Read `${CLAUDE_PLUGIN_ROOT}/resources/vault-conventions.md` and the vault `CLAUDE.md`, especially "About Me" and "Learning Goals", unless they're already in context.
- Today: !`date +%Y-%m-%d`

## Step 1: Fetch

- For a URL, fetch the abstract page. For a title, search for the canonical arXiv or venue page.
- Extract: title, authors, year, venue, arXiv ID, abstract.
- Find code links: the arXiv "Code" link, github.com URLs on the page, the project page.
- Save the metadata and abstract, verbatim, as the raw source `raw/YYYY-MM/paper-<short-name>-<year>.md`. If the user supplies a PDF, put it in `assets/papers/` and reference it.

## Step 2: Vault context

Use the search ladder from the conventions:
- concepts and papers on the same techniques (`20-notes/`);
- projects it could apply to (`01-projects/`);
- MOCs (`10-mocs/`).

If a note for this paper already exists, update it instead.

## Step 3: Write `20-notes/paper-<short-name>-<year>.md`

Use `30-templates/paper.md`. Frontmatter:
- `type: paper`, `status: reading`
- `arxiv`, `github` (empty string if there's none), `year`, `authors`
- specific `tags`
- `sources:` (the raw path and the URL)
- `date_added`, `last_verified`

Sections:
- **Key Contribution**: 2–3 sentences, and why it matters.
- **Core Ideas**: 4–6 ideas. Link each to an existing concept note where one exists; define any new terms.
- **Method**: approach and architecture; how it differs from prior methods ("Unlike X, …").
- **Results**: key numbers against baselines, plus the limitations the authors admit.
- **Relevance to My Work**: based only on the vault CLAUDE.md About Me, Learning Goals, and `01-projects/`. Cover specific projects, concept notes that should be updated, applications to the user's domain, and one experiment to try. Never invent projects or customers.
- **Implementation Notes**: prerequisites, complexity, platform integration points.
- **Citations to Explore**: 3–5 references, marking which ones the vault already has.

Keep the paper's claims apart from your assessment (conventions §2).

## Step 4: Integrate

- Add a line to `index.md`.
- Suggest MOC placement, and concept notes that should link back. Apply them after confirmation.
- Append `## [<today>] ingest | paper: <title>` to `log.md`.
