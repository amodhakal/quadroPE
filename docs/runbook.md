# quadroPE Runbook

## 1. Overview

quadroPE is a Flask-based API backed by PostgreSQL. It exposes a `/health` endpoint for basic liveness checks and is deployed via a CI workflow that runs tests on every change.

## 2. How to check if it's healthy

### Local

1. Ensure Postgres is running.
2. Activate the project environment.
3. Start the app:

   ```bash
   uv run run.py
   ```

4. Hit the health endpoint:

   ```bash
   curl http://localhost:5000/health
   ```

   Expected:

   ```json
   {"status": "ok"}
   ```

### Production

1. Go to: `https://<your-app-domain>/health`
2. Expected JSON: `{"status": "ok"}`.
3. If you see non-200 or a different payload, follow the “Common failures” section.

## 3. Common failures and quick fixes

### App won’t start (ImportError / missing package)

**Symptoms:** stack trace mentioning `ModuleNotFoundError`.  
**Checks and actions:**

- Run `uv sync` to install dependencies.
- Confirm Python version matches the project README.
- Re-run `uv run run.py`.

### DB connection errors

**Symptoms:** errors mentioning `psycopg`, `ECONNREFUSED`, or bad credentials.  
**Checks and actions:**

- Confirm Postgres is running.
- Check `.env` matches your local DB user, password, port.
- Create the DB per README (e.g. `createdb hackathon_db`).

### Health endpoint failing

**Symptoms:** `/health` returns 500 or times out.  
**Checks and actions:**

- Verify app process is running.
- Check logs for stack traces.
- Check DB connectivity.
- If only non-critical downstreams fail, confirm the app degrades gracefully.

## 4. How to deploy

### Pre-deploy

1. Ensure tests pass locally: `uv run pytest` (or the project’s test command).
2. Commit and push to `main` or the deploy branch.

### CI behavior

- GitHub Actions workflow (`.github/workflows/...`) runs tests.
- If tests fail, deployment is blocked.

### Manual rollback

1. Identify last known good commit SHA.
2. `git revert` or re-deploy that commit via your deployment mechanism.
3. Re-run `/health` to confirm recovery.

## 5. Escalation

- **Primary owner:** @<github-handle>
- **Secondary:** @<backup-handle>
- If outage exceeds 30 minutes, open a GitHub issue titled `[INCIDENT] <short summary>` and link any dashboard screenshots and logs.
