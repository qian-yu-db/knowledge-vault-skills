# Knowledge Vault — Claude Code Plugin

An LLM-powered personal knowledge base using Karpathy's compilation pipeline. Install the plugin, run `/setup-vault`, and start compounding knowledge.

## Quick Start

```bash
# 1. Register the marketplace in Claude Code settings
# Add to extraKnownMarketplaces in ~/.claude/settings.json:
#   "knowledge-vault": { "source": { "source": "directory", "path": "/path/to/knowledge-vault" } }

# 2. Enable the plugin
# In Claude Code: /plugins → enable knowledge-vault

# 3. Create your vault
/setup-vault ~/my-knowledge-vault

# 4. Open in Obsidian and start clipping articles
```

## The 4-Phase Pipeline

Based on [Karpathy's LLM knowledge base approach](https://academy.dair.ai/blog/llm-knowledge-bases-karpathy):

| Phase | Command | What it does |
|-------|---------|-------------|
| **1. Ingest** | Obsidian Web Clipper | Clip articles/papers → `00-inbox/` |
| **2. Compile** | `/process-inbox` | LLM deep-compiles sources into 1500-3000 word notes with cross-links |
| **3. Query & Enhance** | `/session-wrap` | Research findings get written back into permanent notes |
| **4. Lint & Maintain** | `/vault-enhance` | Auto-link, enrich weak notes, discover gaps |

## Commands

| Command | Description |
|---------|-------------|
| `/setup-vault <path>` | Bootstrap a new vault from scratch |
| `/process-inbox` | Compile inbox notes into deep, interlinked knowledge |
| `/vault-enhance` | Enrich weak notes, fix links, suggest new content |
| `/session-wrap` | Capture session state + write-back vault-worthy insights |
| `/vault-audit` | Structural health check |
| `/review-outdated` | Find and update stale notes |
| `/build-moc <topic>` | Create/update a Map of Content |
| `/new-paper <url>` | Create a paper note |
| `/new-customer <name>` | Create a customer note |
| `/weekly-quiz [skill]` | Knowledge reinforcement quiz |
| `/project-status` | Workspace project overview |

## Recommended Rhythm

- **Weekly**: `/process-inbox` + `/vault-enhance` + `/weekly-quiz`
- **Monthly**: `/vault-audit` + `/vault-enhance` + `/review-outdated`
- **End of session**: `/session-wrap` (auto-prompted via Stop hook)

## Plugin Structure

```
knowledge-vault/
├── .claude-plugin/
│   ├── plugin.json          # Plugin manifest with Stop hook
│   └── marketplace.json     # Standalone marketplace config
├── commands/                # 10 slash commands
├── skills/
│   └── session-wrap/        # Session wrap with write-back
├── hooks/
│   └── session-wrap-reminder/  # Stop hook for auto-reminders
└── resources/
    ├── templates/           # 15 Obsidian note templates
    └── claude-md-template.md  # Generic CLAUDE.md for new vaults
```
