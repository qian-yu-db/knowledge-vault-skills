#!/bin/bash
# PostToolUse(Write|Edit): lint the vault note that was just written and report
# frontmatter / broken-link errors back to Claude (exit 2 -> stderr to Claude).
set -u
source "$(dirname "$0")/lib.sh"
command -v jq >/dev/null 2>&1 || exit 0

input="$(cat)"
file="$(jq -r '.tool_input.file_path // empty' <<<"$input")"
cwd="$(jq -r '.cwd // empty' <<<"$input")"
case "$file" in *.md) ;; *) exit 0 ;; esac

root="$(vault_root "$cwd")" || exit 0
is_inside "$file" "$root" || exit 0

out="$(run_lint --vault "$root" --file "$file" --format text 2>&1)"
[ $? -eq 1 ] || exit 0

{
  echo "knowledge-vault lint found problems in the note you just wrote:"
  echo "$out" | grep ' ERROR '
  echo "Fix problems your edit introduced. A broken link is fine if you are creating that note later in this same run."
  echo "Do not fix problems that already existed in the note unless the user asked; mention them instead."
} >&2
exit 2
