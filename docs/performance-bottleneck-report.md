# Performance & Bottleneck Report

This report documents the current bottleneck profile for quadroPE and the next optimization priorities.

## Scope and approach

This project currently uses:

- Flask app service behind Nginx in Docker Compose
- PostgreSQL for persistence
- `/health`, `/metrics`, and `/logs` as operational endpoints

Load testing can be executed with:

- `scripts/test_locust.py`
- scenarios in `loadtests/`

## Test setup

- Environment: local Docker Compose stack
- Tooling options: Locust (`scripts/test_locust.py`) or `hey`
- Command: `hey -z 30s -q 50 http://localhost:5000/health`
- Baseline: app and Postgres running on the same host with default project configuration.

## Current bottleneck observations

- The health endpoint is lightweight and stable, but does not represent database-heavy paths.
- Endpoints that hit Postgres (`/users`, `/urls`, `/events`) are expected to be bottlenecked first under concurrent load.
- The default Flask process model is more sensitive to concurrency than multi-worker production servers.
- Under prolonged stress, DB contention and app worker saturation are the primary risk factors.

## Identified bottlenecks

1. **Database contention risk** at higher concurrency (connection pressure and query latency spikes).
2. **App worker saturation risk** under concurrent request bursts.
3. **Limited observability history** (current endpoints provide snapshots, not long-lived time series).

## Mitigations already in place

- Reverse proxy and service decomposition via Docker Compose (`app`, `postgres`, `redis`, `nginx`).
- Restart policies (`unless-stopped`) configured to improve recovery behavior under process crashes.
- Operational visibility endpoints implemented: `/metrics` and `/logs`.

## Next optimizations to execute

1. Run repeatable Locust scenarios for `/users`, `/urls`, and `/events` with increasing concurrency.
2. Capture p50/p95 latency and error rates for each endpoint family.
3. Add indexes for the most common query filters once slow paths are confirmed.
4. Compare single-process vs multi-worker app serving for throughput and tail latency.

## Remaining risks

- Tail latency regressions may appear before average latency changes are noticeable.
- Database saturation can cascade into health check failures if not detected early.
- Missing long-term dashboard history reduces confidence in capacity planning.
