#!/bin/bash
set -euo pipefail
bash "$(cd "$(dirname "$0")" && pwd)/../_fixtures/seed-vault.sh"
