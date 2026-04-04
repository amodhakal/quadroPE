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

1. Go to your deployed app health endpoint, for example: `https://your-domain/health`
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

## 4. Alert playbooks

The app’s alert monitor currently sends Discord alerts when the `/health` check changes state. Use the playbooks below when you see one of those alerts.

### Alert: Service Down

**What it means:** the monitor could not reach `GET /health`, or the endpoint returned a non-200 response.

**Triage steps:**

1. Open the app URL and confirm whether the site is reachable.
2. Call `GET /health` directly and note the response code and body.
3. Check `GET /logs` for the most recent structured log messages around the failure.
4. Check `GET /metrics` to see whether CPU or memory usage is unusually high.
5. Verify Postgres is running and credentials in `.env` match the deployed environment.

**Fix steps:**

1. Restart the app container or process if it is hung.
2. Restart Postgres if database connections are failing.
3. If a bad deploy caused the issue, roll back to the last known good commit.
4. Re-run `GET /health` until it returns `200` with `{"status":"ok"}`.
5. Confirm the Discord alert flips to recovered once the monitor sees the service healthy again.

### Alert: Service Recovered

**What it means:** the monitor can reach `GET /health` again and the app is healthy.

**Follow-up steps:**

1. Record the incident start time and recovery time in the failure manual.
2. Capture the root cause from logs, deploy history, or database state.
3. Update the incident ticket with the exact fix that resolved the outage.
4. If the issue was user-facing, make sure the postmortem includes a prevention action.

### Alert: Health check failing, but app is still up

**What it means:** the web process is responding, but `/health` is returning the wrong status or payload.

**Triage steps:**

1. Call `GET /health` and capture the body.
2. Check `GET /logs` for exceptions or warnings around the time of the failure.
3. Check whether Postgres is reachable from the app host.
4. Review recent deploys or config changes.

**Fix steps:**

1. Restore the last known good config or deploy.
2. Fix the failing dependency or database connection.
3. Re-test `/health` and verify it returns exactly `{"status":"ok"}`.
4. Leave a note in the incident record describing the bad state and the recovery action.

## 5. How to deploy

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

## 6. Escalation

- **Primary owner:** the currently assigned on-call engineer.
- **Secondary:** any available teammate with deploy access.
- If outage exceeds 30 minutes, open a GitHub issue titled `[INCIDENT] short summary` and link relevant dashboard screenshots and logs.
