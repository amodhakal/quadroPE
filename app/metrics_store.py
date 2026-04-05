"""In-memory metrics store for the 4 golden signals.

Tracks per-request latency, traffic counts, error counts, and saturation
(active concurrent requests). Each Gunicorn worker maintains its own copy.
"""

import threading
import time
from collections import defaultdict, deque

_lock = threading.Lock()

MAX_HISTORY = 500

request_log: deque = deque(maxlen=MAX_HISTORY)

traffic_by_endpoint: dict = defaultdict(int)
errors_by_status: dict = defaultdict(int)
total_requests: int = 0
total_errors: int = 0
active_requests: int = 0
peak_active_requests: int = 0
start_time: float = time.time()


def record_request_start():
    global active_requests, peak_active_requests
    with _lock:
        active_requests += 1
        if active_requests > peak_active_requests:
            peak_active_requests = active_requests


def record_request_end(method, path, status_code, latency_ms):
    global total_requests, total_errors, active_requests
    with _lock:
        active_requests -= 1
        total_requests += 1
        endpoint_key = f"{method} {path}"
        traffic_by_endpoint[endpoint_key] += 1

        if status_code >= 400:
            total_errors += 1
            errors_by_status[status_code] += 1

        request_log.append({
            "timestamp": time.time(),
            "method": method,
            "path": path,
            "status": status_code,
            "latency_ms": round(latency_ms, 2),
        })


def get_metrics_snapshot():
    with _lock:
        recent = list(request_log)

    latencies = [r["latency_ms"] for r in recent]
    error_entries = [r for r in recent if r["status"] >= 400]

    if latencies:
        latencies_sorted = sorted(latencies)
        avg_latency = round(sum(latencies) / len(latencies), 2)
        p50 = latencies_sorted[len(latencies_sorted) // 2]
        p95 = latencies_sorted[int(len(latencies_sorted) * 0.95)]
        p99 = latencies_sorted[int(len(latencies_sorted) * 0.99)]
        max_latency = latencies_sorted[-1]
    else:
        avg_latency = p50 = p95 = p99 = max_latency = 0

    uptime = round(time.time() - start_time, 1)
    rps = round(total_requests / uptime, 2) if uptime > 0 else 0
    error_rate = round((total_errors / total_requests) * 100, 2) if total_requests > 0 else 0

    top_endpoints = sorted(traffic_by_endpoint.items(), key=lambda x: -x[1])[:10]

    last_20 = recent[-20:] if recent else []

    return {
        "latency": {
            "avg_ms": avg_latency,
            "p50_ms": p50,
            "p95_ms": p95,
            "p99_ms": p99,
            "max_ms": max_latency,
        },
        "traffic": {
            "total_requests": total_requests,
            "requests_per_second": rps,
            "top_endpoints": [{"endpoint": e, "count": c} for e, c in top_endpoints],
        },
        "errors": {
            "total_errors": total_errors,
            "error_rate_percent": error_rate,
            "by_status": dict(errors_by_status),
        },
        "saturation": {
            "active_requests": active_requests,
            "peak_active_requests": peak_active_requests,
        },
        "uptime_seconds": uptime,
        "recent_requests": [
            {
                "method": r["method"],
                "path": r["path"],
                "status": r["status"],
                "latency_ms": r["latency_ms"],
            }
            for r in reversed(last_20)
        ],
    }
