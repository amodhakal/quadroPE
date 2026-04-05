# Sherlock Mode — Diagnosing a Fake Issue Using the Dashboard & Logs

## The Scenario

**Reported Issue:** Users report that creating short URLs intermittently fails with errors. The system appears mostly healthy, but some requests are being rejected.

---

## Step 1: Check the Dashboard Overview

Navigate to `http://localhost/dashboard` (or `http://localhost:5000/dashboard` locally).

**What we see:**
- **Latency**: Avg latency is normal (~15ms), but p99 has spiked to 200ms+
- **Traffic**: Total requests are climbing normally — the service is receiving traffic
- **Error Rate**: Jumped from 0% to ~12% — something is producing 400-level errors
- **Saturation**: Active requests remain low (1-2), so the server isn't overloaded

**Initial Hypothesis:** The spike in error rate combined with normal latency and low saturation rules out a capacity problem. This looks like a **client-side or validation issue**, not a server crash.

## Step 2: Inspect the Error Breakdown Chart

The **Error Breakdown** doughnut chart shows:
- **HTTP 400**: 85% of all errors
- **HTTP 404**: 15% of errors
- **HTTP 500**: 0%

**Updated Hypothesis:** No 500s means the server is healthy. The 400s indicate bad requests — likely invalid payloads hitting the `POST /urls` endpoint.

## Step 3: Check the Recent Requests Table

The **Recent Requests** table shows a pattern:

| Method | Path | Status | Latency |
|--------|------|--------|---------|
| POST | /urls | 400 | 3ms |
| POST | /urls | 400 | 2ms |
| GET | /health | 200 | 1ms |
| POST | /urls | 201 | 18ms |
| POST | /urls | 400 | 2ms |

**Observation:** Multiple `POST /urls` requests are failing with 400, while some succeed. The fast latency on failures (2-3ms) suggests the server rejects them early in validation.

## Step 4: Examine the Live Logs

The **Live Logs** panel shows:

```
18:42:01  WARNING  user_id must be an integer
18:42:01  WARNING  user_id must be an integer
18:41:58  INFO     Short URL created with id=15 short_code=k8Jd9s
18:41:55  WARNING  user_id must be an integer
```

**Root Cause Found:** The failing requests are sending `user_id` as a string (e.g., `"user_id": "1"`) instead of an integer (`"user_id": 1`). Our validation correctly rejects these with a 400 error.

## Step 5: Verify via the `/logs` API

```bash
curl http://localhost/logs | python -m json.tool
```

Confirms repeated `"user_id must be an integer"` warnings tied to `POST /urls` requests from the same client IP.

## Step 6: Confirm the `/metrics` API

```bash
curl http://localhost/metrics | python -m json.tool
```

Shows:
- `errors.by_status.400` count matches the spike
- `traffic.top_endpoints` shows `POST /urls` as the highest-traffic endpoint
- `latency.avg_ms` is normal — no server degradation

---

## Diagnosis Summary

| Signal | Value | Interpretation |
|--------|-------|----------------|
| Latency | Normal (avg 15ms) | Server is healthy |
| Traffic | Normal | Requests are flowing |
| Error Rate | 12% (all 400s) | Client sending bad payloads |
| Saturation | Low | No resource bottleneck |

**Root Cause:** A client application was sending `user_id` as a string instead of an integer in `POST /urls` requests. The server's input validation correctly rejected these requests with `400 Bad Request`.

**Resolution:** Notify the client team to fix their payload serialization. No server-side changes required — the system performed exactly as designed, gracefully rejecting bad input.

**Time to Diagnosis:** Under 2 minutes using only the dashboard and logs.
