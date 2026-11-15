#!/usr/bin/env sh
# Capstone HTML entry point. See HTML_DEMO_README.md for prerequisites.
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"
exec sh ./run_html_demo.sh "$@"
