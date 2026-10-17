#!/usr/bin/env bash
set -euo pipefail
R311_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$R311_ROOT"
exec .venv/bin/python photo2/review/r311/serve.py "$@"
