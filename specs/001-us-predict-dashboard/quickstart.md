# quickstart.md

Date: 2025-10-22
Feature: 美股预测仪表盘

## Run locally (developer)

1. Create a Python 3.11 virtualenv and activate it.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Fetch sample data for a ticker (AAPL) and write parquet:

```bash
python -m src.data fetch --ticker AAPL
```

4. Run the Streamlit app locally:

```bash
streamlit run src/app.py
```

## Deploy to Streamlit Community Cloud (MVP)

1. Ensure `app.py` is at `src/app.py` and `requirements.txt` contains required packages.
2. Push branch to GitHub and connect the repo in Streamlit Community Cloud.
3. Configure scheduled GitHub Actions workflows for daily fetch and nightly retrain.

## Notes

- By default Prophet is disabled. To enable, follow governance approval steps documented in `research.md` and add `prophet` to `requirements.txt`.

\*\*\* End of quickstart.md
