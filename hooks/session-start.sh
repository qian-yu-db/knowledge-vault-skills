#!/bin/bash
# SessionStart: when the session runs inside the vault, tell Claude the vault's
# state (inbox backlog, lint errors, last session's "Next" step).
set -u
source "$(dirname "$0")/lib.sh"
command -v jq >/dev/null 2>&1 || exit 0

input="$(cat)"
cwd="$(jq -r '.cwd // empty' <<<"$input")"
root="$(vault_root "$cwd")" || exit 0
here="$(cd "${cwd:-.}" 2>/dev/null && pwd -P)" || exit 0
case "$here/" in "$root"/*) ;; *) exit 0 ;; esac

summary="$(run_lint --vault "$root" --summary 2>/dev/null)"
[ -z "$summary" ] && exit 0

jq -n --arg ctx "$summary" '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $ctx}}'
