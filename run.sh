#!/usr/bin/env bash
set -euo pipefail
# run.sh - wrapper to start the Streamlit app with project PYTHONPATH and optional venv activation
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate venv if present
if [ -f "$ROOT/.venv/bin/activate" ]; then
  # shellcheck disable=SC1090
  source "$ROOT/.venv/bin/activate"
fi

export PYTHONPATH="$ROOT"

echo "Starting Streamlit (PYTHONPATH=$PYTHONPATH) ..."
python -m streamlit run src/app.py
