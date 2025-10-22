# US Stock Price Predict - Local Development

This repository contains a small Streamlit-based MVP for US stock price prediction. The project uses a lightweight prediction path (SMA) and stores historical data as Parquet files under `data/`.

## Quickstart — run locally (recommended)

1. Create and activate a virtual environment (macOS / zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -U pip
pip install -r requirements.txt
```

3. (Optional) Fetch a sample ticker to populate `data/`:

```bash
python - <<'PY'
from src.data import fetch_prices, write_parquet
t = 'AAPL'
df = fetch_prices(t)
write_parquet(t, df)
print('wrote', len(df), 'rows')
PY
```

4. Start the Streamlit app (ensure you run from the project root):

```bash
# Simple one-liner (ensures project root is on PYTHONPATH)
PYTHONPATH="$(pwd)" streamlit run src/app.py

# Or use the venv python to run streamlit
python -m streamlit run src/app.py
```

If you see `ModuleNotFoundError: No module named 'src'`, it means Python cannot find the project package on its import path. Use the `PYTHONPATH` approach above or see the alternatives below.

## Short-term convenience: run script

You can create a small wrapper script `run.sh` to standardize startup:

```bash
#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")" && pwd)"
source "$ROOT/.venv/bin/activate" || true
export PYTHONPATH="$ROOT"
python -m streamlit run src/app.py
```

Make it executable: `chmod +x run.sh` and run `./run.sh`.

## Long-term / Recommended: editable install

Turning this repository into an editable install removes the need to set `PYTHONPATH` and makes imports consistent in all environments (local, CI, deployment). Steps:

1. Add a small `pyproject.toml` (or `setup.cfg`) to define the package.
2. Run:

```bash
pip install -e .
```

After this, `import src` (or the package name you choose) will work without modifying `PYTHONPATH`.

## Running tests

```bash
# activate venv first
pytest -q
```

## Troubleshooting

- `ModuleNotFoundError: No module named 'src'` — use `PYTHONPATH=$(pwd)` or install the project via `pip install -e .`.
- `streamlit: command not found` — ensure the venv is activated and `streamlit` is installed in it.
- `yfinance` network or SSL issues during install — ensure OpenSSL is available via Homebrew and set `CPPFLAGS`/`LDFLAGS` as needed.

If you need me to scaffold `pyproject.toml` or add `run.sh` to the repo, tell me and I will create the files and commit them.
