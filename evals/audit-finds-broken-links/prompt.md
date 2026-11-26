---
description: The audit must use the lint script and surface the one broken link in the fixture vault.
max_turns: 25
allowed_tools: [Read, Glob, Grep, Skill, "Bash(uv run *)", "Bash(date *)", "Bash(ls *)"]
---

Run a health check on my knowledge vault (it's the current directory) and tell me what's broken. Don't change any files.
