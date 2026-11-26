#!/bin/bash
# Stop: once per session, after a substantive session (many tool calls), show the
# user a one-line reminder that /knowledge-vault:session-wrap can capture it.
# Uses systemMessage (user-visible, no tokens, cannot loop) instead of blocking.
set -u
command -v jq >/dev/null 2>&1 || exit 0

input="$(cat)"
[ "$(jq -r '.stop_hook_active // false' <<<"$input")" = "true" ] && exit 0
session="$(jq -r '.session_id // empty' <<<"$input")"
transcript="$(jq -r '.transcript_path // empty' <<<"$input")"
[ -n "$session" ] && [ -f "$transcript" ] || exit 0

data="${1:-${CLAUDE_PLUGIN_DATA:-}}"
[ -n "$data" ] || data="${TMPDIR:-/tmp}/knowledge-vault"
flags="$data/wrap-reminded"
mkdir -p "$flags" 2>/dev/null || exit 0
flag="$flags/$session"
[ -e "$flag" ] && exit 0

threshold="${KNOWLEDGE_VAULT_WRAP_MIN_TOOL_CALLS:-25}"
tool_calls="$(grep -o '"type":"tool_use"' "$transcript" 2>/dev/null | wc -l | tr -d ' ')"
[ "${tool_calls:-0}" -ge "$threshold" ] || exit 0
grep -Eq '"skill":"[^"]*session-wrap' "$transcript" 2>/dev/null && exit 0

touch "$flag"
find "$flags" -type f -mtime +14 -delete 2>/dev/null
jq -n --arg n "$tool_calls" '{systemMessage: ("Substantive session (" + $n + " tool calls). Run /knowledge-vault:session-wrap to log it and capture reusable insights.")}'
