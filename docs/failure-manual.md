# Failure Manual — Failure Modes & Recovery

This document catalogs every known failure mode in the system, what the user/operator sees, and how to recover.

---

## Architecture Overview

```
Client → Nginx (port 80) → App ×6 (Gunicorn, port 8000) → PostgreSQL (port 5432)
                                                         → Redis (port 6379)
```

All services run via Docker Compose with `restart: always` to enable automatic recovery.

---

## 1. App Container Crash

| Detail | Description |
|--------|-------------|
| **Trigger** | `docker kill <app-container>`, OOM kill, unhandled exception in Gunicorn worker |
| **Symptom** | Intermittent 502 Bad Gateway from Nginx; remaining 5 replicas continue serving |
| **Detection** | `docker ps` shows fewer than 6 app containers; `GET /health` still returns 200 via other replicas |
| **Recovery** | `docker compose up -d` reconciles the desired state and restarts the missing container(s) |
| **User impact** | Minimal — Nginx load-balances across the surviving replicas. Some in-flight requests may fail with 502. |
| **Tested** | Yes — killed `app-4` container, confirmed traffic still served, ran `docker compose up -d` to restore |

## 2. Nginx (Load Balancer) Crash

| Detail | Description |
|--------|-------------|
| **Trigger** | `docker kill <nginx-container>`, config error, port conflict |
| **Symptom** | All traffic on port 80 fails with connection refused |
| **Detection** | `curl http://localhost/health` returns connection refused |
| **Recovery** | `docker compose up -d` restarts Nginx |
| **User impact** | Complete outage on port 80 until Nginx is restored. App containers remain healthy. |
| **Mitigation** | App containers are still reachable directly on port 8000 if needed for debugging. |

## 3. PostgreSQL Crash

| Detail | Description |
|--------|-------------|
| **Trigger** | `docker kill <postgres-container>`, disk full, corrupted WAL |
| **Symptom** | All data endpoints return 500 Internal Server Error with JSON `{"error": "..."}` |
| **Detection** | `GET /health` returns 200 (app is alive), but `GET /users` returns 500; logs show `psycopg`/`peewee.OperationalError` |
| **Recovery** | `docker compose up -d` restarts Postgres. Data persists in the `postgres-data` Docker volume. |
| **User impact** | All CRUD operations fail. Health endpoint still responds (it doesn't query the DB). |
| **Mitigation** | Postgres has a health check (`pg_isready`) — app containers wait for it via `depends_on: condition: service_healthy`. |

## 4. Redis Crash

| Detail | Description |
|--------|-------------|
| **Trigger** | `docker kill <redis-container>`, memory limit exceeded |
| **Symptom** | Cache misses; slightly increased latency as all reads hit PostgreSQL directly |
| **Detection** | `docker ps` shows Redis stopped; app logs may show Redis connection warnings |
| **Recovery** | `docker compose up -d` restarts Redis. Cache rebuilds on subsequent requests. |
| **User impact** | Negligible — the app falls through to direct DB queries. No errors returned to users. |

## 5. Invalid Client Input (Bad JSON, Wrong Types, Missing Fields)

| Detail | Description |
|--------|-------------|
| **Trigger** | Client sends malformed JSON, missing required fields, or wrong types |
| **Symptom** | Clean JSON error response with 400 or 422 status code |
| **Detection** | Response body contains `{"error": "<description>"}` — no stack traces exposed |
| **Recovery** | Client-side fix — correct the request payload |
| **User impact** | Single request rejected. No server-side impact. |

### Specific validation rules:

| Endpoint | Validation | Error |
|----------|-----------|-------|
| `POST /users` | `username` and `email` must be non-empty strings | 400: `"username must be a non-empty string"` |
| `POST /urls` | `user_id` must be an integer | 400: `"user_id must be an integer"` |
| `POST /urls` | `original_url` and `title` must be non-empty strings | 400: `"original_url must be a string"` |
| `POST /urls` | `user_id` must reference an existing user | 400: `"User not found"` |
| `POST /users/bulk` | File must be a `.csv` upload in the `file` field | 400: `"Missing 'file' field"` or `"Invalid file type"` |
| `PUT /users/<id>` | Body must be valid JSON | 400: `"Invalid JSON"` |
| Any endpoint | Non-existent resource ID | 404: `{"error": "Not found"}` |

## 6. Non-Existent Route

| Detail | Description |
|--------|-------------|
| **Trigger** | Client requests a URL path that doesn't exist |
| **Symptom** | 404 response with `{"error": "Not found"}` |
| **Detection** | Logged as a warning in app logs |
| **Recovery** | None needed — informational. Client should fix the URL. |

## 7. Inactive Short Code Redirect

| Detail | Description |
|--------|-------------|
| **Trigger** | Client attempts to redirect using a short code that has been deactivated (`is_active: false`) |
| **Symptom** | 404 response |
| **Detection** | Logged as warning: `"Short code inactive: <code>"` |
| **Recovery** | Re-activate the URL via `PUT /urls/<id>` with `{"is_active": true}` |

## 8. Full System Outage (All Containers Down)

| Detail | Description |
|--------|-------------|
| **Trigger** | `docker compose down`, host machine reboot, Docker daemon crash |
| **Symptom** | All endpoints unreachable |
| **Recovery** | `docker compose up -d` — all services start in dependency order (Postgres → Redis → App → Nginx) |
| **Data impact** | None — Postgres data persists in the `postgres-data` volume. Redis cache is rebuilt on demand. |

---

## Incident Response Checklist

1. **Confirm** — `curl http://localhost/health` — is the app reachable?
2. **Identify scope** — check `docker ps` to see which containers are running
3. **Collect evidence** — `GET /logs` for recent app logs, `docker logs <container>` for container-level logs
4. **Classify** — is it app-level, DB-level, infra-level, or client-level?
5. **Recover** — `docker compose up -d` to restore desired state
6. **Verify** — re-run the failing request and confirm `GET /health` returns 200
7. **Document** — record the timeline and root cause in `docs/incidents/`

---

## Chaos Mode Test Results

| Test | Command | Result |
|------|---------|--------|
| Kill app container | `docker kill pe-hackathon-template-2026-app-4` | Remaining 5 replicas continue serving; `docker compose up -d` restores the 6th |
| Kill nginx | `docker kill pe-hackathon-template-2026-nginx-1` | Port 80 goes down; `docker compose up -d` restores it |
| Send garbage JSON to `POST /users` | `curl -X POST -H "Content-Type: application/json" -d '{"bad":1}' /users` | Returns `400 {"error": "username must be a non-empty string"}` |
| Send non-JSON to `POST /urls` | `curl -X POST -d 'not json' /urls` | Returns `400 {"error": "Invalid JSON"}` |
| Request non-existent user | `GET /users/99999` | Returns `404 {"error": "Not found"}` |
| Request non-existent URL | `GET /urls/99999` | Returns `404 {"error": "Not found"}` |
