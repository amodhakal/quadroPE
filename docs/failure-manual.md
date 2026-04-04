# Failure Manual / Failure Modes

This document describes what failure looks like in quadroPE, how to confirm each failure mode, and how to recover quickly.

## 1. Failure mode catalog

### A) App process unavailable

- **Symptoms:** `GET /health` times out or returns connection refused.
- **Where seen first:** Discord "Service Down" alert from the health monitor.
- **Likely causes:** crashed process, container stopped, startup failure.
- **Recovery:** restart app process/container, then confirm `GET /health` returns `200` with `{"status":"ok"}`.

### B) Database unavailable or credentials mismatch

- **Symptoms:** 500s on data endpoints, errors mentioning `psycopg`/connection refused in logs.
- **Where seen first:** `/logs` endpoint and application stderr/stdout logs.
- **Likely causes:** Postgres stopped, wrong `.env` credentials, wrong host/port.
- **Recovery:** start Postgres, verify `.env` (`DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_NAME`), retry request.

### C) Invalid client payloads

- **Symptoms:** 400/422 responses with polite JSON error messages.
- **Where seen first:** API response body and `/logs` warning entries.
- **Likely causes:** missing required JSON fields, wrong types (for example `user_id` not integer).
- **Recovery:** correct request schema and retry. No server restart needed.

### D) Health endpoint degraded while app is reachable

- **Symptoms:** app responds on other routes but `/health` returns non-200.
- **Where seen first:** monitoring check and Discord alert.
- **Likely causes:** dependency degradation (typically DB reachability).
- **Recovery:** validate DB connectivity and environment config, then confirm `/health` recovers.

## 2. Incident response checklist

1. Confirm incident with `GET /health`.
1. Collect evidence from `GET /logs` and, if available, `GET /metrics`.
1. Identify whether failure is app-level, DB-level, or request-schema-level.
1. Apply targeted recovery (restart app, recover DB, rollback bad deploy, or fix request schema).
1. Verify recovery by re-running failing request and `/health`.
1. Record timeline and root cause in a new incident note under `docs/`.

## 3. Standard incident note format

Create a new file per incident, for example:

- `docs/incidents/incident-2026-04-04-health-down.md`

Include:

- Summary
- Impacted endpoints
- Timeline (UTC)
- Root cause
- Mitigation
- Prevention actions

## 4. Prevention actions backlog

- [ ] Add an automated test for at least one previously observed bad payload case.
- [ ] Add dashboard chart(s) for health status, request errors, and DB connectivity signals.
- [ ] Add explicit alert thresholds for sustained 5xx rates and repeated health check failures.
