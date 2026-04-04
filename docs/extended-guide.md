# quadroPE — Extended Guide

Use this page as a quick reference after you complete the main setup in `README.md`.

## Environment profiles

The app can run with different DB targets depending on context. A practical profile setup is:

- **Local (default for this repo)**
  - DB name: `hackathon_db`
  - Health endpoint: `http://localhost:5000/health`
- **Dev / shared environment**
  - DB name: your team convention (for example `hackathon_db_dev`)
  - Keep credentials outside source control.
- **Prod**
  - Use managed secrets and a production DB.
  - Never commit production credentials in `.env`.

### Recommended `.env` values for local

- `DATABASE_NAME=hackathon_db`
- `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hackathon_db`

## API and operations references

- API contract and examples: [`docs/API.md`](/docs/API.md)
- Operations runbook: [`docs/runbook.md`](/docs/runbook.md)
- Incident report template: [`docs/failure-manual.md`](/docs/failure-manual.md)
- Performance template: [`docs/performance-bottleneck-report.md`](/docs/performance-bottleneck-report.md)

## Data loading and testing helpers

- Load CSV seed data: [`scripts/load_csv.py`](/scripts/load_csv.py)
- Locust test runner script: [`scripts/test_locust.py`](/scripts/test_locust.py)
- Locust scenarios directory: [`loadtests/`](/loadtests/)

## Suggested engineering workflow

1. Run the app and verify health (`/health`).
1. Load seed data and validate list endpoints.
1. Run tests (`uv run pytest`).
1. Capture performance baseline before optimizations.
1. Open PR with test evidence and any known limitations.
