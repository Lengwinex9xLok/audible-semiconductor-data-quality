#!/usr/bin/env sh
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"
if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    printf '%s\n' 'Python 3 is required. Install it before running this demo.' >&2
    exit 1
fi
for arg in "$@"; do
    if [ "$arg" = "--no-refresh" ]; then
        exec "$PYTHON" html_dashboard.py "$@"
    fi
done
exec "$PYTHON" html_dashboard.py --require-live "$@"
