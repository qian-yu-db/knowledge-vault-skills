#!/bin/bash
# Shared helpers for knowledge-vault hooks.

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LINT="$HOOK_DIR/../scripts/vault_lint.py"

# Run the lint script with uv when available (project convention), else python3.
run_lint() {
  if command -v uv >/dev/null 2>&1; then
    uv run --quiet --script "$LINT" "$@"
  else
    python3 "$LINT" "$@"
  fi
}

# Print the resolved vault root: plugin option first, then the given cwd.
vault_root() {
  local candidate="${CLAUDE_PLUGIN_OPTION_VAULT_PATH:-$1}"
  candidate="${candidate/#\~/$HOME}"
  [ -n "$candidate" ] && [ -d "$candidate" ] && (cd "$candidate" && pwd -P)
}

# True when $1 (a path) is inside $2 (a directory).
is_inside() {
  local p
  p="$(cd "$(dirname "$1")" 2>/dev/null && pwd -P)/$(basename "$1")" || return 1
  case "$p/" in "$2"/*) return 0 ;; *) return 1 ;; esac
}
