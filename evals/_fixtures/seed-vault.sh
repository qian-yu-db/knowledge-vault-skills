#!/bin/bash
# Shared scaffold: copy the fixture vault (and the plugin's templates) into the
# eval run's empty workspace. Called from each case's scaffold.sh.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
plugin_root="$(cd "$here/../.." && pwd)"
cp -R "$here/vault/." .
mkdir -p 30-templates 40-archive
cp "$plugin_root"/resources/templates/*.md 30-templates/
