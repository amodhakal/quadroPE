# Performance & Bottleneck Report (Template)

> This document is a template.
> Replace all placeholder values (for example: `<X>`, `<Y>`, `<Z>`, `<E>`, `<N>`, `<table.column>`) with actual measured results.

## How to use this template

1. Run a baseline load test against your local or deployed app.
1. Record exact command, duration, and environment details.
1. Capture p50/p95 latency, throughput, and error rate.
1. Apply one change at a time and re-run the same test for fair comparison.

## Test setup

- Environment: local / staging
- Tool: hey / k6 / ab / wrk
- Command: `hey -z 30s -q 50 http://localhost:5000/health`
- Baseline: app running with default config, Postgres on same host.

## Observations

- Throughput: ~<X> requests/second.
- Median latency (p50): <Y> ms.
- p95 latency: <Z> ms.
- Error rate: <E>% (4xx/5xx).

## Identified bottlenecks

1. **Database contention** at higher concurrency (connections saturate, latency spikes).
2. **Single-process Flask server** becomes CPU-bound around <N> concurrent requests.
3. Any other real observation you can make from your tests.

## Changes made

- Enabled connection pooling / tuned max connections.
- Switched to a production-grade WSGI server (e.g., gunicorn or uvicorn with workers).
- Added basic indexes on `<table.column>` to avoid full scans on common queries.

## Results after changes

- New throughput: <X2> requests/second.
- p95 latency improved from <Z> ms to <Z2> ms.
- Error rate reduced from <E>% to <E2>% under the same load.

## Remaining risks

- Under extreme load (>N RPS), still CPU-bound – consider horizontal scaling.
- Need better observability (metrics, tracing) for deeper analysis.
