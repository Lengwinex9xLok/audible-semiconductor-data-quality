#!/usr/bin/env sh
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"
if command -v python3 >/dev/null 2>&1; then
    exec python3 html_dashboard.py "$@"
fi
exec python html_dashboard.py "$@"
