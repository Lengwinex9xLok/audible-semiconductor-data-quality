#!/usr/bin/env sh
# Capstone HTML entry point. See the project README for prerequisites.
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"
exec sh ./run_html_demo.sh "$@"
