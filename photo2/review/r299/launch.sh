#!/bin/sh
set -eu
cd "$(dirname "$0")/../../.."
exec .venv/bin/python -m photo2.r299.serve "$@"
