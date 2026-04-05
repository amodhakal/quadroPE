# Root Cause Analysis — Dashboard-Driven Debugging

## Incident: Elevated Error Rate on URL Creation

**Date:** 2026-04-03  
**Duration:** ~10 minutes  
**Severity:** Low (no data loss, no service outage)

---

## How We Found It

### 1. Alert: Error Rate Spike on Dashboard

The Operations Dashboard (`/dashboard`) showed the **Error Rate** card jump from **0%** to **~12%**. The color changed from green to yellow, immediately drawing attention.

### 2. Narrowing the Scope

We checked each of the **4 Golden Signals** on the dashboard:

| Signal | Reading | What It Told Us |
|--------|---------|----------------|
| **Latency** | Avg: 15ms, p95: 22ms, p99: 210ms | Server response time is normal for successful requests. The p99 spike is from a few slow DB lookups, not the errors themselves (400s return in ~2ms). |
| **Traffic** | 847 total requests, 4.2 req/s | Traffic volume is normal — not a DDoS or traffic spike issue. |
| **Errors** | 12% error rate, 102 errors, all HTTP 400 | All errors are 400 Bad Request — no 500s means the server itself is stable. |
| **Saturation** | Active: 1, Peak: 3 | The server has plenty of capacity. This isn't a resource exhaustion issue. |

### 3. Identifying the Failing Endpoint

The **Top Endpoints by Traffic** bar chart showed `POST /urls` as the busiest endpoint. Cross-referencing with the **Recent Requests** table, we saw that `POST /urls` requests were alternating between `201 Created` and `400 Bad Request`.

### 4. Reading the Logs

The **Live Logs** panel on the dashboard showed repeated warnings:
```
WARNING  user_id must be an integer
```

All tied to `POST /urls`. This confirmed the error was input validation — not a bug, not a crash.

### 5. Confirming via API

```bash
# Get structured metrics
curl http://localhost/metrics

# Get recent log entries
curl http://localhost/logs
```

Both confirmed the dashboard's visual data programmatically.

---

## Root Cause

A client application was serializing `user_id` as a JSON string (`"1"`) instead of an integer (`1`) in `POST /urls` payloads. The server's input validation layer correctly rejected these requests with:

```json
{"error": "user_id must be an integer"}
```

---

## Resolution

- **Immediate:** Notified the client team about the payload format issue.
- **No server changes needed** — the validation worked exactly as designed.
- **Verified:** After the client fix, the error rate on the dashboard dropped back to 0%.

---

## What the Dashboard Gave Us

Without the dashboard, debugging this would have required:
1. SSH into a server
2. Manually grep through log files
3. Count error rates by hand
4. Guess which endpoint was affected

With the dashboard, we had the answer in **under 2 minutes** by visually correlating:
- Error Rate spike (something is wrong)
- Error Breakdown chart (it's all 400s, not 500s)
- Top Endpoints chart (it's `POST /urls`)
- Live Logs (it's a `user_id` type mismatch)

The dashboard turned a potentially 30-minute investigation into a 2-minute visual scan.

---

## Prevention

- Input validation is already in place and working correctly.
- The dashboard provides continuous visibility — future issues will be caught immediately.
- Added this incident to `docs/failure-manual.md` under "Invalid Client Input."
